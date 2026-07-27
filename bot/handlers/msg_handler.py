from bot_instance import bot
from config import DB_PATH
import sqlite3

@bot.message_handler(commands=['msg'])
def msg_cmd(message):
    """שלח הודעה פרטית לשחקן אחר"""
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=2)
    
    if len(parts) < 3:
        bot.reply_to(message, "שימוש: /msg [שם] [הודעה]\nלדוגמה: /msg יהונתן היי, מה קורה?")
        return
    
    target_name = parts[1]
    msg_text = parts[2]
    
    # חפש שחקן
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, display_name FROM users WHERE display_name LIKE ? OR username LIKE ?", 
              (f"%{target_name}%", f"%{target_name}%"))
    results = c.fetchall()
    conn.close()
    
    if not results:
        bot.reply_to(message, f"❌ לא נמצא: {target_name}")
        return
    
    target_id, target_display = results[0]
    
    if target_id == user_id:
        bot.reply_to(message, "❌ אי אפשר לשלוח לעצמך!")
        return
    
    # קבל שם של השולח
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT display_name FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    sender_name = row[0] if row and row[0] else (message.from_user.username or str(user_id))
    conn.close()
    
    # שלח לנמען
    try:
        bot.send_message(target_id, f"🏰 **Gild Economy** 💬\n\n**{sender_name}** שולח לך:\n\n{msg_text}\n\n📋 /menu — חזרה לתפריט")
        bot.reply_to(message, f"✅ ההודעה נשלחה ל-{target_display or target_name}")
    except:
        bot.reply_to(message, "❌ לא ניתן לשלוח הודעה (המשתמש חסם את הבוט)")

@bot.message_handler(commands=['group'])
def group_cmd(message):
    """קישור לקבוצת השחקנים"""
    msg = """👥 **קבוצת שחקנים**

🔗 הצטרף לקבוצה:
(בקש מהאדמין קישור לקבוצה)

💬 **צ'אט במשחק:**
/shout [הודעה] — שלח לכולם
/board — לוח מודעות
/msg [שם] [הודעה] — הודעה פרטית"""
    bot.reply_to(message, msg)
