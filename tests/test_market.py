import sqlite3
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'services'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot', 'handlers'))

# עקוף את config עם DB זמני
test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
os.environ['TEST_DB_PATH'] = test_db.name

import config
config.DB_PATH = test_db.name

from database import init_db, init_resources_db, get_resources
from market_service import sell_resource, get_market_listings, buy_from_market

PASS = 0
FAIL = 0

def check(desc, condition):
    global PASS, FAIL
    if condition:
        print(f"PASS: {desc}")
        PASS += 1
    else:
        print(f"FAIL: {desc}")
        FAIL += 1

# Setup
init_db()
init_resources_db()

# צור טבלת market לבדיקות
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS market (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER,
    resource TEXT,
    amount REAL,
    price_per_unit REAL,
    created_at TEXT
)""")
conn.commit()
conn.close()

# צור 2 משתמשים לבדיקות
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (1, "player1"))
c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (2, "player2"))
# תן להם משאבים
for uid in [1, 2]:
    c.execute("INSERT OR IGNORE INTO resources (user_id) VALUES (?)", (uid,))
conn.commit()
conn.close()

# תן לשחקן 1 מים ו-Gild
conn = sqlite3.connect(test_db.name)
c = conn.cursor()
c.execute("UPDATE resources SET water=100, gild=50 WHERE user_id=1")
c.execute("UPDATE resources SET gild=100 WHERE user_id=2")
conn.commit()
conn.close()

print("=" * 50)
print("MARKET SERVICE TESTS")
print("=" * 50)

# =========== sell_resource ===========

# 1. מכירה רגילה
ok, msg = sell_resource(1, "water", 10, 2.0)
check("sell_resource: מכירה רגילה עובדת", ok == True)

# 2. משאב לא קיים
ok, msg = sell_resource(1, "oil", 10, 2.0)
check("sell_resource: משאב לא מוכר נדחה", ok == False and "לא מוכר" in msg)

# 3. אין מספיק משאב
ok, msg = sell_resource(1, "water", 200, 2.0)
check("sell_resource: אין מספיק משאב נדחה", ok == False and "אין מספיק" in msg)

# 4. רשימה ריקה
listings = get_market_listings()
check("get_market_listings: מחזיר רשימה (לא ריקה)", len(listings) > 0)

# 5. הרשימה מכילה את ההצעה שלנו
water_listings = [l for l in listings if l[2] == "water"]
check("get_market_listings: מוצא הצעת water", len(water_listings) > 0)
check("get_market_listings: מחיר נכון", water_listings[0][4] == 2.0)
check("get_market_listings: כמות נכונה", water_listings[0][3] == 10.0)

# =========== buy_from_market ===========

listing_id = water_listings[0][0]

# 6. קניה רגילה - player2 קונה מ-player1
ok, result = buy_from_market(2, listing_id, 3.0)
check("buy_from_market: קניה רגילה עובדת", ok == True)
if ok:
    check("buy_from_market: resource נכון בחזרה", result["resource"] == "water")
    check("buy_from_market: cost נכון (3*2=6)", abs(result["cost"] - 6.0) < 0.01)

# 7. אי אפשר לקנות מעצמך
ok, result = buy_from_market(1, listing_id, 2.0)
check("buy_from_market: קניה מעצמך נדחית", ok == False)

# 8. הצעה לא קיימת
ok, result = buy_from_market(1, 9999, 1.0)
check("buy_from_market: הצעה לא קיימת נדחית", ok == False)

# 9. קניה חלקית - נשאר 7 בשוק (10-3=7)
remaining = get_market_listings()
water_remaining = [l for l in remaining if l[0] == listing_id]
check("buy_from_market: נשארה כמות חלקית בשוק", len(water_remaining) > 0 and abs(water_remaining[0][3] - 7.0) < 0.01)

# 10. קנה את השאר - השורה נמחקת
ok, result = buy_from_market(2, listing_id, 7.0)
check("buy_from_market: קניית יתרה מחקה הצעה", ok == True)
final_listings = [l for l in get_market_listings() if l[0] == listing_id]
check("buy_from_market: ההצעה נמחקה מהשוק", len(final_listings) == 0)

# 11. אי אפשר לקנות יותר ממה שיש
# נמכור 5 מים ונסה לקנות 10
ok, _ = sell_resource(1, "water", 5, 1.0)
new_listing = [l for l in get_market_listings() if l[2] == "water" and l[3] == 5.0]
if new_listing:
    ok, result = buy_from_market(2, new_listing[0][0], 10.0)
    check("buy_from_market: קניית יותר ממה שיש נדחית", ok == False)

# =========== תוצאות ===========
print("=" * 50)
print(f"TOTAL: {PASS} passed, {FAIL} failed")
if FAIL > 0:
    print("❌ יש בדיקות שנכשלו!")
    sys.exit(1)
else:
    print("✅ כל הבדיקות עברו!")

# ניקוי
os.unlink(test_db.name)
