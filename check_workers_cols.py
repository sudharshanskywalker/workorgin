import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(workers)")
cols = cursor.fetchall()
print("Workers table columns:")
for col in cols:
    print(col)
conn.close()
