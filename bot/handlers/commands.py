import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'services'))
from config import *
from database import *
from bot_instance import bot
import sqlite3

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
    conn = sqlite3.connect(DB_PATH)
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
    NL = chr(10)
    parts = []
    parts.append('📦 המשאבים שלך')
    parts.append('')
    parts.append('💧 מים: ' + format(row[1], '.2f'))
    parts.append('⚫ פחם: ' + format(row[2], '.2f'))
    parts.append('🟠 נחושת: ' + format(row[3], '.2f'))
    parts.append('🥇 זהב: ' + format(row[4], '.2f'))
    parts.append('🌾 חיטה: ' + format(row[6], '.2f'))
    parts.append('🟤 אדמה: ' + format(row[7], '.2f'))
    parts.append('🪵 עץ: ' + format(row[8], '.2f'))
    parts.append('🪨 אבנים: ' + format(row[9], '.2f'))
    parts.append('')
    parts.append('💰 Gild: ' + format(row[5], '.2f'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND count>0", (message.from_user.id,))
    workers = c.fetchall()
    c.execute("SELECT building_type, count FROM buildings WHERE user_id=? AND count>0", (message.from_user.id,))
    buildings = c.fetchall()
    conn.close()
    if workers:
        parts.append('')
        parts.append('👷 עובדים:')
        for wt, cnt in workers:
            parts.append(wt + ': ' + str(cnt))
    if buildings:
        parts.append('')
        parts.append('🏠 מבנים:')
        for bt, cnt in buildings:
            parts.append(bt + ': ' + str(cnt))
    bot.reply_to(message, NL.join(parts))


@bot.message_handler(commands=['sell'])
def sell_cmd(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "שימוש: /sell משאב כמות מחיר")
        return
    _, resource, amount_str, price_str = parts
    if resource not in ALL_RESOURCE_IDX:
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
    idx = ALL_RESOURCE_IDX[resource]
    if row[idx] < amount:
        bot.reply_to(message, f"אין מספיק {resource}")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE resources SET {resource}={resource}-? WHERE user_id=?", (amount, message.from_user.id))
    c.execute("INSERT INTO market (seller_id, resource, amount, price_per_unit, created_at) VALUES (?,?,?,?,?)", (message.from_user.id, resource, amount, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    emoji = RESOURCE_EMOJI[resource]
    bot.reply_to(message, f"✅ הצעה נפתחה: {emoji} {amount} {resource} במחיר {price} Gild ליחידה")

@bot.message_handler(commands=['market'])
def market_cmd(message):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_active=?, session_active=1 WHERE user_id=?",
             (datetime.now().isoformat(), message.from_user.id))
    conn.commit()
    conn.close()
    bot.reply_to(message, "⏳ סשן התחיל! כל שנייה שאתה פעיל — אתה מרוויח.")

@bot.message_handler(commands=['endsession'])
def end_session(message):
    update_time(message.from_user.id, message.from_user.username)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET session_active=0 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ סשן הסתיים. בדוק את היתרה עם /balance")

@bot.message_handler(commands=['build'])
def build_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 2:
        names = ', '.join(BUILDING_COST.keys())
        bot.reply_to(message, f'שימוש: /build שם_מבנה\nאפשרויות: {names}')
        return
    building_type = parts[1]
    ok, msg = build_building(message.from_user.id, building_type)
    if ok:
        bot.reply_to(message, f'✅ נבנה {building_type} בהצלחה!')
    else:
        bot.reply_to(message, f'❌ {msg}')

@bot.message_handler(commands=['hire'])
def hire_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 2:
        names = ', '.join(HIRE_COST.keys())
        bot.reply_to(message, f'שימוש: /hire סוג_עובד\nאפשרויות: {names}')
        return
    worker_type = parts[1]
    ok, msg = hire_worker(message.from_user.id, worker_type)
    if ok:
        bot.reply_to(message, f'✅ גויס {worker_type} בהצלחה!')
    else:
        bot.reply_to(message, f'❌ {msg}')

@bot.message_handler(commands=['store'])
def store_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 3:
        names = ', '.join(ALL_RESOURCE_IDX.keys())
        bot.reply_to(message, f'שימוש: /store משאב כמות\nאפשרויות: {names}\nשער: {NPC_BUY_RATE} יחידות ל-1 Gild')
        return
    resource = parts[1]
    try:
        amount = float(parts[2])
    except ValueError:
        bot.reply_to(message, 'כמות חייבת להיות מספר')
        return
    if amount <= 0:
        bot.reply_to(message, 'כמות חייבת להיות חיובית')
        return
    ok, msg = buy_from_system(message.from_user.id, resource, amount)
    if ok:
        bot.reply_to(message, f'✅ קנית {amount} {resource} מהמערכת')
    else:
        bot.reply_to(message, f'❌ {msg}')

@bot.message_handler(func=lambda m: True)
def every_message(message):
    update_time(message.from_user.id, message.from_user.username)

