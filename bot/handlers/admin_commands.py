import subprocess
import os
from bot_instance import bot

ADMIN_IDS = [5010371391]

def is_admin(user_id):
    return user_id in ADMIN_IDS

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
