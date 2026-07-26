from config import *
from database import update_time
from bot_instance import bot
import sqlite3

@bot.message_handler(commands=['startsession'])
def start_session(message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET session_active=1 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    conn.close()
    update_time(message.from_user.id, message.from_user.username)
    bot.reply_to(message, "✅ סשן התחיל! המשאבים שלך מייצרים.")

@bot.message_handler(commands=['endsession'])
def end_session(message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET session_active=0 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "🛑 סשן הסתיים.")
