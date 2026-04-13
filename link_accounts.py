import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Link workers to users by email
cursor.execute('''
UPDATE workers 
SET user_id = (SELECT id FROM users WHERE users.email = workers.email)
WHERE user_id IS NULL
''')

# Link requests to users by email
cursor.execute('''
UPDATE worker_requests 
SET user_id = (SELECT id FROM users WHERE users.email = worker_requests.email)
WHERE user_id IS NULL
''')

conn.commit()
conn.close()
print("Linked existing workers and requests to user accounts based on email.")
