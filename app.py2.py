
import streamlit as st
import sqlite3
import datetime

# Database setup
conn = sqlite3.connect("pocket_money.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    amount REAL,
    date TEXT
)
""")
conn.commit()

# Monthly budget (change it as you like)
MONTHLY_BUDGET = 1000

# Functions
def get_total_spent():
    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()[0]
    return result if result else 0

def add_expense(name, amount):
    date = datetime.date.today().isoformat()
    cursor.execute("INSERT INTO expenses (name, amount, date) VALUES (?, ?, ?)", (name, amount, date))
    conn.commit()

def remove_expense(expense_id):
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()

def get_expenses():
    cursor.execute("SELECT id, name, amount, date FROM expenses ORDER BY id DESC")
    return cursor.fetchall()

# Web App UI
st.title("💰 Riyal Tracker")
st.write("Track your pocket money and expenses easily.")

# Balance
spent = get_total_spent()
balance = MONTHLY_BUDGET - spent
st.metric("Remaining Balance", f"{balance} ﷼", f"-{spent} ﷼ spent")

# Add expense
st.subheader("➕ Add Expense")
name = st.text_input("Item")
amount = st.number_input("Amount (﷼)", min_value=0.0, step=0.5)
if st.button("Add"):
    if name and amount > 0:
        add_expense(name, amount)
        st.success("Expense added!")
        st.experimental_rerun()

# Expense list
st.subheader("📋 Expense List")
expenses = get_expenses()
for exp in expenses:
    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1:
        st.write(exp[1])
    with col2:
        st.write(f"{exp[2]} ﷼")
    with col3:
        st.write(exp[3])
    with col4:
        if st.button("❌", key=exp[0]):
            remove_expense(exp[0])
            st.experimental_rerun()
