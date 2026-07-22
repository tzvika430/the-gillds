from telebot import types
from bot_instance import bot
import sqlite3
from config import DB_PATH

# שמירת מצב רישום זמני
register_state = {}

@bot.message_handler(commands=['register'])
def start_register(message):
    user_id = message.from_user.id
    
    # בדוק אם כבר רשום
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, display_name FROM users WHERE user_id=?", (user_id,))
    existing = c.fetchone()
    conn.close()
    
    if existing and existing[1]:
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
        keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
        keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
        bot.send_message(user_id, f"✅ אתה כבר רשום כ-**{existing[1]}**!\nשלח /profile לפרופיל שלך.", reply_markup=keyboard)
        return
    
    register_state[user_id] = {"step": "name"}
    
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add("❌ בטל הרשמה")
    bot.send_message(user_id, """🎮 **הרשמה למשחק Gild Economy**

📝 שלב 1/3: **בחר שם שחקן**

איך קוראים לך בממלכה?
שלח את השם שלך (או כינוי):""", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in register_state and register_state[m.from_user.id]["step"] == "name")
def register_get_name(message):
    user_id = message.from_user.id
    
    if message.text == "❌ בטל הרשמה":
        del register_state[user_id]
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
        keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
        keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
        bot.send_message(user_id, "ההרשמה בוטלה.", reply_markup=keyboard)
        return
    
    name = message.text.strip()
    if len(name) < 2 or len(name) > 20:
        bot.send_message(user_id, "❌ שם צריך להיות בין 2 ל-20 תווים. נסה שוב:")
        return
    
    register_state[user_id]["name"] = name
    register_state[user_id]["step"] = "kingdom"
    
    bot.send_message(user_id, f"""✅ שם: **{name}**

📝 שלב 2/3: **בחר שם לממלכה שלך**

איך תקרא לממלכה? (2-20 תווים):""")

@bot.message_handler(func=lambda m: m.from_user.id in register_state and register_state[m.from_user.id]["step"] == "kingdom")
def register_get_kingdom(message):
    user_id = message.from_user.id
    
    if message.text == "❌ בטל הרשמה":
        del register_state[user_id]
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
        keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
        keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
        bot.send_message(user_id, "ההרשמה בוטלה.", reply_markup=keyboard)
        return
    
    kingdom = message.text.strip()
    if len(kingdom) < 2 or len(kingdom) > 20:
        bot.send_message(user_id, "❌ שם ממלכה צריך להיות בין 2 ל-20 תווים. נסה שוב:")
        return
    
    register_state[user_id]["kingdom"] = kingdom
    register_state[user_id]["step"] = "confirm"
    
    name = register_state[user_id]["name"]
    
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("✅ אשר הרשמה", "❌ בטל הרשמה")
    
    bot.send_message(user_id, f"""📋 **סיכום הרשמה:**

👤 שם שחקן: **{name}**
🏰 שם ממלכה: **{kingdom}**

האם לאשר?""", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in register_state and register_state[m.from_user.id]["step"] == "confirm")
def register_confirm(message):
    user_id = message.from_user.id
    
    if message.text == "❌ בטל הרשמה" or message.text != "✅ אשר הרשמה":
        del register_state[user_id]
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
        keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
        keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
        bot.send_message(user_id, "ההרשמה בוטלה.", reply_markup=keyboard)
        return
    
    name = register_state[user_id]["name"]
    kingdom = register_state[user_id]["kingdom"]
    username = message.from_user.username or str(user_id)
    
    # שמור ב-DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE users SET display_name=?, kingdom=? WHERE user_id=?""", 
              (name, kingdom, user_id))
    conn.commit()
    conn.close()
    
    del register_state[user_id]
    
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
    keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
    keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
    
    bot.send_message(user_id, f"""🎉 **ברוך הבא, {name} מ{kingdom}!**

🏰 הממלכה שלך הוקמה!
יש לך 10 Gild, farmer אחד, lumberjack אחד, ו-straw_house.

📦 שלח /resources לראות את המשאבים שלך
📚 שלח /doc למדריך המלא
👤 שלח /profile לפרופיל שלך""", reply_markup=keyboard)
