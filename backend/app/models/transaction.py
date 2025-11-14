from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    account_id = Column(String, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=True)
    
    date = Column(DateTime, index=True, default=datetime.utcnow)
    description = Column(String)
    amount = Column(Float)
    
    category = Column(String, index=True)
    category_confidence = Column(Float)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    
    merchant_name = Column(String, nullable=True)
    pending = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
