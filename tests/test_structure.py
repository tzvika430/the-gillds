import os

required_paths = [
    "bot/src/bot.py",
    "docs/MASTER_PLAN.md",
    "docs/BOT_MAP.md",
    "database",
    "logs",
    "backups",
    "tests"
]

print("=== SLH DEV STRUCTURE TEST ===")

failed = False

for path in required_paths:
    if os.path.exists(path):
        print(f"OK: {path}")
    else:
        print(f"MISSING: {path}")
        failed = True

if failed:
    print("STATUS: FAILED")
else:
    print("STATUS: PASSED")
