import subprocess
import os
from bot_instance import bot

def is_admin(user_id):
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] == 1

@bot.message_handler(commands=['status'])
def status_cmd(message):
    if not is_admin(message.from_user.id):
        return
    import sqlite3
    from config import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM workers")
        workers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM market")
        market = c.fetchone()[0]
        conn.close()
        msg = f"""🟢 בוט חי ופועל

👥 משתמשים: {users}
👷 עובדים: {workers}
🏪 הצעות שוק: {market}"""
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"🔴 שגיאה: {e}")

@bot.message_handler(commands=['logs'])
def logs_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    lines = int(parts[1]) if len(parts) > 1 else 10
    try:
        result = subprocess.run(['tail', f'-{lines}', os.path.expanduser('~/bot_error.log')], 
                                capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        if output:
            bot.reply_to(message, f"📋 לוגים:\n\n{output[-1500:]}")
        else:
            bot.reply_to(message, "📋 אין לוגים")
    except Exception as e:
        bot.reply_to(message, f"שגיאה: {e}")

@bot.message_handler(commands=['tests'])
def tests_cmd(message):
    if not is_admin(message.from_user.id):
        return
    bot.reply_to(message, "🧪 מריץ בדיקות...")
    try:
        r1 = subprocess.run(['python3', os.path.expanduser('~/SLH-DEV/tests/test_structure.py')], 
                            capture_output=True, text=True, timeout=15)
        r2 = subprocess.run(['python3', os.path.expanduser('~/SLH-DEV/tests/test_market.py')], 
                            capture_output=True, text=True, timeout=15)
        output = (r1.stdout + r2.stdout)[-1000:]
        if "FAIL" not in output and "Traceback" not in output:
            bot.reply_to(message, f"✅ כל הבדיקות עברו!")
        else:
            bot.reply_to(message, f"❌ יש בעיה:\n{output[-800:]}")
    except Exception as e:
        bot.reply_to(message, f"שגיאה: {e}")

@bot.message_handler(commands=['doc'])
def doc_cmd(message):
    msg = """🎮 **מדריך Gild Economy**

📌 **התחלה מהירה:**
1️⃣ לחץ 👤 פרופיל — לראות את המשאבים שלך
2️⃣ לחץ 🏗️ בניה — לבנות מבנים
3️⃣ לחץ 👷 עובדים — לשכור עובדים

🏗️ **בנייה:**
🏠 צריף קש — 100 חיטה, 100 אדמה, 50 עץ, 20 מים
🧱 בית לבנים — 200 אדמה, 200 אבנים, 100 עץ, 50 מים
🪚 מנסרה — 100 עץ, 50 חיטה, 50 אדמה, 50 פחם
🏰 בסיס צבאי — 200 אדמה, 200 אבנים, 100 עץ, 50 נחושת

👷 **עובדים:**
👨‍🌾 חקלאי (1 Gild) — מייצר חיטה+אדמה+אבנים
🪓 חוטב עצים (1 Gild) — מייצר עץ
💧 שואב מים (1 Gild) — מייצר מים
⛏️ כורה פחם (2 Gild) — מייצר פחם
🟠 כורה נחושת (3 Gild) — מייצר נחושת
🥇 כורה זהב (5 Gild) — מייצר זהב

⚔️ **חיילים:**
🪖 חייל (2 Gild) — צריך בסיס צבאי
🎖️ מפקד (10 Gild) — צריך 6 חיילים
👑 גנרל (30 Gild) — צריך 3 מפקדים

🏪 **שוק:**
📦 מכור — בחר משאב, כמות, מחיר
🛒 קנה — ראה הצעות וקנה
📋 צפה — /market

💡 **טיפים:**
• כל העובדים והחיילים צורכים מים כל יום
• מפקדים וגנרלים צורכים גם זהב
• חיילים מפחיתים סיכוי להיטרף ע"י טורפים
• ⚔️ קרב — תקוף שחקן וקח 10% מהמשאבים שלו!

📢 **צ'אט:** /shout [הודעה] • /board — לוח מודעות"""
    bot.reply_to(message, msg)

@bot.message_handler(commands=['ops'])
def ops_cmd(message):
    if not is_admin(message.from_user.id):
        return
    import sqlite3
    from config import DB_PATH
    parts = message.text.split()
    subcmd = parts[1] if len(parts) > 1 else "help"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if subcmd == "users":
        c.execute("SELECT user_id, username FROM users LIMIT 20")
        rows = c.fetchall()
        msg = "👥 **משתמשים:**\n"
        for uid, uname in rows:
            c2 = conn.cursor()
            c2.execute("SELECT gild FROM resources WHERE user_id=?", (uid,))
            g = c2.fetchone()
            gild = g[0] if g else 0
            msg += f"• {uname or uid}: {gild:.1f} Gild\n"
        bot.reply_to(message, msg)
    
    elif subcmd == "market":
        c.execute("SELECT id, seller_id, resource, amount, price_per_unit FROM market LIMIT 20")
        rows = c.fetchall()
        if rows:
            msg = "🏪 **הצעות שוק:**\n"
            for lid, sid, res, amt, price in rows:
                msg += f"#{lid} | {res} | {amt:.1f} | {price:.2f} Gild\n"
        else:
            msg = "📭 אין הצעות"
        bot.reply_to(message, msg)
    
    elif subcmd == "workers":
        c.execute("SELECT user_id, worker_type, count FROM workers LIMIT 30")
        rows = c.fetchall()
        msg = "👷 **עובדים:**\n"
        for uid, wt, cnt in rows:
            msg += f"• {uid}: {wt} x{cnt}\n"
        bot.reply_to(message, msg)
    
    elif subcmd == "buildings":
        c.execute("SELECT user_id, building_type, count FROM buildings LIMIT 30")
        rows = c.fetchall()
        msg = "🏠 **מבנים:**\n"
        for uid, bt, cnt in rows:
            msg += f"• {uid}: {bt} x{cnt}\n"
        bot.reply_to(message, msg)
    
    elif subcmd == "sql":
        if len(parts) < 3:
            bot.reply_to(message, "שימוש: /ops sql [שאילתה]")
        else:
            query = " ".join(parts[2:])
            try:
                c.execute(query)
                rows = c.fetchall()[:20]
                msg = f"📊 תוצאה ({len(rows)} שורות):\n"
                for row in rows:
                    msg += str(row) + "\n"
                bot.reply_to(message, msg[-2000:])
            except Exception as e:
                bot.reply_to(message, f"❌ {e}")
    
    elif subcmd == "help":
        msg = """🔧 **פקודות Ops:**
/ops users - רשימת משתמשים
/ops market - הצעות שוק
/ops workers - עובדים
/ops buildings - מבנים
/ops sql [שאילתה] - הרצת SQL
/ops help - עזרה"""
        bot.reply_to(message, msg)
    
    else:
        bot.reply_to(message, f"לא מוכר. /ops help לעזרה")
    
    conn.close()

@bot.message_handler(commands=['pay'])
def pay_cmd(message):
    msg = """💳 **Gild Economy - תשלום**

⭐ חודשי: **2.99 USDT** | 💎 רבעוני: **6.99 USDT**

📤 רשת **TON**

✅ אחרי העברה שלח /paid"""
    bot.reply_to(message, msg)
    bot.send_message(message.chat.id, "`UQDhfyUPSJ8x9xnoeccTl55PEny7zUvDW8UabZ7PdDo52noF`")

@bot.message_handler(commands=['paid'])
def paid_cmd(message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "שימוש: /paid [מזהה עסקה]\nלדוגמה: /paid 123456789")
        return
    tx_id = parts[1]
    # שולח התראה למנהל
    admin_msg = f"""💰 **התראת תשלום!**

משתמש: `{user_id}`
מזהה עסקה: `{tx_id}`

לאישור: `/approve {user_id}`"""
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, admin_msg)
        except:
            pass
    bot.reply_to(message, "✅ בקשת התשלום נשלחה לאישור. תקבל הודעה אחרי האישור.")

@bot.message_handler(commands=['approve'])
def approve_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "שימוש: /approve user_id")
        return
    target_id = int(parts[1])
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_paid=1 WHERE user_id=?", (target_id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ תשלום אושר למשתמש {target_id}")
    try:
        bot.send_message(target_id, "✅ התשלום אושר! המשאבים שלך ממשיכים לייצר. תודה!")
    except:
        pass

@bot.message_handler(commands=['makeadmin'])
def makeadmin_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "שימוש: /makeadmin user_id")
        return
    target = int(parts[1])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (target,))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ משתמש {target} הוא עכשיו אדמין")

@bot.message_handler(commands=['removeadmin'])
def removeadmin_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "שימוש: /removeadmin user_id")
        return
    target = int(parts[1])
    if target == 5010371391:
        bot.reply_to(message, "❌ אי אפשר להסיר את האדמין הראשי")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin=0 WHERE user_id=?", (target,))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ משתמש {target} כבר לא אדמין")
