import sqlite3, os, sys, tempfile

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

init_db(); init_resources_db(); init_worker_model_db()

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS buildings (user_id INTEGER, building_type TEXT, count INTEGER, PRIMARY KEY(user_id, building_type))")
c.execute("CREATE TABLE IF NOT EXISTS workers (user_id INTEGER, worker_type TEXT, count INTEGER, PRIMARY KEY(user_id, worker_type))")
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (1, "test"))
c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (1,))
c.execute("UPDATE resources SET gild=50, wheat=500, soil=500, wood=500, stones=500 WHERE user_id=1")
conn.commit()
conn.close()

print("=" * 50)
print("BUILDING TESTS")
print("=" * 50)

ok, msg = build_building(1, "straw_house")
check("build straw_house", ok == True)
ok, msg = build_building(1, "brick_house")
check("build brick_house", ok == True)
ok, msg = build_building(1, "sawmill")
check("build sawmill", ok == True)
ok, msg = build_building(1, "barracks")
check("build barracks", ok == True)
ok, msg = build_building(1, "castle")
check("unknown building fails", ok == False)
ok, msg = hire_worker(1, "soldier")
check("hire soldier", ok == True)
for _ in range(5):
    hire_worker(1, "soldier")
ok, msg = hire_worker(1, "commander")
check("hire commander with 6 soldiers", ok == True)

print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL: print("❌ יש בדיקות שנכשלו!"); sys.exit(1)
else: print("✅ כל הבדיקות עברו!")

os.unlink(test_db.name)
