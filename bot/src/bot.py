import telebot
from telebot import types
import time
import sqlite3
from datetime import datetime, timedelta
import threading
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'services'))
from config import *
from database import *

from bot_instance import bot
# ================ DATABASE ================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    total_seconds INTEGER DEFAULT 0,
                    today_seconds INTEGER DEFAULT 0,
                    balance REAL DEFAULT 0,
                    last_active TEXT,
                    multiplier REAL DEFAULT 1.0,
                    last_reset DATE,
                    session_active INTEGER DEFAULT 0)''')
    conn.commit()
    try:
        c.execute("ALTER TABLE users ADD COLUMN session_active INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()

def init_resources_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS resources (
                    user_id INTEGER PRIMARY KEY,
                    water REAL DEFAULT 0,
                    coal REAL DEFAULT 0,
                    copper REAL DEFAULT 0,
                    gold REAL DEFAULT 0,
                    gild REAL DEFAULT 50)""")
    c.execute("""CREATE TABLE IF NOT EXISTS market (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER,
                    resource TEXT,
                    amount REAL,
                    price_per_unit REAL,
                    created_at TEXT)""")
    conn.commit()
    conn.close()


init_db()

def init_worker_model_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for col in ['wheat', 'soil', 'wood', 'stones']:
        try:
            c.execute(f"ALTER TABLE resources ADD COLUMN {col} REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    c.execute("""CREATE TABLE IF NOT EXISTS buildings (
                    user_id INTEGER,
                    building_type TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, building_type))""")
    c.execute("""CREATE TABLE IF NOT EXISTS workers (
                    user_id INTEGER,
                    worker_type TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, worker_type))""")
    conn.commit()
    conn.close()

init_resources_db()
init_worker_model_db()

def reset_active_sessions_on_startup():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_active=? WHERE session_active=1",
              (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

reset_active_sessions_on_startup()

# ================ HELPER FUNCTIONS ================
def background_ticker():
    while True:
        time.sleep(10)
        for user_id, username in get_active_users():
            try:
                update_time(user_id, username)
            except Exception as e:
                print(f"⚠️ שגיאה בעדכון משתמש {user_id}: {e}")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT DISTINCT user_id FROM workers')
        all_worker_users = [r[0] for r in c.fetchall()]
        conn.close()
        for user_id in all_worker_users:
            try:
                produce_by_workers(user_id, 10)
            except Exception as e:
                print(f"⚠️ שגיאה בייצור פועלים למשתמש {user_id}: {e}")

# ================ COMMANDS ================
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'handlers'))
from commands import *

print("✅ Gild Bot is running...")

ticker_thread = threading.Thread(target=background_ticker, daemon=True)
ticker_thread.start()

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"⚠️ הבוט קרס מתקלת רשת, מתחבר מחדש בעוד 5 שניות: {e}")
        time.sleep(5)
