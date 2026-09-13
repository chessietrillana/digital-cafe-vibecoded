# Study: Public Signup Page

Reverses `doc/study/0001-digital-cafe-mvp.md`'s Open Question 4, which
concluded "no public registration page for this version... customer
accounts are admin-created only," and directly interacts with
`doc/study/0003-public-browsing.md`, which made browsing public but left
the "Log in to add this to your cart" prompt as the only path forward
for an anonymous visitor. This doc covers adding self-service signup. No
code is written in this step.

## 1. Existing codebase — what this touches

- **Auth setup**: `django.contrib.auth.urls` is included at `/accounts/`
  in `digital_cafe/urls.py`, giving us `/accounts/login/` and
  `/accounts/logout/` for free via Django's built-in views. **Django
  does not ship a signup view or URL** — `contrib.auth.urls` covers
  login/logout/password-change/password-reset, but account *creation*
  is deliberately left to each project, since it's inherently
  app-specific (what fields, what happens after). This has to be a
  real view I write, not just a template override like
  `templates/registration/login.html` was.
- **`AUTH_PASSWORD_VALIDATORS`** (`digital_cafe/settings.py`) is already
  configured with all four of Django's standard validators
  (`UserAttributeSimilarityValidator`, `MinimumLengthValidator`,
  `CommonPasswordValidator`, `NumericPasswordValidator`). These already
  apply project-wide to any password set through Django's forms —
  relevant because it means signup's password validation is **already
  handled with zero new code**, not something to design.
- **`templates/base.html`'s nav** (as of `doc/study/0003-public-browsing.md`)
  is already conditional per-link: `Home` always, `Cart`/`Order
  History`/`Log out` when authenticated, `Log in` when not. This study
  needs to decide where `Sign up` fits into that same structure.
- **`templates/cafe/product_detail.html`**: for an anonymous visitor on
  an active product, currently shows only *"Log in to add this to your
  cart"* (added in the public-browsing feature) with no path to actually
  become a customer without already knowing to find a signup link
  elsewhere.
- **CLAUDE.md's tech-stack constraints**: "Django's built-in auth, no
  custom user model." This is fully respected by everything proposed
  below — no model changes, no migration, nothing added to
  `INSTALLED_APPS`.

## 2. Proposed form: `UserCreationForm`, with one addition

Django's built-in `django.contrib.auth.forms.UserCreationForm` is the
standard tool for exactly this — it's tied to the default `User` model
(no custom user model needed, matching CLAUDE.md), and out of the box
collects `username`, `password1`, `password2`, with matching-password
validation and full `AUTH_PASSWORD_VALIDATORS` enforcement built in via
its `clean_password2()`.

**Proposed addition: include `first_name` (optional) in the form.**
This isn't strictly necessary, but it's directly load-bearing for an
existing feature: the home page's greeting
(`request.user.first_name or request.user.username`) and
`doc/wiki/setup.md`'s own setup instructions currently say the *only*
way to get a named greeting is for an admin to manually set `First
name` in Django admin after the fact. There's no self-service profile
page in this app — if signup doesn't collect `first_name`, a
self-registered customer is permanently stuck being greeted by their
username unless an admin edits their account for them. Given that,
skipping it feels like an oversight rather than a deliberate scope cut,
but I'm flagging it as an explicit choice rather than silently expanding
the form (see Open Question 1).

Concretely: subclass `UserCreationForm`, add
`first_name = forms.CharField(required=False)` to `Meta.fields`
(alongside the default `"username"`) — `ModelForm`'s normal save
behavior sets it, no need to override `save()` beyond what
`UserCreationForm` already does for password hashing.

**Not proposing an email field.** Nothing in this app uses email
anywhere — no password-reset-by-email flow, no order confirmation
emails, no admin notifications. Adding it would just be an unused form
field. Flagged in Open Question 1 alongside `first_name` in case you'd
rather capture it for future use, but my default is to leave it out.

## 3. View, URL, and template

- **View**: a plain function-based `signup` view in `cafe/views.py`,
  matching this codebase's existing style (every other view here is a
  function, not a class-based view) — `GET` renders the form, `POST`
  validates + creates the user, then handles post-signup behavior (§4).
- **URL**: `/accounts/signup/`, registered in `digital_cafe/urls.py`
  right next to the existing `path('accounts/', include('django.contrib.auth.urls'))`,
  rather than inside `cafe/urls.py`'s own (root-level) URL space. This
  groups all three auth-related URLs under the same `/accounts/` prefix
  Django's own login/logout already use, even though signup itself has
  to be hand-written.
- **Template**: `templates/registration/signup.html`, following the
  same `registration/` naming convention already used for
  `login.html` — not because Django requires it for a custom view (it
  doesn't), just for consistency with the one auth template that
  already exists.

## 4. Post-signup behavior: auto-login, and `next` handling

**Proposed: log the new user in automatically** (call
`django.contrib.auth.login(request, user)` right after
`form.save()`), then redirect — rather than redirecting to the login
page and making them immediately re-enter the same credentials they
just typed. There's no email verification step in this app, so there's
no reason to interpose a second login; the friction of "type your
password twice in a row" is pure cost with no offsetting benefit here.

**Proposed: honor `?next=`, exactly like the login page does.**
`templates/registration/login.html` already carries `next` through a
hidden field (added during the public-browsing work) so that, e.g.,
clicking "Log in to add this to your cart" from a product page returns
the visitor to that same product after logging in. If a "Sign up" link
is added in that same spot (§5), signup should behave identically —
carry `next` through the same way, redirect there after the new
account is created and auto-logged-in. This is a direct, low-judgment
extension of a pattern this app already has, not a new design decision.

## 5. Where should "Sign up" appear?

Three places, proposed together since they're the same underlying
pattern (offering signup wherever login is currently offered to an
anonymous visitor):

1. **Nav** (`templates/base.html`): add a "Sign up" link next to "Log
   in" in the already-conditional (`{% if %}...{% else %}`) block —
   `Home | Log in | Sign up` when anonymous.
2. **Login page**: a "Don't have an account? Sign up" link — standard
   cross-link pattern, costs nothing, directly useful for a visitor who
   landed on login without an account.
3. **Signup page**: the reverse — "Already have an account? Log in."
4. **Product detail page, anonymous + active product** (the case §1
   flagged): change *"Log in to add this to your cart"* to offer both,
   e.g. *"[Log in](…) or [sign up](…) to add this to your cart"* — this
   is the concrete answer to your question about whether public
   browsing and signup should interact. Right now an anonymous visitor
   who wants to buy something only sees a path for people who already
   have an account; adding signup without surfacing it here would leave
   that gap unaddressed.

All four reuse the same `?next=` value where relevant (the product-page
one in particular — see §4).

## 6. Validation — mostly already handled, nothing new to design

Per your prompt's explicit concerns:

- **Duplicate usernames**: already handled. `User.username` is
  `unique=True` at the model level, and `UserCreationForm` already
  validates this and raises "A user with that username already
  exists." — no new code.
- **Password requirements**: already handled, per §1 —
  `AUTH_PASSWORD_VALIDATORS` is global, already configured, and
  `UserCreationForm` already enforces it. Same rules that would apply
  to a password an admin sets for someone in Django admin.
- **Username character rules**: Django's default `UnicodeUsernameValidator`
  (letters, digits, and `@/./+/-/_`, ≤150 chars) applies automatically;
  not proposing anything custom here.
- **Not proposing**: email verification, CAPTCHA/bot protection, terms-of-service
  acceptance, or rate-limiting signup attempts. None of these were
  asked for, and this is a course project without the exposure that
  would justify them — flagging only so leaving them out reads as a
  deliberate scope boundary, not an oversight.

## 7. Design options considered and rejected

- **Custom `User` model / custom signup fields beyond `first_name`** —
  rejected outright; CLAUDE.md's tech stack section is explicit: "no
  custom user model."
- **Class-based `CreateView`** — Django's more common pattern for this
  exact flow, but this codebase's `cafe/views.py` is 100% function-based
  views throughout; matching that existing style over introducing the
  only CBV in the project.
- **Email field** — rejected per §2; nothing in the app uses it.
- **Redirect-to-login instead of auto-login after signup** — considered
  and presented as the main open question below rather than silently
  decided, since reasonable apps do either.

## 8. Open questions — resolved

All resolved after your review; recorded here for the historical record:

1. **Collect `first_name` at signup? — RESOLVED: yes.** Confirmed it'd
   be a real gap otherwise.
2. **Auto-login after signup vs. redirect to login? — RESOLVED:
   auto-login.** Confirmed no reason to make a new user re-enter
   credentials with no email verification step in play.
3. **How many of the four "Sign up" placements? — RESOLVED: all four**
   (nav, login page cross-link, signup page cross-link, product-detail
   prompt). Explicitly wanted fully closed, not partially — the whole
   point of this feature is closing the gap public browsing opened.