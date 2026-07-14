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


def produce_by_workers(user_id, seconds):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=?", (user_id,))
    workers = c.fetchall()
    for worker_type, count in workers:
        if count <= 0 or worker_type not in WORKER_TO_RESOURCE:
            continue
        resource = WORKER_TO_RESOURCE[worker_type]
        amount = count * seconds * WORKER_RATE
        c.execute(f"UPDATE resources SET {resource}={resource}+? WHERE user_id=?", (amount, user_id))
        if worker_type == 'farmer':
            for byres, ratio in FARMER_BYPRODUCTS.items():
                c.execute(f"UPDATE resources SET {byres}={byres}+? WHERE user_id=?", (amount*ratio, user_id))
    conn.commit()
    conn.close()



def build_building(user_id, building_type):
    if building_type not in BUILDING_COST:
        return False, 'מבנה לא מוכר'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT wheat, soil, wood, stones FROM resources WHERE user_id=?', (user_id,))
    wheat, soil, wood, stones = c.fetchone()
    have = {'wheat': wheat, 'soil': soil, 'wood': wood, 'stones': stones}
    cost = BUILDING_COST[building_type]
    for res, amt in cost.items():
        if have[res] < amt:
            conn.close()
            return False, f'אין מספיק {res}, צריך {amt}, יש {have[res]:.2f}'
    for res, amt in cost.items():
        c.execute(f'UPDATE resources SET {res}={res}-? WHERE user_id=?', (amt, user_id))
    c.execute("""INSERT INTO buildings (user_id, building_type, count) VALUES (?, ?, 1)
                 ON CONFLICT(user_id, building_type) DO UPDATE SET count = count + 1""", (user_id, building_type))
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
    if worker_type in WORKER_BUILDING:
        building_type = WORKER_BUILDING[worker_type]
        c.execute('SELECT count FROM buildings WHERE user_id=? AND building_type=?', (user_id, building_type))
        b = c.fetchone()
        building_count = b[0] if b else 0
        capacity = building_count * BUILDING_CAPACITY.get(building_type, 0)
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
                 ON CONFLICT(user_id, worker_type) DO UPDATE SET count = count + 1''', (user_id, worker_type))
    conn.commit()
    conn.close()
    return True, 'OK'


def get_active_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE session_active=1")
    users = c.fetchall()
    conn.close()
    return users


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

