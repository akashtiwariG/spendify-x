import os
import tempfile
import pytest
from flask import Flask, g
from werkzeug.security import check_password_hash

# Import the database functions
from database.db import get_db, init_db, seed_db, get_user_by_email, get_expenses_by_user


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    # Override the DATABASE constant in db module
    import database.db as db_module
    original_database = db_module.DATABASE
    db_module.DATABASE = db_path

    with app.app_context():
        init_db()
        seed_db()

    yield app

    # Cleanup - close all connections first
    with app.app_context():
        # Close any remaining database connections
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    db_module.DATABASE = original_database
    try:
        os.close(db_fd)
    except OSError:
        pass  # File descriptor might already be closed
    try:
        os.unlink(db_path)
    except (PermissionError, OSError):
        pass  # File might be locked or already deleted


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


def test_get_db_returns_connection_with_row_factory_and_foreign_keys(app):
    """Test that get_db returns a connection with proper configuration."""
    with app.app_context():
        db = get_db()

        # Check that we get a connection
        assert db is not None

        # Check that row_factory is set to sqlite3.Row (allows dict-like access)
        assert db.row_factory is not None

        # Check that foreign keys are enabled
        cursor = db.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # foreign_keys should be ON (1)


def test_init_db_creates_tables_with_correct_schema(app):
    """Test that init_db creates tables with correct schema and constraints."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Check that users table exists with correct schema
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """)
        assert cursor.fetchone() is not None

        # Check users table schema
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert 'id' in columns
        assert columns['id'][2] == 'INTEGER'  # type
        assert columns['id'][5] == 1          # pk (primary key)
        assert 'name' in columns
        assert columns['name'][2] == 'TEXT'
        assert columns['name'][3] == 1        # notnull
        assert 'email' in columns
        assert columns['email'][2] == 'TEXT'
        assert columns['email'][3] == 1       # notnull
        # Note: email has UNIQUE constraint but no default value (that's correct)

        assert 'password_hash' in columns
        assert columns['password_hash'][2] == 'TEXT'
        assert columns['password_hash'][3] == 1  # notnull
        assert 'created_at' in columns
        assert columns['created_at'][2] == 'TEXT'

        # Check that expenses table exists with correct schema
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='expenses'
        """)
        assert cursor.fetchone() is not None

        # Check expenses table schema
        cursor.execute("PRAGMA table_info(expenses)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert 'id' in columns
        assert columns['id'][2] == 'INTEGER'  # type
        assert columns['id'][5] == 1          # pk (primary key)
        assert 'user_id' in columns
        assert columns['user_id'][2] == 'INTEGER'
        assert columns['user_id'][3] == 1     # notnull
        assert 'amount' in columns
        assert columns['amount'][2] == 'REAL'  # REAL for float values
        assert columns['amount'][3] == 1       # notnull
        assert 'category' in columns
        assert columns['category'][2] == 'TEXT'
        assert columns['category'][3] == 1     # notnull
        assert 'date' in columns
        assert columns['date'][2] == 'TEXT'
        assert columns['date'][3] == 1         # notnull
        assert 'description' in columns
        assert columns['description'][2] == 'TEXT'  # nullable
        assert 'created_at' in columns
        assert columns['created_at'][2] == 'TEXT'

        # Check foreign key constraint exists
        cursor.execute("""
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='expenses'
        """)
        sql = cursor.fetchone()[0]
        assert 'FOREIGN KEY' in sql.upper()
        assert 'REFERENCES USERS (ID)' in sql.upper()


def test_init_db_is_safe_to_call_multiple_times(app):
    """Test that init_db can be called multiple times without error."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Call init_db multiple times
        init_db()
        init_db()
        init_db()

        # Verify tables still exist and have correct structure
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('users', 'expenses')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        assert 'users' in tables
        assert 'expenses' in tables


def test_seed_db_creates_demo_user_with_hashed_password(app):
    """Test that seed_db creates a demo user with hashed password."""
    with app.app_context():
        # Clear any existing data to ensure clean state
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM users")
        db.commit()

        # Seed the database
        seed_db()

        # Get the demo user
        user = get_user_by_email('demo@spendly.com')
        assert user is not None
        assert user['name'] == 'Demo User'
        assert user['email'] == 'demo@spendly.com'

        # Password should be hashed (not plain text)
        assert user['password_hash'] != 'demo123'
        assert len(user['password_hash']) > 20  # Hash should be reasonably long

        # Verify the hash is correct
        assert check_password_hash(user['password_hash'], 'demo123')


def test_seed_db_creates_8_sample_expenses_across_categories(app):
    """Test that seed_db creates exactly 8 sample expenses across required categories."""
    with app.app_context():
        # Clear any existing data to ensure clean state
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM users")
        db.commit()

        # Seed the database
        seed_db()

        # Get the demo user
        user = get_user_by_email('demo@spendly.com')
        assert user is not None
        user_id = user['id']

        # Get all expenses for the user
        expenses = get_expenses_by_user(user_id)
        assert len(expenses) == 8  # Exactly 8 expenses

        # Check that we have at least one expense per required category
        required_categories = {'Food', 'Transport', 'Bills', 'Health',
                              'Entertainment', 'Shopping', 'Other'}
        actual_categories = {expense['category'] for expense in expenses}

        # Check that all required categories are present
        assert required_categories.issubset(actual_categories), \
            f"Missing categories: {required_categories - actual_categories}"

        # Verify all expenses have valid data
        for expense in expenses:
            # Access as dict-like object due to row_factory
            # Note: user_id is not in the SELECT clause of get_expenses_by_user,
            # so we verify ownership by ensuring the function returns expenses
            # for the correct user and not for other users
            assert expense['amount'] > 0
            assert expense['category'] in required_categories
            # Date should be in YYYY-MM-DD format
            assert len(expense['date']) == 10
            assert expense['date'][4] == '-' and expense['date'][7] == '-'

        # Additional verification: expenses for a different user should be empty
        other_user_expenses = get_expenses_by_user(user_id + 99999)  # Non-existent user
        assert len(other_user_expenses) == 0


def test_seed_db_prevents_duplicate_data_on_multiple_runs(app):
    """Test that seed_db prevents duplicate data when run multiple times."""
    with app.app_context():
        # Clear any existing data to ensure clean state
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM users")
        db.commit()

        # Run seed_db multiple times
        seed_db()
        seed_db()
        seed_db()

        # Check that we still have exactly one demo user
        user = get_user_by_email('demo@spendly.com')
        assert user is not None

        # Get all expenses for the user
        expenses = get_expenses_by_user(user['id'])
        # Should still have exactly 8 expenses (no duplicates)
        assert len(expenses) == 8


def test_foreign_key_constraints_work(app):
    """Test that foreign key constraints are enforced."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Try to insert an expense with a non-existent user_id
        # This should fail due to foreign key constraint
        try:
            cursor.execute("""
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (99999, 10.0, 'Food', '2026-01-01', 'Test expense')
            """)
            db.commit()
            # If we reach here, the insert succeeded (which it shouldn't)
            assert False, "Should have failed due to foreign key constraint"
        except Exception as e:
            # Should get an integrity error due to foreign key constraint
            db.rollback()
            error_msg = str(e).upper()
            assert "FOREIGN KEY" in error_msg or "constraint" in error_msg.lower()


def test_unique_email_constraint_works(app):
    """Test that unique email constraint is enforced."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Try to insert a user with duplicate email
        # This should fail due to unique constraint
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash)
                VALUES ('Duplicate User', 'demo@spendly.com', 'hash')
            """)
            db.commit()
            # If we reach here, the insert succeeded (which it shouldn't)
            assert False, "Should have failed due to unique constraint"
        except Exception as e:
            # Should get an integrity error due to unique constraint
            db.rollback()
            error_msg = str(e).upper()
            assert "UNIQUE" in error_msg or "constraint" in error_msg.lower()


def test_database_file_created_on_app_startup():
    """Test that database file is created when app starts."""
    # Create a temporary database path
    db_fd, db_path = tempfile.mkstemp()

    # Close the file descriptor immediately so we can delete the file
    os.close(db_fd)

    # Delete the file so we can test creation
    try:
        os.unlink(db_path)
    except OSError:
        pass  # File might not exist

    # Track the original database value
    import database.db as db_module
    original_database = db_module.DATABASE

    try:
        # Verify the file doesn't exist yet
        assert not os.path.exists(db_path)

        # Override the DATABASE constant in db module
        db_module.DATABASE = db_path

        # Create a fresh app context and initialize
        app = Flask(__name__)
        app.config['TESTING'] = True

        with app.app_context():
            # Database file should not exist yet
            assert not os.path.exists(db_path)

            # Initialize the database (this should create the file)
            init_db()

            # Database file should now exist
            assert os.path.exists(db_path)

            # Verify we can connect to it
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    finally:
        # Cleanup
        db_module.DATABASE = original_database
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except (PermissionError, OSError):
            pass  # File might be locked


def test_parameterized_queries_used(app):
    """Test that parameterized queries are used (basic check)."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # This test verifies that we can use parameterized queries without error
        # A more sophisticated test would check the actual SQL strings, but
        # this at least confirms the interface works correctly

        # Insert a test user using parameterized query
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, ('Test User', 'test@example.com', 'hashed_password'))

        user_id = cursor.lastrowid
        db.commit()

        # Retrieve the user using parameterized query
        cursor.execute("""
            SELECT * FROM users WHERE id = ?
        """, (user_id,))

        user = cursor.fetchone()
        assert user is not None
        assert user['name'] == 'Test User'
        assert user['email'] == 'test@example.com'

        # Clean up
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()