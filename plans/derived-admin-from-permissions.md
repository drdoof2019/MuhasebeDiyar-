# Derived Admin From Permissions — Plan

## Goal
`is_admin` becomes a derived flag: if ALL 6 permission checkboxes are checked → admin; if any is unchecked → regular user. Removes the separate admin concept from the UI — one permission grid controls everything.

## The 6 permissions (ALL must be True for admin)
`can_view_transactions`, `can_add_transaction`, `can_edit_transaction`, `can_delete_transaction`, `can_view_reports`, `can_manage_users`

## Changes

### 1. [`routes/users.py`](routes/users.py)
Add module-level constant + helper:
```python
ALL_PERMS = (
    'can_view_transactions', 'can_add_transaction', 'can_edit_transaction',
    'can_delete_transaction', 'can_view_reports', 'can_manage_users',
)

def _is_all_perms(form):
    return all(p in form for p in ALL_PERMS)
```

**`create()`** ([`routes/users.py:26`](routes/users.py:26)):
- Replace `is_admin=False` with `is_admin=_is_all_perms(request.form)`.

**`edit()`** ([`routes/users.py:73`](routes/users.py:73)):
- Compute `is_admin = _is_all_perms(request.form)`.
- **Safety guard**: if demoting (`user.is_admin and not is_admin`) and this is the last admin (`User.query.filter_by(is_admin=True).count() <= 1`), block with flash "Son yöneticiyi düşüremezsiniz" — prevents total lockout in production.
- Set `user.is_admin = is_admin`.
- If `user.permissions` is None (seeded admin has no Permission row), CREATE a new Permission row; else update existing fields. Currently the code skips permission updates when `user.permissions` is falsy.

### 2. [`templates/users/create.html`](templates/users/create.html:28)
- Add an info note under the "Yetkiler" heading: *"Tüm yetkileri işaretlerseniz kullanıcı yönetici olur."*
- (Optional) small JS live "Yönetici" badge when all 6 checked — minor UX nicety.

### 3. [`templates/users/edit.html`](templates/users/edit.html:35)
- Remove the `{% if not user.is_admin %} ... {% else %} <info alert> {% endif %}` wrapper (lines 35-83) so the permission grid is **always editable**.
- Change each checkbox `checked` state from:
  `user.permissions and user.permissions.can_X`
  to:
  `user.is_admin or (user.permissions and user.permissions.can_X)`
  → seeded admin (no Permission row) shows all 6 checked.
- Add the same info note about all-permissions = admin.

### 4. [`templates/users/list.html`](templates/users/list.html:31)
No change — already shows "Yönetici" / "Kullanıcı" badge based on `is_admin`, which is now derived.

## Result
- Grant all 6 permissions → badge "Yönetici", full access.
- Uncheck any permission → badge "Kullanıcı", limited access.
- Cannot lock out the system: last admin can't be demoted.

## Files to modify
1. [`routes/users.py`](routes/users.py) — `create()` + `edit()` logic
2. [`templates/users/create.html`](templates/users/create.html) — info note (+ optional JS badge)
3. [`templates/users/edit.html`](templates/users/edit.html) — always show permission grid, default-checked for admin
