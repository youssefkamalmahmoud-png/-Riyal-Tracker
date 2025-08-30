 
import streamlit as st
import sqlite3
import datetime

# ----------------- Database Setup -----------------
conn = sqlite3.connect("riyals.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              type TEXT,
              amount REAL,
              note TEXT,
              date TEXT)''')
conn.commit()

# ----------------- Helper Functions -----------------
def add_transaction(t_type, amount, note):
    date = datetime.date.today().strftime("%Y-%m-%d")
    c.execute("INSERT INTO transactions (type, amount, note, date) VALUES (?, ?, ?, ?)", 
              (t_type, amount, note, date))
    conn.commit()

def get_total():
    c.execute("SELECT SUM(amount) FROM transactions")
    total = c.fetchone()[0]
    return total if total else 0

def get_transactions():
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    return c.fetchall()

# ----------------- UI -----------------
st.set_page_config(page_title="Riyal Tracker", page_icon="💰", layout="centered")
st.title("💰 Riyal Tracker")

menu = ["Add Expense", "Add Eid Money", "View Balance", "History"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Expense":
    st.subheader("➖ Add Expense")
    amount = st.number_input("Amount", min_value=1.0, step=1.0)
    note = st.text_input("Note")
    if st.button("Save Expense"):
        add_transaction("expense", -amount, note)
        st.success("Expense added successfully!")

elif choice == "Add Eid Money":
    st.subheader("🎁 Add Eid Money")
    amount = st.number_input("Amount", min_value=1.0, step=1.0)
    giver = st.text_input("From (giver's name)")
    if st.button("Save Eid Money"):
        add_transaction("eid", amount, f"From {giver}")
        st.success("Eid money added successfully!")

elif choice == "View Balance":
    st.subheader("📊 Balance")
    total = get_total()
    st.metric("Current Balance", f"{total:.2f} ﷼")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Expected for Month"):
            st.info(f"You should have about {total:.2f} ﷼ at the end of the month.")
    with col2:
        if st.button("Expected for Year"):
            st.info(f"You should have about {total*12:.2f} ﷼ at the end of the year.")

elif choice == "History":
    st.subheader("📜 Transaction History")
    rows = get_transactions()
    for r in rows:
        st.write(f"{r[4]} | {r[1]} | {r[2]} ﷼ | {r[3]}")
