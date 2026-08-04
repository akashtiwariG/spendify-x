import os
import sqlite3

from flask import g, current_app
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    db = getattr(g, '_database', None)
    if db is None:
        # Use the database path from the current app's config, or fall back to the default
        database_path = current_app.config.get('DATABASE', DATABASE)
        db = g._database = sqlite3.connect(database_path)
        db.row_factory = sqlite3.Row
        # Enable foreign key constraints
        db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    db = get_db()
    cursor = db.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    db.commit()

def seed_db():
    """Inserts sample data for development."""
    db = get_db()
    cursor = db.cursor()
    # Check if we already have a user
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count > 0:
        return  # Already seeded
    # Hash the password
    password_hash = generate_password_hash('demo123')
    # Insert demo user
    cursor.execute('''
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    ''', ('Demo User', 'demo@spendly.com', password_hash))
    user_id = cursor.lastrowid
    # Categories as per spec: Food, Transport, Bills, Health, Entertainment, Shopping, Other
    # We need 8 expenses total, at least one per category.
    # We'll create a list of sample expenses.
    sample_expenses = [
        (user_id, 15.50, 'Lunch at cafe', '2026-07-05', 'Food'),          # Food
        (user_id, 8.00, 'Snack', '2026-07-07', 'Other'),                 # Other
        (user_id, 50.00, 'Taxi fare', '2026-07-03', 'Transport'),       # Transport
        (user_id, 30.00, 'Bus pass', '2026-07-15', 'Transport'),        # Transport
        (user_id, 100.00, 'Electricity bill', '2026-07-01', 'Bills'),   # Bills
        (user_id, 20.00, 'Pharmacy', '2026-07-08', 'Health'),           # Health
        (user_id, 25.00, 'Movie ticket', '2026-07-12', 'Entertainment'),# Entertainment
        (user_id, 60.00, 'New shirt', '2026-07-18', 'Shopping'),        # Shopping
    ]
    for expense in sample_expenses:
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, description, date, category)
            VALUES (?, ?, ?, ?, ?)
        ''', expense)
    db.commit()


def get_user_by_email(email):
    """Get a user by email address."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    return cursor.fetchone()


def create_user(name, email, password_hash):
    """Create a new user."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    ''', (name, email, password_hash))
    db.commit()
    return cursor.lastrowid


def get_user_by_id(user_id):
    """Get a user by their ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()


def update_user_name(user_id, name):
    """Update a user's name."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
    db.commit()
    return cursor.rowcount > 0


def update_user_email(user_id, email):
    """Update a user's email, ensuring the new email is unique."""
    db = get_db()
    cursor = db.cursor()
    # First, check if the email is already taken by another user
    cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id))
    if cursor.fetchone() is not None:
        return False  # Email already exists
    # Update the email
    cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
    db.commit()
    return cursor.rowcount > 0


def update_user_password(user_id, password_hash):
    """Update a user's password."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    db.commit()
    return cursor.rowcount > 0


def get_expenses_by_user(user_id, limit=None, offset=None, category=None, start_date=None, end_date=None):
    """Get expenses for a user with optional filtering and pagination."""
    db = get_db()
    cursor = db.cursor()

    # Build query dynamically based on filters
    query = '''
        SELECT id, amount, category, date, description, created_at
        FROM expenses
        WHERE user_id = ?
    '''
    params = [user_id]

    if category:
        query += ' AND category = ?'
        params.append(category)

    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)

    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    query += ' ORDER BY date DESC, created_at DESC'

    if limit is not None:
        query += ' LIMIT ?'
        params.append(limit)
        if offset is not None:
            query += ' OFFSET ?'
            params.append(offset)

    cursor.execute(query, params)
    return cursor.fetchall()


def get_expense_by_id_and_user(expense_id, user_id):
    """Get a specific expense by ID, ensuring it belongs to the user."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, amount, category, date, description, created_at
        FROM expenses
        WHERE id = ? AND user_id = ?
    ''', (expense_id, user_id))
    return cursor.fetchone()


def create_expense(user_id, amount, category, date, description):
    """Create a new expense for a user."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, category, date, description))
    db.commit()
    return cursor.lastrowid


def update_expense(expense_id, user_id, amount, category, date, description):
    """Update an existing expense, ensuring it belongs to the user."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE expenses
        SET amount = ?, category = ?, date = ?, description = ?
        WHERE id = ? AND user_id = ?
    ''', (amount, category, date, description, expense_id, user_id))
    db.commit()
    return cursor.rowcount > 0


def delete_expense(expense_id, user_id):
    """Delete an expense, ensuring it belongs to the user."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
    db.commit()
    return cursor.rowcount > 0


def get_expense_summary(user_id, start_date=None, end_date=None):
    """Get expense summary statistics for a user."""
    db = get_db()
    cursor = db.cursor()

    query = '''
        SELECT
            COUNT(*) as count,
            SUM(amount) as total,
            AVG(amount) as average,
            MIN(amount) as minimum,
            MAX(amount) as maximum
        FROM expenses
        WHERE user_id = ?
    '''
    params = [user_id]

    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)

    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    cursor.execute(query, params)
    result = cursor.fetchone()

    if result:
        return {
            'count': result['count'],
            'total': result['total'] or 0,
            'average': result['average'] or 0,
            'minimum': result['minimum'] or 0,
            'maximum': result['maximum'] or 0
        }
    else:
        return {
            'count': 0,
            'total': 0,
            'average': 0,
            'minimum': 0,
            'maximum': 0
        }


def get_expense_by_category(user_id, start_date=None, end_date=None):
    """Get expenses grouped by category for a user."""
    db = get_db()
    cursor = db.cursor()

    query = '''
        SELECT
            category,
            SUM(amount) as total,
            COUNT(*) as count,
            AVG(amount) as average
        FROM expenses
        WHERE user_id = ?
    '''
    params = [user_id]

    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)

    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    query += ' GROUP BY category ORDER BY total DESC'

    cursor.execute(query, params)
    results = cursor.fetchall()

    # Convert to list of dictionaries
    categories = []
    for row in results:
        categories.append({
            'category': row['category'],
            'total': row['total'],
            'count': row['count'],
            'average': row['average']
        })

    return categories