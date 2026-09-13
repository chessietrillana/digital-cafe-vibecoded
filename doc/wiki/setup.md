# Setup — running Digital Cafe locally

## Prerequisites

Python 3.13 must be installed. On this machine it's available at
`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13`
alongside the system's default Python; adjust the path below if your
Python 3.13 binary lives elsewhere.

## First-time setup

```bash
# from the repo root
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
```

## Creating accounts

You need at least one superuser, for Django admin (managing products,
and for troubleshooting cart/order/user data):

```bash
python manage.py createsuperuser
```

**Regular customer accounts don't need to be created manually** —
anyone can self-register at `/accounts/signup/` (username, optional
first name, password), which also logs them straight in. That's the
normal path now; only use Django admin's **Authentication and
Authorization → Users → Add user** if you specifically want to create a
customer account yourself (e.g. test data) without going through the
signup form. Either way, set a `First name` if you want the home page's
"Welcome, {name}!" greeting to use a name rather than the username — the
signup form collects this directly; admin-created accounts need it set
manually.

Signup never grants staff/superuser status — that's still
`createsuperuser`/admin-only.

## Adding products

Products aren't seeded automatically. Log into `/admin/` and add some
under **Cafe → Products**. Only products with `is_active` checked show
up on the customer-facing home page.

Product images are optional and uploaded per-product from that same
admin form. Uploaded files are written to `media/products/` (created
automatically on first upload) and served locally via a dev-only route
wired up in `digital_cafe/urls.py`. `media/` is gitignored, same as
`db.sqlite3` — a fresh clone of this repo starts with no product images
until someone uploads them through admin. A product with no image shows
a placeholder on the home and detail pages instead of a broken image.

## Running the app

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — the home page and product detail pages
are visible without logging in. Log in (or sign up) to add items to a
cart and check out, or go to `/admin/` directly with the superuser
account.
