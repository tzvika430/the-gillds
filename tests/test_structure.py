import os
import re

BASE = "/data/data/com.termux/files/home/SLH-DEV"

required_paths = [
    "bot/src/bot.py",
    "bot/services/config.py",
    "bot/services/database.py",
    "bot/services/bot_instance.py",
    "bot/handlers/commands.py",
    "docs/MASTER_PLAN.md",
    "database",
    "logs",
    "backups",
    "tests",
]

print("=== SLH DEV STRUCTURE TEST ===")
failed = False

for path in required_paths:
    full = os.path.join(BASE, path)
    if os.path.exists(full):
        print(f"OK: {path}")
    else:
        print(f"MISSING: {path}")
        failed = True

cmds_path = os.path.join(BASE, "bot/handlers/commands.py")
if os.path.exists(cmds_path):
    src = open(cmds_path, encoding="utf-8").read()
    pattern = re.compile(r"@bot\.message_handler\((.*?)\)")
    matches = list(pattern.finditer(src))
    catchall_positions = []
    named_positions = []
    for m in matches:
        if "commands=" in m.group(1):
            named_positions.append(m.start())
        else:
            catchall_positions.append(m.start())
    if catchall_positions and named_positions:
        if min(catchall_positions) < max(named_positions):
            print("MISORDERED: catch-all handler (func=lambda) appears before a named command handler")
            failed = True
        else:
            print("OK: catch-all handler is registered last")
    else:
        print("OK: no catch-all handler conflict detected")
else:



    print("MISSING: bot/handlers/commands.py (cannot check handler order)")
    failed = True

if failed:
    print("STATUS: FAILED")
else:
    print("STATUS: PASSED")
