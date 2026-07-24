import sqlite3, os, sys, tempfile

test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'services'))

import config
config.DB_PATH = test_db.name

from database import init_db, init_resources_db, init_worker_model_db, get_resources
from economy_service import produce_by_workers

PASS = 0; FAIL = 0
def check(desc, condition):
    global PASS, FAIL
    if condition: print(f"PASS: {desc}"); PASS += 1
    else: print(f"FAIL: {desc}"); FAIL += 1

init_db(); init_resources_db(); init_worker_model_db()

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS workers (user_id INTEGER, worker_type TEXT, count INTEGER, PRIMARY KEY(user_id, worker_type))")
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (1, "test"))
c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (1,))
c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'farmer', 1)", (1,))
c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'lumberjack', 1)", (1,))
c.execute("UPDATE resources SET gild=10 WHERE user_id=1")
conn.commit()
conn.close()

print("=" * 50)
print("ECONOMY TESTS")
print("=" * 50)

row_before = get_resources(1)
wheat_before = row_before[6] if len(row_before) > 6 else 0
soil_before = row_before[7] if len(row_before) > 7 else 0

produce_by_workers(1, 10)

row_after = get_resources(1)
wheat_after = row_after[6] if len(row_after) > 6 else 0
soil_after = row_after[7] if len(row_after) > 7 else 0

check("wheat increased", wheat_after > wheat_before)
check("soil increased (byproduct)", soil_after > soil_before)

from config import WORKER_RATE, FARMER_BYPRODUCTS
check("WORKER_RATE = 1/10", WORKER_RATE == 1/10)
check("soil byproduct = 0.5", FARMER_BYPRODUCTS['soil'] == 0.5)
check("stones byproduct = 0.5", FARMER_BYPRODUCTS['stones'] == 0.5)

conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("INSERT OR IGNORE INTO workers (user_id, worker_type, count) VALUES (?, 'soldier', 5)", (1,))
conn.commit()
conn.close()

gild_before = get_resources(1)[5]
produce_by_workers(1, 10)
gild_after = get_resources(1)[5]
check("soldiers don't affect gild", gild_after == gild_before)

print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL: print("❌ יש בדיקות שנכשלו!"); sys.exit(1)
else: print("✅ כל הבדיקות עברו!")

os.unlink(test_db.name)
