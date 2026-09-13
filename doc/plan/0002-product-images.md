# Plan: Product Images

Based on `doc/study/0002-product-images.md` (as resolved after review —
`ImageField` + Pillow approved, `media/` gitignored, images shown on
home + detail pages only, no order-history snapshotting, CSS/SVG
placeholder, no size/dimension limits).

Branch: `feat/product-images`, off `main`.

## 1. Dependency

- [ ] Activate the venv, `pip install Pillow`, confirm it resolves to
      `12.3.0` as checked in the study doc (re-verify at install time in
      case a newer patch has shipped since; if so, pin whatever the
      latest is rather than forcing the stale version number).
- [ ] `pip freeze > requirements.txt`, confirm `Pillow==<version>` is
      now listed alongside `Django==5.2.17`.
- [ ] Commit: `build: add Pillow dependency for product images`.

## 2. Model + migration

- [ ] Add `image = models.ImageField(upload_to="products/", blank=True)`
      to `Product` in `cafe/models.py` (no `null=True` — see study doc
      §4 for why).
- [ ] `python manage.py makemigrations cafe`, review the generated
      migration (should be a single additive `AddField`, no data
      migration needed since existing rows get the empty string).
- [ ] `python manage.py migrate`.
- [ ] Commit: `feat: add image field to Product model`.

## 3. Media storage settings

- [ ] Add `MEDIA_URL = "media/"` and `MEDIA_ROOT = BASE_DIR / "media"`
      to `digital_cafe/settings.py`.
- [ ] Wire up dev-only media serving in `digital_cafe/urls.py`:
      `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`
      guarded the standard Django way (this helper is a no-op unless
      `DEBUG=True`, so no extra guard needed beyond using the helper
      itself).
- [ ] Add `media/` to `.gitignore`, alongside the existing
      `db.sqlite3`/`.venv/` entries.
- [ ] Commit: `feat: configure media storage for uploaded product images`.

## 4. Admin

- [ ] Confirm `ProductAdmin` picks up the new field automatically in
      the add/change form (no code change needed for basic
      functionality — verify during manual testing in step 6).
- [ ] Optional: add a read-only thumbnail-preview method to
      `ProductAdmin.list_display` so the product list view shows a small
      image per row. Include if it's a clean small addition; skip if it
      adds noticeable complexity — this was flagged as low-priority/
      optional in the study doc, not a hard requirement.
- [ ] Commit (only if the optional addition is included):
      `feat: show product image thumbnail in admin product list`.

## 5. Templates: placeholder + display on home and detail pages

- [ ] Add a placeholder block to `static/cafe/css/style.css`: a styled
      `.product-image-placeholder` (muted tan box, sized to match where
      a real `<img>` would sit) — CSS/inline-SVG only, no binary asset
      file, matching the study doc's approach and the site's existing
      CSS-only look.
- [ ] `templates/cafe/home.html`: inside each `.product-card`, show
      `{{ product.image.url }}` as an `<img>` (thumbnail-sized via CSS)
      when `product.image` is set, else render the placeholder block.
- [ ] `templates/cafe/product_detail.html`: same conditional, larger
      image sizing appropriate to the detail page's `.card`.
- [ ] Explicitly **not** touching `templates/cafe/cart.html` or
      `templates/cafe/order_history.html` — confirmed out of scope.
- [ ] Commit: `feat: display product images on home and detail pages`.

## 6. Manual verification pass

- [ ] Run the dev server, confirm:
  - [ ] A product with no image shows the placeholder on both the home
        page and its detail page (all current sample products have no
        image yet, so this is the default state to check first).
  - [ ] Upload an image to a product via `/admin/cafe/product/<id>/change/`,
        confirm it saves and appears at `MEDIA_ROOT/products/`.
  - [ ] That product now shows the real image (not the placeholder) on
        both the home page and its detail page.
  - [ ] The image renders correctly via the dev server's media-serving
        route (i.e. `product.image.url` actually resolves to a working
        `<img src>`, not a 404).
  - [ ] Cart and order history pages are unchanged (no image column/
        thumbnail appeared there).
  - [ ] Uploading a non-image file (e.g. a `.txt` renamed to `.jpg`, or
        genuinely non-image content) through the admin form is rejected
        by `ImageField`'s validation, confirming Pillow's validation is
        actually wired up and not silently bypassed.
  - [ ] `git status` shows `media/` is untracked/ignored, not staged.
- [ ] Fix anything broken found during this pass, committing fixes as
      `fix:` commits.

## 7. Rendezvous

- [ ] Merge `feat/product-images` into `main`.
- [ ] Re-run the key parts of the manual verification pass against
      `main` post-merge (placeholder shows, upload works, image
      displays, `media/` stays untracked).
- [ ] Confirm `main` is left in a working, runnable state.

## 8. Sync docs

- [ ] Update `doc/wiki/models.md`: add the `image` field to the
      `Product` table, with a one-line note on why no snapshot for it
      in `OrderLine` (unlike name/price) — it's not a financial/history
      integrity concern.
- [ ] Update `doc/wiki/setup.md`: note that `media/` is created
      automatically on first upload and is gitignored, so a fresh clone
      starts with no product images until someone uploads via admin.
- [ ] Commit: `docs: sync wiki with product images feature`.
