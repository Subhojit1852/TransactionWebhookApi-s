from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    source_account = Column(String)
    destination_account = Column(String)
    amount = Column(Float)
    currency = Column(String)

    status = Column(String, default="PROCESSING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
