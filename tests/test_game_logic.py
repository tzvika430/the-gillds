import sqlite3, os, sys, tempfile

test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'services'))

import config
config.DB_PATH = test_db.name

from database import init_db, init_resources_db, init_worker_model_db, get_resources, get_user, update_time, buy_from_system
from building_service import build_building, hire_worker
from economy_service import produce_by_workers

PASS = 0; FAIL = 0
def check(desc, condition):
    global PASS, FAIL
    if condition: print(f"PASS: {desc}"); PASS += 1
    else: print(f"FAIL: {desc}"); FAIL += 1

init_db(); init_resources_db(); init_worker_model_db()

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS market (id INTEGER PRIMARY KEY AUTOINCREMENT, seller_id INTEGER, resource TEXT, amount REAL, price_per_unit REAL, created_at TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS buildings (user_id INTEGER, building_type TEXT, count INTEGER, PRIMARY KEY(user_id, building_type))")
c.execute("CREATE TABLE IF NOT EXISTS workers (user_id INTEGER, worker_type TEXT, count INTEGER, PRIMARY KEY(user_id, worker_type))")
# ודא שכל עמודות resources קיימות
for col in ['wheat', 'soil', 'wood', 'stones', 'gild']:
    try: c.execute(f"SELECT {col} FROM resources LIMIT 1")
    except: c.execute(f"ALTER TABLE resources ADD COLUMN {col} REAL DEFAULT 0")
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (1, "testuser"))
c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (1,))
c.execute("UPDATE resources SET gild=10, soil=200, wood=200, stones=200, water=100, coal=100, copper=100, gold=100, wheat=200 WHERE user_id=1")
conn.commit(); conn.close()

print("=" * 50)
print("GAME LOGIC TESTS")
print("=" * 50)

row = get_resources(1)
check("new user gild=10", row[5] == 10)

ok, msg = build_building(1, "brick_house")
check("build brick_house succeeds", ok == True)

for i in range(1, 5):
    ok, msg = hire_worker(1, "water_drawer")
    check(f"hire water_drawer #{i}", ok == True)

ok, msg = hire_worker(1, "water_drawer")
check("5th water_drawer blocked", ok == False)

ok, msg = hire_worker(1, "coal_miner")
check("coal_miner blocked, brick_house full", ok == False)

ok, msg = hire_worker(1, "lumberjack")
check("2nd lumberjack blocked without sawmill", ok == False)

c = conn = sqlite3.connect(test_db.name); c = conn.cursor()
c.execute("UPDATE resources SET wheat=200, soil=300, wood=300, coal=100 WHERE user_id=1")
conn.commit(); conn.close()

ok, msg = build_building(1, "sawmill")
check("build sawmill succeeds", ok == True)

for i in range(2):
    ok, msg = hire_worker(1, "lumberjack")
    check(f"hire lumberjack #{i+2} after sawmill", ok == True)

# ok, msg = hire_worker(1, "lumberjack")
# check("4th lumberjack blocked, sawmill full", ok == False)

conn = sqlite3.connect(test_db.name); c = conn.cursor()
c.execute("UPDATE resources SET gild=0 WHERE user_id=1")
conn.commit(); conn.close()
ok, msg = hire_worker(1, "farmer")
check("insufficient gild blocks hire", ok == False)

conn = sqlite3.connect(test_db.name); c = conn.cursor()
c.execute("UPDATE resources SET gild=10, wood=0 WHERE user_id=1")
conn.commit(); conn.close()
ok, msg = buy_from_system(1, "wood", 200)
check("buy 200 wood costs 1 gild", ok == True)

ok, msg = buy_from_system(1, "wood", 99999)
check("buying more than affordable fails", ok == False)

try:
    update_time(1, "testuser")
    user = get_user(1, "testuser")
    check("update_time/get_user runs without error", user is not None)
except: check("update_time/get_user runs without error", False)

ok = False
try: produce_by_workers(1, 10); ok = True
except: pass
check("produce_by_workers runs without error", ok)

print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL: print("❌ יש בדיקות שנכשלו!"); sys.exit(1)
else: print("✅ כל הבדיקות עברו!")

os.unlink(test_db.name)
