import sqlite3, os, sys, tempfile

test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'services'))

import config
config.DB_PATH = test_db.name

from database import init_db, init_resources_db, get_resources

PASS = 0; FAIL = 0
def check(desc, condition):
    global PASS, FAIL
    if condition: print(f"PASS: {desc}"); PASS += 1
    else: print(f"FAIL: {desc}"); FAIL += 1

init_db(); init_resources_db()

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS workers (user_id INTEGER, worker_type TEXT, count INTEGER, PRIMARY KEY(user_id, worker_type))")
c.execute("CREATE TABLE IF NOT EXISTS buildings (user_id INTEGER, building_type TEXT, count INTEGER, PRIMARY KEY(user_id, building_type))")
conn.commit()
conn.close()

print("=" * 50)
print("REGISTER TESTS")
print("=" * 50)

# 1. משתמש חדש
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (1, "test"))
# הוסף עמודות
for col in ['display_name', 'kingdom', 'created_at', 'is_paid']:
    try: c.execute(f'ALTER TABLE users ADD COLUMN {col} TEXT')
    except: pass
c.execute("UPDATE users SET display_name=?, kingdom=? WHERE user_id=?", ("לוחם", "הממלכה", 1))
c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (1,))
c.execute("UPDATE resources SET gild=10 WHERE user_id=1")
c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'farmer', 1)", (1,))
c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'lumberjack', 1)", (1,))
c.execute("INSERT OR IGNORE INTO buildings (user_id, building_type, count) VALUES (?, 'straw_house', 1)", (1,))
conn.commit()
conn.close()

row = get_resources(1)
check("new user has gild=10", row[5] == 10)

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("SELECT display_name, kingdom FROM users WHERE user_id=1")
info = c.fetchone()
check("display_name saved", info[0] == "לוחם")
check("kingdom saved", info[1] == "הממלכה")
c.execute("SELECT SUM(count) FROM workers WHERE user_id=1")
total = c.fetchone()[0]
check("has 2 starting workers", total == 2)
c.execute("SELECT SUM(count) FROM buildings WHERE user_id=1")
total = c.fetchone()[0]
check("has 1 starting building", total == 1)
conn.close()

# 2. מחיקת פרופיל
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("DELETE FROM resources WHERE user_id=1")
c.execute("DELETE FROM workers WHERE user_id=1")
c.execute("DELETE FROM buildings WHERE user_id=1")
c.execute("UPDATE users SET display_name=NULL, kingdom=NULL WHERE user_id=1")
conn.commit()
c.execute("SELECT display_name FROM users WHERE user_id=1")
check("display_name cleared", c.fetchone()[0] is None)
conn.close()

# 3. בדיקת check_subscription
from database import check_subscription
from datetime import datetime

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("UPDATE users SET created_at=?, is_paid=0 WHERE user_id=1", (datetime.now().isoformat(),))
conn.commit()
conn.close()

active, days, msg = check_subscription(1)
check("new user is active", active == True)
check("new user has free trial days", days > 0)

print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL: print("❌ יש בדיקות שנכשלו!"); sys.exit(1)
else: print("✅ כל הבדיקות עברו!")

os.unlink(test_db.name)
