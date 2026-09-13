# Plan: Digital Cafe MVP (login, browse, cart, checkout, order history)

Based on `doc/study/0001-digital-cafe-mvp.md` (as revised after review —
merge-on-duplicate-add confirmed, cart edit/remove in scope, empty-cart
message confirmed, no signup page, no product images, `OrderLine.product`
uses `PROTECT`).

Branch: `feat/digital-cafe-mvp`, off `main`.

## 1. Project scaffolding

- [ ] Create venv at `.venv/` using the Python 3.13 binary
      (`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -m venv .venv`).
- [ ] Activate venv, `pip install Django==5.2.17`.
- [ ] `pip freeze > requirements.txt`, confirm it contains `Django==5.2.17`
      plus the resolved `asgiref`/`sqlparse` versions.
- [ ] `django-admin startproject digital_cafe .` (project files at repo
      root, alongside `CLAUDE.md`/`doc/`).
- [ ] `python manage.py startapp cafe`.
- [ ] Add `"cafe"` to `INSTALLED_APPS` in `digital_cafe/settings.py`.
- [ ] Add a `.gitignore` covering `.venv/`, `db.sqlite3`,
      `__pycache__/`, `*.pyc`.
- [ ] Commit: `chore: scaffold Django project and cafe app`.

## 2. Models (`cafe/models.py`)

- [ ] `Product`: `name` (`CharField`), `description`
      (`TextField(blank=True)`), `price`
      (`DecimalField(max_digits=8, decimal_places=2)`), `is_active`
      (`BooleanField(default=True)`), `created_at`
      (`DateTimeField(auto_now_add=True)`).
- [ ] `CartItem`: `user` (`FK(User, on_delete=CASCADE)`), `product`
      (`FK(Product, on_delete=CASCADE)`), `quantity`
      (`PositiveIntegerField`), `added_at`
      (`DateTimeField(auto_now_add=True)`),
      `unique_together = ("user", "product")`. Add a `MinValueValidator(1)`
      on `quantity` so it can't be saved as 0 via a form bypass.
- [ ] `Order`: `user` (`FK(User, on_delete=PROTECT)`), `created_at`
      (`DateTimeField(auto_now_add=True)`). Add a `total()` method
      summing `line.subtotal()` over `self.orderline_set.all()`.
- [ ] `OrderLine`: `order` (`FK(Order, on_delete=CASCADE)`), `product`
      (`FK(Product, on_delete=PROTECT)`), `product_name` (`CharField`),
      `unit_price` (`DecimalField(max_digits=8, decimal_places=2)`),
      `quantity` (`PositiveIntegerField`). Add a `subtotal()` method
      (`unit_price * quantity`).
- [ ] Sensible `__str__` methods on all four models (for admin
      readability).
- [ ] `python manage.py makemigrations cafe`, review the generated
      migration file.
- [ ] `python manage.py migrate`.
- [ ] Commit: `feat: add Product, CartItem, Order, OrderLine models`.

## 3. Django admin (`cafe/admin.py`)

- [ ] Register `Product` with `list_display` for name/price/is_active.
- [ ] Register `CartItem` with `list_display` for user/product/quantity.
- [ ] Register `Order` with `list_display` for user/created_at/total,
      and an inline `TabularInline` for its `OrderLine`s (read-only
      fields, since lines shouldn't be hand-edited after the fact).
- [ ] Register `OrderLine` standalone too (per spec: "manages ...
      order lines via Django admin").
- [ ] Commit: `feat: register cafe models in Django admin`.

## 4. Auth / login gating

- [ ] Configure `LOGIN_URL`, `LOGIN_REDIRECT_URL` in settings (login
      page is the effective landing page; redirect to home after login).
- [ ] Wire up `django.contrib.auth.urls` (`LoginView`, `LogoutView`) in
      the project `urls.py` under `/accounts/`.
- [ ] Create `templates/registration/login.html` (overriding the
      default template) matching the site's base template — username +
      password fields only, no signup link (per confirmed decision: no
      public registration).
- [ ] `python manage.py createsuperuser` locally for testing (not
      committed — just a local dev step) — note in `doc/wiki` setup
      instructions later.
- [ ] Commit: `feat: add login/logout via Django built-in auth views`.

## 5. Base template + home page (product listing)

- [ ] `templates/base.html` — minimal shared layout: nav (Home / Cart /
      Order History / Logout when authenticated), block for page
      content.
- [ ] `cafe/views.py`: `home` view, `@login_required`, lists
      `Product.objects.filter(is_active=True)`, greets
      `request.user.first_name or request.user.username`.
- [ ] `templates/cafe/home.html`: greeting + product grid/list, each
      linking to its detail page.
- [ ] URL: `/` → `home`.
- [ ] Commit: `feat: add home page listing active products`.

## 6. Product detail + add to cart

- [ ] `cafe/forms.py`: `AddToCartForm` with a `quantity`
      `IntegerField(min_value=1, initial=1)`.
- [ ] `product_detail` view, `@login_required`, shows name/description/
      price + the add-to-cart form.
- [ ] `add_to_cart` view, `@login_required`, `POST`-only: validates the
      form, then `get_or_create`s the user's `CartItem` for that product
      and increments `quantity` by the submitted amount if it already
      existed (confirmed merge behavior), rejecting inactive products.
      Redirects back to the product detail page with a confirmation
      message (Django messages framework).
- [ ] URLs: `/products/<int:pk>/`, `/products/<int:pk>/add/`.
- [ ] Templates: `product_detail.html`.
- [ ] Commit: `feat: add product detail page and add-to-cart action`.

## 7. Cart view (edit/remove) + checkout

- [ ] `cart_view`, `@login_required`: lists the user's `CartItem`s with
      per-line subtotal and a running total; shows "your cart is empty"
      with no confirm button when there are no items (confirmed
      behavior).
- [ ] `update_cart_item` view, `@login_required`, `POST`-only: updates a
      single `CartItem`'s quantity (or deletes it if set to 0 /
      "remove" is submitted) — this is the confirmed in-scope
      edit/remove capability.
- [ ] `remove_cart_item` view (or fold into the above as one action) —
      deletes a `CartItem` outright.
- [ ] `checkout` view, `@login_required`, `POST`-only, wrapped in
      `transaction.atomic()`:
  - [ ] Reject with a message if the cart is empty (defensive check even
        though the template won't show a confirm button in that case).
  - [ ] Create `Order(user=request.user)`.
  - [ ] For each `CartItem`, create an `OrderLine` copying
        `product_name=product.name`, `unit_price=product.price`,
        `quantity=cart_item.quantity`.
  - [ ] Delete the user's `CartItem` rows.
  - [ ] Redirect to an order confirmation / order detail page.
- [ ] URLs: `/cart/`, `/cart/<int:item_id>/update/`,
      `/cart/<int:item_id>/remove/`, `/cart/checkout/`.
- [ ] Templates: `cart.html` (with inline quantity-update and remove
      controls per line, and the confirm-checkout form).
- [ ] Commit: `feat: add cart view with edit/remove and checkout flow`.

## 8. Order history

- [ ] `order_history` view, `@login_required`, lists
      `request.user.order_set.all()` ordered by `-created_at`, each
      with its lines and `total()` (computed from stored `unit_price`,
      never current `Product.price`).
- [ ] Optional `order_detail` view for a single past order (nice-to-have
      if `order_history` doesn't already show full line detail inline —
      decide during implementation based on how the list page reads).
- [ ] URL: `/orders/`.
- [ ] Template: `order_history.html`.
- [ ] Commit: `feat: add order history page`.

## 9. Manual verification pass

- [ ] Run the dev server (`python manage.py runserver`), confirm:
  - [ ] Any URL redirects to login when logged out.
  - [ ] Login → home shows greeting + product list.
  - [ ] Product detail → add to cart (including adding the same
        product twice → quantity merges, not duplicates).
  - [ ] Cart page → edit quantity, remove an item, confirm totals
        update correctly.
  - [ ] Checkout → order created with correct timestamp and prices;
        cart is now empty.
  - [ ] Change a product's price in admin after an order exists →
        order history still shows the original price paid.
  - [ ] Order history lists the completed order correctly.
  - [ ] Django admin: superuser can view/edit all four models; deleting
        a `Product` referenced by an `OrderLine` is blocked
        (`PROTECT`), deleting one that was never ordered succeeds.
- [ ] Fix anything broken found during this pass, committing fixes as
      `fix:` commits.

## 10. Rendezvous (step 4 of the CLAUDE.md workflow)

- [ ] Merge `feat/digital-cafe-mvp` into `main`.
- [ ] Re-run the manual verification pass against `main` post-merge.
- [ ] Confirm `main` is left in a working, runnable state.

## 11. Sync docs (step 5 of the CLAUDE.md workflow)

- [ ] Write/update `doc/wiki/` covering: models, URLs/routes, how to
      set up the venv and run the app locally (including creating a
      superuser and at least one regular customer account, since
      there's no signup page), and a description of each customer-facing
      page.
- [ ] Commit: `docs: sync wiki with digital cafe MVP`.