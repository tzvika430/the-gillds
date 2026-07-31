from bot_instance import bot
from config import DB_PATH, FORTRESS_COST
import sqlite3
from telebot import types

fortress_projects = {}

@bot.callback_query_handler(func=lambda call: call.data == "fortress_new")
def inline_fortress_new(call):
    call.message.text = "/fortress open"
    fortress_cmd(call.message)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "fortress_donate")
def inline_fortress_donate(call):
    bot.send_message(call.message.chat.id, "📦 **תרום משאבים**\n\n/fortress give [משאב] [כמות]\n\nמשאבים: soil, stones, wood, gold, copper")
    bot.answer_callback_query(call.id, "השתמש בפקודה /fortress give")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fortress_join_"))
def inline_fortress_join(call):
    pid = call.data.replace("fortress_join_", "")
    call.message.text = f"/fortress join {pid}"
    fortress_cmd(call.message)
    bot.answer_callback_query(call.id, "מצטרף...")

@bot.callback_query_handler(func=lambda call: call.data == "fortress_status")
def inline_fortress_status(call):
    call.message.text = "/fortress"
    fortress_cmd(call.message)
    bot.answer_callback_query(call.id, "סטטוס פרויקט")

@bot.callback_query_handler(func=lambda call: call.data == "fortress_menu")
def inline_fortress_menu(call):
    from button_handler import show_main_menu
    show_main_menu(call.message.chat.id)
    bot.answer_callback_query(call.id, "תפריט ראשי")

@bot.message_handler(commands=['fortress'])
def fortress_cmd(message):
    parts = message.text.split()
    subcmd = parts[1] if len(parts) > 1 else "status"
    user_id = message.from_user.id
    
    my_project = None
    my_role = None
    for pid, proj in fortress_projects.items():
        if proj["owner"] == user_id:
            my_project, my_role = proj, "owner"
            break
        if proj["partner"] == user_id:
            my_project, my_role = proj, "partner"
            break
    
    if subcmd == "open" or subcmd == "start":
        if my_project:
            bot.reply_to(message, "❌ כבר יש לך פרויקט.")
            return
        fortress_projects[user_id] = {
            "owner": user_id, "partner": None,
            "resources": {"soil": 0, "stones": 0, "wood": 0, "gold": 0, "copper": 0},
            "owner_donated": False, "partner_donated": False
        }
        msg = "🏯 **פרויקט מצודה נפתח!**\n\n"
        msg += "📊 **מונה תרומות:**\n"
        for r, amt in FORTRESS_COST.items():
            msg += f"• {r}: 0/{amt}\n"
        msg += f"\n🆔 קוד: {user_id}\n🤝 /fortress join [שם]\n📦 /fortress give [משאב] [כמות]\n\n⏳ מחכים לשחקן נוסף שיצטרף..."
        
        inline_kb = types.InlineKeyboardMarkup()
        inline_kb.add(types.InlineKeyboardButton("📦 תרום משאבים", callback_data="fortress_donate"),
                      types.InlineKeyboardButton("📊 צפה בסטטוס", callback_data="fortress_status"))
        inline_kb.add(types.InlineKeyboardButton("↩️ תפריט ראשי", callback_data="fortress_menu"))
        bot.send_message(message.chat.id, msg, reply_markup=inline_kb)
    
    elif subcmd == "join":
        if len(parts) < 3:
            bot.reply_to(message, "/fortress join [שם]")
            return
        owner_name = parts[2]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE display_name LIKE ? OR username LIKE ?", (f"%{owner_name}%", f"%{owner_name}%"))
        row = c.fetchone()
        conn.close()
        if not row:
            bot.reply_to(message, f"❌ לא נמצא: {owner_name}")
            return
        owner_id = row[0]
        if owner_id not in fortress_projects:
            bot.reply_to(message, "❌ אין פרויקט פתוח.")
            return
        if fortress_projects[owner_id]["partner"]:
            bot.reply_to(message, "❌ כבר יש שותף.")
            return
        if owner_id == user_id:
            bot.reply_to(message, "❌ לא יכול להצטרף לעצמך.")
            return
        fortress_projects[owner_id]["partner"] = user_id
        bot.reply_to(message, f"✅ הצטרפת ל-{owner_name}!")
        bot.send_message(owner_id, f"🤝 שחקן הצטרף למצודה שלך!")
    
    elif subcmd == "give":
        if not my_project:
            bot.reply_to(message, "❌ אין לך פרויקט. /fortress open")
            return
        if len(parts) < 4:
            bot.reply_to(message, "/fortress give [משאב] [כמות]\nמשאבים: soil, stones, wood, gold, copper")
            return
        resource = parts[2]
        try: amount = float(parts[3])
        except:
            bot.reply_to(message, "כמות חייבת להיות מספר")
            return
        if resource not in FORTRESS_COST:
            bot.reply_to(message, f"צריך: {', '.join(FORTRESS_COST.keys())}")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(f"SELECT {resource} FROM resources WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row or row[0] < amount:
            conn.close()
            bot.reply_to(message, f"❌ אין מספיק {resource}")
            return
        c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)-? WHERE user_id=?", (amount, user_id))
        conn.commit()
        conn.close()
        
        needed = FORTRESS_COST[resource]
        my_project["resources"][resource] += min(amount, needed - my_project["resources"][resource])
        if my_role == "owner": my_project["owner_donated"] = True
        else: my_project["partner_donated"] = True
        
        done = all(my_project["resources"][r] >= FORTRESS_COST[r] for r in FORTRESS_COST)
        both = my_project["owner_donated"] and my_project["partner_donated"]
        
        if done and both:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO buildings (user_id, building_type, count) VALUES (?, 'fortress', 1)", (my_project["owner"],))
            conn.commit()
            conn.close()
            bot.send_message(my_project["owner"], "🏯 **המצודה נבנתה!** 🎉\nעכשיו אפשר לגייס 🐉🐕")
            if my_project["partner"]:
                bot.send_message(my_project["partner"], "🏯 **המצודה נבנתה!** 🎉\nעכשיו אפשר לגייס 🐉🐕")
            for pid in list(fortress_projects.keys()):
                if fortress_projects[pid]["owner"] == my_project["owner"]:
                    del fortress_projects[pid]
        else:
            status = "📦 **תרומה התקבלה!**\n"
            for r, amt in FORTRESS_COST.items():
                status += f"• {r}: {my_project['resources'][r]:.0f}/{amt}\n"
            status += f"\n🤝 תרומה משני הצדדים: {'✅' if both else '❌'}"
            bot.reply_to(message, status)
            bot.send_message(message.chat.id, "💡 **טיפ:** שחקן נוסף חייב להצטרף ולתרום!")
    
    else:
        if my_project:
            status = "🏯 **פרויקט מצודה**\n\n"
            for r, amt in FORTRESS_COST.items():
                status += f"• {r}: {my_project['resources'][r]:.0f}/{amt}\n"
            status += f"\n🤝 שותף: {'יש' if my_project['partner'] else 'אין'}"
            status += "\n📦 /fortress give [משאב] [כמות]"
            bot.reply_to(message, status)
        else:
            msg = "🏯 **מצודה** — מבנה משותף\n\n"
            msg += "📜 **חוקים:**\n• דרושים 2 שחקנים\n• כל אחד חייב לתרום\n• גם אם לאחד יש הכל — חייב שותף\n\n"
            msg += "💰 **עלות:**\n"
            for r, amt in FORTRESS_COST.items():
                msg += f"• {r}: {amt}\n"
            msg += "\n🏯 /fortress open — פתח פרויקט\n🤝 /fortress join [שם] — הצטרף\n📦 /fortress give [משאב] [כמות] — תרום"
            bot.reply_to(message, msg)
