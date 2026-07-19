import sqlite3
import re
import os
import sys

BOT_SRC = "/data/data/com.termux/files/home/SLH-DEV/bot/src/bot.py"
TEST_DB = "/data/data/com.termux/files/home/SLH-DEV/tests/test_economy.db"

if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

CONFIG_SRC = "/data/data/com.termux/files/home/SLH-DEV/bot/services/config.py"
src = open(BOT_SRC, encoding="utf-8").read()
DB_SRC = "/data/data/com.termux/files/home/SLH-DEV/bot/services/database.py"
src = src + "\n" + open(CONFIG_SRC, encoding="utf-8").read()
src = src + "\n" + open(DB_SRC, encoding="utf-8").read()

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

from datetime import datetime, timedelta
ns = {"sqlite3": sqlite3, "datetime": datetime, "timedelta": timedelta}
exec("DB_PATH = " + repr(TEST_DB), ns)
CONSTS = ["HIRE_COST", "WORKER_BUILDING", "BUILDING_CAPACITY",
          "BUILDING_COST", "WORKER_TO_RESOURCE", "FARMER_BYPRODUCTS",
          "WORKER_RATE", "PREDATOR_DAILY_THRESHOLD_PLAYERS",
          "PREDATOR_WEEKLY_SECONDS", "PREDATOR_DAILY_SECONDS",
          "TIGER_EAT_COUNT", "LION_EAT_COUNT",
          "PREDATOR_PROTECTED_TYPE", "PREDATOR_PROTECTED_MIN",
          "DEFAULT_BUILDING_CAPACITY", "NPC_BUY_RATE", "ALL_RESOURCE_IDX"]
for name in CONSTS:
    exec(extract_const(name), ns)

FUNCS = ["get_or_create_worker_state", "hire_worker",
         "build_building", "get_resources", "produce_by_workers",
         "get_user", "update_time", "init_predator_state",
         "get_total_player_count", "get_last_predator_event",
         "set_last_predator_event", "get_eligible_predator_targets",
         "eat_random_workers", "check_and_trigger_predator_event",
         "buy_from_system"]
for name in FUNCS:
    exec(extract_func(name), ns)

conn = sqlite3.connect(TEST_DB)
c = conn.cursor()
c.execute("""CREATE TABLE users (
    user_id INTEGER PRIMARY KEY, username TEXT,
    total_seconds INTEGER DEFAULT 0, today_seconds INTEGER DEFAULT 0,
    balance REAL DEFAULT 0, last_active TEXT,
    multiplier REAL DEFAULT 1.0, last_reset DATE,
    session_active INTEGER DEFAULT 0)""")
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
c.execute("""CREATE TABLE predator_state (
    id INTEGER PRIMARY KEY, last_event_at TEXT)""")
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
get_user = ns["get_user"]
update_time = ns["update_time"]

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

update_time(USER, "testuser")
u = get_user(USER, "testuser")
check("update_time/get_user runs without error", u is not None)


init_predator_state = ns["init_predator_state"]
get_eligible_predator_targets = ns["get_eligible_predator_targets"]
eat_random_workers = ns["eat_random_workers"]
check_and_trigger_predator_event = ns["check_and_trigger_predator_event"]

init_predator_state()

USER3 = 777777
conn = sqlite3.connect(TEST_DB)
cc = conn.cursor()
cc.execute("INSERT INTO workers VALUES (?, 'farmer', 1)", (USER3,))
conn.commit()
conn.close()

USER4 = 666666
conn = sqlite3.connect(TEST_DB)
cc = conn.cursor()
cc.execute("INSERT INTO workers VALUES (?, 'farmer', 2)", (USER4,))
cc.execute("INSERT INTO workers VALUES (?, 'lumberjack', 1)", (USER4,))
conn.commit()
conn.close()

eligible = get_eligible_predator_targets(1)
check("farmer-only player NOT eligible (protected)", USER3 not in eligible)
check("player with 2 farmers IS eligible", USER4 in eligible)

chosen = eat_random_workers(USER3, 1)
check("cannot eat the last protected farmer", len(chosen) == 0)

result1 = check_and_trigger_predator_event()
check("first predator check triggers an event", result1 is not None)

result2 = check_and_trigger_predator_event()
check("second immediate check does not trigger", result2 is None)
buy_from_system = ns["buy_from_system"]
ok, msg = buy_from_system(USER, "wood", 200)
check("buy 200 wood costs exactly 1 gild", ok == True)
row_after = get_resources(USER)
ok2, msg2 = buy_from_system(USER, "gold", 999999999)
check("buying more than affordable fails", ok2 == False)

print()
print("TOTAL:", passed, "passed,", failed, "failed")
sys.exit(1 if failed else 0)
