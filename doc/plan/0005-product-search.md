# Plan: Product Search on the Home Page

Based on `doc/study/0005-product-search.md` (as resolved after review —
case-insensitive substring match via `icontains`, name-only (not
description), reuses the existing `home` view/template/grid via
`?q=` on `/`, works identically for anonymous and logged-in visitors,
no JS live-filtering).

Branch: `feat/product-search`, off `main`.

## 1. `SearchForm`

- [ ] `cafe/forms.py`: add `SearchForm(forms.Form)` with
      `q = forms.CharField(required=False)`, matching the existing
      `AddToCartForm`/`SignupForm` convention of routing user input
      through a form class.
- [ ] Commit: `feat: add SearchForm for the home page search bar`.

## 2. `home` view: filter by query

- [ ] `cafe/views.py`: in `home`, build a `SearchForm(request.GET)`,
      pull `query = form.cleaned_data.get("q", "").strip()` when valid
      (empty `request.GET` is still a valid, all-blank form), and only
      apply `.filter(name__icontains=query)` on top of the existing
      `is_active=True` filter when `query` is non-empty.
- [ ] Pass both `products` and `query` (the stripped string, `""` when
      no search is active) into the template context.
- [ ] Commit: `feat: filter home page products by name via ?q=`.

## 3. Template: search form + clear link + differentiated empty state

- [ ] `templates/cafe/home.html`:
  - Add the search `<form method="get">` (submits back to `/`) with
    the `q` input (`value="{{ query }}"`) and a submit button, placed
    right after the "MENU:" heading and before the product grid.
  - Show a "Clear search" link to plain `{% url 'home' %}`, only when
    `query` is non-empty.
  - Differentiate the empty-result message: `query` set + no products
    → `No products match "{{ query }}".`; no `query` + no products →
    keep the existing generic "No products available right now."
  - The `<ul class="product-list">` grid loop itself is unchanged.
- [ ] Commit: `feat: add search bar and differentiated empty state to home page`.

## 4. Minor CSS (only if needed)

- [ ] Check how the search form looks against the site's existing
      shared input/button styles once rendered (step 5's verification
      pass). Only add CSS (e.g. a small flex-row class to lay the input
      and button out inline) if the default stacking actually looks
      wrong — per the study doc, no new CSS is expected to be strictly
      necessary.
- [ ] Commit (only if a CSS change is actually made):
      `feat: lay out the search form inline`.

## 5. Manual verification pass

- [ ] Run the dev server, confirm, **logged out** (search must work
      without login, per the study doc):
  - [ ] `/` shows the search box, pre-populated as empty, full catalog
        showing.
  - [ ] Searching a substring that matches one product (e.g. part of
        "Cappuccino") shows only that product, and the input still
        shows the typed term.
  - [ ] Search is case-insensitive (e.g. "LATTE" matches "Latte").
  - [ ] Search does **not** match on a term that only appears in a
        product's `description`, not its `name` — confirms the
        name-only decision actually holds.
  - [ ] A query matching zero products shows
        `No products match "<query>".`, not the generic empty-catalog
        message.
  - [ ] "Clear search" link appears only when a query is active, and
        clicking it returns to the full, unfiltered catalog.
  - [ ] An inactive product never appears in search results even if its
        name matches the query (confirms search stays layered on top
        of the existing `is_active` filter).
  - [ ] The searched-for product's link still correctly navigates to
        its detail page (grid markup/links unaffected by filtering).
- [ ] Repeat the core search-and-filter checks **logged in** — confirm
      no behavior differs by auth state, and that nothing about
      cart/checkout/order history was touched by this change (quick
      regression spot-check, not the full suite, since this feature
      doesn't touch those views).
- [ ] Fix anything broken found during this pass, committing fixes as
      `fix:` commits.

## 6. Rendezvous

- [ ] Merge `feat/product-search` into `main`.
- [ ] Re-run the key checks from step 5 against `main` post-merge.
- [ ] Confirm `main` is left in a working, runnable state.

## 7. Sync docs

- [ ] Update `doc/wiki/routes.md`: note on the `/` row that it accepts
      an optional `?q=` search parameter, name-only, case-insensitive
      substring match.
- [ ] Commit: `docs: sync wiki with product search feature`.
