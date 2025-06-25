from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from typing import Optional, List
from Backend.logic import insert_transaction, fetch_all_transactions, fetch_monthly_summary
from Backend.db import create_table
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    date: constr(pattern=r'^\d{4}-\d{2}-\d{2}$')
    type: constr(pattern='^(income|expense)$')
    category: str
    amount: float = Field(gt=0)
    description: Optional[str] = ""

@app.on_event("startup")
def startup_event():
    create_table()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Finance Tracker API!"}


@app.post("/transactions")
def add_transaction(tx: Transaction):
    success = insert_transaction(tx.date, tx.type, tx.category, tx.amount, tx.description)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add transaction")
    return {"message": "Transaction added", "transaction": tx.dict()}

@app.get("/transactions", response_model=List[Transaction])
def get_transactions():
    df = fetch_all_transactions()
    return df.to_dict(orient="records")

@app.get("/summary")
def get_summary():
    summary = fetch_monthly_summary()
    if summary.empty:
        return {"message": "No data available"}
    summary.index = summary.index.astype(str)
    return summary.to_dict(orient="records")
