from config import *
from database import update_time, get_resources, get_active_users
from bot_instance import bot
from telebot import types
import sqlite3
import os

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # בדוק אם רשום - אם לא, שלח להרשמה
    c.execute("SELECT display_name FROM users WHERE user_id=?", (user_id,))
    existing = c.fetchone()
    if not existing or not existing[0]:
        conn.close()
        from register_handler import start_register
        start_register(message)
        return
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (user_id,))
    c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'farmer', 1)", (user_id,))
    c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'lumberjack', 1)", (user_id,))
    c.execute("INSERT OR IGNORE INTO buildings (user_id, building_type, count) VALUES (?, 'straw_house', 1)", (user_id,))
    conn.commit()
    conn.close()
    msg = """🏰 **ברוך הבא ל-Gild Economy!** 🏰

🎮 משחק אסטרטגיה כלכלי בטלגרם

⛏️ **כריית משאבים** — farmer ו-lumberjack עובדים אוטומטית
🏗️ **בניית מבנים** — straw_house, brick_house, sawmill
👷 **שכירת עובדים** — water_drawer, coal_miner, copper_miner, gold_miner
🏪 **שוק מסחר** — קנה ומכור משאבים לשחקנים אחרים
⚔️ **מלחמה** — `/attack`

📚 לחץ /doc למדריך המלא
📋 **תפריט** — `/menu`
👤 לחץ /profile לפרופיל שלך"""
    keyboard = get_main_keyboard()
    bot.reply_to(message, msg, reply_markup=keyboard)

@bot.message_handler(commands=['time'])
def time_status(message):
    update_time(message.from_user.id, message.from_user.username)
    row = get_resources(message.from_user.id)
    gild = row[5] if row else 0
    bot.reply_to(message, f"⏰ זמן עודכן | 💰 Gild: {gild:.2f}")

@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT water, coal, copper, gold, wheat, soil, wood, stones, gild FROM resources WHERE user_id=?", (user_id,))
    res = c.fetchone()
    if not res:
        bot.reply_to(message, "שלח /start קודם!")
        conn.close()
        return
    water, coal, copper, gold, wheat, soil, wood, stones, gild = res
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=?", (user_id,))
    workers = c.fetchall()
    c.execute("SELECT building_type, count FROM buildings WHERE user_id=?", (user_id,))
    buildings = c.fetchall()
    workers_str = ", ".join([f"{wt}: {cnt}" for wt, cnt in workers]) if workers else "אין"
    buildings_str = ", ".join([f"{bt}: {cnt}" for bt, cnt in buildings]) if buildings else "אין"
    c.execute("SELECT display_name, kingdom FROM users WHERE user_id=?", (user_id,))
    info = c.fetchone()
    dname = info[0] if info and info[0] else username
    kdom = info[1] if info and info[1] else "לא הוגדרה"
    msg = f"""👤 **{dname}** | 🏰 **{kdom}**

📦 **משאבים:**
💧 מים: {water:.1f} | ⚫ פחם: {coal:.1f}
🟠 נחושת: {copper:.1f} | 🥇 זהב: {gold:.1f}
🌾 חיטה: {wheat:.1f} | 🟤 אדמה: {soil:.1f}
🪵 עץ: {wood:.1f} | 🪨 אבנים: {stones:.1f}
💰 Gild: {gild:.2f}

👷 **עובדים:** {workers_str}
🏗️ **מבנים:** {buildings_str}"""
    bot.reply_to(message, msg)

@bot.message_handler(commands=['menu'])
def menu_cmd(message):
    keyboard = get_main_keyboard()
    bot.send_message(message.chat.id, "📋 תפריט ראשי:", reply_markup=keyboard)

@bot.message_handler(commands=['balance'])
def balance(message):
    row = get_resources(message.from_user.id)
    gild = row[5] if row else 0
    bot.reply_to(message, f"💰 Gild: {gild:.2f}")

@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT r.user_id, r.gild, u.display_name, u.username FROM resources r LEFT JOIN users u ON r.user_id=u.user_id ORDER BY r.gild DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.reply_to(message, "אין שחקנים עדיין")
        return
    msg = "🏆 **טבלת מובילים:**\n"
    for i, (uid, gild, dname, uname) in enumerate(rows, 1):
        name = dname if dname else (uname or uid)
        msg += f"{i}. {name}: {gild:.1f} Gild\n"
    bot.reply_to(message, msg)

# ============ מקלדת פקודות ============

def get_main_keyboard():
    from telebot import types
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ קרב")
    keyboard.add("🏪 שוק", "🏆 מובילים", "💳 תשלום")
    keyboard.add("🏗️ בניה", "👷 עובדים", "🛒 חנות")
    return keyboard

def send_with_menu(chat_id, text):
    """שולח הודעה עם כפתורים"""
    keyboard = get_main_keyboard()
    bot.send_message(chat_id, text, reply_markup=keyboard)

def reply_with_menu(message, text):
    """עונה עם כפתורים"""
    keyboard = get_main_keyboard()
    bot.reply_to(message, text, reply_markup=keyboard)

def get_build_keyboard():
    from telebot import types
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('/build straw_house'),
        types.KeyboardButton('/build brick_house'),
        types.KeyboardButton('/build sawmill'),
        types.KeyboardButton('↩️ חזור')
    )
    return keyboard

def get_hire_keyboard():
    from telebot import types
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('/hire farmer'),
        types.KeyboardButton('/hire lumberjack'),
        types.KeyboardButton('/hire water_drawer'),
        types.KeyboardButton('/hire coal_miner'),
        types.KeyboardButton('/hire copper_miner'),
        types.KeyboardButton('/hire gold_miner'),
        types.KeyboardButton('↩️ חזור')
    )
    return keyboard

def get_market_keyboard():
    from telebot import types
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('🏪 /market'),
        types.KeyboardButton('📦 /resources')
    )
    keyboard.add(
        types.KeyboardButton('/sell '),
        types.KeyboardButton('/buy '),
        types.KeyboardButton('↩️ חזור')
    )
    return keyboard

@bot.message_handler(commands=['deleteprofile'])
def delete_profile_cmd(message):
    user_id = message.from_user.id
    
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("✅ כן, מחק הכל", "❌ לא, בטל")
    
    bot.send_message(user_id, """⚠️ **אזהרה!**
    
זה ימחק את כל הנתונים שלך:
- משאבים
- מבנים
- עובדים
- שם וממלכה

אין אפשרות לשחזר!

האם אתה בטוח?""", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == '✅ כן, מחק הכל')
def confirm_delete(message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM resources WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM workers WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM buildings WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM market WHERE seller_id=?", (user_id,))
    c.execute("UPDATE users SET display_name=NULL, kingdom=NULL WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ קרב")
    keyboard.add("🏪 שוק", "🏆 מובילים", "💳 תשלום")
    keyboard.add("🏗️ בניה", "👷 עובדים", "🛒 חנות")
    
    bot.send_message(user_id, "🗑️ הפרופיל נמחק.\nשלח /register ליצור פרופיל חדש, או /start להתחלה.", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == '❌ לא, בטל')
def cancel_delete(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ קרב")
    keyboard.add("🏪 שוק", "🏆 מובילים", "💳 תשלום")
    keyboard.add("🏗️ בניה", "👷 עובדים", "🛒 חנות")
    
    bot.send_message(message.from_user.id, "✅ המחיקה בוטלה.", reply_markup=keyboard)
