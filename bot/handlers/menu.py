from telebot import types
from bot_instance import bot

# ============ גזע — 6 כפתורים ============
def show_main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ צבא")
    keyboard.add("💰 כלכלה", "🏗️ בניה", "👷 עובדים")
    keyboard.add("👥 קהילה")
    bot.send_message(chat_id, "📋 תפריט ראשי:", reply_markup=keyboard)

# ============ ענף צבא ============
def show_army_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🎯 גיוס", "🕵️ מודיעין")
    keyboard.add("⚔️ מלחמה")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "⚔️ **צבא**\n\n🎯 גיוס — גייס חיילים\n🕵️ מודיעין — שלח מרגלים\n⚔️ מלחמה — תקוף שחקנים", reply_markup=keyboard)

def show_recruit_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🪖 חייל", "🎖️ מפקד", "👑 גנרל")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "🎯 **גיוס חיילים**", reply_markup=keyboard)

# ============ ענף כלכלה ============
def show_economy_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏪 שוק", "🛒 חנות")
    keyboard.add("🏆 מובילים", "💳 תשלום")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "💰 **כלכלה**\n\n🏪 שוק — קנה/מכור לשחקנים\n🛒 חנות — קנה/מכור למערכת\n🏆 מובילים — טבלת דירוג\n💳 תשלום — המשך משחק", reply_markup=keyboard)

# ============ ענף בניה ============
def show_build_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏠 צריף קש", "🧱 בית לבנים")
    keyboard.add("🪚 מנסרה", "🏰 בסיס צבאי")
    keyboard.add("🕵️ בית מרגלים")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "🏗️ **בניה**", reply_markup=keyboard)

# ============ ענף עובדים ============
def show_workers_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("👨‍🌾 חקלאי", "🪓 חוטב עצים")
    keyboard.add("💧 שואב מים", "⛏️ כורה פחם")
    keyboard.add("🟠 כורה נחושת", "🥇 כורה זהב")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "👷 **עובדים**", reply_markup=keyboard)

# ============ ענף קהילה ============
def show_community_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("📢 /shout", "📋 /board")
    keyboard.add("💬 שיחה")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "👥 **קהילה**\n\n📢 /shout — שלח לכולם\n📋 /board — לוח מודעות\n💬 שיחה — הודעה פרטית", reply_markup=keyboard)
