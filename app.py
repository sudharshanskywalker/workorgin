from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import sqlite3
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
from bot import get_bot_response   # chatbot import

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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