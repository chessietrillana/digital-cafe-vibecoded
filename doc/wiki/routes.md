# Routes / pages

All routes below except the login/logout pair and `/admin/` require
login (`@login_required`); an unauthenticated request to any of them
redirects to `/accounts/login/`.

| URL | View | Purpose |
|---|---|---|
| `/accounts/login/` | Django's built-in `LoginView` | The effective landing page — username + password only, no signup link. |
| `/accounts/logout/` | Django's built-in `LogoutView` | Logs out, redirects to login. |
| `/` | `cafe.views.home` | Lists active products, greets the customer by first name (or username if no first name is set). |
| `/products/<id>/` | `cafe.views.product_detail` | Shows a product's name, description, price, and an add-to-cart form. |
| `/products/<id>/add/` | `cafe.views.add_to_cart` | `POST`-only. Adds/merges the product into the customer's cart. |
| `/cart/` | `cafe.views.cart_view` | Shows the customer's current cart with per-line subtotal, running total, and a checkout confirmation form. Shows "Your cart is empty." with no checkout form when empty. |
| `/cart/<item_id>/update/` | `cafe.views.update_cart_item` | `POST`-only. Updates a cart line's quantity; setting quantity to 0 removes it. |
| `/cart/checkout/` | `cafe.views.checkout` | `POST`-only. Converts the cart into a completed `Order` + `OrderLine`s (snapshotting name/price), clears the cart, redirects to order history. |
| `/orders/` | `cafe.views.order_history` | Lists the customer's past orders (newest first) with their line items and totals, using the price actually paid — not current product prices. |
| `/admin/` | Django admin | Superuser-only management of `Product`, `CartItem`, `Order` (with inline `OrderLine`s), and `OrderLine`. |

URL names (for `{% url %}` / `reverse()`): `login`, `logout`, `home`,
`product_detail`, `add_to_cart`, `cart`, `update_cart_item`, `checkout`,
`order_history`.
