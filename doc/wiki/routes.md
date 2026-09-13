# Routes / pages

**Browsing is public** (`/` and `/products/<id>/`) — no login required.
Everything that mutates a cart or places an order, plus order history,
stays behind `@login_required`; an unauthenticated request to one of
those redirects to `/accounts/login/?next=<that URL>`, and logging in
sends them back to the exact page they were trying to reach.

| URL | View | Login required? | Purpose |
|---|---|---|---|
| `/accounts/login/` | Django's built-in `LoginView` | — | Username + password. Honors `?next=` (via a hidden form field, not just the query string) to return the visitor to wherever they came from. Cross-links to `/accounts/signup/`. |
| `/accounts/signup/` | `cafe.views.signup` | — | Self-service account creation — username, optional first name, password (Django's `UserCreationForm`, no email field). Auto-logs the new user in and honors `?next=` the same way login does; cross-links to `/accounts/login/`. |
| `/accounts/logout/` | Django's built-in `LogoutView` | Yes | Logs out, redirects to login. |
| `/` | `cafe.views.home` | **No** | Lists active products. Accepts an optional `?q=` search parameter — case-insensitive substring match on `name` only (not `description`), layered on top of the existing `is_active` filter; shows "No products match "…"." when a search has no results, vs. the generic "No products available right now." when there's no search and the catalog is genuinely empty. Works identically whether logged in or not. Greets the customer by first name (or username) when logged in; shows a generic "Welcome to Chessie's Digital Cafe!" heading when not. Nav shows Cart/Order History/Log out when authenticated, or Log in/Sign up links when not. |
| `/products/<id>/` | `cafe.views.product_detail` | **No** | Shows a product's name, description, price. Authenticated + active product → the add-to-cart form. Anonymous + active product → "Log in or sign up to add this to your cart" (`?next=` back to this same page for both links). Either way, an inactive product always shows "This product is currently unavailable" instead — that part doesn't depend on login state. |
| `/products/<id>/add/` | `cafe.views.add_to_cart` | Yes | `POST`-only. Adds/merges the product into the customer's cart. |
| `/cart/` | `cafe.views.cart_view` | Yes | Shows the customer's current cart with per-line subtotal, running total, and a checkout confirmation form. Shows "Your cart is empty." with no checkout form when empty. |
| `/cart/<item_id>/update/` | `cafe.views.update_cart_item` | Yes | `POST`-only. Updates a cart line's quantity; setting quantity to 0 removes it. |
| `/cart/checkout/` | `cafe.views.checkout` | Yes | `POST`-only. Converts the cart into a completed `Order` + `OrderLine`s (snapshotting name/price), clears the cart, redirects to order history. |
| `/orders/` | `cafe.views.order_history` | Yes | Lists the customer's past orders (newest first) with their line items and totals, using the price actually paid — not current product prices. |
| `/admin/` | Django admin | Yes (superuser) | Superuser-only management of `Product`, `CartItem`, `Order` (with inline `OrderLine`s), and `OrderLine`. |

URL names (for `{% url %}` / `reverse()`): `login`, `signup`, `logout`,
`home`, `product_detail`, `add_to_cart`, `cart`, `update_cart_item`,
`checkout`, `order_history`.
