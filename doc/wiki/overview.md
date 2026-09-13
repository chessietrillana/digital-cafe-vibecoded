# Digital Cafe — Overview

Digital Cafe is a login-gated Django app for a coffee shop. A logged-in
customer browses products, adds them to a cart, checks out into a
permanent order, and can review past orders. A superuser manages the
catalog and order data via Django admin.

There is **no public browsing** — every customer-facing page requires
login, and there is **no public signup page** — customer accounts are
created by a superuser via Django admin (or `createsuperuser`/the admin
"Add user" form).

## Tech stack

- Python 3.13
- Django 5.2.17 (pinned exactly in `requirements.txt`) — the current LTS
  release on the 5.x line
- SQLite (`db.sqlite3`, not committed — see `.gitignore`)
- Server-rendered Django templates, no frontend framework
- Django's built-in `auth.User` model — no custom user model
- venv + `requirements.txt` — no Docker/Poetry

## Project layout

- `digital_cafe/` — the Django project (settings, root `urls.py`).
- `cafe/` — the single app holding all models, views, forms, URLs, and
  admin config for this app's whole feature set (products, cart, orders).
- `templates/` — project-level template root:
  - `templates/base.html` — shared layout (nav, messages).
  - `templates/registration/login.html` — overrides Django's default
    login template.
  - `templates/cafe/` — app-specific page templates.
- `doc/study/`, `doc/plan/` — design history for each feature (see
  `0001-digital-cafe-mvp.md` in each for the reasoning behind the
  current data model and view flow).
