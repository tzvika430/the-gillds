import telebot
from telebot import types
import time
import sqlite3
from datetime import datetime, timedelta
import threading

# ================ CONFIG ================
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()
BASE_RATE = 0.003858

bot = telebot.TeleBot(TOKEN)

try:
    bot_info = bot.get_me()
    print(f"✅ טוקן תקין! מחובר לבוט @{bot_info.username}")
except Exception as e:
    print(f"❌ טוקן לא תקין או אין חיבור לאינטרנט: {e}")
    raise SystemExit(1)

# ================ DATABASE ================
def init_db():
    conn = sqlite3.connect('economy.db')
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
    conn = sqlite3.connect('economy.db')
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

RESOURCE_RATES = {"water": 1/1000, "coal": 1/3000, "copper": 1/6000, "gold": 1/30000}
RESOURCE_EMOJI = {"water": "💧", "coal": "⚫", "copper": "🟠", "gold": "🥇"}

init_db()
init_resources_db()

def reset_active_sessions_on_startup():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("UPDATE users SET last_active=? WHERE session_active=1",
              (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

reset_active_sessions_on_startup()

# ================ HELPER FUNCTIONS ================
def get_user(user_id, username):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, username, last_reset) VALUES (?, ?, ?)",
                 (user_id, username, datetime.now().date()))
        conn.commit()
        user = (user_id, username, 0, 0, 0, None, 1.0, str(datetime.now().date()), 0)
    if user[7] != datetime.now().date():
        c.execute("UPDATE users SET today_seconds=0, last_reset=? WHERE user_id=?",
                 (datetime.now().date(), user_id))
        conn.commit()
    conn.close()
    return user

def update_time(user_id, username):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    user = get_user(user_id, username)
    if user[5] and user[8]:
        last = datetime.fromisoformat(user[5])
        seconds = (datetime.now() - last).total_seconds()
        earnings = seconds * BASE_RATE * user[6]
        c.execute("""UPDATE users SET
                    total_seconds = total_seconds + ?,
                    today_seconds = today_seconds + ?,
                    balance = balance + ?,
                    last_active = ?
                    WHERE user_id = ?""",
                 (int(seconds), int(seconds), earnings, datetime.now().isoformat(), user_id))
        conn.commit()
        get_resources(user_id)
        c.execute("UPDATE resources SET water=water+?, coal=coal+?, copper=copper+?, gold=gold+? WHERE user_id=?",
                 (seconds*RESOURCE_RATES["water"], seconds*RESOURCE_RATES["coal"],
                  seconds*RESOURCE_RATES["copper"], seconds*RESOURCE_RATES["gold"], user_id))
        conn.commit()
    conn.close()

def get_resources(user_id):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM resources WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO resources (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = (user_id, 0, 0, 0, 0, 50)
    conn.close()
    return row

def get_active_users():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE session_active=1")
    users = c.fetchall()
    conn.close()
    return users

def background_ticker():
    while True:
        time.sleep(10)
        for user_id, username in get_active_users():
            try:
                update_time(user_id, username)
            except Exception as e:
                print(f"⚠️ שגיאה בעדכון משתמש {user_id}: {e}")

# ================ COMMANDS ================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🏰 ברוך הבא למשחק האסטרטגיה Gild!\n\nפקודות זמינות עכשיו:\n/resources - המשאבים שלך\n/sell - מכירת משאב בשוק\n/buy - קניית משאב מהשוק\n/market - צפייה בשוק\n/leaderboard - לוח מובילים\n\nבקרוב:\n🏗️ בניה - הקמת מבנים\n⚔️ מלחמה - קרבות בין שחקנים\n🛡️ בחר אסטרטגיית לחימה")

@bot.message_handler(commands=['time'])
def time_status(message):
    user = get_user(message.from_user.id, message.from_user.username)
    hours_total = user[2] / 3600
    hours_today = user[3] / 3600
    earnings_today = user[3] * BASE_RATE * user[6]
    text = f"🕒 סטטוס\n\n👤 {message.from_user.first_name}\n⏱️ זמן כולל: {hours_total:.1f} שעות\n📅 היום: {hours_today:.1f} שעות\n💰 רווחים היום: ${earnings_today:.2f}\n💎 יתרה כוללת: ${user[4]:.2f}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['balance'])
def balance(message):
    user = get_user(message.from_user.id, message.from_user.username)
    bot.reply_to(message, f"💰 יתרה: ${user[4]:.2f}")

@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.reply_to(message, "אין עדיין משתמשים בטבלה.")
        return
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    lines = ["🏆 טבלת המובילים", ""]
    for i, (username, bal) in enumerate(rows):
        name = f"@{username}" if username else "משתמש אנונימי"
        lines.append(f"{medals[i]} {name} — ${bal:.2f}")
    bot.reply_to(message, "\n".join(lines))

@bot.message_handler(commands=['resources'])
def resources_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    row = get_resources(message.from_user.id)
    text = f"📦 המשאבים שלך\n\n💧 מים: {row[1]:.2f}\n⚫ פחם: {row[2]:.2f}\n🟠 נחושת: {row[3]:.2f}\n🥇 זהב: {row[4]:.2f}\n\n💰 Gild: {row[5]:.2f}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['sell'])
def sell_cmd(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "שימוש: /sell משאב כמות מחיר")
        return
    _, resource, amount_str, price_str = parts
    if resource not in RESOURCE_RATES:
        bot.reply_to(message, "משאב לא מוכר")
        return
    try:
        amount = float(amount_str)
        price = float(price_str)
    except ValueError:
        bot.reply_to(message, "כמות ומחיר חייבים להיות מספרים")
        return
    if amount <= 0 or price <= 0:
        bot.reply_to(message, "כמות ומחיר חייבים להיות חיוביים")
        return
    update_time(message.from_user.id, message.from_user.username)
    row = get_resources(message.from_user.id)
    idx = {"water": 1, "coal": 2, "copper": 3, "gold": 4}[resource]
    if row[idx] < amount:
        bot.reply_to(message, f"אין מספיק {resource}")
        return
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute(f"UPDATE resources SET {resource}={resource}-? WHERE user_id=?", (amount, message.from_user.id))
    c.execute("INSERT INTO market (seller_id, resource, amount, price_per_unit, created_at) VALUES (?,?,?,?,?)", (message.from_user.id, resource, amount, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    emoji = RESOURCE_EMOJI[resource]
    bot.reply_to(message, f"✅ הצעה נפתחה: {emoji} {amount} {resource} במחיר {price} Gild ליחידה")

@bot.message_handler(commands=['market'])
def market_cmd(message):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT id, seller_id, resource, amount, price_per_unit FROM market ORDER BY resource ASC, price_per_unit ASC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    if not rows:
        bot.reply_to(message, "אין הצעות בשוק")
        return
    out = ["שוק המשאבים:", ""]
    for lid, sid, res, amt, price in rows:
        out.append(f"#{lid} - {amt:.2f} {res} @ {price:.2f} Gild ליחידה")
    out.append("")
    out.append("לקנייה: /buy מספר_הצעה כמות")
    bot.reply_to(message, "\n".join(out))

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "שימוש: /buy מספר_הצעה כמות")
        return
    try:
        listing_id = int(parts[1])
        amount_requested = float(parts[2])
    except ValueError:
        bot.reply_to(message, "פורמט לא תקין")
        return
    if amount_requested <= 0:
        bot.reply_to(message, "כמות חייבת להיות חיובית")
        return
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT seller_id, resource, amount, price_per_unit FROM market WHERE id=?", (listing_id,))
    listing = c.fetchone()
    if not listing:
        conn.close()
        bot.reply_to(message, "הצעה לא קיימת")
        return
    seller_id, resource, avail_amount, price = listing
    if seller_id == message.from_user.id:
        conn.close()
        bot.reply_to(message, "אי אפשר לקנות מעצמך")
        return
    if amount_requested > avail_amount + 1e-9:
        conn.close()
        bot.reply_to(message, f"יש רק {avail_amount:.2f} בהצעה הזו")
        return
    total_cost = amount_requested * price
    buyer_row = get_resources(message.from_user.id)
    if buyer_row[5] < total_cost:
        conn.close()
        bot.reply_to(message, f"אין מספיק Gild, צריך {total_cost:.2f}")
        return
    c.execute("UPDATE resources SET gild=gild-? WHERE user_id=?", (total_cost, message.from_user.id))
    c.execute(f"UPDATE resources SET {resource}={resource}+? WHERE user_id=?", (amount_requested, message.from_user.id))
    c.execute("UPDATE resources SET gild=gild+? WHERE user_id=?", (total_cost, seller_id))
    if abs(amount_requested - avail_amount) < 1e-9:
        c.execute("DELETE FROM market WHERE id=?", (listing_id,))
    else:
        c.execute("UPDATE market SET amount=amount-? WHERE id=?", (amount_requested, listing_id))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ קנית {amount_requested:.2f} {resource} תמורת {total_cost:.2f} Gild")

@bot.message_handler(commands=['startsession'])
def start_session(message):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("UPDATE users SET last_active=?, session_active=1 WHERE user_id=?",
             (datetime.now().isoformat(), message.from_user.id))
    conn.commit()
    conn.close()
    bot.reply_to(message, "⏳ סשן התחיל! כל שנייה שאתה פעיל — אתה מרוויח.")

@bot.message_handler(commands=['endsession'])
def end_session(message):
    update_time(message.from_user.id, message.from_user.username)
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("UPDATE users SET session_active=0 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ סשן הסתיים. בדוק את היתרה עם /balance")

@bot.message_handler(func=lambda m: True)
def every_message(message):
    update_time(message.from_user.id, message.from_user.username)

print("✅ Gild Bot is running...")

ticker_thread = threading.Thread(target=background_ticker, daemon=True)
ticker_thread.start()

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"⚠️ הבוט קרס מתקלת רשת, מתחבר מחדש בעוד 5 שניות: {e}")
        time.sleep(5)
