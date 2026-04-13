import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Update John Doe
cursor.execute("UPDATE workers SET location='New York, NY', work_hours='Full Time', hourly_rate=45 WHERE name='John Doe'")
# Update Sarah Smith
cursor.execute("UPDATE workers SET location='Brooklyn, NY', work_hours='Part Time', hourly_rate=60 WHERE name='Sarah Smith'")
# Update Mike Johnson
cursor.execute("UPDATE workers SET location='Queens, NY', work_hours='Flexible', hourly_rate=50 WHERE name='Mike Johnson'")
# Update Emily Davis
cursor.execute("UPDATE workers SET location='Manhattan, NY', work_hours='Full Time', hourly_rate=30 WHERE name='Emily Davis'")

conn.commit()
conn.close()
print("Mock data updated with locations and work hours.")
