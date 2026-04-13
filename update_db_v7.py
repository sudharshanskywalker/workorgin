import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 1. Add columns to worker_requests
columns_to_add = [
    ('dob', 'TEXT'),
    ('age', 'INTEGER'),
    ('phone', 'TEXT')
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE worker_requests ADD COLUMN {col_name} {col_type}")
        print(f"Added {col_name} column to worker_requests")
    except sqlite3.OperationalError:
        print(f"{col_name} column already exists in worker_requests")

# 2. Add columns to workers
for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE workers ADD COLUMN {col_name} {col_type}")
        print(f"Added {col_name} column to workers")
    except sqlite3.OperationalError:
        print(f"{col_name} column already exists in workers")

conn.commit()
conn.close()
