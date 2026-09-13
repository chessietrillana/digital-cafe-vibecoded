# Study: Public Browsing (No Login Required to Browse)

Reverses part of the original customer-journey spec captured in
`doc/study/0001-digital-cafe-mvp.md` §6 ("no public browsing before
login" was an explicit requirement there). This doc is the record of
that reversal: the catalog (home + product detail) becomes public;
adding to cart, cart management, checkout, and order history stay
login-required. No code is written in this step.

This doesn't touch CLAUDE.md's own hard rules (workflow, no external
repos, terminal-only, etc.) — it's a change to this project's own
earlier feature decision, not to the process rules governing how I
work.

## 1. Existing codebase — what this touches

`cafe/urls.py` currently routes seven views, all behind `@login_required`
in `cafe/views.py`:

| URL | View | Currently |
|---|---|---|
| `/` | `home` | `@login_required` |
| `/products/<id>/` | `product_detail` | `@login_required` |
| `/products/<id>/add/` | `add_to_cart` | `@login_required`, POST-only |
| `/cart/` | `cart_view` | `@login_required` |
| `/cart/<id>/update/` | `update_cart_item` | `@login_required`, POST-only |
| `/cart/checkout/` | `checkout` | `@login_required`, POST-only |
| `/orders/` | `order_history` | `@login_required` |

`doc/study/0001-digital-cafe-mvp.md` §6 explains the original choice of
per-view `@login_required` decorators over Django 5.1+'s
`LoginRequiredMiddleware` specifically because it's "unambiguous about
what's protected." That reasoning holds even more now that this becomes
a **mixed** public/protected app — the surgical fix is removing the
decorator from exactly two views, not introducing a site-wide default
that then needs explicit exemptions for the public ones.

`templates/base.html`'s nav is currently entirely wrapped in
`{% if user.is_authenticated %}` — there's no nav at all for a logged-out
visitor right now, because none existed (everything required login). That
assumption breaks once `home`/`product_detail` are reachable
unauthenticated.

## 2. Proposed change: which views stop requiring login

Only two:

- `home` — becomes public.
- `product_detail` — becomes public.

Everything else (`add_to_cart`, `cart_view`, `update_cart_item`,
`checkout`, `order_history`) **keeps** `@login_required`, per your
request that only cart/checkout require login.

## 3. A real bug this surfaces: the home page greeting

I checked this live rather than assuming: `django.contrib.auth.models.AnonymousUser`
has `username = ''` but genuinely **has no `first_name` attribute at
all** — not an empty string, the attribute doesn't exist.

```
>>> AnonymousUser().first_name
AttributeError: 'AnonymousUser' object has no attribute 'first_name'
```

`home`'s current line —

```python
greeting_name = request.user.first_name or request.user.username
```

— would throw a 500 error for every anonymous visitor the moment this
view stops requiring login. This isn't a style choice, it's a bug that
has to be fixed as part of this change. Proposed fix: branch on
`request.user.is_authenticated` in the view, and pass different context
to the template (or nothing) for the anonymous case — see §5 for what
anonymous visitors should actually see instead of a greeting.

## 4. Nav: what should a logged-out visitor see?

Proposed:

- **"Home"** — always visible (it's public now).
- **"Cart" / "Order History"** — hidden when logged out. Both pages
  stay login-required, so showing links that immediately bounce to the
  login page is confusing rather than helpful — the visitor didn't ask
  to log in, they clicked "Cart."
- **A "Log in" link** — needs to be added for logged-out visitors.
  Right now there's no login link anywhere in the nav, because the old
  design didn't need one (login was the forced landing page, not
  something you'd navigate to from elsewhere). Once browsing is public,
  an anonymous visitor needs some way to discover the login page.
  (There's still no signup link, per the confirmed no-public-registration
  decision in `doc/study/0001-digital-cafe-mvp.md`.)
- **"Log out"** — stays authenticated-only, as now.

Concretely, `base.html`'s nav becomes conditional per-link rather than
the whole block being conditional:

```
Home            [always]
Cart            [if authenticated]
Order History   [if authenticated]
Log in          [if NOT authenticated]
Log out         [if authenticated]
```

## 5. Home page content for anonymous visitors

Proposed: replace the personalized `"Welcome, {name}!"` heading with a
generic one (e.g. `"Welcome to Digital Cafe"`) when not authenticated,
keeping the personalized greeting for logged-in customers. The product
grid itself (image/name/price, linking to detail pages) stays identical
for both — the whole point of this feature is that the catalog itself
doesn't change based on login state.

Open question below (§8.1) on whether to add an explicit "Log in to
place an order" call-to-action on the home page for anonymous visitors,
or leave it at just the nav's "Log in" link.

## 6. Product detail page for anonymous visitors — the add-to-cart form

This is the trickier case, and where I don't want to guess silently.

`product_detail` is becoming public, but `add_to_cart` (what its form
`POST`s to) stays login-required. If the form is left as-is and simply
rendered for everyone:

- An anonymous visitor sees the quantity form and an "Add to cart"
  button, exactly like a logged-in customer would.
- They fill in a quantity and submit. `@login_required` intercepts the
  `POST` to `/products/<id>/add/` and redirects to
  `/accounts/login/?next=/products/<id>/add/`.
- After logging in, Django's `LoginView` follows `next` — but that's a
  **`GET`** to `/products/<id>/add/`, not a resubmission of their
  original `POST`. `add_to_cart`'s own code
  (`if request.method != "POST": return redirect("product_detail", pk=pk)`)
  just bounces them back to the product page having **silently added
  nothing** — no error, no explanation, the quantity they entered is
  just gone. That's a genuinely confusing dead end, not a security
  problem (nothing unsafe happens) but a real UX gap.

**Proposed fix:** don't show the add-to-cart form at all to anonymous
visitors. Show the product's name/description/price (that part's fully
public), and where the form would be, show something like *"Log in to
add this to your cart"* linking to `/accounts/login/?next=/products/<id>/`
— so after logging in, they land back on **that same product's page**
(a `GET`, which works cleanly with Django's `next` redirect) and can
then use the real add-to-cart form as a logged-in customer. This avoids
the silent-quantity-loss dead end entirely, at the cost of one extra
click (log in, then re-submit the form) versus a hypothetical
single-step flow.

## 7. Directly visiting a protected URL while logged out

For the views that stay `@login_required` (`/cart/`, `/orders/`, and
`POST /products/<id>/add/`, `/cart/<id>/update/`, `/cart/checkout/`):
Django's default `@login_required` behavior already handles this
correctly with **no extra code needed** —

- `GET /cart/` or `GET /orders/` while logged out → redirects to
  `/accounts/login/?next=/cart/` (or `/orders/`) → after login, lands
  exactly back on that page. This works cleanly since it's a `GET`.
- A direct `POST` to `/products/<id>/add/`, `/cart/<id>/update/`, or
  `/cart/checkout/` while logged out (not reachable through normal
  navigation once §6's fix is in place, but reachable by anyone crafting
  a request directly, e.g. via `curl`) → same redirect-to-login
  treatment, and same caveat as §6: the original `POST` isn't replayed
  after login. This is standard, expected behavior for any
  login-protected form endpoint on the web, not something specific to
  this app or this change — I'm not proposing any special handling for
  it beyond what §6 already does for the one path reachable through
  normal UI navigation (the product detail page's form).

No settings changes needed here — `LOGIN_URL = 'login'` and the default
`next`-param handling in Django's built-in `LoginView` already do the
right thing.

## 8. Open questions — resolved

All resolved after your review; recorded here for the historical record:

1. **Anonymous-visitor call-to-action on the home page — RESOLVED:
   minimal.** Just the nav's "Log in" link — no banner/CTA on the home
   page itself.
2. **Inactive products and direct-URL access — RESOLVED: no change,
   confirmed correctly out of scope.**
3. **Flash message on redirect-to-login — RESOLVED: no.** Django's
   default (silent redirect to the login page) is clear enough on its
   own.

Also approved as proposed: the §6 fix (hiding the add-to-cart form for
anonymous visitors and linking to login with `?next=` back to that same
product page, rather than showing the form and hitting the
silent-quantity-loss dead end).