import sqlite3

def create_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Create the products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
    print("Database created and table 'products' initialized.")
