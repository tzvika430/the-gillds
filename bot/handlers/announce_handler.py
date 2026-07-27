from bot_instance import bot
from config import DB_PATH
import sqlite3

@bot.message_handler(commands=['announce'])
def announce_cmd(message):
    if message.from_user.id not in [5010371391]:
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "שימוש: /announce [הודעה]")
        return
    
    msg = parts[1]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [r[0] for r in c.fetchall()]
    conn.close()
    
    sent = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **עדכון המערכת**\n\n{msg}\n\n📋 שלח /menu לחזרה לתפריט")
            from button_handler import show_main_menu
            show_main_menu(uid)
            sent += 1
        except Exception as e:
            print(f"Failed to send to {uid}: {e}")
    
    bot.reply_to(message, f"📢 ההודעה נשלחה ל-{sent} מתוך {len(users)} שחקנים!")
