import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT name, avatar, cv FROM worker_requests LIMIT 5")
rows = cursor.fetchall()
print("Worker Requests Sample:")
for row in rows:
    print(row)

cursor.execute("SELECT name, avatar FROM workers LIMIT 5")
rows = cursor.fetchall()
print("\nWorkers Sample:")
for row in rows:
    print(row)
conn.close()
