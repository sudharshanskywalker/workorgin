import sqlite3
from datetime import datetime

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Insert Users (Example)
cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ('Admin User', 'admin@example.com', 'admin123')
            )

# Insert Services
services = [
    ("Plumbing", "Fix leaks, install pipes, and bathroom fittings.", "Wrench", "Home Maintenance"),
    ("Electrical", "Wiring, lighting installation, and appliance repair.", "Zap", "Home Maintenance"),
    ("Cleaning", "Deep cleaning for homes and offices.", "Spray", "Home Services"),
    ("Carpentry", "Furniture repair, custom cabinets, and woodwork.", "Hammer", "Home Maintenance"),
    ("Painting", "Interior and exterior painting services.", "Paintbrush", "Home Improvement"),
    ("Gardening", "Lawn care, planting, and landscape design.", "Flower2", "Outdoor")
]

cur.executemany("INSERT INTO services (title, description, icon_name, category) VALUES (?, ?, ?, ?)", services)

# Insert Workers and Skills
workers = [
    {
        "name": "John Doe",
        "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=200&h=200",
        "profession": "Plumber",
        "rating": 4.8,
        "review_count": 124,
        "location": "New York, NY",
        "hourly_rate": 45,
        "bio": "Experienced plumber with over 10 years of experience in residential and commercial plumbing. I specialize in leak detection and bathroom renovations.",
        "skills": ["Pipe Repair", "Leak Detection", "Installation", "Maintenance"],
    },
    {
        "name": "Sarah Smith",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=200&h=200",
        "profession": "Electrician",
        "rating": 4.9,
        "review_count": 89,
        "location": "Brooklyn, NY",
        "hourly_rate": 60,
        "bio": "Certified electrician focusing on safe and efficient electrical solutions. Available for emergency call-outs and planned installations.",
        "skills": ["Wiring", "Lighting", "Circuit Breakers", "Safety Inspections"],
    },
    {
        "name": "Mike Johnson",
        "avatar": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&q=80&w=200&h=200",
        "profession": "Carpenter",
        "rating": 4.7,
        "review_count": 56,
        "location": "Queens, NY",
        "hourly_rate": 50,
        "bio": "Passionate woodworker creating custom furniture and providing high-quality repair services.",
        "skills": ["Cabinet Making", "Furniture Repair", "Wood Carving", "Restoration"],
    },
    {
        "name": "Emily Davis",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&q=80&w=200&h=200",
        "profession": "Cleaner",
        "rating": 4.6,
        "review_count": 204,
        "location": "Manhattan, NY",
        "hourly_rate": 30,
        "bio": "Detailed-oriented professional cleaner making your space shine. Eco-friendly products used upon request.",
        "skills": ["Deep Cleaning", "Organization", "Eco-friendly", "Sanitization"],
    },
]

for worker in workers:
    cur.execute('''INSERT INTO workers (name, avatar, profession, rating, review_count, location, hourly_rate, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (worker['name'], worker['avatar'], worker['profession'], worker['rating'], worker['review_count'], worker['location'], worker['hourly_rate'], worker['bio']))
    
    worker_id = cur.lastrowid
    
    for skill in worker['skills']:
        cur.execute("INSERT INTO worker_skills (worker_id, skill) VALUES (?, ?)", (worker_id, skill))

connection.commit()
connection.close()

print("Database initialized successfully!")
