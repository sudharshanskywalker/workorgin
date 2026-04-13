from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import sqlite3
import json
from datetime import datetime

from functools import wraps
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_purposes'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def home():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services LIMIT 6').fetchall()
    workers = conn.execute("SELECT *, avatar as profile_image FROM workers WHERE status = 'approved' LIMIT 4").fetchall()
    conn.close()
    return render_template('home.html', services=services, workers=workers)

@app.route('/services')
def services():
    category = request.args.get('category')
    search_query = request.args.get('q', '').lower()
    location = request.args.get('location', '')
    location = request.args.get('location', '')
    work_hours = request.args.get('work_hours', '')
    
    conn = get_db_connection()
    
    query = "SELECT *, avatar as profile_image FROM workers WHERE status = 'approved'"
    params = []
    
    if search_query:
        query += ' AND (lower(name) LIKE ? OR lower(profession) LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    if category:
        # Assuming profession maps loosely to category for now, or we could join with services
        query += ' AND lower(profession) LIKE ?'
        params.append(f'%{category.lower()}%')
        
    if location:
        query += ' AND lower(location) LIKE ?'
        params.append(f'%{location.lower()}%')
        
    if work_hours:
        query += ' AND work_hours LIKE ?'
        params.append(f'%{work_hours}%')
    
    workers_rows = conn.execute(query, params).fetchall()
    
    # Fetch skills for each worker
    workers = []
    for row in workers_rows:
        worker = dict(row)
        skills_rows = conn.execute('SELECT skill FROM worker_skills WHERE worker_id = ?', (worker['id'],)).fetchall()
        worker['skills'] = [s['skill'] for s in skills_rows]
        workers.append(worker)
        
    categories_rows = conn.execute('SELECT DISTINCT category FROM services').fetchall()
    categories = [row['category'] for row in categories_rows]
    
    conn.close()
    
    return render_template('services.html', 
                           workers=workers, 
                           categories=categories, 
                           selected_category=category, 
                           search_query=search_query,
                           selected_location=location,
                           work_hours=work_hours)

@app.route('/worker/<int:worker_id>')
def worker_profile(worker_id):
    conn = get_db_connection()
    worker_row = conn.execute('SELECT *, avatar as profile_image FROM workers WHERE id = ?', (worker_id,)).fetchone()
    
    if not worker_row:
        conn.close()
        return "Worker not found", 404
        
    worker = dict(worker_row)
    skills_rows = conn.execute('SELECT skill FROM worker_skills WHERE worker_id = ?', (worker_id,)).fetchall()
    worker['skills'] = [s['skill'] for s in skills_rows]
    
    # Fetch portfolio images
    portfolio_rows = conn.execute('SELECT image_path FROM portfolio_images WHERE worker_id = ?', (worker_id,)).fetchall()
    worker['portfolio'] = [img['image_path'] for img in portfolio_rows]
    
    # Fetch real reviews
    reviews_rows = conn.execute('''
        SELECT r.*, u.name as user_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.worker_id = ? 
        ORDER BY r.timestamp DESC
    ''', (worker_id,)).fetchall()
    reviews = [dict(r) for r in reviews_rows]
    
    conn.close()
    return render_template('worker_profile.html', worker=worker, reviews=reviews)

@app.route('/worker/<int:worker_id>/review', methods=['POST'])
@login_required
def submit_review(worker_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_data = session.get('user', {})
    if 'id' not in user_data:
        flash('Session issue. Please re-login.', 'error')
        return redirect(url_for('login'))
        
    user_id = user_data['id']

    
    if not rating:
        flash('Please select a rating.', 'error')
        return redirect(url_for('worker_profile', worker_id=worker_id))
        
    conn = get_db_connection()
    conn.execute('INSERT INTO reviews (worker_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
                 (worker_id, user_id, int(rating), comment))
    
    # Update worker rating and count
    stats = conn.execute('SELECT COUNT(*) as count, AVG(rating) as avg FROM reviews WHERE worker_id = ?', (worker_id,)).fetchone()
    avg_rating = round(stats['avg'], 1) if stats['avg'] is not None else 0.0
    conn.execute('UPDATE workers SET rating = ?, review_count = ? WHERE id = ?', 
                 (avg_rating, stats['count'], worker_id))
    
    conn.commit()
    conn.close()
    
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('worker_profile', worker_id=worker_id))

@app.route('/join', methods=['GET', 'POST'])
@login_required
def join_pro():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        profession = request.form.get('profession')
        experience = request.form.get('experience')
        location = request.form.get('location')
        avatar = request.form.get('avatar')
        # Remove unused payment/rate fields
        work_hours = request.form.get('work_hours')
        aadhaar = request.form.get('aadhaar')
        bio = request.form.get('bio')
        dob = request.form.get('dob')
        age = request.form.get('age')
        phone = request.form.get('phone')
        skills = request.form.get('skills')
        
        # Handle File Uploads
        avatar_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                avatar_filename = filename

        cv_filename = None
        if 'cv' in request.files:
            file = request.files['cv']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"CV_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                cv_filename = filename

        user_id = session.get('user', {}).get('id')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO worker_requests 
            (name, email, profession, experience, location, avatar, work_hours, aadhaar, cv, bio, dob, age, phone, user_id, status, skills) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, profession, experience, location, avatar_filename, work_hours, aadhaar, cv_filename, bio, dob, age, phone, user_id, 'pending', skills))
        
        request_id = cur.lastrowid
        
        # Handle multiple portfolio images
        if 'portfolio' in request.files:
            files = request.files.getlist('portfolio')
            for i, file in enumerate(files[:10]): # Limit to 10 images
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"PORTFOLIO_{request_id}_{i}_{datetime.now().strftime('%M%S')}_{filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    conn.execute('INSERT INTO portfolio_images (request_id, image_path) VALUES (?, ?)', (request_id, filename))

        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
    return render_template('join.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        
        if user:
            session['user'] = dict(user)
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
            
        conn = get_db_connection()
        
        # Check if email exists
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user:
            flash('Email already registered', 'error')
            conn.close()
            return render_template('signup.html')
            
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)', (name, email, phone, password))
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        session['user'] = {'id': user_id, 'name': name, 'email': email, 'phone': phone}
        flash('Account created successfully!', 'success')
        return redirect(url_for('home'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user_data = session.get('user', {})
    user_id = user_data.get('id')
    
    if not user_id:
        # Session might be stale, clear it
        session.pop('user', None)
        flash('Session invalid. Please re-login.', 'error')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # Fetch user details
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Check if user is also a worker
    worker_row = conn.execute('SELECT *, avatar as profile_image FROM workers WHERE user_id = ?', (user_id,)).fetchone()
    
    worker = None
    bookings = []
    if worker_row:
        worker = dict(worker_row)
        # Fetch worker skills
        skills_rows = conn.execute('SELECT skill FROM worker_skills WHERE worker_id = ?', (worker['id'],)).fetchall()
        worker['skills'] = [s['skill'] for s in skills_rows]
        
        # Fetch worker portfolio
        portfolio_rows = conn.execute('SELECT image_path FROM portfolio_images WHERE worker_id = ?', (worker['id'],)).fetchall()
        worker['portfolio'] = [p['image_path'] for p in portfolio_rows]
        
        # Fetch bookings for this worker (booked customers)
        bookings_rows = conn.execute('''
            SELECT b.*, u.name as user_name, u.email as user_email, u.phone as user_phone
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            WHERE b.worker_id = ?
            ORDER BY b.id DESC
        ''', (worker['id'],)).fetchall()
        bookings = [dict(b) for b in bookings_rows]
    
    conn.close()
    return render_template('profile.html', user=user, worker=worker, bookings=bookings)

@app.route('/admin')
@login_required
def admin_dashboard():
    # Only allow specific emails to access admin
    admin_emails = ['admin@example.com', 'kishor123@gnail.com', 'sudharsan@gmail.com']
    if session.get('user', {}).get('email') not in admin_emails:
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    requests_rows = conn.execute('SELECT *, avatar as profile_image FROM worker_requests').fetchall()
    requests = []
    for row in requests_rows:
        req = dict(row)
        portfolio = conn.execute('SELECT image_path FROM portfolio_images WHERE request_id = ?', (req['id'],)).fetchall()
        req['portfolio'] = [img['image_path'] for img in portfolio]
        requests.append(req)
        
    workers_rows = conn.execute('SELECT *, avatar as profile_image FROM workers').fetchall()
    workers_list = []
    for row in workers_rows:
        w = dict(row)
        portfolio = conn.execute('SELECT image_path FROM portfolio_images WHERE worker_id = ?', (w['id'],)).fetchall()
        w['portfolio'] = [img['image_path'] for img in portfolio]
        workers_list.append(w)
    
    # Real-time Stats
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    active_pros = conn.execute("SELECT COUNT(*) FROM workers WHERE status = 'approved'").fetchone()[0]
    pending_apps = len(requests)
    
    conn.close()
    return render_template('admin.html', 
                          requests=requests, 
                          active_workers=workers_list,
                          total_bookings=total_bookings,
                          active_pros=active_pros,
                          pending_apps=pending_apps)

@app.route('/book_pro', methods=['POST'])
def book_pro_route():
    if not session.get('user'):
        return {'success': False, 'message': 'Login required'}, 401
    
    worker_id = request.form.get('worker_id')
    user_data = session.get('user', {})
    if 'id' not in user_data:
        return {'success': False, 'message': 'Session expired. Please re-login.'}, 401
        
    user_id = user_data['id']

    
    conn = get_db_connection()
    conn.execute('INSERT INTO bookings (worker_id, user_id, status) VALUES (?, ?, ?)', (worker_id, user_id, 'Pending'))
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Booking recorded'}

@app.route('/admin/approve/<int:request_id>', methods=['POST'])
def approve_worker(request_id):
    conn = get_db_connection()
    worker_request = conn.execute('SELECT * FROM worker_requests WHERE id = ?', (request_id,)).fetchone()
    
    if worker_request:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO workers (name, avatar, profession, location, rating, review_count, bio, work_hours, aadhaar, dob, age, phone, user_id, email, status, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            worker_request['name'], 
            worker_request['avatar'], 
            worker_request['profession'], 
            worker_request['location'],
            0.0, 0,   
            worker_request['bio'] if worker_request['bio'] else f"Professional {worker_request['profession']}",
            worker_request['work_hours'],
            worker_request['aadhaar'],
            worker_request['dob'],
            worker_request['age'],
            worker_request['phone'],
            worker_request['user_id'],
            worker_request['email'],
            'approved',
            worker_request['skills']
        ))
        
        worker_id = cur.lastrowid
        
        # Link portfolio images to the new worker record
        conn.execute('UPDATE portfolio_images SET worker_id = ?, request_id = NULL WHERE request_id = ?', (worker_id, request_id))
        
        # Also populate worker_skills table
        if worker_request['skills']:
            skills_list = worker_request['skills'].split(',')
            for skill in skills_list:
                if skill.strip():
                    conn.execute('INSERT INTO worker_skills (worker_id, skill) VALUES (?, ?)', (worker_id, skill.strip()))
        
        conn.execute('DELETE FROM worker_requests WHERE id = ?', (request_id,))
        conn.commit()
        flash(f'Worker {worker_request["name"]} approved successfully!', 'success')
    
    conn.close()
    return redirect(url_for( 'admin_dashboard' ))

@app.route('/admin/reject/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    conn = get_db_connection()
    # Optional: Delete associated portfolio images first if cleanup is desired
    conn.execute('DELETE FROM portfolio_images WHERE request_id = ?', (request_id,))
    conn.execute('DELETE FROM worker_requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    flash('Application rejected and removed.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_worker/<int:worker_id>', methods=['POST'])
def delete_worker(worker_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM workers WHERE id = ?', (worker_id,))
    conn.execute('DELETE FROM worker_skills WHERE worker_id = ?', (worker_id,))
    conn.execute('DELETE FROM reviews WHERE worker_id = ?', (worker_id,))
    conn.commit()
    conn.close()
    flash('Worker profile deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/accept_booking/<int:booking_id>', methods=['POST'])
@login_required
def accept_booking(booking_id):
    conn = get_db_connection()
    # Ensure current user is the worker for this booking
    user_id = session['user']['id']
    booking = conn.execute('''
        SELECT b.* FROM bookings b
        JOIN workers w ON b.worker_id = w.id
        WHERE b.id = ? AND w.user_id = ?
    ''', (booking_id, user_id)).fetchone()
    
    if booking:
        conn.execute("UPDATE bookings SET status = 'Accepted' WHERE id = ?", (booking_id,))
        conn.commit()
        flash('Booking accepted!', 'success')
    else:
        flash('Unauthorized action or booking not found.', 'error')
        
    conn.close()
    return redirect(url_for('profile'))

@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    conn = get_db_connection()
    # Ensure current user is the worker for this booking
    user_id = session['user']['id']
    booking = conn.execute('''
        SELECT b.* FROM bookings b
        JOIN workers w ON b.worker_id = w.id
        WHERE b.id = ? AND w.user_id = ?
    ''', (booking_id, user_id)).fetchone()
    
    if booking:
        conn.execute("UPDATE bookings SET status = 'Rejected' WHERE id = ?", (booking_id,))
        conn.commit()
        flash('Booking rejected.', 'info')
    else:
        flash('Unauthorized action or booking not found.', 'error')
        
    conn.close()
    return redirect(url_for('profile'))

@app.route('/chat', methods=['POST'])
def chat_assistant():
    data = request.json
    user_message = data.get('message', '').lower()
    
    response = ""
    action = None
    
    # Python Bot Intent Mapping
    intents = {
        'plumber': {
            'keywords': ['plumb', 'leak', 'pipe', 'tap', 'toilet', 'drain'],
            'response': "I'm JARVIS! 🤖 I've found several expert plumbers for you. Would you like to check them out?",
            'action': {"type": "link", "url": "/services?category=home maintenance", "label": "List Plumbers"}
        },
        'electrician': {
            'keywords': ['electr', 'wire', 'light', 'fan', 'switch', 'shock', 'power'],
            'response': "Power issues? ⚡ I can link you with our top-rated electricians right now.",
            'action': {"type": "link", "url": "/services?category=home maintenance", "label": "List Electricians"}
        },
        'cleaning': {
            'keywords': ['clean', 'maid', 'sweep', 'wash', 'mop', 'housekeep'],
            'response': "Need a spotless home? 🧼 I've filtered out the best cleaning professionals for you.",
            'action': {"type": "link", "url": "/services?category=home services", "label": "List Cleaners"}
        },
        'carpenter': {
            'keywords': ['carpent', 'wood', 'furnitur', 'table', 'chair', 'door'],
            'response': "Working with wood? 🪵 I can find you a skilled carpenter in your area.",
            'action': {"type": "link", "url": "/services?category=home maintenance", "label": "List Carpenters"}
        }
    }

    # Match intents
    for intent, data in intents.items():
        if any(kw in user_message for kw in data['keywords']):
            response = data['response']
            action = data['action']
            break

    # Fallback and help logic
    if not response:
        if any(kw in user_message for kw in ['how', 'book', 'step', 'process']):
            response = "It's easy! 1️⃣ Search for a service. 2️⃣ Pick a pro. 3️⃣ Press 'Book Now'. I'll handle the rest! 🚀"
        elif any(kw in user_message for kw in ['hi', 'hello', 'hey', 'start']):
            response = "Hello! I am JARVIS. 🤖 I can help you find plumbers, electricians, and more. What are you looking for?"
        elif any(kw in user_message for kw in ['who', 'what', 'you']):
            response = "I'm JARVIS, your personal AI assistant designed to make your life easier by connecting you with local workers! 🤖"
        else:
            response = "I'm not quite sure about that, but try asking for a 'plumber', 'electrician' or 'cleaner'. I'm here to help! 🤖"
        
    return jsonify({
        "response": response,
        "action": action
    })

# --- Context Processors ---
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(debug=True)
