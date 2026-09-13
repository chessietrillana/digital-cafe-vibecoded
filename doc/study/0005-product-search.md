# Study: Product Search on the Home Page

Adds a search bar to the home page so customers can filter the product
grid by name. No code is written in this step.

## 1. Existing codebase — what this touches

- `cafe/views.py`'s `home` view currently does exactly one query —
  `Product.objects.filter(is_active=True).order_by("name")` — with no
  request-driven filtering at all.
- `templates/cafe/home.html` renders that queryset as a
  `<ul class="product-list">` of `.product-card` items (image/placeholder,
  name link, price) — this is the exact grid built in the responsive
  3-column-grid styling work, and reused as-is for empty state ("No
  products available right now.").
- `cafe/urls.py`: `home` is the sole `path("", ...)` route — there's no
  existing `/search/`-style URL.
- `Product` has both `name` (`CharField`) and `description`
  (`TextField`, optional/`blank=True`) — either or both could be
  searched.
- Per CLAUDE.md's tech stack ("No frontend framework"): this has to be
  a plain server-rendered form submission (`GET` → filtered page
  reload), not a JS live-filter-as-you-type widget. Worth stating
  explicitly since "search bar" can imply live filtering to some
  readers — that's not on the table here given the stack constraint.
- Per `doc/study/0003-public-browsing.md`: `home` has **no**
  `@login_required` — it's fully public. A search that filters the same
  public queryset doesn't introduce any new access question; it's the
  same data, just narrowed.

## 2. Proposed matching semantics

- **Case-insensitive substring match**, via Django's `icontains`
  lookup (`Product.objects.filter(is_active=True, name__icontains=query)`).
  This is the standard, idiomatic choice for "search by name" — fully
  parameterized (no injection risk), and on SQLite, `icontains`
  already does case-insensitive `LIKE` matching for ASCII without any
  extra code. Not proposing exact-match or whole-word matching — a
  substring search is what "filter products by name" almost always
  means in practice (e.g. typing "latte" should find "Iced Latte" too).
- **Name only, not description — proposed, but flagged as the one
  real open question here** (§8.1). Your prompt explicitly raised this,
  and I don't want to guess: the request says "filter products by
  name," so name-only is the literal reading and keeps results
  predictable (what you typed is visibly in the result's name). Matching
  descriptions too would surface less-obvious hits (e.g. searching
  "oat" could match a latte whose description mentions oat milk, even
  though "oat" isn't in its name) — potentially useful, potentially just
  confusing. My default is name-only; confirming rather than deciding
  silently.
- Search only ever narrows the **already-`is_active`-filtered**
  queryset — it can't surface a retired/inactive product that wouldn't
  otherwise appear on the home page. Same visibility rule as today,
  just with an added filter on top.
- An empty or whitespace-only query is treated as "no search active" —
  shows the full catalog, not a query that (harmlessly, since every
  string contains the empty substring) would match everything anyway.
  This matters for driving the UI state in §4 (whether to show a "no
  results" vs. "no products at all" message, and whether to show a
  "clear search" link).

## 3. Reusing the home page — no new view, template, or URL

Directly answering your question: **reuse the existing `home` view,
template, and grid markup**, with `?q=<search term>` as a query
parameter on the same `/` URL — not a separate `/search/` page or
template.

Reasoning: a dedicated search results page would mean either
duplicating the entire `.product-list`/`.product-card` grid markup in a
second template (a second place to keep in sync with any future styling
change), or awkwardly sharing a partial template for just the grid.
Since the home page **is** the product catalog and search only narrows
it, there's no actual second "place" search results conceptually belong
— `/` with a `q` param is bookmarkable and shareable exactly like a
dedicated `/search/` URL would be, with none of the duplication.

Concretely: `home` reads `request.GET.get("q", "")`, filters when
non-empty, and passes both the (possibly filtered) `products` queryset
and the raw `query` string back to the same `cafe/home.html` template
— the grid `{% for product in products %}` loop is completely
unchanged, it just iterates over fewer items when a search is active.

## 4. Template changes

- A `<form method="get">` (submitting back to `/`) with a single
  `<input type="text" name="q" value="{{ query }}">` and a submit
  button, placed above the product grid (right after the "MENU:"
  heading). Using `value="{{ query }}"` means the typed term stays
  visible in the box after submitting, instead of the input clearing
  itself. `GET`, not `POST`, since a search is a read — it doesn't
  mutate anything, so it should be bookmarkable/shareable and doesn't
  need a CSRF token, consistent with how every other read-only page in
  this app already works.
- **Proposed: a "Clear search" link**, shown only when a query is
  active, pointing back to plain `/` — otherwise the only way to reset
  is manually deleting the text.
- **Proposed: differentiate the empty state.** Right now, zero products
  always shows "No products available right now." — accurate when the
  catalog is genuinely empty, misleading when it's actually "your
  search matched nothing." Proposed: when `query` is set and there are
  no results, show something like `No products match "latte".` instead
  of the generic message.
- No new CSS anticipated — the site's shared stylesheet already styles
  `input[type="text"]` and `button` generically (rounded corners,
  caramel button, etc. from the cozy-theme work), so the search form
  picks up consistent styling for free. Might add a small flex-row
  class to lay the input and button out inline rather than stacked, but
  that's a minor layout detail, not a new design.

## 5. Form handling: a `SearchForm`, matching existing convention

Every other piece of user input in this app already goes through a
`django.forms.Form` subclass (`AddToCartForm`, `SignupForm` in
`cafe/forms.py`) rather than reading `request.GET`/`request.POST`
directly. Proposing the same here — a small `SearchForm` with one field,
`q = forms.CharField(required=False)` — purely for consistency with the
codebase's existing pattern, not because a single text field strictly
needs form-class validation.

## 6. Public browsing interaction

Directly answering your question: **yes, search works identically for
anonymous and logged-in visitors** — no new decision needed here,
really, since `home` is already fully public
(`doc/study/0003-public-browsing.md`) and this just adds a filter on
top of a view that already has no login gate. There's no scenario where
search needs to behave differently based on auth state; it's the same
public product grid either way.

## 7. Design options considered and rejected

- **JS live-filtering (search-as-you-type)** — rejected; CLAUDE.md's
  "no frontend framework" rule, and this app has zero custom JavaScript
  anywhere today. A plain form submission stays consistent with that.
- **Separate `/search/` view + template** — rejected per §3; pure
  duplication of the grid markup for no real benefit over `?q=` on the
  existing home URL.
- **Matching descriptions by default** — not rejected outright, genuinely
  open — see Open Question 1 below.
- **Whole-word or exact-match search** — rejected in favor of substring
  matching (§2); substring is the more forgiving, expected default for
  this kind of search box.

## 8. Open questions — resolved

1. **Search `name` only, or `name` + `description`? — RESOLVED:
   name-only.** Matches the original request's literal wording
   ("filter products by name") and keeps results predictable — the
   searched term stays visible in what's shown.