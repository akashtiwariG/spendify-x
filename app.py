from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, seed_db, get_user_by_email, create_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # In production, use a secure random key
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour


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
def profile():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for("login"))

    return f"Profile page for {session['user_name']} — coming in Step 4"


@app.route("/expenses/add")
@login_required
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
@login_required
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    return "Delete expense — coming in Step 9"


# Initialize and seed the database before running the app
with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)