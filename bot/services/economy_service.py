import sqlite3
from config import DB_PATH, WORKER_TO_RESOURCE, WORKER_RATE, FARMER_BYPRODUCTS

def produce_by_workers(user_id, seconds):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT worker_type, count FROM workers WHERE user_id=?", (user_id,))
    workers = c.fetchall()
    for worker_type, count in workers:
        if count <= 0 or worker_type not in WORKER_TO_RESOURCE:
            continue
        resource = WORKER_TO_RESOURCE.get(worker_type)
        if resource is None:
            continue  # soldier/commander/general לא מייצרים
        amount = count * seconds * WORKER_RATE
        c.execute(f"UPDATE resources SET {resource}=COALESCE({resource},0)+? WHERE user_id=?", (amount, user_id))
        if worker_type == 'farmer':
            for byres, ratio in FARMER_BYPRODUCTS.items():
                c.execute(f"UPDATE resources SET {byres}=COALESCE({byres},0)+? WHERE user_id=?", (amount*ratio, user_id))
    conn.commit()
    conn.close()
