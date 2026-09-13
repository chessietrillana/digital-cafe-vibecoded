# Study: Product Images

Follows up on `doc/study/0001-digital-cafe-mvp.md`'s Open Question 5,
which deferred product images entirely ("skip for now, agreed it's low
priority"). This doc covers adding them: storage setup, the model field,
no-image display behavior, and the new dependency this requires. No code
is written in this step.

## 1. Goal

Let a superuser upload an image per `Product` via Django admin, and show
it to customers on the pages where they see that product (home listing,
product detail). Products without an image should still display
sensibly, not broken or blank.

## 2. Existing codebase — what this touches

- `cafe/models.py` — `Product` currently has `name`, `description`,
  `price`, `is_active`, `created_at`. No image-related field exists.
- `digital_cafe/settings.py` — has `STATIC_URL`/`STATICFILES_DIRS`
  (added for the site's CSS/fonts) but **no `MEDIA_ROOT`/`MEDIA_URL`**
  yet. Static and media are different things in Django and this project
  currently only has the former:
  - `static/` = source-controlled assets that ship with the app code
    (the CSS file, fonts config). Same for every deploy, edited by
    whoever edits the code.
  - `media/` = user-uploaded runtime content (what this feature needs) —
    written to disk by Django when a superuser uploads a file through
    admin, not part of the source tree in the usual sense.
- `templates/cafe/home.html` and `templates/cafe/product_detail.html` —
  where the image would actually be displayed.
- `cafe/admin.py` — `ProductAdmin` would pick up the new field
  automatically in its add/change form; no code changes strictly needed
  there, though I'm proposing one small optional addition (§7).
- `requirements.txt` — currently only `Django==5.2.17` plus Django's own
  transitive deps (`asgiref`, `sqlparse`). Nothing image-related.

## 3. New dependency: Pillow — needs your approval

Per CLAUDE.md, new dependencies need approval before I add them. Django's
`ImageField` (the natural field type here — see §4) **requires Pillow**
to validate that an uploaded file is actually a decodable image; without
it, `makemigrations`/`migrate` and form validation involving an
`ImageField` raise an error telling you to install it. There's no way to
get Django's image-upload validation without some imaging library, and
Pillow is the standard/only one Django documents for this.

I checked live against this project's own venv (not from memory):

```
.venv/bin/pip install --dry-run Pillow
→ Would install pillow-12.3.0
```

A `cp313` wheel exists for Pillow 12.3.0, so it installs cleanly on this
project's Python 3.13 venv. If approved, I'd pin it exactly in
`requirements.txt` the same way `Django==5.2.17` is pinned:
`Pillow==12.3.0`.

**If you'd rather not add a dependency for this**, §8 below has a
zero-dependency alternative (`URLField` instead of `ImageField`) — worth
reading before approving Pillow, in case that's a better fit.

## 4. Proposed field on `Product`

```python
image = models.ImageField(upload_to="products/", blank=True)
```

- **`ImageField`, not `FileField`**: validates the upload is actually a
  readable image (via Pillow) and gives Django admin a nicer widget
  (thumbnail of the current image + file picker), rather than a generic
  file-upload input that would accept anything.
- **`upload_to="products/"`**: files land at `MEDIA_ROOT/products/...`,
  keeping product images in their own subfolder rather than dumped at
  the media root — the only subfolder needed right now, but keeps room
  for other upload types later without a migration.
- **`blank=True` — deliberately no `null=True`.** This is a real Django
  gotcha worth calling out rather than silently getting right or wrong:
  for `FileField`/`ImageField`, Django's own documented convention is to
  avoid `null=True`, because the field already has one representation of
  "no file" (an empty string), and adding `null=True` creates a second,
  redundant one (`NULL`) — meaning "no image" could be stored two
  different ways depending on code path, which is exactly the kind of
  ambiguity worth avoiding. `blank=True` alone makes it optional in
  forms/admin while keeping a single unambiguous "empty" representation.
- No `default` needed — existing `Product` rows simply get the empty
  string (no image) when this migration runs; no data migration
  required.

## 5. `MEDIA_ROOT` / `MEDIA_URL` setup (local dev)

Proposed settings addition:

```python
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
```

And, in `digital_cafe/urls.py`, the standard Django dev-only pattern to
actually serve uploaded files when `DEBUG=True`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**This is dev-only serving**, same caveat that already applies to the
rest of this project's settings (`DEBUG=True`, the insecure
`SECRET_KEY`, empty `ALLOWED_HOSTS`) — Django's own docs are explicit
that this helper is not for production use. Since this whole project is
currently in "quick-start development settings" mode per
`settings.py`'s own header comment, I'm treating that as consistent with
the project's current stage rather than a gap introduced by this
feature. Production-grade media serving (a real web server, or
cloud/object storage) would be a separate discussion if/when this
project needs a real deployment target — out of scope here.

`media/` would be added to `.gitignore` alongside `db.sqlite3` — see
Open Question 1.

## 6. No-image display behavior

Proposed: **show a placeholder, don't just omit the image**, so the
product grid on the home page stays visually consistent whether or not
every product has a photo yet (useful early on, since none of the 9
sample products currently in the dev DB have one).

Concretely: `{% if product.image %}<img src="{{ product.image.url }}">{% else %}` a simple placeholder block styled with the site's existing warm/coffee CSS (e.g. a muted tan box with "No image" text, or a simple inline SVG coffee-cup icon) `{% endif %}`. I'm proposing to build this placeholder purely in CSS/inline SVG rather than sourcing an actual placeholder image file — keeps it in the existing `static/cafe/css/style.css`, no binary asset to source or commit, and matches how the site's look has been done so far (CSS-only, no images at all yet).

Shown on: the home page product grid (small/thumbnail-sized) and the
product detail page (larger). See Open Question 3 on whether cart/order
history should also show a thumbnail.

## 7. Admin (optional, small addition)

`ProductAdmin` already gets a working image upload field for free once
it's on the model — Django's admin renders `ImageField` with a file
picker and, when editing an existing product, a link to the current
file. The one optional improvement I'm flagging (not required, cheap to
add or skip): a read-only thumbnail preview method in `list_display`,
so the admin's product list view shows a small image per row instead of
just a filename link. Low priority — happy to include it or skip it.

## 8. Alternative considered: `URLField` instead of `ImageField`

Worth presenting as a real alternative rather than only a rejected
option, since it changes the shape of this feature significantly:

```python
image_url = models.URLField(blank=True)
```

Customer/admin pastes a link to an already-hosted image (e.g. an image
they uploaded somewhere else, or a stock photo URL) instead of
uploading a file through Django admin.

**Pros:** zero new dependencies (no Pillow), no `MEDIA_ROOT`/media
serving setup, no uploaded files to manage/gitignore/back up — the
simplest possible version of this feature.

**Cons:** no upload-through-admin workflow (superuser needs to host the
image somewhere else first and paste a URL); no validation that the URL
actually points to an image (a `URLField` only validates it's a
well-formed URL, not that it resolves to a viewable image); a broken
external link silently breaks the image with no server-side way to
detect it.

I'd lean toward `ImageField` (§4) as the better experience for actually
running/demoing this app — "superuser uploads a photo in admin" matches
how the rest of this project's admin-managed data works (products,
prices, etc. are all edited directly in admin, not by pasting
externally-prepared values) — but flagging `URLField` clearly as the
lower-effort/zero-dependency path in case you'd rather avoid adding
Pillow.

## 9. Open questions — resolved

All resolved after your review; recorded here for the historical record:

1. **Commit uploaded images to git, or gitignore `media/`? — RESOLVED:
   gitignore.** Same treatment as `db.sqlite3` — uploaded files are
   runtime data, not source.
2. **`ImageField` vs. `URLField`? — RESOLVED: `ImageField`.** Pillow
   approved as a new dependency, pinned `Pillow==12.3.0`.
3. **Where should images appear? — RESOLVED: home + detail pages
   only.** Cart and order history stay focused on transactional data,
   no product thumbnails there. Also resolved: order history does
   **not** snapshot the image — only price gets that integrity
   guarantee; a product's current image is fine to show if it were ever
   displayed there (moot now, since it isn't shown there at all).
4. **Placeholder style — RESOLVED: CSS/inline-SVG placeholder, as
   proposed in §6.**
5. **File size / dimension limits — RESOLVED: none.** Django's default
   validation (must be a decodable image) is sufficient.
