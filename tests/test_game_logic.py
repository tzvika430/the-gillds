import sqlite3
import re
import os
import sys

BOT_SRC = "/data/data/com.termux/files/home/SLH-DEV/bot/src/bot.py"
TEST_DB = "/data/data/com.termux/files/home/SLH-DEV/tests/test_economy.db"

if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

src = open(BOT_SRC, encoding="utf-8").read()

def extract_const(name):
    pat_multi = r"^" + name + r" = \{\s*\n.*?^\}"
    m = re.search(pat_multi, src, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(0)
    m = re.search(r"^" + name + r" = .*$", src, re.MULTILINE)
    return m.group(0)

def extract_func(name):
    pat = r"^def " + name + r"\(.*?(?=^def |\Z)"
    m = re.search(pat, src, re.MULTILINE | re.DOTALL)
    return m.group(0)

ns = {"sqlite3": sqlite3}
exec("DB_PATH = " + repr(TEST_DB), ns)
CONSTS = ["HIRE_COST", "WORKER_BUILDING", "BUILDING_CAPACITY",
          "BUILDING_COST", "WORKER_TO_RESOURCE", "FARMER_BYPRODUCTS",
          "WORKER_RATE"]
for name in CONSTS:
    exec(extract_const(name), ns)

FUNCS = ["get_or_create_worker_state", "hire_worker",
         "build_building", "get_resources", "produce_by_workers"]
for name in FUNCS:
    exec(extract_func(name), ns)

conn = sqlite3.connect(TEST_DB)
c = conn.cursor()
c.execute("""CREATE TABLE resources (
    user_id INTEGER PRIMARY KEY,
    water REAL DEFAULT 0, coal REAL DEFAULT 0,
    copper REAL DEFAULT 0, gold REAL DEFAULT 0,
    gild REAL DEFAULT 50, wheat REAL DEFAULT 0,
    soil REAL DEFAULT 0, wood REAL DEFAULT 0,
    stones REAL DEFAULT 0)""")
c.execute("""CREATE TABLE workers (
    user_id INTEGER, worker_type TEXT, count INTEGER DEFAULT 0,
    PRIMARY KEY(user_id, worker_type))""")
c.execute("""CREATE TABLE buildings (
    user_id INTEGER, building_type TEXT, count INTEGER DEFAULT 0,
    PRIMARY KEY(user_id, building_type))""")
conn.commit()
conn.close()

passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        print("PASS:", name)
        passed += 1
    else:
        print("FAIL:", name)
        failed += 1

get_or_create_worker_state = ns["get_or_create_worker_state"]
hire_worker = ns["hire_worker"]
build_building = ns["build_building"]
get_resources = ns["get_resources"]

USER = 999999

get_or_create_worker_state(USER)
row = get_resources(USER)
check("new user gild=10", row[5] == 10)
check("new user soil=200", row[7] == 200)
check("new user stones=200", row[9] == 200)
check("new user wood=200", row[8] == 200)

ok, msg = build_building(USER, "brick_house")
check("build brick_house succeeds", ok == True)

for i in range(4):
    ok, msg = hire_worker(USER, "water_drawer")
    check("hire water_drawer #" + str(i+1), ok == True)

ok, msg = hire_worker(USER, "water_drawer")
check("5th water_drawer blocked", ok == False)

ok, msg = hire_worker(USER, "coal_miner")
check("coal_miner blocked, brick_house full", ok == False)

conn = sqlite3.connect(TEST_DB)
cc = conn.cursor()
cc.execute("UPDATE resources SET gild=gild+100 WHERE user_id=?", (USER,))
conn.commit()
conn.close()

all_lj_ok = True
for i in range(30):
    ok, msg = hire_worker(USER, "lumberjack")
    if not ok:
        all_lj_ok = False
check("lumberjack unlimited, 30 hires", all_lj_ok == True)

USER2 = 888888
get_or_create_worker_state(USER2)
conn = sqlite3.connect(TEST_DB)
c = conn.cursor()
c.execute("UPDATE resources SET gild=0 WHERE user_id=?", (USER2,))
conn.commit()
conn.close()
ok, msg = hire_worker(USER2, "farmer")
check("insufficient gild blocks hire", ok == False)

print()
print("TOTAL:", passed, "passed,", failed, "failed")
sys.exit(1 if failed else 0)
