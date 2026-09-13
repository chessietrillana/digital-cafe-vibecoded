# Plan: Public Browsing (No Login Required to Browse)

Based on `doc/study/0003-public-browsing.md` (as resolved after review —
`home`/`product_detail` become public, everything else stays
login-required, nav becomes conditional per-link, add-to-cart form
hidden for anonymous visitors, no home-page CTA banner, no flash
message on redirect-to-login).

Branch: `feat/public-browsing`, off `main`.

## 1. Views: drop `@login_required` where it no longer applies

- [ ] `cafe/views.py`: remove `@login_required` from `home`.
- [ ] Fix the greeting bug identified in the study doc (§3): branch on
      `request.user.is_authenticated` in `home`, passing
      `greeting_name` only when authenticated (or restructure the
      context so the template handles both cases without ever touching
      `request.user.first_name` on an anonymous user).
- [ ] `cafe/views.py`: remove `@login_required` from `product_detail`.
- [ ] Leave `add_to_cart`, `cart_view`, `update_cart_item`, `checkout`,
      `order_history` untouched — still `@login_required`.
- [ ] Commit: `feat: make home and product detail pages public`.

## 2. Home page template: anonymous vs. authenticated greeting

- [ ] `templates/cafe/home.html`: conditional heading —
      `"Welcome, {{ greeting_name }}!"` when authenticated,
      `"Welcome to Digital Cafe"` (generic) when not. No other content
      differences — the product grid is identical either way, per the
      study doc.
- [ ] Commit: `feat: show a generic heading on the home page when logged out`.

## 3. Product detail template: hide add-to-cart form when anonymous

- [ ] `templates/cafe/product_detail.html`: wrap the existing
      `is_active` conditional in an outer
      `{% if user.is_authenticated %}` / `{% else %}` — authenticated +
      active → real form (unchanged); authenticated + inactive →
      existing "currently unavailable" message (unchanged); anonymous
      (regardless of `is_active`) → a link reading "Log in to add this
      to your cart" pointing to
      `{% url 'login' %}?next={{ request.path|urlencode }}`.
- [ ] Commit: `feat: prompt anonymous visitors to log in instead of showing the add-to-cart form`.

## 4. Nav: per-link conditionals + a "Log in" link

- [ ] `templates/base.html`: restructure the nav block so:
  - "Home" renders unconditionally.
  - "Cart" and "Order History" render only when
    `user.is_authenticated`.
  - A new "Log in" link (`{% url 'login' %}`) renders only when
    **not** authenticated.
  - The "Log out" form stays authenticated-only, as now.
- [ ] Commit: `feat: show a conditional nav for logged-out visitors`.

## 5. Manual verification pass

- [ ] Run the dev server, confirm, **logged out**:
  - [ ] `/` loads without redirecting to login, shows the generic
        heading and the full product grid.
  - [ ] Nav shows "Home" and "Log in" only — no "Cart"/"Order
        History"/"Log out".
  - [ ] `/products/<id>/` for an active product loads without
        redirecting, shows name/description/price and a "Log in to add
        this to your cart" link (no quantity form).
  - [ ] Clicking that link lands on the login page with `?next=` set to
        that same product's URL; logging in redirects back to that
        exact product page (not home, not the add-to-cart URL).
  - [ ] `/products/<id>/` for an inactive product still shows "This
        product is currently unavailable" (unchanged from before,
        confirming study doc §8.2).
  - [ ] `GET /cart/` redirects to login with `?next=/cart/`; logging in
        lands back on `/cart/`.
  - [ ] `GET /orders/` redirects to login with `?next=/orders/`; same
        pattern.
  - [ ] A direct `POST` to `/products/<id>/add/` while logged out
        redirects to login (no server error, no silent cart mutation).
- [ ] Confirm, **logged in** (regression check — nothing here should
      have changed):
  - [ ] `/` shows the personalized `"Welcome, {name}!"` greeting.
  - [ ] Nav shows "Home", "Cart", "Order History", "Log out" — no "Log
        in".
  - [ ] `/products/<id>/` shows the real add-to-cart form and it still
        works (add, merge-on-duplicate).
  - [ ] Full cart → checkout → order history flow still works
        end-to-end (re-run the same spot checks as the MVP's original
        verification pass, not the full 32-check suite, since none of
        that logic changed).
- [ ] Fix anything broken found during this pass, committing fixes as
      `fix:` commits.

## 6. Rendezvous

- [ ] Merge `feat/public-browsing` into `main`.
- [ ] Re-run the key logged-out and logged-in checks from step 5
      against `main` post-merge.
- [ ] Confirm `main` is left in a working, runnable state.

## 7. Sync docs

- [ ] Update `doc/wiki/routes.md`: mark `home` and `product_detail` as
      public in the route table (currently the whole table's preamble
      says every route requires login except login/logout/admin — that
      statement needs correcting).
- [ ] Update `doc/wiki/overview.md`: its current framing ("There is no
      public browsing... every customer-facing page requires login") is
      now wrong and needs updating to describe the new mixed
      public/protected model.
- [ ] Commit: `docs: sync wiki with public browsing feature`.
