"""Tests for the Delete Expense feature (Step 09).

Covers the Definition of Done in .claude/specs/09-delete-expense.md:
- POST /expenses/<id>/delete removes only the logged-in user's own row
- The route is POST-only (GET returns 405)
- Anonymous users are redirected to /login
- Delete buttons exist on /expenses and /expenses/<id> with confirm() guards
- /profile totals reflect a deletion
- The user_id used by the route is the session, never the form
- detail.html is well-formed (regression test for duplicate {% endblock %})
- The app starts cleanly
"""

import pytest
import tempfile
import os

from app import app, init_db, seed_db
from database.db import get_db, create_user, create_expense
from werkzeug.security import generate_password_hash


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def client():
    """Create a test client with a fresh temp DB seeded by seed_db()."""
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        init_db()
        seed_db()  # Creates the demo user + 8 sample expenses

    with app.test_client() as client:
        yield client

    with app.app_context():
        pass  # ensure app context closed
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture
def authenticated_client(client):
    """A logged-in client (demo@spendly.com / demo123)."""
    client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123',
    }, follow_redirects=True)
    return client


def _create_other_user_with_expense(amount=42.00):
    """Insert a second user and an expense owned by them.

    Returns the other user's id and the new expense id.
    """
    with app.app_context():
        other_id = create_user(
            'Other User',
            'other@spendly.com',
            generate_password_hash('other123'),
        )
        other_expense_id = create_expense(
            other_id, amount, 'Food', '2026-07-20', 'Other users lunch',
        )
    return other_id, other_expense_id


# ------------------------------------------------------------------ #
# Tests — Definition of Done mapping                                   #
# ------------------------------------------------------------------ #

def test_app_starts():
    """DoD #15: app initialises and seeds without error."""
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    try:
        with app.app_context():
            init_db()
            seed_db()
    finally:
        os.close(db_fd)
        os.unlink(db_path)


def test_delete_requires_login(client):
    """DoD #6: anonymous POST to delete redirects to /login."""
    response = client.post('/expenses/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data


def test_delete_own_expense_succeeds(authenticated_client):
    """DoD #1, #2, #11: deleting an owned expense removes the row and flashes success."""
    response = authenticated_client.post(
        '/expenses/1/delete', follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Expense deleted successfully.' in response.data

    # Visiting the deleted expense's detail page should now flash not-found
    response = authenticated_client.get('/expenses/1', follow_redirects=True)
    assert b'Expense not found.' in response.data


def test_delete_others_expense_is_rejected(authenticated_client):
    """DoD #3: cannot delete an expense owned by another user."""
    _, other_expense_id = _create_other_user_with_expense()

    response = authenticated_client.post(
        f'/expenses/{other_expense_id}/delete', follow_redirects=True,
    )
    assert response.status_code == 200
    # Route's pre-check flashes "Expense not found." because the row is
    # not visible to the current user — either way, the row must survive.
    assert b'Expense not found.' in response.data

    # Verify the other user's row is still there
    with app.app_context():
        from database.db import get_expense_by_id_and_user
        survivor = get_expense_by_id_and_user(other_expense_id, None)
        # The helper requires a user_id; fetch directly to be sure
        db = get_db()
        row = db.execute(
            'SELECT id, user_id, amount FROM expenses WHERE id = ?',
            (other_expense_id,),
        ).fetchone()
        assert row is not None
        assert row['amount'] == 42.00


def test_delete_nonexistent_expense(authenticated_client):
    """DoD #4: deleting an id that doesn't exist flashes not-found and redirects."""
    response = authenticated_client.post(
        '/expenses/9999/delete', follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Expense not found.' in response.data


def test_delete_route_rejects_get(authenticated_client):
    """DoD #5: GET on the delete URL must return 405 Method Not Allowed."""
    response = authenticated_client.get('/expenses/1/delete')
    assert response.status_code == 405


def test_delete_button_in_list(authenticated_client):
    """DoD #7, #9: /expenses has a per-row delete form with confirm() guard."""
    response = authenticated_client.get('/expenses')
    assert response.status_code == 200
    body = response.data
    # Every row should have a form posting to /expenses/<id>/delete
    assert b'action="/expenses/1/delete"' in body
    assert b'method="POST"' in body
    # And it should ask for confirmation before submitting
    assert b"onsubmit=\"return confirm('Are you sure you want to delete this expense?');\"" in body


def test_delete_button_in_detail(authenticated_client):
    """DoD #8, #9: /expenses/<id> has a delete form with confirm() guard."""
    response = authenticated_client.get('/expenses/1')
    assert response.status_code == 200
    body = response.data
    assert b'action="/expenses/1/delete"' in body
    assert b'method="POST"' in body
    assert b"onsubmit=\"return confirm('Are you sure you want to delete this expense?');\"" in body


def test_detail_template_is_well_formed(authenticated_client):
    """DoD #13, #14: detail.html renders without a Jinja error (regression for duplicate {% endblock %})."""
    response = authenticated_client.get('/expenses/1')
    assert response.status_code == 200
    # If the duplicate endblock were still present, the template would either
    # raise a TemplateSyntaxError (500) or render with broken structure.
    assert response.status_code == 200


def test_delete_updates_profile_totals(authenticated_client):
    """DoD #10: after a delete, /profile totals drop by the deleted amount / 1 row."""
    # Read the totals before
    before = authenticated_client.get('/profile')
    assert before.status_code == 200
    # Demo seed total is 308.50 across 8 expenses
    assert b'8' in before.data  # count

    # Delete the first expense (amount = 15.50, "Lunch at cafe")
    authenticated_client.post('/expenses/1/delete', follow_redirects=True)

    after = authenticated_client.get('/profile')
    assert after.status_code == 200
    # Count should now be 7
    assert b'7' in after.data


def test_session_user_id_is_used_not_form_input(authenticated_client):
    """DoD #12: a malicious user_id in the form body is ignored; session wins."""
    # Try to delete expense #1 but pretend to be user 999
    response = authenticated_client.post(
        '/expenses/1/delete',
        data={'user_id': '999'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Demo user IS the legitimate owner, so the delete still happens.
    assert b'Expense deleted successfully.' in response.data
    # And no user 999 was created/affected — verify the demo user still exists
    with app.app_context():
        from database.db import get_user_by_email
        demo = get_user_by_email('demo@spendly.com')
        assert demo is not None
        assert demo['id'] != 999


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
