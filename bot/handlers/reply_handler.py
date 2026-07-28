from bot_instance import bot
from config import DB_PATH
import sqlite3

# שמירת הודעות אחרונות — (sender_id, sender_name, msg_text, chat_type)
last_messages = {}
MAX_REPLY_HISTORY = 20

@bot.message_handler(commands=['reply'])
def reply_cmd(message):
    """ענה להודעה האחרונה — קבוצתית או פרטית"""
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        bot.reply_to(message, "שימוש: /reply [הודעה]\nעונה להודעה האחרונה שנשלחה אליך")
        return
    
    reply_text = parts[1]
    
    # קבל שם של המגיב
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT display_name FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    replier_name = row[0] if row and row[0] else (message.from_user.username or str(user_id))
    conn.close()
    
    # מצא את ההודעה האחרונה שהשחקן קיבל
    last_for_user = None
    for msg_id, msg_data in last_messages.items():
        if msg_data.get('target_id') == user_id or msg_data.get('chat_type') == 'shout':
            last_for_user = msg_data
            break
    
    if not last_for_user:
        bot.reply_to(message, "❌ אין הודעה לענות עליה")
        return
    
    original_sender = last_for_user['sender_name']
    original_text = last_for_user['text']
    chat_type = last_for_user.get('chat_type', 'shout')
    
    if chat_type == 'private':
        # שלח בחזרה לשולח המקורי
        target_id = last_for_user['sender_id']
        try:
            bot.send_message(target_id, f"💬 **{replier_name}** (ל-**{original_sender}**):\n\n{reply_text}\n\n📋 /menu — חזרה לתפריט")
            bot.reply_to(message, f"✅ התשובה נשלחה ל-{original_sender}")
        except:
            bot.reply_to(message, "❌ לא ניתן לשלוח תשובה")
    else:
        # שלח לכולם כציטוט
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = [r[0] for r in c.fetchall()]
        conn.close()
        
        sent = 0
        for uid in users:
            if uid != user_id:
                try:
                    bot.send_message(uid, f"💬 **{replier_name}** (ל-**{original_sender}**):\n\n{reply_text}\n\n📋 /menu — חזרה לתפריט")
                    sent += 1
                except:
                    pass
        
        bot.reply_to(message, f"💬 התשובה נשלחה ל-{sent} שחקנים!")
    
    # שמור את התגובה להמשך
    last_messages[message.message_id] = {
        'sender_id': user_id,
        'sender_name': replier_name,
        'text': reply_text,
        'chat_type': chat_type,
        'target_id': last_for_user.get('sender_id'),
        'original_text': original_text
    }

# עדכון shout_cmd ו-msg_cmd — שמירת הודעות
import chat_handler
original_shout = chat_handler.shout_cmd if hasattr(chat_handler, 'shout_cmd') else None
original_msg = None
try:
    from msg_handler import msg_cmd
    original_msg = msg_cmd
except:
    pass

# Monkey-patch shout_cmd לשמור הודעות
if original_shout:
    def new_shout(message):
        # שמור את ההודעה לפני שליחה
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)
        if len(parts) >= 2:
            from config import DB_PATH
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT display_name FROM users WHERE user_id=?", (user_id,))
            row = c.fetchone()
            sender_name = row[0] if row and row[0] else (message.from_user.username or str(user_id))
            conn.close()
            
            last_messages[message.message_id] = {
                'sender_id': user_id,
                'sender_name': sender_name,
                'text': parts[1],
                'chat_type': 'shout'
            }
        original_shout(message)
    
    chat_handler.shout_cmd = new_shout
    print("shout_cmd patched")
