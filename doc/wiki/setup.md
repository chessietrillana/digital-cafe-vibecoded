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

There is no public signup page. You need at least:

1. **A superuser**, for Django admin (managing products, and for
   troubleshooting cart/order data):

   ```bash
   python manage.py createsuperuser
   ```

2. **At least one regular customer account**, since customers can't
   self-register. Easiest way: log into `/admin/` as the superuser above,
   go to **Authentication and Authorization → Users → Add user**, and
   create a plain (non-staff, non-superuser) user. Set a `First name` if
   you want the home page's "Welcome, {name}!" greeting to use a name
   rather than the username.

## Adding products

Products aren't seeded automatically. Log into `/admin/` and add some
under **Cafe → Products**. Only products with `is_active` checked show
up on the customer-facing home page.

## Running the app

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — you'll be redirected to
`/accounts/login/` immediately, since there's no public browsing before
login. Log in with a customer account to see the storefront, or go to
`/admin/` directly with the superuser account.
