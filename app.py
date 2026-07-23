import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("web_expenses.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, category TEXT, amount REAL, description TEXT
        )
    ''')
    cursor.execute('CREATE TABLE IF NOT EXISTS savings_vault (total_saved REAL)')
    cursor.execute("SELECT COUNT(*) FROM savings_vault")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO savings_vault VALUES (0.0)")
    conn.commit()
    conn.close()

# Initialize Database
init_db()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Modern Expense Tracker", page_icon="💰", layout="wide")

st.title("💰 Modern Expense Tracker Dashboard")

# --- CALCULATE ANALYTICS ---
conn = sqlite3.connect("web_expenses.db")
cursor = conn.cursor()
current_year = datetime.now().strftime("%Y")
current_month = datetime.now().strftime("%Y-%m")

cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f"{current_month}%",))
month_total = cursor.fetchone()[0] or 0.0

cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f"{current_year}%",))
year_total = cursor.fetchone()[0] or 0.0

cursor.execute("SELECT SUM(amount) FROM expenses")
all_time_total = cursor.fetchone()[0] or 0.0

cursor.execute("SELECT total_saved FROM savings_vault")
saved_balance = cursor.fetchone()[0] or 0.0
conn.close()

# --- ROW 1: ANALYTICAL CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("THIS MONTH", f"₹{month_total:,.2f}")
col2.metric("THIS YEAR", f"₹{year_total:,.2f}")
col3.metric("ALL TIME TOTAL", f"₹{all_time_total:,.2f}")
col4.metric("SAVINGS VAULT BALANCE", f"₹{saved_balance:,.2f}")

st.divider()

# --- ROW 2: INPUT CONTROLS & LOGS ---
input_col, status_col = st.columns(2)

with input_col:
    st.subheader("📝 Record New Expense Entry")
    
    with st.form("expense_form", clear_on_submit=True):
        category = st.selectbox(
            "Category", 
            ["Groceries", "Stationary", "Taxes", "Rent/Bills", "Entertainment", "Transport", "Other"]
        )
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
        remarks = st.text_input("Remarks / Description", placeholder="Spent on...")
        
        submitted = st.form_submit_button("Add Expense", type="primary")

        if submitted:
            if amount > 0:
                date_str = datetime.now().strftime("%Y-%m-%d")
                conn = sqlite3.connect("web_expenses.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                    (date_str, category, amount, remarks)
                )
                conn.commit()
                conn.close()
                st.session_state["status_msg"] = f"✅ Successfully added ₹{amount:.2f} under {category}!"
                st.rerun()
            else:
                st.session_state["status_msg"] = "❌ Error: Please enter an amount greater than 0."

with status_col:
    st.subheader("🔔 System Log Status")
    status = st.session_state.get(
        "status_msg", 
        "Click 'Add Expense' to log transactions and update live data cards."
    )
    st.info(status)

# --- RECENT TRANSACTIONS TABLE ---
st.divider()
st.subheader("📊 Transaction History")
conn = sqlite3.connect("web_expenses.db")
df = pd.read_sql_query("SELECT date AS Date, category AS Category, amount AS 'Amount (₹)', description AS Description FROM expenses ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("No transactions recorded yet.")

# --- FOOTER / CREDITS ---
st.divider()
st.markdown("**By: Nipurna Bhatta, Sumedh Dhungana, Aarohi Rai, Yashvi Bijukchhe**")
