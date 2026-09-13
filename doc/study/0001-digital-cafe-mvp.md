# Study: Digital Cafe MVP (login, browse, cart, checkout, order history)

## 1. Goal

Build the first working version of Digital Cafe: a logged-in customer can
browse products, add them to a cart, check out into a permanent order
record, and view their order history. A superuser manages the catalog and
orders via Django admin.

This doc covers feasibility, the proposed data model, the proposed
request/view flow, and design decisions/tradeoffs. No code is written in
this step.

## 2. Feasibility

Straightforward for Django + SQLite. Nothing here needs anything beyond
Django's built-in auth, the ORM, and server-rendered templates:

- Login-gated app: Django's built-in `LoginView`/`LogoutView` plus
  `@login_required` on every customer-facing view.
- Browsing + detail pages: plain `ListView`/`DetailView` or function-based
  views over a `Product` model.
- Cart: a DB-backed table scoped to `request.user` (see §4).
- Checkout: a view that, in one transaction, copies cart rows into a new
  `Order` + `OrderLine` rows (snapshotting price), then deletes the cart
  rows.
- Order history: a view listing the logged-in user's `Order` rows with
  their `OrderLine` children.
- Admin: `admin.site.register()` for all four models.

No new dependencies are needed for any of this — everything is covered by
Django itself. I'm not proposing adding anything beyond `Django`,
`asgiref`, and `sqlparse` (Django's own required dependencies) to
`requirements.txt`.

## 3. Existing codebase

None yet — this is a brand-new repo with no commits and no code. Nothing
to reuse or account for.

## 4. Tech stack decisions

### Python / Django version

- **Python 3.13** — already installed on this machine at
  `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13`
  (confirmed by running it), alongside the system's default Python 3.11.
  I'll create the project's venv with the 3.13 binary explicitly.
- **Django 5.2.17**, pinned exactly in `requirements.txt`
  (`Django==5.2.17`). I checked live against PyPI (via `pip install
  --dry-run`) rather than relying on memory:
  - The latest Django release overall is actually the 6.x line (6.1.1),
    but you asked for **Django 5.x**, so I'm staying on that line rather
    than substituting a newer major version without discussion.
  - Within 5.x, **5.2 is the LTS (Long Term Support) release** — it gets
    security and data-loss fixes for a much longer window than the
    non-LTS 5.0/5.1 releases (which are already end-of-life). 5.2.17 is
    the newest patch release on that LTS branch as of today. For a course
    project you'll likely keep coming back to, pinning to the LTS branch
    means less risk of it going unsupported mid-project.
  - Pinning the *exact* patch version (`==5.2.17`) rather than a range
    keeps installs reproducible; bumping the patch version later (for
    security fixes) is a one-line, easy-to-review change.
- `asgiref` and `sqlparse` are Django's own required dependencies and will
  be pinned to whatever versions `Django==5.2.17` resolves to — not a new
  dependency I'm choosing, just what ships with Django.

### Project / app layout

- One Django project: `digital_cafe`.
- One Django app: `cafe`, holding all models, views, templates, and URLs
  for this MVP. The whole feature set (products, cart, orders) is small
  enough that splitting into multiple apps (e.g. `catalog` +
  `orders`) would be premature structure for what's currently ~4 models
  and ~5 views. I'd rather split later if/when the app grows than
  over-structure it now.
- SQLite file (`db.sqlite3`) via Django's default `DATABASES` setting —
  no config needed.

## 5. Data model proposal

Four models, matching exactly the four things the spec says the
superuser manages via admin ("products, cart items, orders, and order
lines") — I'm treating that enumeration as confirmation that there is
**no separate `Cart` model**. The cart is implicitly "the logged-in
user's `CartItem` rows"; there's no need for a `Cart` row to hang them
off of, since every user has at most one (implicit) cart and it's always
identified by `request.user`.

### `Product`

| Field | Type | Reasoning |
|---|---|---|
| `name` | `CharField` | Shown on home + detail pages. |
| `description` | `TextField(blank=True)` | Not explicitly required by the spec, but a product detail page with just a name and price feels incomplete for a "coffee shop" catalog; optional so it's not a blocker for admin data entry. |
| `price` | `DecimalField(max_digits=8, decimal_places=2)` | Money must never be a `FloatField` (rounding errors). 8 digits comfortably covers coffee-shop prices with headroom. |
| `is_active` | `BooleanField(default=True)` | Lets the superuser retire a product (stop it appearing on the home page) without deleting it and orphaning historical `OrderLine`/`CartItem` rows that reference it. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Standard bookkeeping, useful for admin sorting. |

### `CartItem`

| Field | Type | Reasoning |
|---|---|---|
| `user` | `ForeignKey(User, on_delete=CASCADE)` | Scopes the cart row to a customer. `CASCADE` because a cart row has no meaning without its user. |
| `product` | `ForeignKey(Product, on_delete=CASCADE)` | If a product is truly deleted (not just deactivated), an unpurchased cart line referencing it should go too — nothing to preserve. |
| `quantity` | `PositiveIntegerField` | Chosen on the product detail page's add-to-cart form. Validated `>= 1`. |
| `added_at` | `DateTimeField(auto_now_add=True)` | Bookkeeping / admin sorting. |
| *(constraint)* | `unique_together = ("user", "product")` | **Confirmed** — see Open Question 1 below (now resolved): adding a product already in the cart increases its quantity rather than creating a duplicate row. Note: this constraint had been drafted into the schema before that was actually confirmed; going forward, a schema-level decision like this that's still an open question gets flagged rather than committed silently, even in a draft study doc. |

### `Order`

| Field | Type | Reasoning |
|---|---|---|
| `user` | `ForeignKey(User, on_delete=PROTECT)` | The order history requirement means this is a financial/historical record. I'm proposing `PROTECT` (block deletion of a user who has orders) rather than Django's default `CASCADE`, so that deleting a user account can never silently wipe out order history. This is a deliberate deviation from the default — flagging it here rather than guessing silently. |
| `created_at` | `DateTimeField(auto_now_add=True)` | This is the "timestamp" the spec explicitly asks for when a cart converts to an order. |

No `status` field: the spec describes checkout as directly producing "a
completed order" — there's no draft/pending/shipped lifecycle mentioned,
so I'm not adding one. No stored `total` field either — total is
computed from the order's `OrderLine`s (`sum(unit_price * quantity)`) as
a model method/property, not stored redundantly. Storing it would risk
the stored value silently drifting from its source rows; computing it is
always correct and the row counts here are small enough that this is
never a performance concern.

### `OrderLine`

| Field | Type | Reasoning |
|---|---|---|
| `order` | `ForeignKey(Order, on_delete=CASCADE)` | A line has no meaning without its parent order. |
| `product` | `ForeignKey(Product, on_delete=PROTECT)` | **Reconsidered from an earlier `SET_NULL, null=True)` draft.** `Product.is_active` already covers "stop selling this" without deletion, so the only real reason left to hard-delete a `Product` is correcting a genuine data-entry mistake — and if it has `OrderLine` history, it wasn't a mistake, it was actually sold. `PROTECT` blocks deletion exactly in that case (consistent with the already-approved `PROTECT` on `Order.user`), while a never-ordered product can still be hard-deleted freely. No `null=True` needed since the FK is never nulled out. |
| `product_name` | `CharField` | **Snapshot** of the product's name at purchase time. The spec requires the *price* paid to be permanently recorded regardless of later price changes; I'm extending that same reasoning to the name. This is needed even with `PROTECT` above, because a product can still be *renamed* (not deleted) after purchase — without this snapshot, an old order would silently start showing today's product name instead of what the customer actually bought. |
| `unit_price` | `DecimalField(max_digits=8, decimal_places=2)` | The price actually charged, copied from `Product.price` at checkout time. This is the field the spec explicitly requires ("recorded permanently"). |
| `quantity` | `PositiveIntegerField` | Copied from the `CartItem` at checkout time. |

Line subtotal (`unit_price * quantity`) is a computed property, not a
stored field, for the same reason as `Order` totals above.

## 6. Request / view flow

Mapped directly to the customer journey in the prompt:

1. `GET /` (or any page) while unauthenticated → redirected to
   `/accounts/login/` (Django's built-in `LoginView`, using
   `django.contrib.auth`'s default auth backend against the built-in
   `User` model). This is the landing page — no view is reachable without
   auth.
2. `GET /` after login → home view, `@login_required`, lists all
   `Product.objects.filter(is_active=True)`, greeting via
   `request.user.first_name or request.user.username` (see Open Question
   4 on how customer accounts get created/named in the first place).
3. `GET /products/<id>/` → detail view, `@login_required`, shows name +
   price, renders a quantity form that `POST`s to an add-to-cart view,
   which creates/updates the user's `CartItem` and redirects back (e.g.
   to the cart, or back to the same page — open question below).
4. `GET /cart/` (checkout view) → `@login_required`, lists the user's
   current `CartItem` rows with computed subtotals and a total, with a
   "confirm" `POST` form.
5. `POST /cart/checkout/` → `@login_required`, inside a single DB
   transaction: create `Order(user=request.user)`, create one
   `OrderLine` per `CartItem` (snapshotting `product_name` and
   `unit_price` from the current `Product`), then delete the user's
   `CartItem` rows. Redirect to an order confirmation / order detail
   page.
6. `GET /orders/` → `@login_required`, lists `request.user`'s past
   `Order`s with their `OrderLine`s and computed totals (using the stored
   `unit_price`, never current `Product.price`).

Enforcement approach: explicit `@login_required` (or
`LoginRequiredMixin` for any class-based views) on every customer-facing
view, rather than Django 5.1+'s newer `LoginRequiredMiddleware`
site-wide-default option. Both would satisfy "no public browsing before
login," but the middleware approach requires correctly marking select
views (like the login view itself) as exempt, and getting that wrong
would be a security-relevant mistake. Per-view decorators are more
verbose but unambiguous about what's protected, which matters more here
than saving a few lines.

## 7. Admin

`admin.site.register()` for `Product`, `CartItem`, `Order`, `OrderLine`
— matching the spec exactly ("manages products, cart items, orders, and
order lines via Django admin"). `OrderLine` will likely also be shown
inline on the `Order` admin page (`TabularInline`) for convenience, in
addition to being separately registered.

No custom `User` model, no custom admin for `User` — customer accounts
are plain Django `auth.User` rows, manageable via the default admin that
`django.contrib.auth` already registers.

## 8. Design options considered and rejected

- **Session-based cart (no `CartItem` DB model)** — rejected. Since login
  is required for every page anyway, there's no benefit to a
  session/cookie cart, and it would be invisible to Django admin, which
  the spec explicitly requires ("superuser manages ... cart items ...
  via Django admin").
- **Separate `Cart` model wrapping `CartItem`s** — rejected as
  unnecessary indirection. A `Cart` row would only ever have exactly one
  per user and add no information `request.user` doesn't already give
  us; the spec's own admin list (products/cart items/orders/order lines)
  doesn't mention a `Cart` model either.
- **Storing computed totals** (`Order.total`, `OrderLine.subtotal`) —
  rejected in favor of computed properties, to avoid a second source of
  truth that could drift from the underlying rows.
- **Multiple Django apps** (`catalog`, `cart`, `orders`) — rejected for
  now as premature structure for an MVP this size; noted as an easy
  future refactor if the app grows.

## 9. Open questions — resolved

All resolved after your review; recorded here for the historical record
rather than left as open questions:

1. **Duplicate add-to-cart behavior — RESOLVED: merge.** Adding a
   product already in the cart increases the existing `CartItem`'s
   quantity (via `unique_together = ("user", "product")`), rather than
   creating a duplicate row.
2. **Cart editing before checkout — RESOLVED: in scope.** A
   remove/edit-quantity control for cart lines is included in this first
   version, not deferred.
3. **Empty cart at checkout — RESOLVED: as proposed.** Show a "your cart
   is empty" message with no confirm button.
4. **Customer account creation — RESOLVED: as proposed.** No public
   registration page for this version; customer accounts are
   admin-created only. Signup may be added later as a separate feature.
5. **Product images — RESOLVED: skip.** No image field for this
   version, confirmed low priority.

Also reconsidered per your review (not originally open questions, but
worth recording as revisited decisions):

- `OrderLine.product`'s `on_delete` behavior changed from an earlier
  `SET_NULL, null=True)` draft to `PROTECT` — see §5 above. `is_active`
  already covers retiring a product, so hard-deleting one with order
  history isn't a case worth supporting.
- Django/Python version pins were independently re-verified against
  PyPI a second time (not just taken on faith from the first check) —
  same result: 6.1.1 is newest overall, 5.2.17 is newest on the 5.x line
  requested. The "5.2 is LTS" claim itself is Django project release
  policy, not something PyPI's version list encodes — noted here so
  that distinction isn't glossed over.

## 10. requirements.txt (proposed contents)

```
Django==5.2.17
```

(`asgiref` and `sqlparse` will be present in the venv as Django's own
resolved dependencies; I'm listing only the direct, deliberately-chosen
dependency per your "new dependencies need approval" rule — there are no
others to propose for this MVP.)