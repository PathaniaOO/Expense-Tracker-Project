import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Finance Tracker", layout="wide")

API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")

st.title("Financial Expense Tracker")

with st.form("Add Transaction"):
    date = st.date_input("Date")
    ttype = st.selectbox("Type", ["income", "expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        if not category.strip():
            st.warning("Category cannot be empty.")
        else:
            data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": ttype,
                "category": category.strip(),
                "amount": amount,
                "description": description.strip(),
            }
            response = requests.post(f"{API_URL}/transactions", json=data)
            if response.status_code == 200:
                st.success("Transaction added successfully")
            else:
                st.error(f"Failed to add transaction: {response.json().get('detail')}")

if st.button("Show Monthly Summary"):
    response = requests.get(f"{API_URL}/summary")
    if response.status_code == 200:
        summary_data = response.json()
        if "message" in summary_data:
            st.info(summary_data["message"])
        else:
            df = pd.DataFrame(summary_data)
            
            # Ensure columns exist
            for col in ['income', 'expense', 'Net Savings']:
                if col not in df.columns:
                    df[col] = 0
            st.dataframe(df)
            df_plot = df.set_index('month')
            df_plot[['income', 'expense', 'Net Savings']].plot(kind='bar', figsize=(10, 6))
            plt.xticks(rotation=45)
            plt.title("Monthly Income, Expenses, and Net Savings")
            plt.grid(axis='y')
            st.pyplot(plt)
    else:
        st.error("Failed to fetch summary")

if st.checkbox("Show All Transactions"):
    response = requests.get(f"{API_URL}/transactions")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if df.empty:
            st.info("No transactions available.")
        else:
            st.dataframe(df)
    else:
        st.error("Failed to fetch transactions")
