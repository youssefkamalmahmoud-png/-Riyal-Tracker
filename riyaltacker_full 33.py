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
        return (50,0,0)  # default weekly 50

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

# --- Pocket Money Input ---
st.subheader('احسب دخلك وخصم مصاريفك (﷼)')
current_pocket, trash_week, trash_month = get_settings()
pocket_money = st.number_input('المصروف الأسبوعي (افتراضي 50 ﷼)', min_value=0.0, value=float(current_pocket), step=0.01, format="%.2f")

# Trash bonus selection
st.subheader('اختيار مكافأة رمي الزبالة')
trash_option = st.radio('', ['بدون مكافأة', f'{trash_month:.2f} ﷼ في الشهر', f'{trash_week:.2f} ﷼ في الأسبوع'])

# Period selection
st.subheader('فترة الحساب')
period = st.radio('', ['أسبوع', 'شهر', 'سنة'])

# Save / Reset settings
col_save, col_reset = st.columns(2)
with col_save:
    if st.button('حفظ الإعدادات'):
        if trash_option == 'بدون مكافأة':
            tw, tm = 0,0
        elif 'شه' in trash_option:
            tw, tm = 0, trash_month
        else:
            tw, tm = trash_week,0
        set_settings(pocket_money, tw, tm)
        st.success('تم حفظ الإعدادات!')
        st.experimental_rerun()
with col_reset:
    if st.button('إعادة التعيين'):
        set_settings(50,0,0)
        st.experimental_rerun()

# --- Calculate remaining ---
if period == 'أسبوع':
    base = pocket_money
    trash = trash_week
elif period == 'شهر':
    base = pocket_money*4
    trash = trash_month
else:  # سنة
    base = pocket_money*52
    trash = trash_month*12

# Expenses input
st.subheader('تسجيل مصروف')
name = st.text_input('🍔 طعام')
category = st.selectbox('الفئة', ['طعام', 'تسوق أونلاين', 'المتاجر', 'ألعاب', 'أخرى'])
amount = st.number_input('المبلغ (﷼)', min_value=0.0, step=0.01, format="%.2f")
if st.button('إضافة مصروف'):
    if name and amount>0:
        add_expense(name, category, amount, period)
        st.success(f'تمت إضافة {name}')
        st.experimental_rerun()

# Display balances
st.subheader('النتيجة السنوية')
total_exp = get_total_expenses(period)
remaining = round(base - total_exp - trash,2)
st.metric('بعد المصاريف', f'{remaining:.2f} ﷼', f'يبقى لك {remaining:.2f} ﷼')

# Show expense table
expenses = get_expenses(period)
st.subheader('📋 المصروفات')
for exp in expenses:
    col1, col2, col3, col4 = st.columns([2,2,2,1])
    with col1: st.write(exp[1])
    with col2: st.write(exp[2])
    with col3: st.write(f'{exp[3]:.2f} ﷼')
    with col4:
        if st.button('❌', key=exp[0]):
            remove_expense(exp[0])
            st.experimental_rerun()

# Add to Home screen instructions
st.markdown('### Riyal Tracker • يعمل على أي متصفح')
st.markdown('1. افتح هذا التطبيق في متصفح الهاتف.')
st.markdown('2. اضغط على قائمة المتصفح (⋮ أو أيقونة المشاركة).')
st.markdown('3. اختر "إضافة إلى الشاشة الرئيسية".')
st.markdown('4. الآن يمكنك فتحه مثل أي تطبيق عادي!')