## Project: HackPSU — AI assistant instructions

Purpose
 - Help an AI coding agent become immediately productive in this small Flask-style app.
Project: HackPSU — AI assistant instructions

Purpose
- Quickly onboard an AI coding agent to be productive in this repository. Focus is a small Flask-style app in the `app/` package with templates and static assets.

Top-level layout (what to look at)
- `run.py` — application entry (may be empty in this snapshot). If present, this is the canonical runner used by maintainers.
- `config.py` — runtime and configuration constants (currently empty here; changes to runtime behavior usually go here).
- `app/__init__.py` — app factory, blueprint registration and extension init (expected location for wiring; currently a placeholder).
- `app/extensions.py` — place to find shared extension instances (e.g. db, login_manager).
- `app/models.py` — ORM models and domain objects.
- `app/auth_views.py`, `app/main_views.py` — route handlers / blueprints. Prefer adding new routes in one of these files.
- `app/utils.py` — helpers and small utilities referenced by views or models.
- `app/templates/` — Jinja2 templates: `layout.html`, `login.html`, `dashboard.html`, `stories.html`.
- `app/static/style.css` — site CSS.

Big-picture architecture (how this project is organized)
- Standard Flask app layout: a runnable script (`run.py`) and an `app` package that contains views, models, templates and static files.
- app/ is the primary service boundary. Views (routes) live in `auth_views.py` and `main_views.py`. Shared objects (DB, LoginManager, etc.) should be declared in `extensions.py` and imported where needed to avoid circular imports.

Key patterns and conventions for this repo
- Blueprints / route placement: add or update routes inside `auth_views.py` or `main_views.py`. Register them in `app/__init__.py` (the app factory) rather than importing and running handlers at module import time.
- Shared extensions: instantiate extension objects in `app/extensions.py` and import them (from app.extensions import db) in models and app factory.
- Templates extend `layout.html`. Put shared blocks (nav, footer) in `layout.html` and keep page-specific markup in `dashboard.html`, `stories.html`, etc.
- Static assets live under `app/static/` and are referenced from templates via Flask's `url_for('static', filename='style.css')`.

Integration points to check before changing code
- Database: there's a `models.py` file but no explicit DB configuration in `config.py` or `extensions.py` in this snapshot — inspect those files for SQLAlchemy (or other) usage before adding migrations.
- Auth: `auth_views.py` is present — inspect for login-manager usage when modifying session behavior.
- External services: none were found in the current files. If you plan to add integrations (APIs, OAuth), document settings in `config.py` and keep secrets out of repo.

Developer workflows (assumptions & recommended commands)
- Assumption: maintainers use a simple local Flask pattern. If `run.py` contains the app runner, run the app with `python run.py`.
- Alternative (Flask CLI): set `FLASK_APP=run.py` and run via the Flask CLI. On Windows PowerShell:
  $env:FLASK_APP = 'run.py'; $env:FLASK_ENV = 'development'; python -m flask run
- Tests: none detected. If you add tests, put them under `tests/` and run with `pytest`.

What to avoid
- Do not assume database or migration config exists—verify `config.py` / `extensions.py` before creating or running migrations.
- Avoid changing `app/templates/layout.html` without checking other templates that extend it; current templates are minimal placeholders.

Small actionable tasks for an AI agent
1. Inspect `app/__init__.py` first — confirm app factory and where blueprints are registered. If empty, add a standard factory that imports and registers `auth_views` and `main_views`.
2. If adding a DB model, put extension instances in `app/extensions.py`, reference them in `models.py`, and add configuration keys in `config.py`.
3. When creating routes, keep logic in views and small helpers in `app/utils.py` to keep files focused.

Assumptions & notes (explicit)
- Many files in this snapshot are placeholders (empty). This document is written from the repository structure rather than function bodies. Before implementing behavior, inspect those files — they are the canonical source of truth.
- If any automated workflows (CI, tests) exist, they will be in `.github/workflows/` or listed in README; none were found in this snapshot.

If you want different conventions (naming, linting, tests), tell the maintainers and update this file.

---
Please review this and tell me if you'd like any conventions added (tests, linting, CI, or naming rules). I can iterate.
