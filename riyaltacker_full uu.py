import streamlit as st
import sqlite3
import datetime

# --- Database setup ---
conn = sqlite3.connect('pocket_money.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trash_type TEXT,
    font TEXT,
    font_size INT,
    bg_color TEXT,
    text_color TEXT
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
cursor.execute('''
CREATE TABLE IF NOT EXISTS eid_money (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    giver TEXT,
    amount REAL
)''')
conn.commit()

# --- Functions ---
def get_settings():
    cursor.execute('SELECT trash_type, font, font_size, bg_color, text_color FROM settings ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        return result
    else:
        return ('None', 'Arial', 40, '#FFFFFF', '#000000')

def set_settings(trash_type, font, font_size, bg_color, text_color):
    cursor.execute('INSERT INTO settings (trash_type, font, font_size, bg_color, text_color) VALUES (?, ?, ?, ?, ?)',
                   (trash_type, font, font_size, bg_color, text_color))
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

def add_eid_money(giver, amount):
    cursor.execute('INSERT INTO eid_money (giver, amount) VALUES (?, ?)', (giver, amount))
    conn.commit()

def get_total_eid():
    cursor.execute('SELECT SUM(amount), GROUP_CONCAT(giver, ", ") FROM eid_money')
    result = cursor.fetchone()
    if result[0]:
        return result[0], result[1]
    return 0, ''

# --- Streamlit App ---
st.set_page_config(page_title='Riyal Tracker', page_icon='💰', layout='centered')

# Sidebar (Three dots menu)
st.sidebar.title('⚙️ Menu')
menu = st.sidebar.radio('Options', ['Main', 'Settings', 'Eid Money'])

# --- Get Settings ---
trash_type, font, font_size, bg_color, text_color = get_settings()
pocket_money = 50  # fixed pocket money

# Apply Colors and Fonts
st.markdown(f"<style>body{{background-color:{bg_color}; color:{text_color}; font-family:{font};}}</style>", unsafe_allow_html=True)

# Use session_state for safe rerun
if 'rerun' not in st.session_state:
    st.session_state['rerun'] = False
if 'selected_period' not in st.session_state:
    st.session_state['selected_period'] = 'Week'

# --- Main Interface ---
if menu == 'Main':
    # Trash selection
    trash_type = st.radio('اختيار مكافأة رمي الزبالة', ['None', '10 ﷼ في الأسبوع', '50 ﷼ في الشهر'], index=['None','10 ﷼ في الأسبوع','50 ﷼ في الشهر'].index(trash_type))

    # Period buttons
    st.subheader('اختر الفترة:')
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Week'):
            st.session_state['selected_period'] = 'Week'
    with col2:
        if st.button('Month'):
            st.session_state['selected_period'] = 'Month'
    with col3:
        if st.button('Year'):
            st.session_state['selected_period'] = 'Year'

    period = st.session_state['selected_period']

    # Calculate trash amount
    if trash_type == 'None':
        trash = 0
    elif trash_type == '10 ﷼ في الأسبوع':
        trash = 10 if period=='Week' else 10*4 if period=='Month' else 10*52
    else:
        trash = 50 if period=='Month' else 50*12 if period=='Year' else 50/4

    # Calculate remaining balance including Eid money
    total_exp = get_total_expenses(period)
    total_eid, eid_givers = get_total_eid()
    remaining = round(pocket_money - total_exp - trash + total_eid,2)

    # Display main balance with trash and Eid money included
    st.markdown(f"<h1 style='font-size:{font_size}px;'>💰 المبلغ المتوقع للفترة: {remaining:.2f} ﷼ ({eid_givers})</h1>", unsafe_allow_html=True)

    # Add Expense
    st.subheader('➕ تسجيل مصروف')
    category_icon = {'Food':'🍔 طعام','Online Shopping':'🛒 تسوق أونلاين','Stores':'🏬 المتاجر','Toys':'🧸 ألعاب','Other':'📦 أخرى'}
    category = st.selectbox('الفئة', ['Food','Online Shopping','Stores','Toys','Other'])
    name = st.text_input('الوصف')
    amount = st.number_input('المبلغ (﷼)', min_value=0.0, step=0.01, format="%.2f")
    if st.button('إضافة مصروف'):
        if name and amount>0:
            add_expense(category_icon[category], category, amount, period)
            st.session_state['rerun'] = True

    # Show Expenses
    st.subheader('📋 المصروفات')
    expenses = get_expenses(period)
    for exp in expenses:
        col1, col2, col3, col4 = st.columns([2,2,2,1])
        with col1: st.write(exp[1])
        with col2: st.write(exp[2])
        with col3: st.write(f'{exp[3]:.2f} ﷼')
        with col4:
            if st.button('❌', key=exp[0]):
                remove_expense(exp[0])
                st.session_state['rerun'] = True

# Rerun trigger
if st.session_state['rerun']:
    st.session_state['rerun'] = False
    st.experimental_rerun()

# --- Settings Interface ---
elif menu == 'Settings':
    st.header('⚙️ إعدادات')
    font = st.selectbox('اختر الخط', ['Arial','Courier','Times New Roman'], index=['Arial','Courier','Times New Roman'].index(font))
    font_size = st.slider('حجم الخط', 20, 60, font_size)
    bg_color = st.color_picker('لون الخلفية', value=bg_color)
    text_color = st.color_picker('لون النص', value=text_color)
    if st.button('حفظ الإعدادات'): 
        set_settings(trash_type, font, font_size, bg_color, text_color)
        st.session_state['rerun'] = True

# --- Eid Money Interface ---
elif menu == 'Eid Money':
    st.header('🕌 أموال العيد')
    giver = st.text_input('من أعطاك؟')
    amount = st.number_input('المبلغ (﷼)', min_value=0.0, step=0.01, format="%.2f")
    if st.button('إضافة أموال العيد'):
        if giver and amount>0:
            add_eid_money(giver, amount)
            st.session_state['rerun'] = True
    total_eid, eid_givers = get_total_eid()
    st.write(f'إجمالي أموال العيد: {total_eid:.2f} ﷼ ({eid_givers})')
