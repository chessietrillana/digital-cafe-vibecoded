# Plan: Public Signup Page

Based on `doc/study/0004-public-signup.md` (as resolved after review —
`first_name` collected at signup, auto-login after signup, all four
"Sign up" placements approved).

Branch: `feat/public-signup`, off `main`.

## 1. Signup form

- [ ] `cafe/forms.py`: add `SignupForm(UserCreationForm)` with
      `Meta.fields = ("username", "first_name")` (password1/password2
      come from `UserCreationForm` itself) and
      `first_name = forms.CharField(required=False)` declared
      explicitly so it's optional.
- [ ] Commit: `feat: add SignupForm extending UserCreationForm with an optional first name`.

## 2. Signup view

- [ ] `cafe/views.py`: add a `signup` view (function-based, matching
      the rest of this file) —
  - `GET`: render `registration/signup.html` with a fresh `SignupForm`
    and the `next` value (from `request.GET.get('next', '')`) in
    context.
  - `POST`: validate `SignupForm(request.POST)`; on success, save the
    user, call `django.contrib.auth.login(request, user)`, then
    redirect to `request.POST.get('next') or 'home'` (mirroring how
    Django's own `LoginView` resolves `next`, and reusing the same
    hidden-field pattern already on `registration/login.html`).
  - Invalid form: re-render the page with errors, same as any other
    form view in this codebase.
- [ ] Commit: `feat: add signup view with auto-login and next handling`.

## 3. URL

- [ ] `digital_cafe/urls.py`: add
      `path('accounts/signup/', cafe_views.signup, name='signup')`
      next to the existing `django.contrib.auth.urls` include (import
      `cafe.views` there, or route through `cafe/urls.py` and adjust
      the include — whichever keeps `urls.py` cleanest; per the study
      doc, the URL itself must resolve to `/accounts/signup/`
      regardless of which urlconf file defines it).
- [ ] Commit: `feat: wire up /accounts/signup/`.

## 4. Signup template

- [ ] `templates/registration/signup.html`, following
      `templates/registration/login.html`'s existing structure/card
      styling: form with `{% csrf_token %}`, `{{ form.as_p }}`, hidden
      `next` field, submit button, and (per placement 3 in the study
      doc) an "Already have an account? Log in" link pointing to
      `{% url 'login' %}` (carrying `next` through as a query param
      too, so someone who lands on signup by mistake and clicks back to
      login doesn't lose their original destination).
- [ ] Commit: `feat: add signup page template`.

## 5. The other three "Sign up" placements

- [ ] `templates/base.html`: add a "Sign up" link next to "Log in" in
      the nav's existing anonymous-only branch.
- [ ] `templates/registration/login.html`: add a "Don't have an
      account? Sign up" link, carrying `next` through the same way.
- [ ] `templates/cafe/product_detail.html`: change the anonymous +
      active-product prompt from "Log in to add this to your cart" to
      offer both login and signup links (both carrying `?next=` back to
      that same product page, matching the existing login link's
      pattern).
- [ ] Commit: `feat: add sign-up links to nav, login page, and the product detail prompt`.

## 6. Manual verification pass

- [ ] Run the dev server, confirm, **logged out**:
  - [ ] `/accounts/signup/` loads, shows username/first name/password
        fields (no email field).
  - [ ] Submitting with a `username` that already exists shows Django's
        standard "A user with that username already exists" error, no
        account created, no crash.
  - [ ] Submitting with mismatched `password1`/`password2` shows the
        standard mismatch error.
  - [ ] Submitting a password that fails `AUTH_PASSWORD_VALIDATORS`
        (e.g. too short, or entirely numeric) is rejected with Django's
        standard validator error message.
  - [ ] Submitting valid data (with a `first_name`) creates the `User`,
        logs them in automatically (no second login step), and lands
        them on the expected page (`home` when there was no `next`).
  - [ ] Home page immediately shows `"Welcome, {first_name}!"` for that
        new user — confirms the `first_name` actually got saved and is
        wired into the existing greeting.
  - [ ] Repeat, this time starting from the product detail page's
        "sign up" link (with `next` pointing at that product) — confirm
        after signup they land back on that exact product page, not
        home, and can now see/use the real add-to-cart form.
  - [ ] Nav shows "Sign up" next to "Log in" when logged out.
  - [ ] Login page shows the "Sign up" cross-link; signup page shows
        the "Log in" cross-link.
- [ ] Confirm, **logged in** (regression check):
  - [ ] Nav no longer shows "Log in"/"Sign up" (unchanged from the
        public-browsing feature's existing behavior).
  - [ ] `/accounts/signup/` while already authenticated doesn't error
        (per the study doc, no special redirect-away guard is being
        added — just confirming it doesn't break, not that it does
        anything special).
- [ ] Fix anything broken found during this pass, committing fixes as
      `fix:` commits.

## 7. Rendezvous

- [ ] Merge `feat/public-signup` into `main`.
- [ ] Re-run the key checks from step 6 against `main` post-merge.
- [ ] Confirm `main` is left in a working, runnable state.

## 8. Sync docs

- [ ] Update `doc/wiki/routes.md`: add `/accounts/signup/` to the route
      table (no login required).
- [ ] Update `doc/wiki/overview.md`: its current "no public signup
      page" statement is now wrong and needs correcting to describe
      self-service signup.
- [ ] Update `doc/wiki/setup.md`: its "Creating accounts" section
      currently says a regular customer account can only be created by
      an admin via Django admin — note that customers can now also
      self-register via `/accounts/signup/`, while admin creation
      remains how you'd create a superuser (signup never grants
      staff/superuser status).
- [ ] Commit: `docs: sync wiki with public signup feature`.