from config import *
from database import update_time, get_resources, buy_from_system
from building_service import build_building, hire_worker
from bot_instance import bot
from basic_commands import get_main_keyboard
import sqlite3

@bot.message_handler(commands=['resources'])
def resources_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    row = get_resources(message.from_user.id)
    if not row:
        bot.reply_to(message, "שלח /start קודם!")
        return
    water, coal, copper, gold = row[1], row[2], row[3], row[4]
    gild = row[5]
    wheat = row[6] if len(row) > 6 else 0
    soil = row[7] if len(row) > 7 else 0
    wood = row[8] if len(row) > 8 else 0
    stones = row[9] if len(row) > 9 else 0
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=?", (message.from_user.id,))
    workers = c.fetchall()
    c.execute("SELECT building_type, count FROM buildings WHERE user_id=?", (message.from_user.id,))
    buildings = c.fetchall()
    conn.close()
    wstr = ", ".join([f"{w}: {c}" for w, c in workers]) if workers else "אין"
    bstr = ", ".join([f"{b}: {c}" for b, c in buildings]) if buildings else "אין"
    msg = f"""📦 המשאבים שלך

💧 מים: {water:.2f}
⚫ פחם: {coal:.2f}
🟠 נחושת: {copper:.2f}
🥇 זהב: {gold:.2f}
🌾 חיטה: {wheat:.2f}
🟤 אדמה: {soil:.2f}
🪵 עץ: {wood:.2f}
🪨 אבנים: {stones:.2f}

💰 Gild: {gild:.2f}

👷 עובדים:
{wstr}

🏠 מבנים:
{bstr}"""
    keyboard = get_main_keyboard()
    bot.reply_to(message, msg, reply_markup=keyboard)

@bot.message_handler(commands=['build'])
def build_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "שימוש: /build מבנה\nאפשרויות: straw_house, brick_house, sawmill")
        return
    building_type = parts[1]
    ok, msg = build_building(message.from_user.id, building_type)
    if ok:
        bot.reply_to(message, f"✅ נבנה {building_type}!")
    else:
        bot.reply_to(message, f"❌ {msg}")

@bot.message_handler(commands=['hire'])
def hire_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "שימוש: /hire סוג\nאפשרויות: farmer, lumberjack, water_drawer, coal_miner, copper_miner, gold_miner")
        return
    worker_type = parts[1]
    ok, msg = hire_worker(message.from_user.id, worker_type)
    if ok:
        bot.reply_to(message, f"✅ {worker_type} התקבל לעבודה!")
    else:
        bot.reply_to(message, f"❌ {msg}")

@bot.message_handler(commands=['store'])
def store_cmd(message):
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 3:
        names = ', '.join(ALL_RESOURCE_IDX.keys())
        bot.reply_to(message, f'שימוש: /store משאב כמות\nאפשרויות: {names}\nשער: {NPC_BUY_RATE} יחידות ל-1 Gild')
        return
    resource = parts[1]
    try: amount = float(parts[2])
    except ValueError:
        bot.reply_to(message, 'כמות חייבת להיות מספר')
        return
    if amount <= 0:
        bot.reply_to(message, 'כמות חייבת להיות חיובית')
        return
    ok, msg = buy_from_system(message.from_user.id, resource, amount)
    if ok:
        cost = amount / NPC_BUY_RATE
        bot.reply_to(message, f'✅ קנית {amount} {resource} מהמערכת\n💰 עלות: {cost:.2f} Gild\n⏰ שער: 1 Gild = {NPC_BUY_RATE} יחידות')
    else:
        bot.reply_to(message, f'❌ {msg}')


@bot.message_handler(commands=['sellstore'])
def sellstore_cmd(message):
    """מכור משאבים למערכת"""
    update_time(message.from_user.id, message.from_user.username)
    parts = message.text.split()
    if len(parts) != 3:
        names = ', '.join(ALL_RESOURCE_IDX.keys())
        bot.reply_to(message, f'שימוש: /sellstore משאב כמות\nאפשרויות: {names}\nשער: {int(NPC_BUY_RATE/2)} יחידות = 1 Gild (חצי ממחיר הקנייה)')
        return
    resource = parts[1]
    try: amount = float(parts[2])
    except ValueError:
        bot.reply_to(message, 'כמות חייבת להיות מספר')
        return
    if amount <= 0:
        bot.reply_to(message, 'כמות חייבת להיות חיובית')
        return
    
    # בדוק שיש מספיק
    row = get_resources(message.from_user.id)
    if resource not in ALL_RESOURCE_IDX:
        bot.reply_to(message, 'משאב לא מוכר')
        return
    idx = ALL_RESOURCE_IDX[resource]
    if idx >= len(row) or row[idx] < amount:
        bot.reply_to(message, f'אין מספיק {resource}')
        return
    
    # חצי מחיר - מרוויחים פחות ממכירה לשחקנים
    sell_rate = NPC_BUY_RATE / 2
    earnings = amount / sell_rate
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)-? WHERE user_id=?", (amount, message.from_user.id))
    c.execute("UPDATE resources SET gild=gild+? WHERE user_id=?", (earnings, message.from_user.id))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, f'✅ מכרת {amount} {resource} למערכת\n💰 קיבלת: {earnings:.2f} Gild\n⏰ שער: {int(sell_rate)} יחידות = 1 Gild')
