# db.py or products/crud.py

import sqlite3

def delete_product_by_barcode(barcode):
    try:
        conn = sqlite3.connect("your_database.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE barcode = ?", (barcode,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error deleting:", e)
        return False
