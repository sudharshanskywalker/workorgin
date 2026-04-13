from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import sqlite3
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from bot import get_bot_response   # chatbot import

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_purposes'

# Fix for redirection issues behind proxies like PythonAnywhere/Vercel
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['email'] != 'admin@example.com':
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- HOME ----------------


@app.route('/')
def home():
    conn = get_db_connection()

    services = conn.execute('SELECT * FROM services LIMIT 6').fetchall()

    workers = conn.execute(
        "SELECT *, avatar as profile_image FROM workers WHERE status='approved' LIMIT 4"
    ).fetchall()

    conn.close()

    return render_template('home.html', services=services, workers=workers)


# ---------------- ADMIN DASHBOARD ----------------

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()

    # Get worker requests
    requests_rows = conn.execute('SELECT * FROM worker_requests ORDER BY timestamp DESC').fetchall()
    requests = []
    for row in requests_rows:
        req = dict(row)
        # Fetch portfolio images for this request
        port_rows = conn.execute('SELECT image_path FROM portfolio_images WHERE request_id=?', (req['id'],)).fetchall()
        req['portfolio'] = [p['image_path'] for p in port_rows]
        req['profile_image'] = req.get('avatar')
        requests.append(req)

    # Get active workers
    workers_rows = conn.execute("SELECT *, avatar as profile_image FROM workers WHERE status='approved'").fetchall()
    active_workers = []
    for row in workers_rows:
        w = dict(row)
        # Get portfolio for icons in table
        port = conn.execute('SELECT image_path FROM portfolio_images WHERE worker_id=?', (w['id'],)).fetchone()
        w['portfolio'] = [port['image_path']] if port else []
        active_workers.append(w)

    # Stats
    pending_apps = len(requests)
    active_pros = len(active_workers)
    total_bookings = conn.execute('SELECT COUNT(*) FROM booking_requests').fetchone()[0]

    conn.close()
    return render_template(
        'admin.html',
        requests=requests,
        active_workers=active_workers,
        pending_apps=pending_apps,
        active_pros=active_pros,
        total_bookings=total_bookings
    )


@app.route('/approve_worker/<int:request_id>', methods=['POST'])
@admin_required
def approve_worker(request_id):
    conn = get_db_connection()
    req = conn.execute('SELECT * FROM worker_requests WHERE id=?', (request_id,)).fetchone()

    if req:
        # Convert row to dict to use .get() safely
        req = dict(req)
        
        # Move to workers table
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO workers 
               (name, avatar, profession, rating, review_count, location, bio, status, 
                work_hours, aadhaar, dob, age, phone, user_id, email, skills, hourly_rate) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (req['name'], req['avatar'], req['profession'], 5.0, 0, req['location'], 
             req.get('bio', f"Experienced {req['profession']}"), 'approved',
             req.get('work_hours'), req.get('aadhaar'), req.get('dob'), req.get('age'),
             req.get('phone'), req.get('user_id'), req.get('email'), req.get('skills'),
             req.get('hourly_rate', 0))
        )
        worker_id = cur.lastrowid

        # Update portfolio images to link to the new worker_id
        conn.execute('UPDATE portfolio_images SET worker_id = ? WHERE request_id = ?', (worker_id, request_id))

        # Add Notification for the worker
        if req.get('user_id'):
            conn.execute(
                'INSERT INTO notifications (user_id, message) VALUES (?, ?)',
                (req['user_id'], "Congratulations! Your professional profile application has been approved by the admin.")
            )

        # Also handle worker_skills table
        if req.get('skills'):
            # Clear existing if any (shouldn't be any for a new worker)
            conn.execute('DELETE FROM worker_skills WHERE worker_id = ?', (worker_id,))
            for skill in req['skills'].split(','):
                if skill.strip():
                    conn.execute('INSERT INTO worker_skills (worker_id, skill) VALUES (?, ?)', (worker_id, skill.strip()))

        # Delete from requests
        conn.execute('DELETE FROM worker_requests WHERE id=?', (request_id,))
        conn.commit()
        flash(f"Professional {req['name']} approved!", 'success')

    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_request/<int:request_id>', methods=['POST'])
@admin_required
def reject_request(request_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM worker_requests WHERE id=?', (request_id,))
    conn.commit()
    conn.close()
    flash("Application rejected and removed.", 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_worker/<int:worker_id>', methods=['POST'])
@admin_required
def delete_worker(worker_id):
    conn = get_db_connection()
    conn.execute("UPDATE workers SET status='deleted' WHERE id=?", (worker_id,))
    conn.commit()
    conn.close()
    flash("Worker profile deactivated.", 'success')
    return redirect(url_for('admin_dashboard'))


# ---------------- SERVICES ----------------

@app.route('/services')
def services():

    category = request.args.get('category')
    search_query = request.args.get('q', '').lower()
    location = request.args.get('location', '')
    work_hours = request.args.get('work_hours', '')

    conn = get_db_connection()

    query = "SELECT *, avatar as profile_image FROM workers WHERE status='approved'"
    params = []

    if search_query:
        query += " AND (lower(name) LIKE ? OR lower(profession) LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])

    if category:
        query += " AND lower(profession) LIKE ?"
        params.append(f'%{category.lower()}%')

    if location:
        query += " AND lower(location) LIKE ?"
        params.append(f'%{location.lower()}%')

    if work_hours:
        query += " AND work_hours LIKE ?"
        params.append(f'%{work_hours}%')

    workers_rows = conn.execute(query, params).fetchall()

    workers = []

    for row in workers_rows:

        worker = dict(row)

        skills_rows = conn.execute(
            'SELECT skill FROM worker_skills WHERE worker_id=?',
            (worker['id'],)
        ).fetchall()

        worker['skills'] = [s['skill'] for s in skills_rows]

        workers.append(worker)

    categories_rows = conn.execute(
        'SELECT DISTINCT category FROM services'
    ).fetchall()

    categories = [row['category'] for row in categories_rows]

    conn.close()

    return render_template(
        'services.html',
        workers=workers,
        categories=categories,
        selected_category=category,
        search_query=search_query,
        selected_location=location,
        work_hours=work_hours
    )


# ---------------- WORKER PROFILE ----------------

@app.route('/worker/<int:worker_id>')
def worker_profile(worker_id):

    conn = get_db_connection()

    worker_row = conn.execute(
        'SELECT *, avatar as profile_image FROM workers WHERE id=?',
        (worker_id,)
    ).fetchone()

    if not worker_row:
        conn.close()
        return "Worker not found", 404

    worker = dict(worker_row)

    skills_rows = conn.execute(
        'SELECT skill FROM worker_skills WHERE worker_id=?',
        (worker_id,)
    ).fetchall()

    worker['skills'] = [s['skill'] for s in skills_rows]

    portfolio_rows = conn.execute(
        'SELECT image_path FROM portfolio_images WHERE worker_id=?',
        (worker_id,)
    ).fetchall()

    worker['portfolio'] = [img['image_path'] for img in portfolio_rows]

    reviews_rows = conn.execute(
        '''
        SELECT r.*, u.name as user_name
        FROM reviews r
        JOIN users u ON r.user_id=u.id
        WHERE r.worker_id=?
        ORDER BY r.timestamp DESC
        ''',
        (worker_id,)
    ).fetchall()

    reviews = [dict(r) for r in reviews_rows]

    conn.close()

    return render_template(
        'worker_profile.html',
        worker=worker,
        reviews=reviews
    )


# ---------------- USER PROFILE & DASHBOARD ----------------

@app.route('/profile')
@login_required
def profile():
    user = session['user']
    conn = get_db_connection()

    # Check if user is also a worker
    worker_row = conn.execute(
        'SELECT *, avatar as profile_image FROM workers WHERE user_id=?',
        (user['id'],)
    ).fetchone()

    worker = None
    bookings = []

    if worker_row:
        worker = dict(worker_row)
        # Get skills
        skills_rows = conn.execute(
            'SELECT skill FROM worker_skills WHERE worker_id=?',
            (worker['id'],)
        ).fetchall()
        worker['skills'] = [s['skill'] for s in skills_rows]

        # Get bookings for this worker
        bookings_rows = conn.execute(
            '''
            SELECT br.*, u.name as user_name, u.email as user_email, u.phone as user_phone
            FROM booking_requests br
            JOIN users u ON br.user_id = u.id
            WHERE br.worker_id = ?
            ORDER BY br.timestamp DESC
            ''', (worker['id'],)
        ).fetchall()
        bookings = [dict(b) for b in bookings_rows]

    conn.close()

    # Fetch notifications
    conn = get_db_connection()
    notifications_rows = conn.execute(
        'SELECT * FROM notifications WHERE user_id=? ORDER BY timestamp DESC LIMIT 10',
        (user['id'],)
    ).fetchall()
    notifications = [dict(n) for n in notifications_rows]
    conn.close()

    return render_template('profile.html', user=user, worker=worker, bookings=bookings, notifications=notifications)


# ---------------- SIGNUP ----------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, email, password]):
            flash('Missing required fields', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                (name, email, phone, password)
            )
            conn.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'error')
        finally:
            conn.close()

    return render_template('signup.html')


# ---------------- JOIN AS PROFESSIONAL ----------------

@app.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        age = request.form.get('age')
        profession = request.form.get('profession')
        experience = request.form.get('experience')
        work_hours = request.form.get('work_hours')
        location = request.form.get('location')
        aadhaar = request.form.get('aadhaar')
        skills = request.form.get('skills', '')
        bio = request.form.get('bio')

        # Handle Profile Photo (avatar)
        avatar_file = request.files.get('photo')  # Note: join.html uses 'photo'
        avatar_filename = None
        if avatar_file and allowed_file(avatar_file.filename):
            avatar_filename = secure_filename(avatar_file.filename)
            avatar_file.save(os.path.join(UPLOAD_FOLDER, avatar_filename))

        # Handle CV
        cv_file = request.files.get('cv')
        cv_filename = None
        if cv_file and allowed_file(cv_file.filename):
            cv_filename = secure_filename(cv_file.filename)
            cv_file.save(os.path.join(UPLOAD_FOLDER, cv_filename))

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            # Save to worker_requests
            cur.execute(
                '''INSERT INTO worker_requests 
                   (name, email, phone, dob, age, profession, experience, work_hours, location, aadhaar, skills, bio, avatar, cv, user_id, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (name, email, phone, dob, age, profession, experience, work_hours, location, aadhaar, skills, bio, avatar_filename, cv_filename, session['user']['id'], 'pending')
            )
            request_id = cur.lastrowid
            
            # Save Portfolio images
            portfolio_files = request.files.getlist('portfolio')
            for p_file in portfolio_files:
                if p_file and allowed_file(p_file.filename):
                    p_filename = secure_filename(p_file.filename)
                    # Unique filename to avoid collisions
                    p_filename = f"req_{request_id}_{p_filename}"
                    p_file.save(os.path.join(UPLOAD_FOLDER, p_filename))
                    cur.execute(
                        'INSERT INTO portfolio_images (request_id, image_path) VALUES (?, ?)',
                        (request_id, p_filename)
                    )

            conn.commit()
            flash('Your application has been submitted and is pending admin approval.', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            conn.rollback()
            flash(f'Error submitting application: {str(e)}', 'error')
        finally:
            conn.close()

    return render_template('join.html')


# ---------------- BOOKING ACTIONS ----------------

@app.route('/book_pro', methods=['POST'])
@login_required
def book_pro():
    worker_id = request.form.get('worker_id')
    user_id = session['user']['id']

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO booking_requests (worker_id, user_id, status) VALUES (?, ?, ?)',
            (worker_id, user_id, 'Pending')
        )
        
        # Add Notification for the worker
        user_name = session['user']['name']
        worker_row = conn.execute('SELECT user_id FROM workers WHERE id=?', (worker_id,)).fetchone()
        if worker_row and worker_row['user_id']:
            conn.execute(
                'INSERT INTO notifications (user_id, message) VALUES (?, ?)',
                (worker_row['user_id'], f"You have a new booking request from {user_name}!")
            )

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()

@app.route('/accept_booking/<int:booking_id>', methods=['POST'])
@login_required
def accept_booking(booking_id):
    conn = get_db_connection()
    conn.execute('UPDATE booking_requests SET status = ? WHERE id = ?', ('Accepted', booking_id))
    conn.commit()
    conn.close()
    flash('Booking accepted!', 'success')
    return redirect(url_for('profile'))

@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    conn = get_db_connection()
    conn.execute('UPDATE booking_requests SET status = ? WHERE id = ?', ('Rejected', booking_id))
    conn.commit()
    conn.close()
    flash('Booking rejected.', 'info')
    return redirect(url_for('profile'))


@app.route('/submit_review/<int:worker_id>', methods=['POST'])
@login_required
def submit_review(worker_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user']['id']

    if not rating or not comment:
        flash('Please provide both a rating and a comment.', 'error')
        return redirect(url_for('worker_profile', worker_id=worker_id))

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO reviews (worker_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
            (worker_id, user_id, rating, comment)
        )
        
        # Update worker's rating/count
        conn.execute('''
            UPDATE workers 
            SET rating = (SELECT AVG(rating) FROM reviews WHERE worker_id = ?),
                review_count = (SELECT COUNT(*) FROM reviews WHERE worker_id = ?)
            WHERE id = ?
        ''', (worker_id, worker_id, worker_id))
        
        conn.commit()
        flash('Thank you for your review!', 'success')
    except Exception as e:
        flash(f'Error submitting review: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('worker_profile', worker_id=worker_id))


# ---------------- CHATBOT ROUTE ----------------

@app.route('/chat', methods=['POST'])
def chat_assistant():

    data = request.get_json()

    user_message = data.get("message", "")

    response, action = get_bot_response(user_message)

    return jsonify({
        "response": response,
        "action": action
    })


# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()

        user = conn.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session['user'] = dict(user)

            flash('Successfully logged in!', 'success')

            next_page = request.args.get('next')

            return redirect(next_page or url_for('home'))

        else:

            flash('Invalid email or password', 'error')

    return render_template('login.html')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('user', None)

    flash('Logged out successfully', 'success')

    return redirect(url_for('home'))


# ---------------- CONTEXT PROCESSOR ----------------

@app.context_processor
def inject_now():

    return {'now': datetime.utcnow()}


# ---------------- RUN SERVER ----------------

if __name__ == '__main__':
    app.run(debug=True)