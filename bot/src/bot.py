import telebot
from telebot import types
import time
import sqlite3
from datetime import datetime, timedelta
import threading
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'services'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'handlers'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'handlers'))
from config import *
from database import *
from economy_service import produce_by_workers

from bot_instance import bot
# ================ DATABASE ================
init_db()

init_resources_db()
init_worker_model_db()

reset_active_sessions_on_startup()
init_predator_state()

# ================ HELPER FUNCTIONS ================
def background_ticker():
    while True:
        time.sleep(60)
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
                produce_by_workers(user_id, 60)
            except Exception as e:
                print(f"⚠️ שגיאה בייצור פועלים למשתמש {user_id}: {e}")
        try:
            result = check_and_trigger_predator_event()
            if result:
                pid, predator, eaten = result
                pname = {"tiger": "נמר", "lion": "אריה"}[predator]
                tally = {}
                for wt in eaten:
                    tally[wt] = tally.get(wt, 0) + 1
                parts_txt = [wt + " x" + str(n) for wt, n in tally.items()]
                eaten_txt = ", ".join(parts_txt)
                msg = pname + " תקף בלילה וטרף: " + eaten_txt
                bot.send_message(pid, msg)
        except Exception as e:
            print(f"⚠️ שגיאה באירוע טורף: {e}")
        # בונוס פסיבי יומי — 0.1 Gild
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE resources SET gild=gild+0.1")
            conn.commit()
            conn.close()
        except:
            pass
        # צריכה יומית
        try:
            from economy_service import consume_daily_resources
            consume_daily_resources()
        except:
            pass
        # ייצור
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT user_id FROM workers")
            for (uid,) in c.fetchall():
                try:
                    produce_by_workers(uid, 30)
                except:
                    pass
            conn.close()
        except:
            pass

# ================ COMMANDS ================
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'handlers'))
from market_commands import *
from admin_commands import *
from menu import show_main_menu
from basic_commands import *
from msg_handler import *
from lore_handler import *
from reply_handler import *
from chat_handler import *
from resource_commands import *
from session_commands import *
from register_handler import *
from attack_handler import *
from trade_handler import *
from spy_handler import *
from announce_handler import *
from shop_handler import *
from sell_handler import *
from spy_handler import *
from announce_handler import *
from shop_handler import *
from sell_handler import *
from button_handler import *
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
