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
    period TEXT,
    trash_type TEXT
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
    cursor.execute('SELECT pocket_money, period, trash_type FROM settings ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        return result
    else:
        return (50, 'Month', 'None')  # default values

def set_settings(pocket_money, period, trash_type):
    cursor.execute('INSERT INTO settings (pocket_money, period, trash_type) VALUES (?, ?, ?)',
                   (pocket_money, period, trash_type))
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

# --- Pocket Money Settings ---
st.subheader('💵 إعداد المصروف الرئيسي والفترة')
current_pocket, current_period, current_trash = get_settings()
period = st.selectbox('اختر الفترة', ['Week', 'Month', 'Year'], index=['Week', 'Month', 'Year'].index(current_period))
pocket_money = st.number_input(f'المبلغ المتوقع للفترة ({period}) ﷼', min_value=0.0, value=float(current_pocket), step=0.01, format="%.2f")
trash_type = st.radio('اختيار مكافأة رمي الزبالة', ['None', '10 ﷼ في الأسبوع', '50 ﷼ في الشهر'], index=['None','10 ﷼ في الأسبوع','50 ﷼ في الشهر'].index(current_trash))

# Save / Reset settings
col1, col2 = st.columns(2)
with col1:
    if st.button('حفظ الإعدادات'):
        set_settings(pocket_money, period, trash_type)
        st.success('تم حفظ الإعدادات!')
        st.experimental_rerun()
with col2:
    if st.button('إعادة التعيين'):
        set_settings(50, 'Month', 'None')
        st.experimental_rerun()

# --- Calculate balances ---
if trash_type == 'None':
    trash = 0
elif trash_type == '10 ﷼ في الأسبوع':
    trash = 10 if period=='Week' else 10*4 if period=='Month' else 10*52
else:
    trash = 50 if period=='Month' else 50*12 if period=='Year' else 50/4

base_amount = pocket_money
if period == 'Week' and current_period != 'Week':
    base_amount = pocket_money / (4 if current_period=='Month' else 52)
elif period == 'Month' and current_period != 'Month':
    base_amount = pocket_money * (4 if current_period=='Week' else 1)
elif period == 'Year' and current_period != 'Year':
    base_amount = pocket_money * (12 if current_period=='Month' else 52)

# --- Add Expense ---
st.subheader('➕ تسجيل مصروف')
category_icon = {'Food':'🍔 طعام','Online Shopping':'🛒 تسوق أونلاين','Stores':'🏬 المتاجر','Toys':'🧸 ألعاب','Other':'📦 أخرى'}
category = st.selectbox('الفئة', ['Food','Online Shopping','Stores','Toys','Other'])
name = st.text_input('الوصف')
amount = st.number_input('المبلغ (﷼)', min_value=0.0, step=0.01, format="%.2f")
if st.button('إضافة مصروف'):
    if name and amount>0:
        add_expense(category_icon[category], category, amount, period)
        st.success(f'تمت إضافة {name} ({category_icon[category]})')
        st.experimental_rerun()

# --- Display balances ---
total_exp = get_total_expenses(period)
remaining = round(base_amount - total_exp - trash,2)
st.subheader('📊 المبالغ')
st.write(f'المبلغ المتوقع للفترة: {base_amount:.2f} ﷼')
st.write(f'المصاريف الإجمالية: {total_exp + trash:.2f} ﷼ (شاملة مكافأة الزبالة)')
st.write(f'المتبقي لك: {remaining:.2f} ﷼')

# --- Show Expenses Table ---
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

# --- Home screen instructions ---
st.markdown('### Riyal Tracker • يعمل على أي متصفح')
st.markdown('1. افتح هذا التطبيق في متصفح الهاتف.')
st.markdown('2. اضغط على قائمة المتصفح (⋮ أو أيقونة المشاركة).')
st.markdown('3. اختر "إضافة إلى الشاشة الرئيسية".')
st.markdown('4. الآن يمكنك فتحه مثل أي تطبيق عادي!')
