import streamlit as st
import sqlite3
import datetime

# --- Database setup ---
conn = sqlite3.connect('pocket_money.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pocket_money REAL,
    trash_week REAL,
    trash_month REAL
)''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    amount REAL,
    period TEXT,
    date TEXT
)''')
conn.commit()

# --- Functions ---
def get_settings():
    cursor.execute('SELECT pocket_money, trash_week, trash_month FROM settings ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        return result
    else:
        return (0,0,0)

def set_settings(pocket_money, trash_week, trash_month):
    cursor.execute('INSERT INTO settings (pocket_money, trash_week, trash_month) VALUES (?, ?, ?)',
                   (pocket_money, trash_week, trash_month))
    conn.commit()

def add_expense(name, category, amount, period):
    date = datetime.date.today().isoformat()
    cursor.execute('INSERT INTO expenses (name, category, amount, period, date) VALUES (?, ?, ?, ?, ?)',
                   (name, category, amount, period, date))
    conn.commit()

def remove_expense(expense_id):
    cursor.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
    conn.commit()

def get_expenses(period):
    cursor.execute('SELECT id, name, category, amount, date FROM expenses WHERE period=? ORDER BY id DESC', (period,))
    return cursor.fetchall()

def get_total_expenses(period):
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE period=?', (period,))
    result = cursor.fetchone()[0]
    return result if result else 0

# --- App UI ---
st.set_page_config(page_title='Riyal Tracker', page_icon='💰', layout='centered')
st.title('💰 Riyal Tracker')

# Settings
st.subheader('⚙️ Settings')
current_pocket, trash_week, trash_month = get_settings()
pocket_money = st.number_input('Set your main pocket money (﷼)', min_value=0.0, value=float(current_pocket))
trash_w = st.number_input('Weekly trash milestone (﷼)', min_value=0.0, value=float(trash_week))
trash_m = st.number_input('Monthly trash milestone (﷼)', min_value=0.0, value=float(trash_month))
if st.button('Save / Change Settings'):
    set_settings(pocket_money, trash_w, trash_m)
    st.success('Settings updated!')
    st.experimental_rerun()

# Period selection
st.subheader('📅 Select period')
period = st.radio('Choose period', ['Week', 'Month', 'Year'])

# Add expense
st.subheader('➕ Add Expense')
name = st.text_input('Item name')
category = st.selectbox('Category', ['Food', 'Online Shopping', 'Stores', 'Toys', 'Other'])
amount = st.number_input('Amount (﷼)', min_value=0.0, step=0.5)
if st.button('Add Expense'):
    if name and amount>0:
        add_expense(name, category, amount, period)
        st.success(f'Added {name} to {period}')
        st.experimental_rerun()

# Display remaining balance
st.subheader('💵 Remaining Balance')
total_exp = get_total_expenses(period)
if period=='Week':
    base = pocket_money/4 if pocket_money>0 else 0  # approximate weekly from monthly
    trash = trash_w
elif period=='Month':
    base = pocket_money
    trash = trash_m
else:  # Year
    base = pocket_money*12  # approximate yearly from monthly
    trash = trash_m*12

remaining = base - total_exp - trash
st.metric(f'{period} Balance', f'{remaining} ﷼', f'-{total_exp+trash} ﷼ spent including trash')

# Show expenses
st.subheader(f'📋 {period} Expenses')
expenses = get_expenses(period)
for exp in expenses:
    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1:
        st.write(exp[1])
    with col2:
        st.write(exp[2])
    with col3:
        st.write(f'{exp[3]} ﷼')
    with col4:
        if st.button('❌', key=exp[0]):
            remove_expense(exp[0])
            st.experimental_rerun()

# --- Shortcut / Home screen instructions ---
st.markdown('### 📱 Add to Home Screen')
st.markdown('1. Open this app in your mobile browser.')
st.markdown('2. Tap the browser menu (⋮ or share icon).')
st.markdown('3. Select "Add to Home screen".')
st.markdown('4. Now you can open it like a real app!')
