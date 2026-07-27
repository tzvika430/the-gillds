import random
from bot_instance import bot
from config import DB_PATH
import sqlite3

@bot.message_handler(commands=['spy'])
def spy_cmd(message):
    user_id = message.from_user.id
    parts = message.text.split()
    
    if len(parts) < 2:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT count FROM workers WHERE user_id=? AND worker_type='spy'", (user_id,))
        row = c.fetchone()
        spies = row[0] if row else 0
        conn.close()
        bot.reply_to(message, f"🕵️ **מודיעין**\n\nיש לך {spies} מרגלים.\nשימוש: /spy [שם שחקן]\nכל מרגל = 10% דיוק.")
        return
    
    target_name = parts[1]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT count FROM workers WHERE user_id=? AND worker_type='spy'", (user_id,))
    row = c.fetchone()
    spies = row[0] if row else 0
    
    if spies < 1:
        conn.close()
        bot.reply_to(message, "❌ אין לך מרגלים! 👷 עובדים ← 🕵️ מרגל")
        return
    
    c.execute("SELECT user_id, display_name FROM users WHERE display_name LIKE ? OR username LIKE ?", 
              (f"%{target_name}%", f"%{target_name}%"))
    results = c.fetchall()
    
    if not results:
        conn.close()
        bot.reply_to(message, f"❌ לא נמצא: {target_name}")
        return
    
    target_id, target_display = results[0]
    
    if target_id == user_id:
        conn.close()
        bot.reply_to(message, "❌ אי אפשר לרגל אחרי עצמך!")
        return
    
    # צרוך מרגל
    c.execute("UPDATE workers SET count=count-1 WHERE user_id=? AND worker_type='spy'", (user_id,))
    c.execute("DELETE FROM workers WHERE user_id=? AND worker_type='spy' AND count<=0", (user_id,))
    
    # אסוף מידע
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND worker_type IN ('soldier','commander','general')", (target_id,))
    army = c.fetchall()
    c.execute("SELECT water, coal, copper, gold, wheat, soil, wood, stones FROM resources WHERE user_id=?", (target_id,))
    res = c.fetchone()
    c.execute("SELECT building_type, count FROM buildings WHERE user_id=?", (target_id,))
    buildings = c.fetchall()
    
    conn.commit()
    conn.close()
    
    accuracy = min(100, spies * 10)
    name = target_display or str(target_id)
    msg = f"🕵️ **דוח מודיעין — {name}**\n🎯 דיוק: {accuracy}%\n\n"
    
    msg += "⚔️ **צבא:**\n"
    if army:
        for wt, cnt in army:
            emoji = {'soldier': '🪖', 'commander': '🎖️', 'general': '👑'}.get(wt, '')
            if accuracy >= 80:
                msg += f"{emoji} {wt}: {cnt}\n"
            elif accuracy >= 50:
                msg += f"{emoji} {wt}: ~{cnt//2*2}-{cnt+2}\n"
            else:
                msg += f"{emoji} {wt}: ???\n"
    else:
        msg += "אין\n"
    
    msg += "\n📦 **משאבים:**\n"
    if res:
        names = ['💧 מים', '⚫ פחם', '🟠 נחושת', '🥇 זהב', '🌾 חיטה', '🟤 אדמה', '🪵 עץ', '🪨 אבנים']
        shown = 0
        max_show = max(2, int(8 * accuracy / 100))
        for i, name in enumerate(names):
            if shown >= max_show: break
            if res[i] > 0:
                if accuracy >= 70:
                    msg += f"{name}: {res[i]:.0f}\n"
                elif accuracy >= 40:
                    msg += f"{name}: ~{res[i]//10*10}\n"
                else:
                    msg += f"{name}: ???\n"
                shown += 1
    
    msg += "\n🏗️ **מבנים:**\n"
    if buildings:
        for bt, cnt in buildings:
            emoji = {'straw_house': '🏠', 'brick_house': '🧱', 'sawmill': '🪚', 'barracks': '🏰', 'spy_house': '🕵️'}.get(bt, '')
            msg += f"{emoji} {bt}: {cnt}\n"
    
    msg += f"\n🕵️ מרגל נשלח. נותרו {spies-1}."
    bot.reply_to(message, msg)
