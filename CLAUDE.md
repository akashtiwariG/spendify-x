# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application called "Spendly" - a personal finance tracker. The application allows users to track expenses, understand spending patterns, and manage their financial life.

## Project Structure

```
expense-tracker/
├── app.py                 # Main Flask application with routes
├── requirements.txt       # Python dependencies
├── database/              # Database layer (minimal implementation)
│   ├── db.py              # Database functions
│   └── __init__.py        # Package init
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   │   └── style.css      # Main stylesheet
│   └── js/                # JavaScript files
│       └── main.js        # Main JavaScript
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with common layout
│   ├── landing.html       # Landing page (modified with modal)
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── privacy.html       # Privacy policy
│   └── terms.html         # Terms of service
└── venv/                  # Virtual environment
```

## Development Setup

1. **Create virtual environment** (if not already present):
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   The application will be available at http://localhost:5001

## Available Routes

- `GET /` - Landing page (with "See how it works" modal)
- `GET /register` - User registration page
- `GET /login` - User login page
- `GET /terms` - Terms of service page
- `GET /privacy` - Privacy policy page
- `GET /logout` - Placeholder (returns "Logout — coming in Step 3")
- `GET /profile` - Placeholder (returns "Profile page — coming in Step 4")
- `GET /expenses/add` - Placeholder (returns "Add expense — coming in Step 7")
- `GET /expenses/<int:id>/edit` - Placeholder (returns "Edit expense — coming in Step 8")
- `GET /expenses/<int:id>/delete` - Placeholder (returns "Delete expense — coming in Step 9")

## Template System

The application uses Jinja2 templating with a base template (`base.html`) that defines:
- Common HTML structure
- CSS imports (including Google Fonts)
- Navigation bar
- Content blocks that child templates override

Child templates extend `base.html` and fill in the `{% block content %}` section.

## Static Assets

- CSS: Located in `static/css/style.css` - Contains all styling for the application
- JavaScript: Located in `static/js/main.js` - Contains frontend JavaScript functionality

## Recent Changes

1. **Modal Implementation** (commits 4080fea, 6f0432b):
   - Added a modal to the landing page that opens when clicking "See how it works"
   - Modal contains an embedded YouTube video (placeholder URL updated in commit 6f0432b)
   - Implemented with vanilla JavaScript (no external libraries)
   - Video stops playing when modal is closed by clearing the iframe src
   - Modal can be closed by clicking the × button or clicking outside the modal

## Common Development Tasks

### Running the Application
```bash
# Activate virtual environment (if needed)
# Windows: venv\Scripts\activate
# Unix/MacOS: source venv/bin/activate

# Start the Flask development server
python app.py
```

### Working with Templates
All HTML templates are in the `templates/` directory. They extend `base.html` and override the `content` block.

When modifying templates:
1. Changes to `base.html` affect all pages
2. Child templates only need to define their unique content
3. Template inheritance follows Jinja2 syntax

### Working with Static Assets
- CSS modifications go in `static/css/style.css`
- JavaScript modifications go in `static/js/main.js`
- Remember to hard-refresh browser (Ctrl+F5) when testing CSS/JS changes

### Database Operations
The database layer is in the `database/` directory:
- `database/db.py` contains database functions
- Currently appears to be a minimal implementation that will need expansion

## Code Style & Conventions

- Flask route decorators directly above function definitions
- Template files use Jinja2 syntax with `{% %}` for logic and `{{ }}` for variables
- CSS uses a combination of custom properties and standard selectors
- JavaScript in `main.js` follows vanilla JS patterns without frameworks

## Important Notes

1. The application uses port 5001 by default (configured in `app.py`)
2. Debug mode is enabled in development (`app.run(debug=True)`)
3. When making changes to templates or static files, browser caching may require a hard refresh
4. The modal implementation uses vanilla JavaScript and modifies the iframe src to start/stop video playback
5. All HTML files extend `base.html` for consistent layout and styling

## Future Development Areas

Based on the placeholder routes in `app.py`, future work will likely include:
- User authentication implementation (login/logout)
- Profile management
- Expense tracking functionality (CRUD operations)
- Data visualization/dashboard features