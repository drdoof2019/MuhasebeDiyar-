# UX Improvements Plan - Transaction Form & Navigation

## Issues Identified

1. **Date not auto-filled** — Transaction add form starts with empty date
2. **No quick-add for dropdowns** — Kategori, Kim ödedi, Ödeme tipi have no inline + buttons
3. **Hardcoded payment methods** — Cannot add new payment types without code change
4. **No category filtering** — All categories shown regardless of entry type (Gider/Gelir)
5. **Note column too narrow** — payer_note is `col-md-1`, barely visible
6. **Yearly report icon broken** — `bi-calendar-year` is not a valid Bootstrap Icon
7. **No payment method management page** — Admin can't add/edit/delete payment methods

---

## Step 1: Auto-fill Today's Date

**File:** `templates/transactions/add.html`

Change the date input default value from empty to today:
```html
value="{{ request.form.get('date', '') if request.form else today_date }}"
```

**File:** `routes/transactions.py`

In `add()` route, pass `today_date`:
```python
from datetime import date
today_date = date.today().strftime('%Y-%m-%d')
```

---

## Step 2: PaymentMethod Model + Migration

**New file:** `models/payment_method.py`

```python
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)      # "Nakit", "Kredi Kartı Peşin"
    slug = db.Column(db.String(32), unique=True, nullable=False)  # "cash", "credit_card_single"
    has_installments = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
```

Default seed data:
| name | slug | has_installments | order |
|------|------|-----------------|-------|
| Nakit | cash | False | 1 |
| Kredi Kartı Peşin | credit_card_single | False | 2 |
| Kredi Kartı Taksitli | credit_card_installment | True | 3 |
| Altın | gold | False | 4 |
| Havale/EFT | transfer | False | 5 |

`TransactionPayer.payment_method` stays as `String(32)` — no schema change needed. The slug in PaymentMethod matches the stored value.

---

## Step 3: Payment Method Management Page

**New file:** `routes/payment_methods.py`
- Admin-only CRUD with `require_admin()` same pattern as categories
- `POST /payment_methods` — add new (name, has_installments checkbox)
- `POST /payment_methods` action=edit — rename
- `POST /payment_methods` action=delete — delete if no linked payers
- Auto-generate slug from name: `name.lower().replace(' ', '_').replace('ı','i').replace('ü','u').replace('ö','o').replace('ş','s').replace('ç','c').replace('ğ','g')`

**New file:** `templates/payment_methods/list.html`
- Same layout as categories/financiers: left form + right table
- Columns: Adı, Slug identifier, Taksitli mi?, İşlem sayısı, İşlemler

**Modify:** `app.py` — register `payment_methods_bp` blueprint

---

## Step 4: Quick-Add + Buttons on Transaction Form

### Dropdown + Button Layout

Each dropdown gets an inline + button appended:

```html
<div class="d-flex align-items-center gap-1">
    <select class="form-select flex-grow-1" id="category_id" name="category_id">
        ...
    </select>
    <button type="button" class="btn btn-outline-primary btn-sm flex-shrink-0" 
            data-bs-toggle="modal" data-bs-target="#quickAddCategoryModal" title="Yeni kategori ekle">
        <i class="bi bi-plus"></i>
    </button>
</div>
```

### Quick-Add Modals

Three Bootstrap modals in add.html and edit.html:

1. **quickAddCategoryModal** — Name input + Type select (expense/income/both)
2. **quickAddFinancierModal** — Name input
3. **quickAddPaymentMethodModal** — Name input + Has installments checkbox

Each modal submits via `fetch()` to a quick-add endpoint, gets back JSON with the new record, and:
- Adds the new option to the dropdown
- Selects it automatically
- Closes the modal

### AJAX Endpoints

**`routes/categories.py`** — Add route:
```python
@categories_bp.route('/categories/quick_add', methods=['POST'])
@login_required
def quick_add():
    name = request.form.get('name', '').strip()
    cat_type = request.form.get('type', 'expense')
    # ... create category, return jsonify(id=c.id, name=c.name, type=c.type)
```

**`routes/financiers.py`** — Add route:
```python
@financiers_bp.route('/financiers/quick_add', methods=['POST'])
@login_required
def quick_add():
    name = request.form.get('name', '').strip()
    # ... create financier, return jsonify(id=f.id, name=f.name)
```

**`routes/payment_methods.py`** — Add route:
```python
@payment_methods_bp.route('/payment_methods/quick_add', methods=['POST'])
@login_required
def quick_add():
    name = request.form.get('name', '').strip()
    has_installments = request.form.get('has_installments') == 'on'
    # ... create method, return jsonify(id=m.id, name=m.name, slug=m.slug, has_installments=m.has_installments)
```

---

## Step 5: Filter Categories by Entry Type

**JavaScript logic in add.html and edit.html:**

When entry_type changes:
- **Gider** → show categories where type = `expense` or `both`
- **Gelir** → show categories where type = `income` or `both`
- **Altın Bozumu / Kasa Notu** → show all categories (or hide category field)

Implementation:
1. Render all categories in the `<select>` but add `data-type` attribute to each `<option>`
2. On `entry_type` change, hide/show options based on their `data-type`
3. If currently selected category becomes hidden, deselect it

```html
<option value="{{ c.id }}" data-type="{{ c.type }}" ...>
    {{ c.name }}
</option>
```

```javascript
function filterCategories() {
    const entryType = document.getElementById('entry_type').value;
    const select = document.getElementById('category_id');
    const options = select.querySelectorAll('option');
    
    options.forEach(opt => {
        if (!opt.value) return; // "-- Seçiniz --"
        const catType = opt.dataset.type;
        if (entryType === 'gold_conversion' || entryType === 'cash_note') {
            opt.style.display = '';
        } else if (entryType === 'expense') {
            opt.style.display = (catType === 'expense' || catType === 'both') ? '' : 'none';
        } else if (entryType === 'income') {
            opt.style.display = (catType === 'income' || catType === 'both') ? '' : 'none';
        }
    });
}
```

This function runs on page load and on `entry_type` change.

---

## Step 6: Widen Payer Note Column

**Current:** `col-md-1` for Note column  
**Change to:** `col-md-2` for Note, reduce Financier from `col-md-3` to `col-md-3` keep

Adjusted payer row layout:
| Field | Current | New |
|-------|---------|-----|
| Kim ödedi | col-md-3 | col-md-3 |
| Tutar | col-md-2 | col-md-2 |
| Ödeme tipi | col-md-3 | col-md-3 |
| Taksit | col-md-2 | col-md-2 |
| Not | col-md-1 | **col-md-2** |
| Sil | col-md-1 | col-md-0 (icon only) |

Apply in: `add.html`, `edit.html`, and the JS `addPayerRow()` function.

---

## Step 7: Fix Yearly Report Icon

**File:** `templates/base.html` line 44

Change `bi-calendar-year` to `bi-calendar3` — `bi-calendar-year` does not exist in Bootstrap Icons.

```html
<!-- Before -->
<i class="bi bi-calendar-year me-2"></i> Yıllık Rapor
<!-- After -->
<i class="bi bi-calendar3 me-2"></i> Yıllık Rapor
```

---

## Step 8: Sidebar Reorganization

Group admin management links under a collapsible submenu:

```html
{% if current_user.is_admin %}
<a href="#adminSubmenu" class="list-group-item ..." data-bs-toggle="collapse">
    <i class="bi bi-gear me-2"></i> Yönetim
    <i class="bi bi-chevron-down float-end small"></i>
</a>
<div class="collapse" id="adminSubmenu">
    <a href="{{ url_for('categories.list') }}" class="list-group-item ... ps-5">
        <i class="bi bi-tags me-2"></i> Kategoriler
    </a>
    <a href="{{ url_for('financiers.list') }}" class="list-group-item ... ps-5">
        <i class="bi bi-person-badge me-2"></i> Finansörler
    </a>
    <a href="{{ url_for('payment_methods.list') }}" class="list-group-item ... ps-5">
        <i class="bi bi-credit-card me-2"></i> Ödeme Yöntemleri
    </a>
</div>
{% endif %}
```

---

## Step 9: Dynamic Payment Method Dropdowns

**File:** `routes/transactions.py`

Pass `payment_methods` to add/edit templates:
```python
payment_methods = PaymentMethod.query.order_by(PaymentMethod.order).all()
```

**File:** `add.html`, `edit.html`

Replace hardcoded `<option>` values with Jinja2 loop:
```html
{% for pm in payment_methods %}
<option value="{{ pm.slug }}" data-has-installments="{{ 'true' if pm.has_installments else 'false' }}">
    {{ pm.name }}
</option>
{% endfor %}
```

Update `toggleInstallment()` JS to check `data-has-installments` instead of hardcoded value:
```javascript
function toggleInstallment(select) {
    const row = select.closest('.payer-row');
    const instGroup = row.querySelector('.installment-count-group');
    const hasInstallments = select.selectedOptions[0].dataset.hasInstallments === 'true';
    instGroup.style.display = hasInstallments ? 'block' : 'none';
}
```

Also update the `addPayerRow()` JS function to use `payment_methods` data from server.

---

## Files to Create
| File | Purpose |
|------|---------|
| `models/payment_method.py` | PaymentMethod model |
| `routes/payment_methods.py` | CRUD + quick_add routes |
| `templates/payment_methods/list.html` | Management page |

## Files to Modify
| File | Changes |
|------|---------|
| `app.py` | Register PaymentMethod model + blueprint; pass payment_methods + today_date to templates |
| `models/__init__.py` | Import PaymentMethod |
| `routes/transactions.py` | Pass payment_methods; add today_date for add form |
| `routes/categories.py` | Add quick_add AJAX endpoint |
| `routes/financiers.py` | Add quick_add AJAX endpoint |
| `seed_sample_data.py` | Seed PaymentMethod defaults |
| `templates/transactions/add.html` | Auto-date, + buttons, modals, category filtering, wider note, dynamic payment methods |
| `templates/transactions/edit.html` | Same changes as add.html |
| `templates/base.html` | Fix icon, group admin links submenu |
| `static/js/app.js` or inline | Category filter JS, modal JS |