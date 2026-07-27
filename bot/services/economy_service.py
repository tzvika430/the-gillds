import sqlite3
from config import DB_PATH, WORKER_TO_RESOURCE, WORKER_RATE, FARMER_BYPRODUCTS

def produce_by_workers(user_id, seconds):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=?", (user_id,))
    workers = c.fetchall()
    for worker_type, count in workers:
        if count <= 0 or worker_type not in WORKER_TO_RESOURCE:
            continue
        resource = WORKER_TO_RESOURCE.get(worker_type)
        if resource is None:
            continue  # soldier/commander/general לא מייצרים
        amount = count * seconds * WORKER_RATE
        c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)+? WHERE user_id=?", (amount, user_id))
        if worker_type == 'farmer':
            for byres, ratio in FARMER_BYPRODUCTS.items():
                c.execute(f"UPDATE resources SET {byres}=COALESCE({byres},0)+? WHERE user_id=?", (amount*ratio, user_id))
    conn.commit()
    conn.close()

def consume_daily_resources():
    import sqlite3
    from config import DB_PATH, DAILY_CONSUMPTION
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM workers GROUP BY user_id")
    users = [r[0] for r in c.fetchall()]
    for user_id in users:
        c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND count>0", (user_id,))
        workers = c.fetchall()
        total_water = 0
        total_gold = 0
        for wt, cnt in workers:
            if 'water' in DAILY_CONSUMPTION and wt in DAILY_CONSUMPTION['water']:
                total_water += DAILY_CONSUMPTION['water'][wt] * cnt
            if 'gold' in DAILY_CONSUMPTION and wt in DAILY_CONSUMPTION['gold']:
                total_gold += DAILY_CONSUMPTION['gold'][wt] * cnt
        if total_water > 0:
            c.execute("UPDATE resources SET water=MAX(0, COALESCE(water,0)-?) WHERE user_id=?", (total_water, user_id))
        if total_gold > 0:
            c.execute("UPDATE resources SET gold=MAX(0, COALESCE(gold,0)-?) WHERE user_id=?", (total_gold, user_id))
    conn.commit()
    conn.close()

def daily_bonus(user_id):
    """בונוס יומי — 1 Gild"""
    import sqlite3
    from config import DB_PATH
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # בדוק מתי היה בונוס אחרון
    c.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    now = datetime.now()
    if row and row[0]:
        try:
            last = datetime.fromisoformat(row[0])
            if (now - last).days < 1:
                conn.close()
                return False, "כבר קיבלת בונוס היום. חזור מחר!"
        except:
            pass
    # תן בונוס
    c.execute("UPDATE resources SET gild=gild+1 WHERE user_id=?", (user_id,))
    c.execute("UPDATE users SET last_bonus=? WHERE user_id=?", (now.isoformat(), user_id))
    conn.commit()
    conn.close()
    return True, "🎁 קיבלת 1 Gild בונוס יומי! חזור מחר לעוד."


def auto_daily_bonus(user_id):
    """בדיקת בונוס יומי אוטומטית — מחזירה הודעה אם הגיע בונוס, אחרת None"""
    import sqlite3
    from config import DB_PATH
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    now = datetime.now()
    if row and row[0]:
        try:
            last = datetime.fromisoformat(row[0])
            if (now - last).days < 1:
                conn.close()
                return None  # כבר קיבל היום
        except:
            pass
    # תן בונוס
    c.execute("UPDATE resources SET gild=gild+1 WHERE user_id=?", (user_id,))
    c.execute("UPDATE users SET last_bonus=? WHERE user_id=?", (now.isoformat(), user_id))
    conn.commit()
    conn.close()
    return "🎁 קיבלת 1 Gild בונוס יומי! חזור מחר לעוד."
