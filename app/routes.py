from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import time

from app.database import SessionLocal
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_transaction(transaction_id: str):
    db = SessionLocal()
    try:
        time.sleep(30)  # simulate external processing

        txn = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

        if txn:
            txn.status = "PROCESSED"
            txn.processed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

@router.post(
    "/v1/webhooks/transactions",
    status_code=status.HTTP_202_ACCEPTED
)
def receive_webhook(
    payload: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing = db.query(Transaction).filter(
        Transaction.transaction_id == payload.transaction_id
    ).first()

    if existing:
        # Idempotent behavior
        return {"message": "Already received"}

    txn = Transaction(**payload.dict())
    db.add(txn)
    db.commit()

    background_tasks.add_task(process_transaction, payload.transaction_id)

    return {"message": "Accepted"}

@router.get(
    "/v1/transactions/{transaction_id}",    
    response_model=TransactionResponse
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    txn = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return txn  
