import sqlite3

def update_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Add hourly_rate and work_hours to worker_requests
    try:
        cursor.execute('ALTER TABLE worker_requests ADD COLUMN hourly_rate INTEGER')
    except sqlite3.OperationalError:
        print("hourly_rate column already exists")
        
    try:
        cursor.execute('ALTER TABLE worker_requests ADD COLUMN work_hours TEXT')
    except sqlite3.OperationalError:
        print("work_hours column already exists")
        
    try:
        cursor.execute('ALTER TABLE worker_requests ADD COLUMN aadhaar TEXT')
    except sqlite3.OperationalError:
        print("aadhaar column already exists")

    # Add work_hours to workers
    try:
        cursor.execute('ALTER TABLE workers ADD COLUMN work_hours TEXT')
    except sqlite3.OperationalError:
        print("work_hours column already exists in workers table")
    
    conn.commit()
    conn.close()
    print("Database updated with new fields.")

if __name__ == '__main__':
    update_db()
