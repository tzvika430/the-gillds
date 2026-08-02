from bot_instance import bot
from config import DB_PATH, FORTRESS_COST, RESOURCE_EMOJI, ALL_RESOURCE_IDX
import sqlite3
from telebot import types

# ========== DB FUNCTIONS ==========

def get_fortress_projects():
    """החזר את כל הפרויקטים הפתוחים מה-DB"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # וודא שיש טבלה
    c.execute("""CREATE TABLE IF NOT EXISTS fortress_projects (
        owner_id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        soil REAL DEFAULT 0, stones REAL DEFAULT 0, wood REAL DEFAULT 0,
        gold REAL DEFAULT 0, copper REAL DEFAULT 0,
        owner_donated INTEGER DEFAULT 0, partner_donated INTEGER DEFAULT 0
    )""")
    c.execute("SELECT * FROM fortress_projects")
    rows = c.fetchall()
    conn.close()
    return rows

def save_fortress_project(owner_id, data):
    """שמור פרויקט ל-DB"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS fortress_projects (
        owner_id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        soil REAL DEFAULT 0, stones REAL DEFAULT 0, wood REAL DEFAULT 0,
        gold REAL DEFAULT 0, copper REAL DEFAULT 0,
        owner_donated INTEGER DEFAULT 0, partner_donated INTEGER DEFAULT 0
    )""")
    c.execute("""INSERT OR REPLACE INTO fortress_projects 
        (owner_id, partner_id, soil, stones, wood, gold, copper, owner_donated, partner_donated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (owner_id, data.get("partner"), data["resources"]["soil"], data["resources"]["stones"],
         data["resources"]["wood"], data["resources"]["gold"], data["resources"]["copper"],
         data["owner_donated"], data["partner_donated"]))
    conn.commit()
    conn.close()

def delete_fortress_project(owner_id):
    """מחק פרויקט מה-DB"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM fortress_projects WHERE owner_id=?", (owner_id,))
    conn.commit()
    conn.close()

# ========== CALLBACKS ==========

@bot.callback_query_handler(func=lambda call: call.data == "fortress_donate")
def inline_fortress_donate(call):
    user_id = call.message.chat.id
    projects = get_fortress_projects()
    project = None
    for row in projects:
        if row[0] == user_id or row[1] == user_id:
            project = {"owner": row[0], "partner": row[1],
                       "resources": {"soil": row[2], "stones": row[3], "wood": row[4], "gold": row[5], "copper": row[6]},
                       "owner_donated": row[7], "partner_donated": row[8]}
            break
    
    if not project:
        bot.send_message(user_id, "❌ אין לך פרויקט.")
        bot.answer_callback_query(call.id)
        return
    
    from database import get_resources
    row = get_resources(user_id)
    
    inline_kb = types.InlineKeyboardMarkup()
    for res in ['soil', 'stones', 'wood', 'gold', 'copper']:
        idx = ALL_RESOURCE_IDX.get(res, -1)
        balance = row[idx] if row and idx < len(row) else 0
        needed = FORTRESS_COST[res] - project["resources"][res]
        emoji = RESOURCE_EMOJI.get(res, "")
        if balance > 0 and needed > 0:
            inline_kb.add(types.InlineKeyboardButton(
                f"{emoji} {res} (יש: {balance:.0f}, צריך: {needed:.0f})",
                callback_data=f"donate_{res}"
            ))
    inline_kb.add(types.InlineKeyboardButton("↩️ תפריט ראשי", callback_data="fortress_menu"))
    
    bot.send_message(user_id, "📦 **תרום משאבים**\n\nבחר משאב לתרום:", reply_markup=inline_kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("donate_"))
def inline_donate_choose(call):
    resource = call.data.replace("donate_", "")
    user_id = call.message.chat.id
    
    from database import get_resources
    row = get_resources(user_id)
    idx = ALL_RESOURCE_IDX.get(resource, -1)
    balance = row[idx] if row and idx < len(row) else 0
    
    # save state for next message
    from bot_instance import bot
    bot.send_message(user_id, f"📦 **{resource}**\nיתרה: {balance:.1f}\n\nהקלד כמות לתרום:")
    bot.answer_callback_query(call.id, f"בחר {resource}")
    
    # register next step
    import chat_handler
    # use a simple approach - just tell them to use /fortress give
    bot.send_message(user_id, f"או השתמש בפקודה:\n/fortress give {resource} [כמות]")

@bot.callback_query_handler(func=lambda call: call.data == "fortress_status")
def inline_fortress_status(call):
    user_id = call.message.chat.id
    projects = get_fortress_projects()
    project = None
    for row in projects:
        if row[0] == user_id or row[1] == user_id:
            project = {"owner": row[0], "partner": row[1],
                       "resources": {"soil": row[2], "stones": row[3], "wood": row[4], "gold": row[5], "copper": row[6]},
                       "owner_donated": row[7], "partner_donated": row[8]}
            break
    
    if project:
        status = "🏯 **סטטוס פרויקט**\n\n📊 **מונה:**\n"
        for r, amt in FORTRESS_COST.items():
            status += f"• {r}: {project['resources'][r]:.0f}/{amt}\n"
        status += f"\n🤝 שותף: {'יש' if project['partner'] else 'אין'}"
    else:
        status = "🏯 אין לך פרויקט פעיל."
    
    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.add(types.InlineKeyboardButton("📦 תרום משאבים", callback_data="fortress_donate"),
                  types.InlineKeyboardButton("↩️ תפריט ראשי", callback_data="fortress_menu"))
    bot.send_message(user_id, status, reply_markup=inline_kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "fortress_menu")
def inline_fortress_menu(call):
    from button_handler import show_main_menu
    show_main_menu(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "fortress_new")
def inline_fortress_new(call):
    call.message.text = "/fortress open"
    fortress_cmd(call.message)
    bot.answer_callback_query(call.id, "נפתח!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fortress_join_"))
def inline_fortress_join(call):
    pid = int(call.data.replace("fortress_join_", ""))
    call.message.text = f"/fortress join {pid}"
    fortress_cmd(call.message)
    bot.answer_callback_query(call.id, "מצטרף...")

# ========== COMMANDS ==========

@bot.message_handler(commands=['fortress'])
def fortress_cmd(message):
    parts = message.text.split()
    subcmd = parts[1] if len(parts) > 1 else "status"
    user_id = message.from_user.id
    
    if subcmd == "open" or subcmd == "start":
        projects = get_fortress_projects()
        for row in projects:
            if row[0] == user_id:
                bot.reply_to(message, "❌ כבר יש לך פרויקט.")
                return
        
        save_fortress_project(user_id, {"partner": None, "resources": {"soil": 0, "stones": 0, "wood": 0, "gold": 0, "copper": 0}, "owner_donated": False, "partner_donated": False})
        
        msg = "🏯 **פרויקט מצודה נפתח!**\n\n📊 **מונה תרומות:**\n"
        for r, amt in FORTRESS_COST.items():
            msg += f"• {r}: 0/{amt}\n"
        msg += f"\n🆔 קוד: {user_id}\n🤝 /fortress join [שם]\n\n⏳ מחכים לשחקן נוסף שיצטרף..."
        
        inline_kb = types.InlineKeyboardMarkup()
        inline_kb.add(types.InlineKeyboardButton("📦 תרום משאבים", callback_data="fortress_donate"),
                      types.InlineKeyboardButton("📊 צפה בסטטוס", callback_data="fortress_status"))
        inline_kb.add(types.InlineKeyboardButton("↩️ תפריט ראשי", callback_data="fortress_menu"))
        bot.send_message(user_id, msg, reply_markup=inline_kb)
    
    elif subcmd == "join":
        if len(parts) < 3:
            bot.reply_to(message, "/fortress join [שם או ID]")
            return
        target = parts[2]
        projects = get_fortress_projects()
        owner_id = None
        for row in projects:
            if str(row[0]) == target and row[1] is None:
                owner_id = row[0]
                break
        
        if not owner_id:
            bot.reply_to(message, "❌ פרויקט לא נמצא או כבר יש שותף.")
            return
        if owner_id == user_id:
            bot.reply_to(message, "❌ לא יכול להצטרף לעצמך.")
            return
        
        # update DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE fortress_projects SET partner_id=? WHERE owner_id=?", (user_id, owner_id))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"✅ הצטרפת לפרויקט!\n\n📦 /fortress give [משאב] [כמות] — תרום")
        bot.send_message(owner_id, f"🤝 שחקן הצטרף למצודה שלך!")
    
    elif subcmd == "give":
        if len(parts) < 4:
            bot.reply_to(message, "/fortress give [משאב] [כמות]")
            return
        resource, amount = parts[2], float(parts[3]) if parts[3].replace('.','').replace('-','').isdigit() else 0
        
        projects = get_fortress_projects()
        project = owner_id = my_role = None
        for row in projects:
            if row[0] == user_id:
                project = {"owner": row[0], "partner": row[1],
                           "resources": {"soil": row[2], "stones": row[3], "wood": row[4], "gold": row[5], "copper": row[6]},
                           "owner_donated": row[7], "partner_donated": row[8]}
                owner_id, my_role = row[0], "owner"
                break
            if row[1] == user_id:
                project = {"owner": row[0], "partner": row[1],
                           "resources": {"soil": row[2], "stones": row[3], "wood": row[4], "gold": row[5], "copper": row[6]},
                           "owner_donated": row[7], "partner_donated": row[8]}
                owner_id, my_role = row[0], "partner"
                break
        
        if not project:
            bot.reply_to(message, "❌ אין לך פרויקט.")
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
        project["resources"][resource] += min(amount, needed - project["resources"][resource])
        if my_role == "owner": project["owner_donated"] = True
        else: project["partner_donated"] = True
        
        done = all(project["resources"][r] >= FORTRESS_COST[r] for r in FORTRESS_COST)
        both = project["owner_donated"] and project["partner_donated"]
        
        if done and both:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO buildings (user_id, building_type, count) VALUES (?, 'fortress', 1)", (project["owner"],))
            conn.commit()
            conn.close()
            delete_fortress_project(owner_id)
            bot.send_message(project["owner"], "🏯 **המצודה נבנתה!** 🎉\nעכשיו אפשר לגייס 🐉🐕")
            if project["partner"]:
                bot.send_message(project["partner"], "🏯 **המצודה נבנתה!** 🎉")
        else:
            save_fortress_project(owner_id, project)
            status = "📦 **תרומה התקבלה!**\n"
            for r, amt in FORTRESS_COST.items():
                status += f"• {r}: {project['resources'][r]:.0f}/{amt}\n"
            bot.reply_to(message, status)
    
    else:
        projects = get_fortress_projects()
        project = None
        for row in projects:
            if row[0] == user_id or row[1] == user_id:
                project = {"owner": row[0], "partner": row[1],
                           "resources": {"soil": row[2], "stones": row[3], "wood": row[4], "gold": row[5], "copper": row[6]}}
                break
        
        if project:
            status = "🏯 **פרויקט מצודה**\n\n📊 **מונה:**\n"
            for r, amt in FORTRESS_COST.items():
                status += f"• {r}: {project['resources'][r]:.0f}/{amt}\n"
            bot.reply_to(message, status)
        else:
            msg = "🏯 **מצודה** — מבנה משותף\n\n📜 **חוקים:**\n• דרושים 2 שחקנים\n• כל אחד חייב לתרום\n• גם אם לאחד יש הכל — חייב שותף\n\n💰 **עלות:**\n"
            for r, amt in FORTRESS_COST.items():
                msg += f"• {r}: {amt}\n"
            msg += "\n🏯 /fortress open — פתח פרויקט\n🤝 /fortress join [ID] — הצטרף\n📦 /fortress give [משאב] [כמות] — תרום"
            bot.reply_to(message, msg)
