import sqlite3
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
    import sqlite3
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("⚔️ צבאי", "💰 כלכלי")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "🏗️ **בניה** — בחר תחום:", reply_markup=inline_kb)

@bot.message_handler(func=lambda m: m.text == "👷 עובדים")
def btn_workers(message):
    show_workers_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "💬 שיחה")
def btn_chat(message):
    from msg_handler import chat_cmd
    chat_cmd(message)

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
    bot.send_message(message.chat.id, "⚔️ **צא לקרב?**\n\nמנצח לוקח 10% משאבים + 1 Gild", reply_markup=inline_kb)

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
    bot.send_message(message.chat.id, "🛒 **חנות**\n\nקנייה: 500 יח׳ = 1 Gild\nמכירה: 250 יח׳ = 1 Gild", reply_markup=inline_kb)

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
    import sqlite3
    mapping = {"🏠 צריף קש": "straw_house", "🧱 בית לבנים": "brick_house", "🪚 מנסרה": "sawmill", "🏰 בסיס צבאי": "barracks", "🕵️ בית מרגלים": "spy_house",
        "🏯 מצודה": "fortress",
        "🏯 מצודה": "fortress"}
    building = mapping.get(message.text)
    if building:
        message.text = f"/build {building}"
        from resource_commands import build_cmd
        build_cmd(message)

@bot.message_handler(func=lambda m: m.text in ["👨‍🌾 חקלאי", "🪓 חוטב עצים", "💧 שואב מים", "⛏️ כורה פחם", "🟠 כורה נחושת", "🥇 כורה זהב", "🪖 חייל", "🎖️ מפקד", "👑 גנרל", "🕵️ מרגל", "🐉 דרקון", "🐕 כלב מחץ", "דרקון", "כלב מחץ"])
def btn_hire_action(message):
    import sqlite3
    mapping = {"👨‍🌾 חקלאי": "farmer", "🪓 חוטב עצים": "lumberjack", "💧 שואב מים": "water_drawer", "⛏️ כורה פחם": "coal_miner", "🟠 כורה נחושת": "copper_miner", "🥇 כורה זהב": "gold_miner", "🪖 חייל": "soldier", "🎖️ מפקד": "commander", "👑 גנרל": "general", "🕵️ מרגל": "spy",
        "🐉 דרקון": "dragon",
        "🐕 כלב מחץ": "wardog"}
    worker = mapping.get(message.text)
    if worker:
        message.text = f"/hire {worker}"
        from resource_commands import hire_cmd
        hire_cmd(message)

@bot.message_handler(func=lambda m: m.text == "🏯 מצודה")
def btn_fortress(message):
    user_id = message.from_user.id
    import sqlite3
    from config import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT count FROM buildings WHERE user_id=? AND building_type='fortress'", (user_id,))
    row = c.fetchone()
    has_fortress = row and row[0] > 0
    conn.close()
    
    if has_fortress:
        bot.send_message(message.chat.id, "🏯 יש לך מצודה!\n\n🎯 גיוס ← 🐉🐕")
        return
    
    from fortress_handler import fortress_projects
    open_projects = []
    for pid, proj in fortress_projects.items():
        if proj["partner"] is None and pid != user_id:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT display_name FROM users WHERE user_id=?", (pid,))
            row = c.fetchone()
            name = row[0] if row and row[0] else str(pid)
            conn.close()
            open_projects.append((pid, name))
    
    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.add(types.InlineKeyboardButton("🏯 מצודה חדשה", callback_data="fortress_new"))
    for pid, name in open_projects:
        proj = fortress_projects[pid]
        donated = sum(proj["resources"].values())
        total = sum(FORTRESS_COST.values())
        pct = int(donated / total * 100) if total > 0 else 0
        inline_kb.add(types.InlineKeyboardButton(f"🤝 {name} ({pct}%)", callback_data=f"fortress_join_{pid}"))
    
    from config import FORTRESS_COST
    msg = "🏯 **מצודה** — מבנה משותף\n\n"
    msg += "📜 **חוקים:**\n• דרושים 2 שחקנים\n• כל אחד חייב לתרום\n• גם אם לאחד יש הכל — חייב שותף\n\n"
    msg += "💰 **עלות:**\n"
    for r, amt in FORTRESS_COST.items():
        msg += f"• {r}: {amt}\n"
    msg += "\n⚠️ **בהקמה חדשה יש צורך בשחקן נוסף שיצטרף למיזם!**"
    if open_projects:
        msg += "\n\n🤝 **יזמים שפתחו מצודה — להצטרפות:**"
    
    bot.send_message(message.chat.id, msg, reply_markup=inline_kb)

@bot.message_handler(func=lambda m: m.text == "🏯 מצודה חדשה")
def btn_fortress_start(message):
    message.text = "/fortress open"
    from fortress_handler import fortress_cmd
    fortress_cmd(message)

@bot.message_handler(func=lambda m: m.text.startswith("🤝 הצטרף ל-"))
@bot.message_handler(func=lambda m: m.text.startswith("🤝 הצטרף ל-"))
def btn_fortress_join(message):
    owner_name = message.text[10:]
    message.text = f"/fortress join {owner_name}"
    from fortress_handler import fortress_cmd
    fortress_cmd(message)

@bot.message_handler(func=lambda m: m.text == "💳 תשלום")
def btn_pay(message):
    from admin_commands import pay_cmd
    pay_cmd(message)

@bot.callback_query_handler(func=lambda call: call.data == "community_shout")
def inline_community_shout(call):
    bot.send_message(call.message.chat.id, "📢 שלח את ההודעה שלך לכולם:\n/shout [ההודעה]")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "community_board")
def inline_community_board(call):
    call.message.text = "/board"
    from chat_handler import board_cmd
    board_cmd(call.message)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "community_chat")
def inline_community_chat(call):
    from msg_handler import chat_cmd
    chat_cmd(call.message)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text == "👤 פרופיל")
def btn_profile(message):
    from basic_commands import profile_cmd
    profile_cmd(message)

@bot.message_handler(func=lambda m: m.text == "📚 מדריך")
def btn_doc(message):
    from admin_commands import doc_cmd
    doc_cmd(message)
