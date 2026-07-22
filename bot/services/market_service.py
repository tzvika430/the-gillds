import sqlite3
from datetime import datetime
from config import DB_PATH, ALL_RESOURCE_IDX
from database import get_resources

def sell_resource(user_id, resource, amount, price):
    if resource not in ALL_RESOURCE_IDX:
        return False, 'משאב לא מוכר'
    row = get_resources(user_id)
    idx = ALL_RESOURCE_IDX[resource]
    if row[idx] < amount:
        return False, f'אין מספיק {resource}'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)-? WHERE user_id=?", (amount, user_id))
    c.execute("INSERT INTO market (seller_id, resource, amount, price_per_unit, created_at) VALUES (?,?,?,?,?)", 
              (user_id, resource, amount, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True, 'OK'

def get_market_listings(limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, seller_id, resource, amount, price_per_unit FROM market ORDER BY resource ASC, price_per_unit ASC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def buy_from_market(buyer_id, listing_id, amount_requested):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT seller_id, resource, amount, price_per_unit FROM market WHERE id=?", (listing_id,))
    listing = c.fetchone()
    if not listing:
        conn.close()
        return False, 'הצעה לא קיימת'
    seller_id, resource, avail_amount, price = listing
    if seller_id == buyer_id:
        conn.close()
        return False, 'אי אפשר לקנות מעצמך'
    if amount_requested > avail_amount + 1e-9:
        conn.close()
        return False, f'יש רק {avail_amount:.2f} בהצעה הזו'
    total_cost = amount_requested * price
    buyer_row = get_resources(buyer_id)
    if buyer_row[5] < total_cost:
        conn.close()
        return False, f'אין מספיק Gild, צריך {total_cost:.2f}'
    c.execute("UPDATE resources SET gild=gild-? WHERE user_id=?", (total_cost, buyer_id))
    c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)+? WHERE user_id=?", (amount_requested, buyer_id))
    c.execute("UPDATE resources SET gild=gild+? WHERE user_id=?", (total_cost, seller_id))
    if abs(amount_requested - avail_amount) < 1e-9:
        c.execute("DELETE FROM market WHERE id=?", (listing_id,))
    else:
        c.execute("UPDATE market SET amount=amount-? WHERE id=?", (amount_requested, listing_id))
    conn.commit()
    conn.close()
    return True, {"resource": resource, "cost": total_cost}
