from bot_instance import bot
from config import DB_PATH
import sqlite3

# שמירת הודעות אחרונות
chat_messages = []  # (user_id, username, message)
MAX_MESSAGES = 50

@bot.message_handler(commands=['shout'])
def shout_cmd(message):
    user_id = message.from_user.id
    
    # קבל את ההודעה (אחרי /shout)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "שימוש: /shout [הודעה]\nשלח הודעה לכל השחקנים!")
        return
    
    text = parts[1]
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    
    # קבל display_name
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT display_name FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    display_name = row[0] if row and row[0] else username
    conn.close()
    
    # שמור בלוח
    chat_messages.append((user_id, display_name, text))
    if len(chat_messages) > MAX_MESSAGES:
        chat_messages.pop(0)
    
    # שלח לכל השחקנים
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [r[0] for r in c.fetchall()]
    conn.close()
    
    sent = 0
    for uid in users:
        if uid != user_id:
            try:
                bot.send_message(uid, f"📢 **{display_name}:** {text}")
                sent += 1
            except:
                pass
    
    bot.reply_to(message, f"📢 ההודעה נשלחה ל-{sent} שחקנים!")

@bot.message_handler(commands=['board'])
def board_cmd(message):
    """הצג את לוח המודעות"""
    if not chat_messages:
        bot.reply_to(message, "📋 לוח המודעות ריק. שלח /shout [הודעה]!")
        return
    
    msg = "📋 **לוח מודעות**\n\n"
    for uid, name, text in chat_messages[-10:]:
        msg += f"**{name}:** {text}\n"
    
    bot.reply_to(message, msg)
