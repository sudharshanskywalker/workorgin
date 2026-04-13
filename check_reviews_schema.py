import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA table_info(reviews)")
    cols = cursor.fetchall()
    print("Reviews table columns:")
    for col in cols:
        print(col)
except Exception as e:
    print(f"Error: {e}")
conn.close()
