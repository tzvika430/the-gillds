import sqlite3
from datetime import datetime, timedelta
from config import *

def get_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, username, last_reset) VALUES (?, ?, ?)",
                 (user_id, username, datetime.now().date()))
        conn.commit()
        user = (user_id, username, 0, 0, 0, None, 1.0, str(datetime.now().date()), 0)
        get_or_create_worker_state(user_id)
    if user[7] != datetime.now().date():
        c.execute("UPDATE users SET today_seconds=0, last_reset=? WHERE user_id=?",
                 (datetime.now().date(), user_id))
        conn.commit()
    conn.close()
    return user


def update_time(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    user = get_user(user_id, username)
    if user[5] and user[8]:
        last = datetime.fromisoformat(user[5])
        seconds = (datetime.now() - last).total_seconds()
        earnings = seconds * BASE_RATE * user[6]
        c.execute("""UPDATE users SET
                    total_seconds = total_seconds + ?,
                    today_seconds = today_seconds + ?,
                    balance = balance + ?,
                    last_active = ?
                    WHERE user_id = ?""",
                 (int(seconds), int(seconds), earnings, datetime.now().isoformat(), user_id))
        conn.commit()
    conn.close()


def get_resources(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM resources WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO resources (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = (user_id, 0, 0, 0, 0, 50, 0, 0, 0, 0)
    conn.close()
    return row


def get_or_create_worker_state(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT count FROM buildings WHERE user_id=? AND building_type='straw_house'", (user_id,))
    exists = c.fetchone()
    if not exists:
        c.execute("INSERT INTO buildings VALUES (?, 'straw_house', 1)", (user_id,))
        c.execute("INSERT INTO workers VALUES (?, 'farmer', 1)", (user_id,))
        c.execute("INSERT INTO workers VALUES (?, 'lumberjack', 1)", (user_id,))
        c.execute("INSERT OR IGNORE INTO resources (user_id, gild, soil, stones, wood) VALUES (?, 10, 200, 200, 200)", (user_id,))
        conn.commit()
    conn.close()




def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    total_seconds INTEGER DEFAULT 0,
                    today_seconds INTEGER DEFAULT 0,
                    balance REAL DEFAULT 0,
                    last_active TEXT,
                    multiplier REAL DEFAULT 1.0,
                    last_reset DATE,
                    session_active INTEGER DEFAULT 0)''')
    conn.commit()
    try:
        c.execute("ALTER TABLE users ADD COLUMN session_active INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def init_resources_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS resources (
                    user_id INTEGER PRIMARY KEY,
                    water REAL DEFAULT 0,
                    coal REAL DEFAULT 0,
                    copper REAL DEFAULT 0,
                    gold REAL DEFAULT 0,
                    gild REAL DEFAULT 50)""")
    c.execute("""CREATE TABLE IF NOT EXISTS market (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER,
                    resource TEXT,
                    amount REAL,
                    price_per_unit REAL,
                    created_at TEXT)""")
    conn.commit()
    conn.close()



def init_worker_model_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for col in ['wheat', 'soil', 'wood', 'stones']:
        try:
            c.execute(f"ALTER TABLE resources ADD COLUMN {col} REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    c.execute("""CREATE TABLE IF NOT EXISTS buildings (
                    user_id INTEGER,
                    building_type TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, building_type))""")
    c.execute("""CREATE TABLE IF NOT EXISTS workers (
                    user_id INTEGER,
                    worker_type TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, worker_type))""")
    conn.commit()
    conn.close()


def reset_active_sessions_on_startup():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_active=? WHERE session_active=1",
              (datetime.now().isoformat(),))
    conn.commit()
    conn.close()



def init_predator_state():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS predator_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_event_at TEXT)""")
    c.execute("INSERT OR IGNORE INTO predator_state (id, last_event_at) VALUES (1, NULL)")
    conn.commit()
    conn.close()


def get_total_player_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    n = c.fetchone()[0]
    conn.close()
    return n


def get_last_predator_event():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT last_event_at FROM predator_state WHERE id=1")
    row = c.fetchone()
    conn.close()
    if not row or not row[0]:
        return None
    return datetime.fromisoformat(row[0])


def set_last_predator_event(dt):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE predator_state SET last_event_at=? WHERE id=1", (dt.isoformat(),))
    conn.commit()
    conn.close()


def get_eligible_predator_targets(needed):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT user_id FROM workers WHERE count > 0")
    user_ids = [r[0] for r in c.fetchall()]
    eligible = []
    # חישוב הפחתת סיכון מחיילים
    soldier_reduction = 0
    for uid in user_ids:
        c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND worker_type IN ('soldier','commander','general')", (uid,))
        for wt, cnt in c.fetchall():
            soldier_reduction += SOLDIER_RISK_REDUCTION.get(wt, 0) * cnt
    for uid in user_ids:
        c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND count>0", (uid,))
        rows = c.fetchall()
        total = sum(cnt for wt, cnt in rows)
        farmer_count = sum(cnt for wt, cnt in rows if wt == PREDATOR_PROTECTED_TYPE)
        reserved = PREDATOR_PROTECTED_MIN if farmer_count >= PREDATOR_PROTECTED_MIN else 0
        eatable = total - reserved
        if eatable >= needed:
            eligible.append(uid)
    conn.close()
    return eligible


def eat_random_workers(user_id, needed):
    import random
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND count>0", (user_id,))
    rows = c.fetchall()
    pool = []
    for wt, cnt in rows:
        avail = cnt
        if wt == PREDATOR_PROTECTED_TYPE:
            avail = max(0, cnt - PREDATOR_PROTECTED_MIN)
        pool += [wt] * avail
    random.shuffle(pool)
    chosen = pool[:needed]
    tally = {}
    for wt in chosen:
        tally[wt] = tally.get(wt, 0) + 1
    for wt, n in tally.items():
        c.execute("UPDATE workers SET count=count-? WHERE user_id=? AND worker_type=?", (n, user_id, wt))
    conn.commit()
    conn.close()
    return chosen


def check_and_trigger_predator_event():
    import random
    now = datetime.now()
    last = get_last_predator_event()
    player_count = get_total_player_count()
    interval = PREDATOR_DAILY_SECONDS if player_count >= PREDATOR_DAILY_THRESHOLD_PLAYERS else PREDATOR_WEEKLY_SECONDS
    if last is not None and (now - last).total_seconds() < interval:
        return None
    predator = random.choice(["tiger", "lion"])
    needed = TIGER_EAT_COUNT if predator == "tiger" else LION_EAT_COUNT
    targets = get_eligible_predator_targets(needed)
    set_last_predator_event(now)
    if not targets:
        return None
    # בדיקת הפחתת סיכון מחיילים
    conn2 = sqlite3.connect(DB_PATH)
    c2 = conn2.cursor()
    for uid in targets[:]:
        c2.execute("SELECT worker_type, count FROM workers WHERE user_id=? AND worker_type IN ('soldier','commander','general')", (uid,))
        reduction = sum(SOLDIER_RISK_REDUCTION.get(wt, 0) * cnt for wt, cnt in c2.fetchall())
        if random.random() < reduction:
            targets.remove(uid)
    conn2.close()
    if not targets:
        return None
    user_id = random.choice(targets)
    eaten = eat_random_workers(user_id, needed)
    return (user_id, predator, eaten)


def buy_from_system(user_id, resource, amount):
    if resource not in ALL_RESOURCE_IDX:
        return False, 'משאב לא מוכר'
    cost = amount / NPC_BUY_RATE
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT gild FROM resources WHERE user_id=?', (user_id,))
    row = c.fetchone()
    gild = row[0] if row else 0
    if gild < cost:
        conn.close()
        return False, f'אין מספיק Gild, צריך {cost:.2f}, יש {gild}'
    c.execute(f"UPDATE resources SET gild=gild-?, {resource}=COALESCE({resource},0)+? WHERE user_id=?", (cost, amount, user_id))
    conn.commit()
    conn.close()
    return True, 'OK'


def sell_resource(user_id, resource, amount, price):
    if resource not in ALL_RESOURCE_IDX:
        return False, 'משאב לא מוכר'
    row = get_resources(user_id)
    idx = ALL_RESOURCE_IDX[resource]
    if row[idx] < amount:
        return False, f'אין מספיק {resource}'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)-? WHERE user_id=?", (amount, user_id))
    c.execute("INSERT INTO market (seller_id, resource, amount, price_per_unit, created_at) VALUES (?,?,?,?,?)", (user_id, resource, amount, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True, 'OK'


def get_market_listings(limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, seller_id, resource, amount, price_per_unit FROM market ORDER BY resource ASC, price_per_unit ASC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def buy_from_market(buyer_id, listing_id, amount_requested):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT seller_id, resource, amount, price_per_unit FROM market WHERE id=?", (listing_id,))
    listing = c.fetchone()
    if not listing:
        conn.close()
        return False, 'הצעה לא קיימת'
    seller_id, resource, avail_amount, price = listing
    if seller_id == buyer_id:
        conn.close()
        return False, 'אי אפשר לקנות מעצמך'
    if amount_requested > avail_amount + 1e-9:
        conn.close()
        return False, f'יש רק {avail_amount:.2f} בהצעה הזו'
    total_cost = amount_requested * price
    buyer_row = get_resources(buyer_id)
    if buyer_row[5] < total_cost:
        conn.close()
        return False, f'אין מספיק Gild, צריך {total_cost:.2f}'
    c.execute("UPDATE resources SET gild=gild-? WHERE user_id=?", (total_cost, buyer_id))
    c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)+? WHERE user_id=?", (amount_requested, buyer_id))
    c.execute("UPDATE resources SET gild=gild+? WHERE user_id=?", (total_cost, seller_id))
    if abs(amount_requested - avail_amount) < 1e-9:
        c.execute("DELETE FROM market WHERE id=?", (listing_id,))
    else:
        c.execute("UPDATE market SET amount=amount-? WHERE id=?", (amount_requested, listing_id))
    conn.commit()
    conn.close()
    return True, {"resource": resource, "cost": total_cost}

def get_active_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE session_active=1")
    rows = c.fetchall()
    conn.close()
    return rows

def check_subscription(user_id):
    """בודק אם שחקן בתוקף. מחזיר (is_active, days_left, msg)"""
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT created_at, is_paid FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return True, 999, ""
    
    created = datetime.fromisoformat(row[0])
    is_paid = row[1]
    days_since = (datetime.now() - created).days
    days_left = 7 - days_since
    
    if is_paid:
        return True, 999, ""
    if days_left > 1:
        return True, days_left, ""
    elif days_left == 1:
        return True, 1, "⚠️ מחר מסתיימת תקופת הניסיון!"
    elif days_left == 0:
        return True, 0, "⚠️ היום האחרון בחינם!"
    else:
        return False, days_left, "🔒 תקופת הניסיון הסתיימה. /pay להמשך."
