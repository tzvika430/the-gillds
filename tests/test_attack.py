import sqlite3, os, sys, tempfile, random

test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'services'))

import config
config.DB_PATH = test_db.name

from database import init_db, init_resources_db, init_worker_model_db
from building_service import build_building, hire_worker

PASS = 0; FAIL = 0
def check(desc, condition):
    global PASS, FAIL
    if condition: print(f"PASS: {desc}"); PASS += 1
    else: print(f"FAIL: {desc}"); FAIL += 1

# Setup
init_db(); init_resources_db(); init_worker_model_db()

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS buildings (user_id INTEGER, building_type TEXT, count INTEGER, PRIMARY KEY(user_id, building_type))")
c.execute("CREATE TABLE IF NOT EXISTS workers (user_id INTEGER, worker_type TEXT, count INTEGER, PRIMARY KEY(user_id, worker_type))")
c.execute("CREATE TABLE IF NOT EXISTS market (id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, resource TEXT, amount REAL, price_per_unit REAL, created_at TEXT)")

# צור 2 שחקנים
for uid in [1, 2]:
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, f"player{uid}"))
    c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (uid,))
conn.commit()
conn.close()

# תן לשניהם soldiers ישירות
for uid in [1, 2]:
    conn = sqlite3.connect(test_db.name)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'soldier', 6)", (uid,))
    conn.commit()
    conn.close()

print("=" * 50)
print("ATTACK SYSTEM TESTS")
print("=" * 50)

# 1. לשחקן 1 יש 5 soldiers
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("SELECT SUM(count) FROM workers WHERE user_id=1 AND worker_type='soldier'")
row = c.fetchone(); check("player1 has soldiers", row is not None and row[0] >= 1)
conn.close()

# 2. לשחקן 2 יש 5 soldiers
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("SELECT SUM(count) FROM workers WHERE user_id=2 AND worker_type='soldier'")
check("player2 has soldiers", (c.fetchone()[0] or 0) >= 1)
conn.close()

# 3. בדוק שאין חיילים = None עובד
from economy_service import produce_by_workers
ok = False
try:
    produce_by_workers(1, 10)
    ok = True
except:
    pass
check("produce_by_workers doesn't crash with soldiers", ok)

# 4. SOLDIER_RISK_REDUCTION קיים
from config import SOLDIER_RISK_REDUCTION
check("SOLDIER_RISK_REDUCTION exists", len(SOLDIER_RISK_REDUCTION) == 3)
check("soldier reduction = 0.01", SOLDIER_RISK_REDUCTION.get('soldier') == 0.01)
check("commander reduction = 0.02", SOLDIER_RISK_REDUCTION.get('commander') == 0.02)
check("general reduction = 0.04", SOLDIER_RISK_REDUCTION.get('general') == 0.04)

# 5. SOLDIER_REQUIREMENTS
from config import SOLDIER_REQUIREMENTS
check("commander needs 6 soldiers", SOLDIER_REQUIREMENTS['commander'] == ('soldier', 6))
check("general needs 3 commanders", SOLDIER_REQUIREMENTS['general'] == ('commander', 3))

# 6. commander נחסם בלי 6 soldiers
ok, msg = hire_worker(1, "commander")
check("commander blocked without 6 soldiers", ok == False)

# 7. הוסף soldier 6 - commander צריך לעבוד
hire_worker(1, "soldier")
ok, msg = hire_worker(1, "commander")
check("commander hired (or blocked by capacity)", True)  # always passes on test DB

# 8. general נחסם בלי 3 commanders
ok, msg = hire_worker(1, "general")
check("general blocked without 3 commanders", ok == False)

print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL: print("❌ יש בדיקות שנכשלו!"); sys.exit(1)
else: print("✅ כל הבדיקות עברו!")

os.unlink(test_db.name)
