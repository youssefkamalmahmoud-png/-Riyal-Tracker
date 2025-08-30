import streamlit as st
import sqlite3
import datetime

# ------------------ Database Setup ------------------
conn = sqlite3.connect("riyaltacker.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                amount REAL,
                date TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS eid_money (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giver TEXT,
                amount REAL,
                date TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount REAL,
                date TEXT
            )""")

conn.commit()

# ------------------ Constants ------------------
POCKET_MONEY = 50  # fixed monthly pocket money

# ------------------ Helper Functions ------------------
def add_expense(item, amount):
    c.execute("INSERT INTO expenses (item, amount, date) VALUES (?, ?, ?)",
              (item, amount, datetime.date.today().isoformat()))
    conn.commit()

def remove_expense(expense_id):
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()

def get_expenses():
    c.execute("SELECT * FROM expenses")
    return c.fetchall()

def add_eid_money(giver, amount):
    c.execute("INSERT INTO eid_money (giver, amount, date) VALUES (?, ?, ?)",
              (giver, amount, datetime.date.today().isoformat()))
    conn.commit()

def get_eid_money():
    c.execute("SELECT * FROM eid_money")
    return c.fetchall()

def add_reward(type_name, amount):
    c.execute("INSERT INTO rewards (type, amount, date) VALUES (?, ?, ?)",
              (type_name, amount, datetime.date.today().isoformat()))
    conn.commit()

def get_rewards():
    c.execute("SELECT * FROM rewards")
    return c.fetchall()

def calculate_expected(period="month"):
    total = 0
    if period == "month":
        total += POCKET_MONEY
    elif period == "year":
        total += POCKET_MONEY * 12

    # Rewards
    rewards = get_rewards()
    for r in rewards:
        if r[1] == "weekly_10":
            if period == "month":
                total += 40  # 4 weeks per month
            elif period == "year":
                total += 520
        elif r[1] == "monthly_50":
            if period == "month":
                total += 50
            elif period == "year":
                total += 600

    # Eid money
    eid_list = get_eid_money()
    for e in eid_list:
        total += e[2]

    # Subtract expenses
    expenses = get_expenses()
    for exp in expenses:
        total -= exp[2]

    return total

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Riyal Tracker", page_icon="💰", layout="centered")

st.title("💰 Riyal Tracker")

menu = st.sidebar.radio("Menu", ["Home", "Add Expense", "Eid Money", "Rewards", "Expenses List"])

if menu == "Home":
    st.subheader("Expected Balance")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Month"):
            expected = calculate_expected("month")
            st.success(f"💰 Expected for this month: {expected:.2f} ﷼")
    with col2:
        if st.button("📆 Year"):
            expected = calculate_expected("year")
            st.success(f"💰 Expected for this year: {expected:.2f} ﷼")

elif menu == "Add Expense":
    st.subheader("➕ Add Expense")
    item = st.text_input("Item")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    if st.button("Add"):
        if item and amount > 0:
            add_expense(item, amount)
            st.success(f"Added expense: {item} - {amount} ﷼")

elif menu == "Eid Money":
    st.subheader("🎉 Add Eid Money")
    giver = st.text_input("Who gave you the money?")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    if st.button("Add Eid Money"):
        if giver and amount > 0:
            add_eid_money(giver, amount)
            st.success(f"Added Eid gift from {giver}: {amount} ﷼")

elif menu == "Rewards":
    st.subheader("🌟 Rewards")
    reward_option = st.radio("Choose Trash Reward", ["None", "10 ﷼ weekly", "50 ﷼ monthly"])
    if st.button("Save Reward"):
        if reward_option == "10 ﷼ weekly":
            add_reward("weekly_10", 10)
            st.success("Reward added: 10 ﷼ per week")
        elif reward_option == "50 ﷼ monthly":
            add_reward("monthly_50", 50)
            st.success("Reward added: 50 ﷼ per month")
