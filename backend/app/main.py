from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel, EmailStr
import os

from app.core.database import get_db, engine, Base
from app.models.transaction import Transaction
from app.models.user import User
from app.ml.categorizer import TransactionCategorizer
from app.ml.forecaster import CashFlowForecaster

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance AI Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

categorizer = TransactionCategorizer()
forecaster = CashFlowForecaster()

# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TransactionCreate(BaseModel):
    description: str
    amount: float
    date: datetime

class TransactionResponse(BaseModel):
    id: int
    description: str
    amount: float
    date: datetime
    category: str
    category_confidence: float
    is_anomaly: bool
    
    class Config:
        from_attributes = True

# Routes
@app.get("/")
def root():
    return {"name": "Finance AI Platform", "version": "1.0.0", "status": "operational"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/auth/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(email=user_data.email, hashed_password=user_data.password, full_name=user_data.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "full_name": user.full_name}

@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc()).limit(100).all()

@app.post("/api/transactions", response_model=TransactionResponse)
def create_transaction(txn_data: TransactionCreate, db: Session = Depends(get_db)):
    categorization = categorizer.predict(txn_data.description)
    is_anomaly = abs(txn_data.amount) > 150 and txn_data.amount < 0
    
    transaction = Transaction(
        description=txn_data.description,
        amount=txn_data.amount,
        date=txn_data.date,
        account_id="demo_account",
        category=categorization['category'],
        category_confidence=categorization['confidence'],
        is_anomaly=is_anomaly,
        anomaly_score=abs(txn_data.amount) / 150.0 if is_anomaly else 0.0
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/api/insights")
def get_insights(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    insights = []
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
    
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
        insights.append({
            "type": "savings",
            "title": "Savings Rate",
            "description": f"You're saving {savings_rate:.1f}% of your income",
            "severity": "success" if savings_rate > 20 else "warning"
        })
    
    category_spending = {}
    for t in transactions:
        if t.amount < 0:
            category_spending[t.category] = category_spending.get(t.category, 0) + abs(t.amount)
    
    if category_spending:
        top_category = max(category_spending.items(), key=lambda x: x[1])
        insights.append({
            "type": "spending",
            "title": "Top Spending Category",
            "description": f"You spent ${top_category[1]:.2f} on {top_category[0]}",
            "severity": "info"
        })
    
    return insights

@app.get("/api/forecast")
def get_forecast(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    txn_data = [{'date': t.date, 'amount': t.amount} for t in transactions]
    return forecaster.forecast(txn_data, 5234.67, 90)

@app.post("/api/demo/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """Seed database with demo transactions"""
    demo_txns = [
        ("Salary Deposit", 4500, -30),
        ("Whole Foods", -85.32, -28),
        ("Starbucks", -6.75, -25),
        ("Amazon", -127.45, -24),
        ("Uber", -23.50, -20),
        ("Netflix", -15.99, -15),
        ("Target", -67.89, -10),
        ("Gas Station", -45.00, -7),
        ("Restaurant", -45.60, -3),
    ]
    
    for desc, amt, days in demo_txns:
        date = datetime.now() + timedelta(days=days)
        cat = categorizer.predict(desc)
        txn = Transaction(
            description=desc,
            amount=amt,
            date=date,
            account_id="demo",
            category=cat['category'],
            category_confidence=cat['confidence'],
            is_anomaly=abs(amt) > 150 and amt < 0
        )
        db.add(txn)
    
    db.commit()
    return {"message": "Demo data seeded successfully", "count": len(demo_txns)}
