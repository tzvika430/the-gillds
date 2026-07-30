import sqlite3
from config import DB_PATH, BUILDING_COST, HIRE_COST, WORKER_BUILDING, BUILDING_CAPACITY, DEFAULT_BUILDING_CAPACITY, SOLDIER_REQUIREMENTS

def build_building(user_id, building_type):
    if building_type not in BUILDING_COST:
        return False, 'מבנה לא מוכר'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT water, coal, copper, gold, wheat, soil, wood, stones FROM resources WHERE user_id=?', (user_id,))
    water, coal, copper, gold, wheat, soil, wood, stones = c.fetchone()
    have = {'water': water, 'coal': coal, 'copper': copper, 'gold': gold, 'wheat': wheat, 'soil': soil, 'wood': wood, 'stones': stones}
    cost = BUILDING_COST[building_type]
    for res, amt in cost.items():
        if have[res] < amt:
            conn.close()
            return False, f'אין מספיק {res}, צריך {amt}, יש {have[res]:.2f}'
    for res, amt in cost.items():
        c.execute(f'UPDATE resources SET {res}={res}-? WHERE user_id=?', (amt, user_id))
    c.execute("""INSERT INTO buildings (user_id, building_type, count) VALUES (?, ?, 1)
                ON CONFLICT(user_id, building_type) DO UPDATE SET count = count + 1""",
              (user_id, building_type))
    conn.commit()
    conn.close()
    return True, 'OK'

def hire_worker(user_id, worker_type):
    if worker_type not in HIRE_COST:
        return False, 'סוג עובד לא קיים'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cost = HIRE_COST[worker_type]
    c.execute('SELECT gild FROM resources WHERE user_id=?', (user_id,))
    row = c.fetchone()
    gild = row[0] if row else 0
    if gild < cost:
        conn.close()
        return False, f'אין מספיק Gild, צריך {cost}, יש {gild}'
    # בדיקת היררכיית חיילים
    if worker_type in SOLDIER_REQUIREMENTS and SOLDIER_REQUIREMENTS.get(worker_type):
        req_type, req_count = SOLDIER_REQUIREMENTS[worker_type]
        c.execute("SELECT COALESCE(SUM(count),0) FROM workers WHERE user_id=? AND worker_type=?", (user_id, req_type))
        current = c.fetchone()[0]
        if current < req_count:
            conn.close()
            return False, f'צריך {req_count} {req_type} כדי לגייס {worker_type} (יש לך {current})'
    
    if worker_type in WORKER_BUILDING:
        building_type = WORKER_BUILDING[worker_type]
        c.execute('SELECT count FROM buildings WHERE user_id=? AND building_type=?',
                  (user_id, building_type))
        b = c.fetchone()
        building_count = b[0] if b else 0
        if building_count < 1:
            conn.close()
            return False, f"צריך {building_type} כדי לגייס {worker_type}"
        capacity = building_count * BUILDING_CAPACITY.get(building_type, DEFAULT_BUILDING_CAPACITY)
        same_building_workers = [w for w, bt in WORKER_BUILDING.items() if bt == building_type]
        placeholders = ','.join('?' * len(same_building_workers))
        q2 = 'SELECT COALESCE(SUM(count),0) FROM workers WHERE user_id=? AND worker_type IN (' + placeholders + ')'
        c.execute(q2, tuple([user_id] + same_building_workers))
        current_workers = c.fetchone()[0]
        if current_workers >= capacity:
            conn.close()
            msg = f'אין מקום ב-{building_type} ({current_workers}/{capacity}), בנה עוד מבנים'
            return False, msg
    c.execute('UPDATE resources SET gild=gild-? WHERE user_id=?', (cost, user_id))
    c.execute('''INSERT INTO workers (user_id, worker_type, count) VALUES (?, ?, 1)
                ON CONFLICT(user_id, worker_type) DO UPDATE SET count = count + 1''',
              (user_id, worker_type))
    conn.commit()
    conn.close()
    return True, 'OK'
