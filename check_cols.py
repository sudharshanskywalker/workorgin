import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(worker_requests)")
columns = [info[1] for info in cursor.fetchall()]
print(f"worker_requests columns: {columns}")

cursor.execute("PRAGMA table_info(workers)")
columns = [info[1] for info in cursor.fetchall()]
print(f"workers columns: {columns}")
conn.close()
