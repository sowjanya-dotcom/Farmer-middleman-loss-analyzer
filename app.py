from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from analyzer import load_csv, analyze_all, CropRecord
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data.db')

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.execute('PRAGMA foreign_keys = ON')
    return db


def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    ''')
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_request
def before_request():
    init_db()


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    db = get_db()
    cur = db.execute('SELECT id, username FROM users WHERE id = ?', (uid,))
    row = cur.fetchone()
    if row:
        return {'id': row[0], 'username': row[1]}
    return None


def login_required(fn):
    def wrapper(*a, **kw):
        if not current_user():
            return redirect(url_for('login'))
        return fn(*a, **kw)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route('/')
def index():
    # Show login page first for new users as requested
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template('register.html', error='Provide username and password')
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already taken')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        if row and check_password_hash(row[1], password):
            session['user_id'] = row[0]
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Use sample CSV for now
    csv_path = os.path.join(BASE_DIR, 'sample_data.csv')
    records = load_csv(csv_path)
    results = analyze_all(records)
    user = current_user()
    return render_template('dashboard.html', user=user, rows=results['rows'], total_loss=results['total_loss'])


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    # Parse manual entries from form arrays. Expect fields like crop[], quantity[], farm_gate_price_per_kg[],
    # market_price_per_kg[], transport_cost_per_kg[], storage_loss_percent[]
    crops = request.form.getlist('crop[]')
    qtys = request.form.getlist('quantity_kg[]')
    farm_prices = request.form.getlist('farm_gate_price_per_kg[]')
    market_prices = request.form.getlist('market_price_per_kg[]')
    transport = request.form.getlist('transport_cost_per_kg[]')
    storage = request.form.getlist('storage_loss_percent[]')

    records = []
    try:
        for i in range(len(crops)):
            # skip empty rows
            if not crops[i].strip():
                continue
            rec = CropRecord(
                crop=crops[i].strip(),
                quantity_kg=float(qtys[i] or 0),
                farm_gate_price_per_kg=float(farm_prices[i] or 0),
                market_price_per_kg=float(market_prices[i] or 0),
                transport_cost_per_kg=float(transport[i] or 0),
                storage_loss_percent=float(storage[i] or 0)
            )
            records.append(rec)
    except Exception as e:
        # On parse error, redirect back with a simple message (could improve)
        return render_template('dashboard.html', user=current_user(), rows=[], total_loss=0.0, error='Invalid input: please check numeric fields')

    if not records:
        # Fallback to sample CSV
        csv_path = os.path.join(BASE_DIR, 'sample_data.csv')
        records = load_csv(csv_path)

    results = analyze_all(records)
    return render_template('dashboard.html', user=current_user(), rows=results['rows'], total_loss=results['total_loss'])


if __name__ == '__main__':
    app.run(debug=True)
