from telebot import types
from bot_instance import bot
from menu import show_main_menu, show_army_menu, show_recruit_menu, show_economy_menu, show_build_menu, show_workers_menu, show_community_menu

@bot.message_handler(func=lambda m: m.text in ["📋 תפריט", "↩️ תפריט ראשי"])
def btn_main_menu(message):
    show_main_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "⚔️ צבא")
def btn_army(message):
    show_army_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🎯 גיוס")
def btn_recruit(message):
    show_recruit_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "💰 כלכלה")
def btn_economy(message):
    show_economy_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🏗️ בניה")
def btn_build(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("⚔️ צבאי", "💰 כלכלי")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "🏗️ **בניה** — בחר תחום:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "👷 עובדים")
def btn_workers(message):
    show_workers_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "👥 קהילה")
def btn_community(message):
    show_community_menu(message.chat.id)



@bot.message_handler(func=lambda m: m.text == "🕵️ מודיעין")
def btn_spy(message):
    from spy_handler import spy_cmd
    spy_cmd(message)

@bot.message_handler(func=lambda m: m.text == "⚔️ מלחמה")
def btn_war(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("⚔️ כן, צא לקרב!", "🕊️ לא, שלום")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "⚔️ **צא לקרב?**\n\nמנצח לוקח 10% משאבים + 1 Gild", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "⚔️ כן, צא לקרב!")
def btn_attack_yes(message):
    from attack_handler import attack_cmd
    attack_cmd(message)

@bot.message_handler(func=lambda m: m.text == "🏪 שוק")
def btn_market(message):
    from trade_handler import trade_menu
    trade_menu(message)

@bot.message_handler(func=lambda m: m.text == "🛒 חנות")
def btn_shop(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🛒 קנה", "💰 מכור")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "🛒 **חנות**\n\nקנייה: 500 יח׳ = 1 Gild\nמכירה: 250 יח׳ = 1 Gild", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "🏆 מובילים")
def btn_leaderboard(message):
    from basic_commands import leaderboard
    leaderboard(message)

@bot.message_handler(func=lambda m: m.text == "⚔️ צבאי")
def btn_build_military(message):
    from menu import show_build_military_menu
    show_build_military_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "💰 כלכלי")
def btn_build_economy(message):
    from menu import show_build_economy_menu
    show_build_economy_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text in ["🏠 צריף קש", "🧱 בית לבנים", "🪚 מנסרה", "🏰 בסיס צבאי", "🕵️ בית מרגלים"])
def btn_build_action(message):
    mapping = {"🏠 צריף קש": "straw_house", "🧱 בית לבנים": "brick_house", "🪚 מנסרה": "sawmill", "🏰 בסיס צבאי": "barracks", "🕵️ בית מרגלים": "spy_house"}
    building = mapping.get(message.text)
    if building:
        message.text = f"/build {building}"
        from resource_commands import build_cmd
        build_cmd(message)

@bot.message_handler(func=lambda m: m.text in ["👨‍🌾 חקלאי", "🪓 חוטב עצים", "💧 שואב מים", "⛏️ כורה פחם", "🟠 כורה נחושת", "🥇 כורה זהב", "🪖 חייל", "🎖️ מפקד", "👑 גנרל", "🕵️ מרגל"])
def btn_hire_action(message):
    mapping = {"👨‍🌾 חקלאי": "farmer", "🪓 חוטב עצים": "lumberjack", "💧 שואב מים": "water_drawer", "⛏️ כורה פחם": "coal_miner", "🟠 כורה נחושת": "copper_miner", "🥇 כורה זהב": "gold_miner", "🪖 חייל": "soldier", "🎖️ מפקד": "commander", "👑 גנרל": "general", "🕵️ מרגל": "spy"}
    worker = mapping.get(message.text)
    if worker:
        message.text = f"/hire {worker}"
        from resource_commands import hire_cmd
        hire_cmd(message)

@bot.message_handler(func=lambda m: m.text == "💳 תשלום")
def btn_pay(message):
    from admin_commands import pay_cmd
    pay_cmd(message)

@bot.message_handler(func=lambda m: m.text == "👤 פרופיל")
def btn_profile(message):
    from basic_commands import profile_cmd
    profile_cmd(message)

@bot.message_handler(func=lambda m: m.text == "📚 מדריך")
def btn_doc(message):
    from admin_commands import doc_cmd
    doc_cmd(message)
