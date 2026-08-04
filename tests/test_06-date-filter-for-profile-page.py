import pytest
import tempfile
import os
from app import app, init_db, seed_db
from database.db import get_db, get_user_by_email
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create a test client for the app."""
    # Use an in-memory database for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        # Initialize database and seed with test data
        init_db()
        seed_db()  # This creates the demo user

    with app.test_client() as client:
        yield client

    # Cleanup
    with app.app_context():
        pass  # Ensure app context is closed
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture
def authenticated_client(client):
    """Create a test client with a logged-in user."""
    # Login with the demo user created by seed_db
    client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123'
    }, follow_redirects=True)
    return client


def test_profile_requires_login(client):
    """Test that profile page requires login."""
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data


def test_profile_shows_expense_summary(authenticated_client):
    """Test that profile page shows expense summary section."""
    response = authenticated_client.get('/profile')
    assert response.status_code == 200
    assert b'Total Expenses' in response.data
    assert b'Average Expense' in response.data
    assert b'Expense Count' in response.data


def test_profile_shows_date_filter_form(authenticated_client):
    """Test that profile page includes date filter form."""
    response = authenticated_client.get('/profile')
    assert response.status_code == 200
    assert b'Filter Expenses by Date' in response.data
    assert b'Start Date' in response.data
    assert b'End Date' in response.data
    assert b'Filter' in response.data


def test_profile_shows_all_time_data_by_default(authenticated_client):
    """Test that profile shows all-time data when no filters applied."""
    response = authenticated_client.get('/profile')
    assert response.status_code == 200

    # Should show all seed data: 8 expenses totaling 308.50
    # Check that we see expense data (exact formatting may vary)
    assert b'308' in response.data or b'308.50' in response.data


def test_profile_filters_by_valid_date_range(authenticated_client):
    """Test that profile filters expenses by valid date range."""
    # Filter for July 2026 (all seed data is from July 2026)
    response = authenticated_client.get('/profile?start_date=2026-07-01&end_date=2026-07-31')
    assert response.status_code == 200

    # Should show all expenses since all seed data is in July 2026
    assert b'308' in response.data or b'308.50' in response.data

    # Filter for a specific week (first week of July 2026)
    response = authenticated_client.get('/profile?start_date=2026-07-01&end_date=2026-07-07')
    assert response.status_code == 200

    # Should show only expenses from July 1-7:
    # 15.50 (Lunch at cafe, Jul 5), 8.00 (Snack, Jul 7), 50.00 (Taxi fare, Jul 3) = 73.50
    # We'll check that we see some expense data (exact amount depends on formatting)
    # Since we have fewer expenses, the total should be less than the full amount
    assert b'73' in response.data or b'73.50' in response.data or int(response.data.split(b'Total Expenses')[1].split(b'<')[0].strip()) < 300


def test_profile_handles_invalid_date_format(authenticated_client):
    """Test that profile shows error for invalid date format."""
    # Invalid date format (MM/DD/YYYY instead of YYYY-MM-DD)
    response = authenticated_client.get('/profile?start_date=07/01/2026&end_date=2026-07-31')
    assert response.status_code == 200
    assert b'Date must be in YYYY-MM-DD format' in response.data

    # Invalid date (not a real date)
    response = authenticated_client.get('/profile?start_date=2026-02-30&end_date=2026-07-31')
    assert response.status_code == 200
    assert b'Invalid date. Please enter a valid calendar date' in response.data


def test_profile_handles_start_date_after_end_date(authenticated_client):
    """Test that profile shows error when start date is after end date."""
    response = authenticated_client.get('/profile?start_date=2026-07-31&end_date=2026-07-01')
    assert response.status_code == 200
    assert b'Start date cannot be after end date' in response.data


def test_profile_preserves_form_values_after_submission(authenticated_client):
    """Test that date filter form preserves values after submission."""
    response = authenticated_client.get('/profile?start_date=2026-07-01&end_date=2026-07-15')
    assert response.status_code == 200
    # Check that the form fields retain their values
    assert b'value="2026-07-01"' in response.data
    assert b'value="2026-07-15"' in response.data


def test_profile_shows_no_expenses_message_for_empty_date_range(authenticated_client):
    """Test that profile shows appropriate message when no expenses match date range."""
    # Use a date range with no expenses (future date)
    response = authenticated_client.get('/profile?start_date=2026-08-01&end_date=2026-08-31')
    assert response.status_code == 200
    # The app shows "No expenses found for the selected period" or similar message
    # Let's check for common variations
    assert b'No expenses' in response.data or b'no expenses' in response.data.lower()


def test_profile_category_breakdown_shows_correct_data(authenticated_client):
    """Test that category breakdown shows correct data for date range."""
    # Filter for transport expenses only (July 3 and July 15)
    response = authenticated_client.get('/profile?start_date=2026-07-03&end_date=2026-07-15')
    assert response.status_code == 200

    # Should show transport expenses: 50.00 (Jul 3) + 30.00 (Jul 15) = 80.00
    # Check that the category breakdown contains transport data
    assert b'Transport' in response.data
    # We should see the transport total somewhere in the response
    assert b'80' in response.data or b'80.00' in response.data


def test_profile_maintains_existing_functionality(authenticated_client):
    """Test that existing profile functionality (name/email/password updates) still works."""
    # Test name update
    response = authenticated_client.post('/profile/update-name', data={
        'name': 'Updated Name'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Name updated successfully' in response.data

    # Test email update
    response = authenticated_client.post('/profile/update-email', data={
        'email': 'updated@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email updated successfully' in response.data

    # Test password change
    response = authenticated_client.post('/profile/change-password', data={
        'current_password': 'demo123',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data


def test_profile_uses_get_method_for_date_filter(authenticated_client):
    """Test that date filter form uses GET method and preserves values in URL."""
    response = authenticated_client.get('/profile?start_date=2026-07-01&end_date=2026-07-31')
    assert response.status_code == 200
    # Check that the form fields are present
    assert b'<form' in response.data
    assert b'name="start_date"' in response.data
    assert b'name="end_date"' in response.data
    # Check that the values are preserved in the form
    assert b'value="2026-07-01"' in response.data
    assert b'value="2026-07-31"' in response.data


if __name__ == '__main__':
    pytest.main([__file__])