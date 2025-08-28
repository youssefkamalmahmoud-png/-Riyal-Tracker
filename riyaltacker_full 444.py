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
    trash_month REAL,
    period TEXT
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
    cursor.execute('SELECT pocket_money, trash_week, trash_month, period FROM settings ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        return result
    else:
        return (50, 0, 0, 'Month')  # default values

def set_settings(pocket_money, trash_week, trash_month, period):
    cursor.execute('INSERT INTO settings (pocket_money, trash_week, trash_month, period) VALUES (?, ?, ?, ?)',
                   (pocket_money, trash_week, trash_month, period))
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

# --- Select period and main pocket money ---
st.subheader('اختر الفترة وأدخل مصروفك الأساسي')
current_pocket, trash_week, trash_month, current_period = get_settings()
period = st.selectbox('اختر الفترة', ['Week', 'Month', 'Year'], index=['Week', 'Month', 'Year'].index(current_period))
pocket_money = st.number_input(f'المبلغ المتوقع للفترة ({period}) ﷼', min_value=0.0, value=float(current_pocket), step=0.01, format="%.2f")

# Trash milestone selection
st.subheader('اختيار مكافأة رمي الزبالة')
trash_option = st.radio('', ['None', '10 ﷼ في الأسبوع', '50 ﷼ في الشهر'])
if trash_option == 'None':
    trash_w, trash_m = 0,0
elif trash_option == '10 ﷼ في الأسبوع':
    trash_w, trash_m = 10,0
else:
    trash_w, trash_m = 0,50

# Save / Reset settings
col1, col2 = st.columns(2)
with col1:
    if st.button('حفظ الإعدادات'):
        set_settings(pocket_money, trash_w, trash_m, period)
        st.success('تم حفظ الإعدادات!')
        st.experimental_rerun()
with col2:
    if st.button('إعادة التعيين'):
        set_settings(50,0,0,'Month')
        st.experimental_rerun()

# --- Add Expense ---
st.subheader('تسجيل مصروف')
category_icon = {'Food':'🍔 طعام','Online Shopping':'🛒 تسوق أونلاين','Stores':'🏬 المتاجر','Toys':'🧸 ألعاب','Other':'📦 أخرى'}
category = st.selectbox('الفئة', ['Food','Online Shopping','Stores','Toys','Other'])
name = st.text_input('الوصف')
amount = st.number_input('المبلغ (﷼)', min_value=0.0, step=0.01, format="%.2f")
if st.button('إضافة مصروف'):
    if name and amount>0:
        add_expense(category_icon[category], category, amount, period)
        st.success(f'تمت إضافة {name} ({category_icon[category]})')
        st.experimental_rerun()

# --- Calculate balances ---
total_exp = get_total_expenses(period)
if period=='Week':
    base = pocket_money
    trash = trash_w
elif period=='Month':
    base = pocket_money
    trash = trash_m
else:
    base = pocket_money
    trash = trash_m*12

remaining = round(base - total_exp - trash,2)
st.subheader('💵 النتيجة')
st.write(f'المبلغ المتوقع للفترة: {base:.2f} ﷼')
st.write(f'المصاريف الإجمالية: {total_exp+trash:.2f} ﷼ (شاملة مكافأة الزبالة)')
st.write(f'المتبقي لك: {remaining:.2f} ﷼')

# --- Show Expenses ---
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
            st.experimental_rerun()

# Add to home screen instructions
st.markdown('### Riyal Tracker • يعمل على أي متصفح')
st.markdown('1. افتح هذا التطبيق في متصفح الهاتف.')
st.markdown('2. اضغط على قائمة المتصفح (⋮ أو أيقونة المشاركة).')
st.markdown('3. اختر "إضافة إلى الشاشة الرئيسية".')
st.markdown('4. الآن يمكنك فتحه مثل أي تطبيق عادي!')
