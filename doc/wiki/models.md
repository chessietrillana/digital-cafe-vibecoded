# Data model

All four models live in `cafe/models.py`. There is deliberately no
separate `Cart` model — a customer's cart is just their `CartItem` rows,
identified by `user`.

## `Product`

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField` | |
| `description` | `TextField` | Optional (`blank=True`). |
| `price` | `DecimalField(8, 2)` | Current price — see `OrderLine.unit_price` for what customers actually paid historically. |
| `image` | `ImageField` | Optional (`blank=True`, no `null=True` — Django's own convention for `FileField`/`ImageField`, to avoid two representations of "no file"). Uploaded via Django admin, stored under `MEDIA_ROOT/products/`. Shown on the home page and product detail page only; not shown on the cart or order history pages, and **not snapshotted** onto `OrderLine` — unlike `price`, a product's photo isn't a financial/history integrity concern, so order history just doesn't display it at all. |
| `is_active` | `BooleanField` | `False` hides it from the home page without deleting it. |
| `created_at` | `DateTimeField` | Auto-set on creation. |

Deleting a `Product` that has ever appeared in an `OrderLine` is
**blocked** (`on_delete=PROTECT` on that FK) — deactivate it via
`is_active` instead. A product with no order history can be deleted
freely.

## `CartItem`

One row per `(user, product)` pair — enforced by `unique_together`.
Adding a product to the cart that's already there **increases its
quantity** rather than creating a second row.

| Field | Type | Notes |
|---|---|---|
| `user` | `FK(User, CASCADE)` | |
| `product` | `FK(Product, CASCADE)` | Cart rows for a deleted product are deleted too — nothing worth preserving pre-purchase. |
| `quantity` | `PositiveIntegerField` | Min 1. |
| `added_at` | `DateTimeField` | |

## `Order`

Created at checkout; represents a completed purchase. No `status`
field — checkout directly produces a completed order, there's no
draft/pending lifecycle.

| Field | Type | Notes |
|---|---|---|
| `user` | `FK(User, PROTECT)` | Deleting a user with order history is blocked, to protect financial records. |
| `created_at` | `DateTimeField` | The order timestamp. |

`Order.total()` sums its lines' subtotals — **not stored**, always
computed from `OrderLine` rows.

## `OrderLine`

One row per product purchased in an order. Created at checkout by
copying data off the `CartItem`/`Product` at that moment — this is what
makes order history permanent and independent of later catalog changes.

| Field | Type | Notes |
|---|---|---|
| `order` | `FK(Order, CASCADE)` | |
| `product` | `FK(Product, PROTECT)` | Link back to the current product row, when it still exists. |
| `product_name` | `CharField` | **Snapshot** of the product's name at purchase time — stays correct even if the product is later renamed. |
| `unit_price` | `DecimalField(8, 2)` | **Snapshot** of the price actually charged — stays correct even if the product's price later changes. |
| `quantity` | `PositiveIntegerField` | |

`OrderLine.subtotal()` = `unit_price * quantity`, computed, not stored.

## Design rationale

Full reasoning for each of these choices — including alternatives
considered and rejected (session-based cart, a separate `Cart` model,
stored totals) — is in `doc/study/0001-digital-cafe-mvp.md`. The
`image` field's reasoning (including the `URLField` alternative
considered and not taken) is in `doc/study/0002-product-images.md`.
