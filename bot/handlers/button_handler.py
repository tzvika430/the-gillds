from telebot import types
from bot_instance import bot

# ============ מיפוי כפתורים ============
BUTTON_ACTIONS = {
    # ראשיים
    "👤 פרופיל": ("profile_cmd", "basic_commands"),
    "📚 מדריך": ("doc_cmd", "admin_commands"),
    "⚔️ קרב": ("attack_cmd", "attack_handler"),
    "🏪 שוק": ("trade_menu", "trade_handler"),
    "🏆 מובילים": ("leaderboard", "basic_commands"),
    "💳 תשלום": ("pay_cmd", "admin_commands"),
    "📝 הרשמה": ("start_register", "register_handler"),
    "📢 קהילה": (None, None),  # מטופל בנפרד
    "📋 תפריט": ("show_main_menu", None),
    # בנייה
    "🏠 בית קש": ("build_straw_house", None),
    "🧱 בית לבנים": ("build_brick_house", None),
    "🪚 מנסרה": ("build_sawmill", None),
    "🏰 בסיס צבאי": ("build_barracks", None),
    # עובדים
    "👨‍🌾 חקלאי": ("hire_farmer", None),
    "🪓 חוטב עצים": ("hire_lumberjack", None),
    "💧 שואב מים": ("hire_water_drawer", None),
    "⛏️ כורה פחם": ("hire_coal_miner", None),
    "🟠 כורה נחושת": ("hire_copper_miner", None),
    "🥇 כורה זהב": ("hire_gold_miner", None),
    "🪖 חייל": ("hire_soldier", None),
    "🎖️ מפקד": ("hire_commander", None),
    "👑 גנרל": ("hire_general", None),
}

@bot.message_handler(func=lambda m: m.text in BUTTON_ACTIONS or m.text in ["🏗️ בניה", "👷 עובדים", "📢 קהילה", "↩️ תפריט ראשי"])
def handle_all_buttons(message):
    text = message.text
    
    # תפריטי משנה
    if text == "🏗️ בניה":
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("🏠 בית קש", "🧱 בית לבנים")
        keyboard.add("🪚 מנסרה", "🏰 בסיס צבאי")
        keyboard.add("↩️ תפריט ראשי")
        bot.send_message(message.chat.id, "🏗️ בחר מבנה:", reply_markup=keyboard)
        return
    
    if text == "👷 עובדים":
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("👨‍🌾 חקלאי", "🪓 חוטב עצים")
        keyboard.add("💧 שואב מים", "⛏️ כורה פחם")
        keyboard.add("🟠 כורה נחושת", "🥇 כורה זהב")
        keyboard.add("🪖 חייל", "🎖️ מפקד", "👑 גנרל")
        keyboard.add("↩️ תפריט ראשי")
        bot.send_message(message.chat.id, "👷 בחר עובד:", reply_markup=keyboard)
        return
    
    if text == "📢 קהילה":
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("📢 /shout", "📋 /board")
        keyboard.add("🏆 /leaderboard")
        keyboard.add("↩️ תפריט ראשי")
        bot.send_message(message.chat.id, "📢 קהילה", reply_markup=keyboard)
        return
    
    if text == "↩️ תפריט ראשי":
        show_main_menu(message.chat.id)
        return
    
    # כפתורי פעולה
    if text in BUTTON_ACTIONS:
        action, module = BUTTON_ACTIONS[text]
        
        if action == "show_main_menu":
            show_main_menu(message.chat.id)
            return
        
        # בנייה
        if action.startswith("build_"):
            building = action.replace("build_", "")
            message.text = f"/build {building}"
            from resource_commands import build_cmd
            build_cmd(message)
            return
        
        # עובדים
        if action.startswith("hire_"):
            worker = action.replace("hire_", "")
            message.text = f"/hire {worker}"
            from resource_commands import hire_cmd
            hire_cmd(message)
            return
        
        # פקודות רגילות
        if module:
            mod = __import__(module, fromlist=[action])
            func = getattr(mod, action)
            func(message)

def show_main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ קרב")
    keyboard.add("🏪 שוק", "🏆 מובילים", "💳 תשלום")
    keyboard.add("🏗️ בניה", "👷 עובדים", "🛒 חנות")
    keyboard.add("📝 הרשמה", "📢 קהילה", "📋 תפריט")
    bot.send_message(chat_id, "📋 תפריט ראשי:", reply_markup=keyboard)
