import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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