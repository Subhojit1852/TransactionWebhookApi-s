from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import threading
import time

from app.database import SessionLocal
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionResponse

router = APIRouter()


# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Background Worker Logic
# -----------------------------
def process_transaction_async(transaction_id: str):
    """
    Runs completely outside the request lifecycle.
    Safe for Render free tier.
    """
    db = SessionLocal()
    try:
        # Simulate slow external processing
        time.sleep(30)

        txn = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )

        if txn and txn.status != "PROCESSED":
            txn.status = "PROCESSED"
            txn.processed_at = datetime.utcnow()
            db.commit()

    except Exception as e:
        # In real prod: log this
        db.rollback()
    finally:
        db.close()


# -----------------------------
# Webhook Endpoint (FAST)
# -----------------------------
@router.post(
    "/v1/webhooks/transactions",
    status_code=status.HTTP_202_ACCEPTED
)
def receive_webhook(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Production-grade webhook behavior:
    - Respond immediately
    - Idempotent
    - Offload processing
    """

    # Idempotency check (cheap query)
    existing = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == payload.transaction_id)
        .first()
    )

    if existing:
        return {"message": "Already received"}

    # Minimal DB write (fast)
    txn = Transaction(
        **payload.dict(),
        status="RECEIVED",
        processed_at=None
    )
    db.add(txn)
    db.commit()

    # Fire-and-forget background thread
    threading.Thread(
        target=process_transaction_async,
        args=(payload.transaction_id,),
        daemon=True
    ).start()

    # Return immediately — webhook SLA safe
    return {"message": "Accepted"}


# -----------------------------
# Query Endpoint
# -----------------------------
@router.get(
    "/v1/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    txn = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .first()
    )

    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return txn
