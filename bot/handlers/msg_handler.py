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

@bot.message_handler(commands=['chat'])
def chat_cmd(message):
    """פתח רשימת שחקנים לשיחה פרטית"""
    from telebot import types
    import sqlite3
    from config import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, display_name, username FROM users WHERE user_id != ?", (message.from_user.id,))
    users = c.fetchall()
    conn.close()
    
    if not users:
        bot.reply_to(message, "אין שחקנים אחרים עדיין")
        return
    
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for uid, dname, uname in users:
        name = dname or uname or str(uid)
        keyboard.add(types.KeyboardButton(f"💬 {name}"))
    keyboard.add("↩️ תפריט ראשי")
    
    bot.send_message(message.chat.id, "💬 **שיחה פרטית**\n\nבחר שחקן:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("💬 "))
def handle_chat_click(message):
    target_name = message.text[2:].strip()  # הסר "💬 "
    
    if target_name == "תפריט ראשי":
        return
    
    # שמור את שם היעד ושלח הודעה
    message.text = f"/msg {target_name} "
    bot.reply_to(message, f"💬 התחלת שיחה עם {target_name}.\nהקלד את ההודעה עכשיו:\n(השתמש שוב בפקודה: /msg {target_name} [הודעה])")
