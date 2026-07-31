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
    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.add(types.InlineKeyboardButton("📢 שלח לכולם", callback_data="community_shout"),
                  types.InlineKeyboardButton("📋 לוח מודעות", callback_data="community_board"))
    inline_kb.add(types.InlineKeyboardButton("💬 שיחה פרטית", callback_data="community_chat"))
    bot.send_message(chat_id, "👥 **קהילה**", reply_markup=inline_kb)

# ============ ענף בניה — צבאי ============
def show_build_military_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏰 בסיס צבאי", "🕵️ בית מרגלים")
    keyboard.add("🏯 מצודה")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "🏗️ **בניה צבאית**", reply_markup=keyboard)

# ============ ענף בניה — כלכלי ============
def show_build_economy_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏠 צריף קש", "🧱 בית לבנים")
    keyboard.add("🪚 מנסרה")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "🏗️ **בניה כלכלית**", reply_markup=keyboard)

# ============ ענף גיוס — כולל מרגל ============
def show_recruit_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🪖 חייל", "🎖️ מפקד")
    keyboard.add("👑 גנרל", "🕵️ מרגל")
    keyboard.add("🐉 דרקון", "🐕 כלב מחץ")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(chat_id, "🎯 **גיוס**\n\n🪖 חייל (2 Gild)\n🎖️ מפקד (10 Gild, 6 חיילים)\n👑 גנרל (30 Gild, 3 מפקדים)\n🕵️ מרגל (8 Gild, בית מרגלים)\n🐉 דרקון (50 Gild, מצודה)\n🐕 כלב מחץ (25 Gild, מצודה)", reply_markup=keyboard)
