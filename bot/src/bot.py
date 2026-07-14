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
init_db()

init_resources_db()
init_worker_model_db()

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
