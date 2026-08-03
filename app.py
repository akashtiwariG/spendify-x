from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id, update_user_name, update_user_email, update_user_password
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
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))
    return render_template("profile.html", user=user)


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