# Production Bug Fixes Plan

## Bug 1: Personal seed data leaks into fresh installs

**Root cause:** [`routes/auth.py:48-50`](routes/auth.py:48) auto-calls `Category.seed_defaults()`, `Financier.seed_defaults()`, `PaymentMethod.seed_defaults()` inside `/seed-admin`. These inject hardcoded personal data:
- Financiers: `Hasan`, `Babam`, `Annem`, `Dükkan`, `Altın`, `Diğer` ([`models/financier.py:13`](models/financier.py:13))
- Categories: `Kira`, `Elektrik/Tedaş`, `Su`, `Yakıt`... ([`models/category.py:19`](models/category.py:19))

**Fix:** Remove the three `seed_defaults()` calls from `/seed-admin`. The route should ONLY create the admin user. Customer adds their own financiers/categories/payment methods via the Yönetim UI.

> Note: `seed_sample_data.py` (dev script) keeps its seed calls — only the production `/seed-admin` route is cleaned.

---

## Bug 2: "+" quick-add buttons return "Yetkisiz erişim" for non-admin users

**Root cause:** `quick_add` endpoints all call `require_admin()` which checks ONLY `current_user.is_admin`:
- [`routes/financiers.py:78`](routes/financiers.py:78)
- [`routes/categories.py:80`](routes/categories.py:80)
- [`routes/payment_methods.py:99`](routes/payment_methods.py:99)

A non-admin user with `can_add_transaction=True` hits 403 when clicking "+".

**Fix:** Replace `require_admin()` in the three `quick_add` endpoints with a permission check on `can_add_transaction`. The "+" buttons only appear on the add-transaction form, so `can_add_transaction` is the correct gate. Admins (who have all permissions via [`get_permissions()`](models/user.py:26)) keep access.

New helper pattern per route file:
```python
def require_add_transaction():
    if not current_user.get_permissions().get('can_add_transaction'):
        return jsonify(success=False, error='Yetkisiz erişim'), 403
    return None
```

The full management list pages (`/financiers`, `/categories`, `/payment_methods`) keep `require_admin()` — those are admin-only management screens. Only the inline `quick_add` endpoints change.

---

## Bug 3: New user with `can_manage_users` cannot access Users screen

**Root cause:** [`routes/users.py:19`](routes/users.py:19) `list()` (and `create`, `edit`) call `require_admin()` checking only `is_admin`. The sidebar link correctly shows via [`base.html:60`](templates/base.html:60) (`user_permissions.can_manage_users`), but the route blocks the non-admin user who has that permission.

**Fix:** Replace `require_admin()` in `routes/users.py` with a `can_manage_users` permission check:
```python
def require_manage_users():
    if not current_user.get_permissions().get('can_manage_users'):
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None
```
Apply to `list`, `create`, `edit`.

> Consistency note: This aligns the route guard with the sidebar visibility logic in [`base.html`](templates/base.html), so the link and the access rule always agree.

---

## Files to modify

1. [`routes/auth.py`](routes/auth.py) — remove 3 `seed_defaults()` calls + their imports (lines 43-50).
2. [`routes/financiers.py`](routes/financiers.py) — `quick_add` uses `can_add_transaction` check.
3. [`routes/categories.py`](routes/categories.py) — `quick_add` uses `can_add_transaction` check.
4. [`routes/payment_methods.py`](routes/payment_methods.py) — `quick_add` uses `can_add_transaction` check.
5. [`routes/users.py`](routes/users.py) — `list`/`create`/`edit` use `can_manage_users` check.

## Verification

- Fresh install: `/seed-admin` creates only admin, no financiers/categories/methods pre-filled.
- Non-admin user with `can_add_transaction`: "+" buttons on add-transaction form work (financier/category/method quick-add).
- Non-admin user with `can_manage_users`: can open `/users`, create/edit users.
- Admin user: all of the above still work (admin permissions are all-True via `get_permissions()`).
