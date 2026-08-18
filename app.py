import os
import re

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id, update_user_name, update_user_email, update_user_password, get_expenses_by_user, get_expense_by_id_and_user, create_expense, update_expense, delete_expense, get_expense_summary, get_expense_by_category


def validate_date(date_str):
    """Validate a date string in YYYY-MM-DD format.

    Args:
        date_str (str): Date string to validate

    Returns:
        tuple: (is_valid, error_message) where is_valid is boolean and
               error_message is None if valid, otherwise contains error message
    """
    if not date_str:
        return True, None

    # Check format first
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_str):
        return False, "Date must be in YYYY-MM-DD format."

    # Check if it's a valid calendar date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Invalid date. Please enter a valid calendar date."


app = Flask(__name__)
# SECRET_KEY: required for sessions. Read from env on deploy; fall back to a
# development default so local `python app.py` still works without setup.
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
# DATABASE: allow the deploy target (Railway / Docker / tests) to point the
# SQLite file at a writable path via the DATABASE_PATH env var. Defaults to
# the local file in the project root for `python app.py` development use.
app.config['DATABASE'] = os.environ.get(
    'DATABASE_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spendly.db'),
)


def is_authenticated():
    """Check if user is logged in"""
    return 'user_id' in session


def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # If user is already logged in, redirect to profile
    if is_authenticated():
        return redirect(url_for("profile"))

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input
        if not name:
            flash("Name is required.", "error")
            return render_template("register.html")
        elif not email:
            flash("Email is required.", "error")
            return render_template("register.html")
        elif not password:
            flash("Password is required.", "error")
            return render_template("register.html")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html")
        elif get_user_by_email(email):
            flash("Email already registered.", "error")
            return render_template("register.html")

        # If validation passed, create the user
        password_hash = generate_password_hash(password)
        user_id = create_user(name, email, password_hash)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    # GET request: show the form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in, redirect to profile
    if is_authenticated():
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        # Validate input
        if not email:
            flash("Email is required.", "error")
            return render_template("login.html")

        if not password:
            flash("Password is required.", "error")
            return render_template("login.html")

        # Get user by email
        user = get_user_by_email(email)
        if not user:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # Check password
        if not check_password_hash(user['password_hash'], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # Login successful
        # Regenerate session ID to prevent session fixation
        session.clear()
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']

        # Handle "remember me"
        if remember:
            session.permanent = True
        else:
            session.permanent = False

        flash("Successfully logged in!", "success")
        return redirect(url_for("profile"))

    # GET request: show the form
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


@app.route("/logout")
def logout():
    # Clear session data
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))

    # Get date filter parameters
    form_start_date = request.args.get('start_date', '')
    form_end_date = request.args.get('end_date', '')

    # Validate date format and logic
    error_message = None
    start_date_valid = True
    end_date_valid = True

    if form_start_date:
        is_valid_start, start_date_error = validate_date(form_start_date)
        if not is_valid_start:
            start_date_valid = False
            if not error_message:  # Only set error message if not already set
                error_message = start_date_error

    if form_end_date:
        is_valid_end, end_date_error = validate_date(form_end_date)
        if not is_valid_end:
            end_date_valid = False
            if not error_message:  # Only set error message if not already set
                error_message = end_date_error

    # If both dates are valid, check that start_date is not after end_date
    if start_date_valid and end_date_valid:
        if form_start_date and form_end_date and form_start_date > form_end_date:
            error_message = "Start date cannot be after end date."

    # For database queries, use the form values only if they are valid
    query_start_date = form_start_date if start_date_valid and form_start_date else None
    query_end_date = form_end_date if end_date_valid and form_end_date else None

    # Get expense summary data
    summary_data = get_expense_summary(
        session['user_id'],
        start_date=query_start_date,
        end_date=query_end_date
    )

    # Get category breakdown data
    categories_data = get_expense_by_category(
        session['user_id'],
        start_date=query_start_date,
        end_date=query_end_date
    )

    return render_template("profile.html",
                         user=user,
                         start_date=form_start_date,
                         end_date=form_end_date,
                         total_expenses=summary_data['total'],
                         average_expense=summary_data['average'],
                         expenses_count=summary_data['count'],
                         categories=categories_data,
                         error_message=error_message)


@app.route("/profile/update-name", methods=["POST"])
@login_required
def update_name():
    name = request.form.get("name")
    if not name or not name.strip():
        flash("Name is required.", "error")
        return redirect(url_for("profile"))
    name = name.strip()
    if update_user_name(session['user_id'], name):
        flash("Name updated successfully.", "success")
    else:
        flash("Failed to update name.", "error")
    return redirect(url_for("profile"))

@app.route("/profile/update-email", methods=["POST"])
@login_required
def update_email():
    email = request.form.get("email")
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("profile"))
    email = email.strip()
    if "@" not in email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("profile"))
    if update_user_email(session['user_id'], email):
        flash("Email updated successfully.", "success")
    else:
        flash("Failed to update email. The email may already be in use.", "error")
    return redirect(url_for("profile"))

@app.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "error")
        return redirect(url_for("profile"))
    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for("profile"))
    if len(new_password) < 8:
        flash("New password must be at least 8 characters long.", "error")
        return redirect(url_for("profile"))
    user = get_user_by_id(session['user_id'])
    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))
    if not check_password_hash(user['password_hash'], current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("login"))
    new_hash = generate_password_hash(new_password)
    if update_user_password(session['user_id'], new_hash):
        flash("Password updated successfully.", "success")
    else:
        flash("Failed to update password.", "error")
    return redirect(url_for("profile"))


@app.route("/analytics")
@login_required
def analytics():
    """Analytics Coming Soon page (placeholder)."""
    return render_template("analytics.html")


@app.route("/expenses")
@login_required
def expenses_index():
    """Display a list of expenses with filtering and pagination."""
    # Get query parameters for filtering
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Calculate offset for pagination
    offset = (page - 1) * per_page

    # Get expenses with filters
    expenses = get_expenses_by_user(
        session['user_id'],
        limit=per_page,
        offset=offset,
        category=category if category else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    # Get total count for pagination (without limit/offset)
    all_expenses = get_expenses_by_user(
        session['user_id'],
        category=category if category else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )
    total_count = len(all_expenses)
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    return render_template("expenses/index.html",
                         expenses=expenses,
                         current_page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page,
                         category=category,
                         start_date=start_date,
                         end_date=end_date)


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    """Handle adding a new expense."""
    if request.method == "GET":
        return render_template("expenses/add.html")

    # POST request - process form submission
    amount = request.form.get("amount")
    category = request.form.get("category")
    date = request.form.get("date")
    description = request.form.get("description", "")

    # Validate input
    error = None
    if not amount:
        error = "Amount is required."
    elif not category:
        error = "Category is required."
    elif not date:
        error = "Date is required."
    else:
        is_valid_date, date_error = validate_date(date)
        if not is_valid_date:
            error = date_error

    if error is not None:
        flash(error, "error")
        return render_template("expenses/add.html")

    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        flash("Amount must be a positive number.", "error")
        return render_template("expenses/add.html")

    # Create the expense
    expense_id = create_expense(
        session['user_id'],
        amount_float,
        category,
        date,
        description
    )

    flash("Expense added successfully!", "success")
    return redirect(url_for('expenses_index'))


@app.route("/expenses/<int:id>")
@login_required
def expense_detail(id):
    """Display details of a specific expense."""
    expense = get_expense_by_id_and_user(id, session['user_id'])
    if expense is None:
        flash("Expense not found.", "error")
        return redirect(url_for('expenses_index'))

    return render_template("expenses/detail.html", expense=expense)


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    """Handle editing an existing expense."""
    # First check if the expense exists and belongs to the user
    expense = get_expense_by_id_and_user(id, session['user_id'])
    if expense is None:
        flash("Expense not found.", "error")
        return redirect(url_for('expenses_index'))

    if request.method == "GET":
        return render_template("expenses/edit.html", expense=expense)

    # POST request - process form submission
    amount = request.form.get("amount")
    category = request.form.get("category")
    date = request.form.get("date")
    description = request.form.get("description", "")

    # Validate input
    error = None
    if not amount:
        error = "Amount is required."
    elif not category:
        error = "Category is required."
    elif not date:
        error = "Date is required."

    if error is not None:
        flash(error, "error")
        return render_template("expenses/edit.html", expense=expense)

    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        flash("Amount must be a positive number.", "error")
        return render_template("expenses/edit.html", expense=expense)

    # Update the expense
    if update_expense(id, session['user_id'], amount_float, category, date, description):
        flash("Expense updated successfully!", "success")
        return redirect(url_for('expense_detail', id=id))
    else:
        flash("Failed to update expense.", "error")
        return render_template("expenses/edit.html", expense=expense)


@app.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    """Handle deleting an expense."""
    # First check if the expense exists and belongs to the user
    expense = get_expense_by_id_and_user(id, session['user_id'])
    if expense is None:
        flash("Expense not found.", "error")
        return redirect(url_for('expenses_index'))

    # Delete the expense
    if delete_expense(id, session['user_id']):
        flash("Expense deleted successfully.", "success")
    else:
        flash("Failed to delete expense.", "error")

    return redirect(url_for('expenses_index'))


# Summary Statistics Routes
@app.route("/expenses/summary")
@login_required
def expenses_summary():
    """Get summary statistics for expenses."""
    # Get date range parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Get summary data
    summary = get_expense_summary(
        session['user_id'],
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    # Return as JSON for API consumption
    return jsonify(summary)


@app.route("/expenses/summary/daily")
@login_required
def expenses_summary_daily():
    """Get daily spending trends."""
    # For simplicity, we'll return last 30 days of daily totals
    # In a more advanced implementation, this could accept date range parameters
    summary = get_expense_summary(
        session['user_id']
        # Could add date range parameters here too
    )

    # For now, return basic summary - in a full implementation,
    # we'd have a separate function for daily trends
    return jsonify({
        'period': 'daily',
        'data': summary  # This would be enhanced with actual daily data
    })


@app.route("/expenses/summary/weekly")
@login_required
def expenses_summary_weekly():
    """Get weekly spending trends."""
    summary = get_expense_summary(
        session['user_id']
    )

    return jsonify({
        'period': 'weekly',
        'data': summary  # This would be enhanced with actual weekly data
    })


@app.route("/expenses/summary/monthly")
@login_required
def expenses_summary_monthly():
    """Get monthly spending trends."""
    summary = get_expense_summary(
        session['user_id']
    )

    return jsonify({
        'period': 'monthly',
        'data': summary  # This would be enhanced with actual monthly data
    })


# Category Breakdown Routes
@app.route("/expenses/categories")
@login_required
def expenses_categories():
    """Get spending breakdown by category."""
    # Get date range parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Get category breakdown data
    categories = get_expense_by_category(
        session['user_id'],
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    # Return as JSON for API consumption
    return jsonify({'categories': categories})


@app.route("/expenses/categories/trends")
@login_required
def expenses_categories_trends():
    """Get category spending trends over time."""
    # For now, return current category breakdown
    # In a full implementation, this would show trends over time
    categories = get_expense_by_category(
        session['user_id']
    )

    return jsonify({
        'trends': [
            {
                'category': cat['category'],
                'amount': cat['total'],
                'period': 'current'  # Would be enhanced with time series data
            }
            for cat in categories
        ]
    })


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, '_database'):
        g._database.close()


# Initialise the database schema. `seed_db()` is gated on the SEED_DB env var
# so that restarts on Railway don't wipe user data; flip it on once if you
# need to (re)create the demo user + sample expenses.
with app.app_context():
    init_db()
    if os.environ.get('SEED_DB', '').lower() in ('1', 'true', 'yes'):
        seed_db()


if __name__ == "__main__":
    # Local dev: debug on, port 5001. On Railway/Gunicorn, this block is
    # skipped — `gunicorn app:app` runs the WSGI app directly.
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    port = int(os.environ.get('PORT', '5001'))
    app.run(host='0.0.0.0', debug=debug, port=port)