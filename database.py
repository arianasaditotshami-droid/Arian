import sqlite3

def init_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            referrer_id INTEGER,
            is_blocked INTEGER DEFAULT 0
        )
    ''')
    
    # جدول کدهای هدیه
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            points INTEGER,
            uses_left INTEGER
        )
    ''')
    
    # جدول کانفینگ‌های خریداری شده
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            config_info TEXT,
            date TEXT
        )
    ''')

    # جدول ادمین‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    # جدول کانال‌های اجباری
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forced_channels (
            channel_username TEXT PRIMARY KEY
        )
    ''')

    # جدول دکمه‌های پنل مدیریت (شیشه‌ای/متنی)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()
  
