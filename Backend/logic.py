import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from Backend.db import engine, Session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def insert_transaction(date: str, ttype: str, category: str, amount: float, description: str) -> bool:
    try:
        if ttype not in ('income', 'expense'):
            raise ValueError("Type must be 'income' or 'expense'")
        if amount < 0:
            raise ValueError("Amount must be positive")
        datetime.strptime(date, "%Y-%m-%d")
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return False

    category = category.strip().title()
    description = description.strip()

    session = Session()
    try:
        session.execute(
            text("""
                INSERT INTO transactions (date, type, category, amount, description)
                VALUES (:date, :ttype, :category, :amount, :description)
            """),
            {"date": date, "ttype": ttype, "category": category, "amount": amount, "description": description},
        )
        session.commit()
        logging.info("Transaction inserted successfully.")
        return True
    except Exception as e:
        session.rollback()
        logging.error(f"DB insert error: {e}")
        return False
    finally:
        session.close()

def fetch_all_transactions() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM transactions ORDER BY date", engine)

def fetch_monthly_summary() -> pd.DataFrame:
    df = fetch_all_transactions()
    if df.empty:
        logging.warning("No transactions to summarize.")
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    summary = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
    summary['Net Savings'] = summary.get('income', 0) - summary.get('expense', 0)

    # Convert PeriodIndex to string and reset index
    summary.index = summary.index.astype(str)
    summary.reset_index(inplace=True)
    return summary

def plot_summary(summary: pd.DataFrame) -> None:
    if summary.empty:
        logging.warning("No data available for plotting.")
        return
    ax = summary[['income', 'expense', 'Net Savings']].plot(kind='bar', figsize=(10, 6))
    ax.set_title("Monthly Income, Expenses, and Net Savings")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.show()
