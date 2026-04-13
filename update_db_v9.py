import sqlite3

def update_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Add phone column to users table
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        print("Added phone column to users table.")
    except sqlite3.OperationalError:
        print("phone column already exists in users table.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_db()
