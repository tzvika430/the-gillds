from telebot import types
from bot_instance import bot
from config import DB_PATH, ALL_RESOURCE_IDX, UNIT_SCORE
import sqlite3
import random

@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    attacker_id = message.from_user.id
    
    # בדוק שלשחקן יש חיילים
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND worker_type IN ('soldier','commander','general','wardog','dragon')", (attacker_id,))
    my_units = c.fetchall()
    my_soldiers = sum(UNIT_SCORE.get(wt, 0) * cnt for wt, cnt in my_units)
    
    if my_soldiers == 0:
        bot.reply_to(message, "❌ אין לך חיילים! צריך לפחות soldier אחד כדי לתקוף.\n/build barracks ← /hire soldier")
        conn.close()
        return
    
    # בחר יריב רנדומלי (שיש לו עובדים, לא התוקף עצמו)
    c.execute("SELECT DISTINCT user_id FROM workers WHERE user_id != ?", (attacker_id,))
    targets = [r[0] for r in c.fetchall()]
    
    if not targets:
        bot.reply_to(message, "❌ אין שחקנים אחרים לתקוף כרגע.")
        conn.close()
        return
    
    defender_id = random.choice(targets)
    
    # בדוק חיילים של המגן
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND worker_type IN ('soldier','commander','general','wardog','dragon')", (defender_id,))
    def_units = c.fetchall()
    defender_soldiers = sum(UNIT_SCORE.get(wt, 0) * cnt for wt, cnt in def_units)
    
    # הכרעה
    if defender_soldiers == 0:
        winner = "attacker"
    elif my_soldiers == 0:
        winner = "defender"
    else:
        my_power = my_soldiers * (1 + random.random())
        def_power = defender_soldiers * (1 + random.random())
        winner = "attacker" if my_power >= def_power else "defender"
    
    if winner == "attacker":
        # קח 10% מכל משאב פיזי
        c.execute("SELECT water, coal, copper, gold, wheat, soil, wood, stones, gild FROM resources WHERE user_id=?", (defender_id,))
        res = c.fetchone()
        if not res:
            bot.reply_to(message, "❌ למגן אין משאבים.")
            conn.close()
            return
        
        total_stolen = 0
        stolen_parts = []
        resources_names = ['water', 'coal', 'copper', 'gold', 'wheat', 'soil', 'wood', 'stones']
        
        for i, name in enumerate(resources_names):
            amount = res[i]
            if amount > 0:
                stolen = amount * 0.1
                # הגנת straw_house - בדוק מינימום
                if name in ['wheat', 'soil', 'wood']:
                    needed_for_straw = {'wheat': 100, 'soil': 100, 'wood': 50}[name]
                    if amount - stolen < needed_for_straw:
                        stolen = max(0, amount - needed_for_straw)
                
                if stolen > 0:
                    c.execute(f"UPDATE resources SET {name}=COALESCE({name},0)-? WHERE user_id=?", (stolen, defender_id))
                    c.execute(f"UPDATE resources SET {name}=COALESCE({name},0)+? WHERE user_id=?", (stolen, attacker_id))
                    total_stolen += stolen
                    emoji = {'water':'💧','coal':'⚫','copper':'🟠','gold':'🥇','wheat':'🌾','soil':'🟤','wood':'🪵','stones':'🪨'}.get(name,'')
                    stolen_parts.append(f"{emoji} {name}: {stolen:.1f}")
        
        # +1 Gild למנצח
        c.execute("UPDATE resources SET gild=gild+1 WHERE user_id=?", (attacker_id,))
        
        conn.commit()
        conn.close()
        
        msg = f"⚔️ **ניצחת בקרב!**\n\n"
        if stolen_parts:
            msg += "שלל:\n" + "\n".join(stolen_parts) + "\n"
        msg += "\n💰 +1 Gild"
        bot.reply_to(message, msg)
        
        # הודעה למגן
        try:
            bot.send_message(defender_id, f"⚔️ **הותקפת והפסדת!**\nשחקן אחר ניצח אותך בקרב ולקח 10% מהמשאבים שלך.\n\nגייס חיילים כדי להתגונן: /build barracks ← /hire soldier")
        except:
            pass
    else:
        conn.close()
        bot.reply_to(message, f"❌ **הפסדת בקרב!**\n\nלמגן היו {defender_soldiers} חיילים מול {my_soldiers} שלך.\n\nגייס עוד חיילים ונסה שוב!")
