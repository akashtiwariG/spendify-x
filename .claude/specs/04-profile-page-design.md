# Spec: Profile Page Design

## Overview
The profile page allows authenticated users to view and manage their personal information, such as name, email, and password. This step builds upon the authentication system implemented in previous steps (registration and login/logout) to provide a personalized user experience within the Spendly expense tracker. Users can view their current profile details, update their name and email, and change their password through a secure form.

## Depends on
- Step 1: Database setup (01-database-setup.md) - requires the users table to store user credentials.
- Step 2: Registration (02-registration.md) - requires the user registration system to be functional.
- Step 3: Login and Logout (03-login-logout.md) - requires the authentication system (login/logout) to be functional.

## Routes
- GET /profile - displays the user's profile page - requires login
- POST /profile/update-name - handles form submission to update the user's name - requires login
- POST /profile/update-email - handles form submission to update the user's email - requires login
- POST /profile/change-password - handles form submission to change the user's password - requires login

## Database changes
No database changes required. The existing users table already contains the necessary fields:
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- password_hash (TEXT NOT NULL)
- created_at (TEXT DEFAULT CURRENT_TIMESTAMP)

The existing get_user_by_email() function in database/db.py can be used for email uniqueness checks during email updates.

## Templates
- Create: templates/profile.html - new template for the profile page
- Modify: 
  - templates/base.html: Add a profile link in the navigation bar visible only when the user is logged in
  - (Optional) templates/landing.html: May be updated to show personalized content when logged in (not required for this step)

## Files to create
- templates/profile.html

## Files to modify
- app.py: Add route handlers for /profile (GET), /profile/update-name (POST), /profile/update-email (POST), /profile/change-password (POST)
- templates/base.html: Add conditional navigation for profile link
- templates/profile.html: New template file (listed above)

## New dependencies
No new dependencies. The application already uses:
- Flask (for sessions and routing)
- werkzeug.security (for password hashing, already used in registration)
- sqlite3 (standard library, already used in database/db.py)

## Rules for implementation
- No SQLAlchemy or ORMs - use raw SQLite3 queries via the existing database/db.py module.
- Use parameterized queries only; never use string formatting in SQL.
- Passwords must be hashed using `werkzeug.security.generate_password_hash` and checked with `werkzeug.security.check_password_hash`.
- Use CSS variables from static/css/style.css; never hardcode hex values in CSS or templates.
- All templates must extend base.html.
- Validate input on the server side (name, email format, password strength, etc.).
- Prevent duplicate email registration by checking for existing email before updating a user's email.
- Provide clear error messages to the user via the template using Flask's flash messaging system.
- Ensure the user is logged in before accessing profile routes (use the @login_required decorator).
- On successful profile update, show a success message and refresh the profile view.
- On successful password change, show a success message and prompt the user to log in again (or keep them logged in? Typically, changing password invalidates existing sessions, but for simplicity we can keep the session and show a success message).

## Definition of done
A specific testable checklist. Each item must be something that can be verified by running the app:

1. GET /profile displays the profile page correctly when the user is logged in, showing the user's name, email, and forms to update name, email, and change password.
2. GET /profile redirects to the login page when the user is not logged in.
3. POST /profile/update-name validates the name input (not empty) and updates the user's name in the database.
4. POST /profile/update-email validates the email input (valid format, not empty, not already taken by another user) and updates the user's email in the database.
5. POST /profile/change-password validates the current password (correct), new password (not empty, minimum length 8), and confirm new password (matches new password), then updates the password hash in the database.
6. After a successful profile update (name or email), the user sees a success message and the updated information is reflected on the profile page.
7. After a successful password change, the user sees a success message and is prompted to log in again with the new password (or remains logged in with a notification to use the new password next time).
8. Attempting to update email with an already existing email shows an error message.
9. All form submissions display appropriate error messages for invalid input.
10. The navigation bar in base.html shows a "Profile" link when the user is logged in, and hides it when logged out.
11. All existing functionality (registration, login, logout, landing page, terms, privacy) continues to work without errors.
12. Application runs without errors on http://localhost:5001.