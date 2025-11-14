#!/usr/bin/env python3
"""
Finance AI Platform - Docker Setup Script
This script creates all necessary files and directories for the project
"""

import os
import sys

def create_file(path, content):
    """Create a file with given content"""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"✅ Created: {path}")

def create_project_structure():
    """Create all project files and directories"""
    
    print("🚀 Creating Finance AI Platform project structure...\n")
    
    # Create directories
    directories = [
        'backend/app/api',
        'backend/app/core',
        'backend/app/models',
        'backend/app/ml',
        'backend/app/services',
        'backend/scripts',
        'backend/models',
        'frontend/src/api',
        'frontend/src/components',
        'frontend/src/pages',
        'frontend/public',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        if directory.startswith('backend/app'):
            # Create __init__.py for Python packages
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
    
    print("📁 Directory structure created\n")
    
    # ==================== DOCKER FILES ====================
    
    # docker-compose.yml
    create_file('docker-compose.yml', '''
version: '3.8'

services:
  db:
    image: postgres:14
    container_name: finance-ai-db
    environment:
      POSTGRES_DB: finance_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: finance-ai-redis
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    container_name: finance-ai-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/finance_ai
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
''')

    # Backend Dockerfile
    create_file('backend/Dockerfile', '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''')

    # Backend requirements.txt
    create_file('backend/requirements.txt', '''
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic[email]==2.5.0
pydantic-settings==2.1.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
redis==5.0.1
pytest==7.4.3
httpx==0.25.2
''')

    # Backend .env
    create_file('backend/.env', '''
DATABASE_URL=postgresql://postgres:password@db:5432/finance_ai
REDIS_URL=redis://redis:6379/0
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
''')

    # Backend .dockerignore
    create_file('backend/.dockerignore', '''
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.env
.venv
*.log
.git
.gitignore
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info
''')

    # ==================== BACKEND CODE ====================
    
    # Database configuration
    create_file('backend/app/core/database.py', '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/finance_ai")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

    # User model
    create_file('backend/app/models/user.py', '''
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="user")
''')

    # Transaction model
    create_file('backend/app/models/transaction.py', '''
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
''')

    # ML Categorizer (simplified version)
    create_file('backend/app/ml/categorizer.py', '''
import pickle
import os

class TransactionCategorizer:
    def __init__(self):
        self.rules = {
            'Groceries': ['whole foods', 'trader joe', 'safeway', 'kroger', 'walmart', 'grocery'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza', 'chipotle'],
            'Transportation': ['uber', 'lyft', 'gas', 'parking', 'metro', 'transit'],
            'Entertainment': ['netflix', 'spotify', 'hulu', 'movie', 'theater', 'concert'],
            'Utilities': ['electric', 'water', 'internet', 'phone', 'verizon', 'at&t'],
            'Shopping': ['amazon', 'target', 'best buy', 'mall', 'clothing'],
            'Healthcare': ['pharmacy', 'doctor', 'medical', 'hospital', 'cvs', 'walgreens'],
            'Income': ['salary', 'paycheck', 'deposit', 'transfer in', 'direct dep']
        }
    
    def predict(self, description):
        desc_lower = description.lower()
        for category, keywords in self.rules.items():
            if any(kw in desc_lower for kw in keywords):
                return {'category': category, 'confidence': 0.85}
        return {'category': 'Other', 'confidence': 0.65}
    
    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    def load(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                loaded = pickle.load(f)
                self.rules = loaded.rules
''')

    # ML Forecaster
    create_file('backend/app/ml/forecaster.py', '''
import numpy as np
from datetime import datetime, timedelta

class CashFlowForecaster:
    def forecast(self, transactions, current_balance, days=90):
        income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        expenses = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
        
        daily_income = income / 30
        daily_expenses = expenses / 30
        daily_net = daily_income - daily_expenses
        
        forecast_data = []
        balance = current_balance
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            balance += daily_net + np.random.normal(0, 10)
            
            forecast_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted': round(balance, 2),
                'upper': round(balance * 1.15, 2),
                'lower': round(balance * 0.85, 2)
            })
        
        return forecast_data
''')

    # Main FastAPI app (compact version)
    create_file('backend/app/main.py', '''
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
''')

    # ==================== HELPER SCRIPTS ====================
    
    # Makefile
    create_file('Makefile', '''
.PHONY: help build start stop restart logs clean seed

help:
\t@echo "Finance AI Platform - Docker Commands"
\t@echo "======================================"
\t@echo "make build   - Build Docker images"
\t@echo "make start   - Start all services"
\t@echo "make stop    - Stop all services"
\t@echo "make restart - Restart all services"
\t@echo "make logs    - View logs"
\t@echo "make seed    - Seed demo data"
\t@echo "make clean   - Remove containers and volumes"

build:
\t@echo "🔨 Building Docker images..."
\tdocker-compose build

start:
\t@echo "🚀 Starting services..."
\tdocker-compose up -d
\t@echo "✅ Services started!"
\t@echo "Backend API: http://localhost:8000"
\t@echo "API Docs: http://localhost:8000/docs"
\t@echo ""
\t@echo "Wait 10 seconds for DB to initialize, then run: make seed"

stop:
\t@echo "🛑 Stopping services..."
\tdocker-compose down

restart:
\t@echo "🔄 Restarting services..."
\tdocker-compose restart

logs:
\tdocker-compose logs -f

seed:
\t@echo "🌱 Seeding demo data..."
\tcurl -X POST http://localhost:8000/api/demo/seed
\t@echo ""
\t@echo "✅ Demo data seeded! Check http://localhost:8000/api/transactions"

clean:
\t@echo "🧹 Cleaning up..."
\tdocker-compose down -v
\trm -rf backend/__pycache__ backend/app/__pycache__
''')

    # README
    create_file('README.md', '''
# 🚀 Finance AI Platform

AI-Powered Personal Finance Insights Platform with Docker

## Quick Start

1. **Install Docker Desktop** from docker.com

2. **Build and start services:**
   ```bash
   make build
   make start
   ```

3. **Wait 10 seconds**, then seed demo data:
   ```bash
   make seed
   ```

4. **Access the app:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Commands

- `make start` - Start all services
- `make stop` - Stop services
- `make restart` - Restart services
- `make logs` - View logs
- `make seed` - Add demo data
- `make clean` - Remove everything

## API Endpoints

- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `GET /api/insights` - Get AI insights
- `GET /api/forecast` - Get cash flow forecast
- `POST /api/demo/seed` - Seed demo data

## Next Steps

1. Connect to Plaid for real bank data
2. Train custom ML models
3. Build React frontend
4. Deploy to production

## Troubleshooting

**Port 5432 in use?**
```bash
docker-compose down
# Stop local PostgreSQL
```

**Database not ready?**
```bash
docker-compose logs db
# Wait for "database system is ready to accept connections"
```

**Start fresh:**
```bash
make clean
make build
make start
```
''')

    # .gitignore
    create_file('.gitignore', '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
*.log

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
backend/models/*.pkl
backend/logs/*.log
backend/data/*
!backend/data/.gitkeep
''')

    print("\n✅ All files created successfully!")
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Make sure Docker Desktop is running")
    print("2. Run: make build")
    print("3. Run: make start")
    print("4. Wait 10 seconds, then run: make seed")
    print("5. Visit: http://localhost:8000/docs")
    print("\n🎉 You're ready to go!")

if __name__ == "__main__":
    create_project_structure()