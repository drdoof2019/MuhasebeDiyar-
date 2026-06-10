# Plan: Dynamic Payer Labels + Income/Expense Report Filters

## Overview

Two user requests:
1. **Dynamic payer labels**: The "Ödeme Yapanlar" section in transaction forms always implies expense/payer. For income entries, it should say "Gelen Ödemeler" / "Kimden geldi?" etc.
2. **Income/Expense report filters**: Category and Financier reports should allow filtering by entry type (Gider/Gelir/Tümü).

---

## Task A: Dynamic Payer Section Labels

### Files to modify:
- `templates/transactions/add.html`
- `templates/transactions/edit.html`

### Changes:

#### 1. Add `id` attributes to static HTML elements (both files)

Current:
```html
<h6 class="mb-0">Ödeme Yapanlar</h6>
```
→ Change to:
```html
<h6 class="mb-0" id="payersSectionTitle">Ödeme Yapanlar</h6>
```

Current add button text:
```html
<i class="bi bi-plus-circle me-1"></i> Ödeyen Ekle
```
→ Change to:
```html
<i class="bi bi-plus-circle me-1"></i> <span id="addPayerBtnText">Ödeyen Ekle</span>
```

#### 2. Add `changePayerLabels()` JS function (both files)

```javascript
function changePayerLabels() {
    const type = document.getElementById('entry_type').value;
    const title = document.getElementById('payersSectionTitle');
    const btnText = document.getElementById('addPayerBtnText');
    
    // Also update all existing payer dropdown placeholders
    const placeholders = document.querySelectorAll('select[name="payer_financier_id[]"] option[value=""]');
    
    const labels = {
        'expense': { title: 'Ödeme Yapanlar', btn: 'Ödeyen Ekle', placeholder: '-- Kim ödedi? --' },
        'income': { title: 'Gelen Ödemeler', btn: 'Kişi Ekle', placeholder: '-- Kimden geldi? --' },
        'gold_conversion': { title: 'Altın Kaynağı', btn: 'Ekle', placeholder: '-- Kimin altını? --' },
        'cash_note': { title: 'İlgili Kişiler', btn: 'Ekle', placeholder: '-- Kim? --' }
    };
    
    const label = labels[type] || labels['expense'];
    if (title) title.textContent = label.title;
    if (btnText) btnText.textContent = label.btn;
    placeholders.forEach(opt => opt.textContent = label.placeholder);
}
```

#### 3. Call `changePayerLabels()` from existing functions

In `toggleEntryType()`, add `changePayerLabels()` call.
In `DOMContentLoaded` handler, add `changePayerLabels()` call.

#### 4. Update `addPayerRow()` dynamic HTML

The dynamically generated payer row uses hardcoded `-- Kim ödedi? --`. Change it to use the current entry type's label:

```javascript
function getPayerPlaceholder() {
    const type = document.getElementById('entry_type').value;
    const map = {
        'expense': '-- Kim ödedi? --',
        'income': '-- Kimden geldi? --',
        'gold_conversion': '-- Kimin altını? --',
        'cash_note': '-- Kim? --'
    };
    return map[type] || '-- Kim ödedi? --';
}
```

Then in `addPayerRow()`:
```javascript
'<option value="">' + getPayerPlaceholder() + '</option>' + finOptions +
```

---

## Task B: Category Report — Entry Type Filter

### Files to modify:
- `routes/reports.py` — `category()` function
- `templates/reports/category.html`

### Route changes (`routes/reports.py`):

```python
@reports_bp.route('/reports/category')
@login_required
def category():
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', type=int)
    entry_type = request.args.get('entry_type', 'expense')  # NEW: default to expense

    query = db.session.query(
        Category.name,
        func.sum(Transaction.total_amount).label('total')
    ).join(Transaction)

    # Apply entry_type filter
    if entry_type and entry_type != 'all':
        query = query.filter(Transaction.entry_type == entry_type)

    if year:
        query = query.filter(extract('year', Transaction.date) == year)
    if month:
        query = query.filter(extract('month', Transaction.date) == month)

    results = query.group_by(Category.name).order_by(func.sum(Transaction.total_amount).desc()).all()

    years = db.session.query(func.distinct(extract('year', Transaction.date))).order_by(
        extract('year', Transaction.date).desc()
    ).all()
    years = [int(y[0]) for y in years if y[0]]

    return render_template('reports/category.html', 
                           results=results, year=year, month=month, years=years,
                           entry_type=entry_type)  # NEW
```

### Template changes (`templates/reports/category.html`):

1. Add entry_type dropdown to filter form (after month dropdown):
```html
<div class="col-auto">
    <label class="form-label small">İşlem Tipi</label>
    <select class="form-select form-select-sm" name="entry_type" onchange="this.form.submit()">
        <option value="expense" {{ 'selected' if entry_type == 'expense' else '' }}>Gider</option>
        <option value="income" {{ 'selected' if entry_type == 'income' else '' }}>Gelir</option>
        <option value="all" {{ 'selected' if entry_type == 'all' else '' }}>Tümü</option>
    </select>
</div>
```

2. Dynamic page title:
```jinja2
{% block page_title %}Kategori Raporu ({% if entry_type == 'expense' %}Giderler{% elif entry_type == 'income' %}Gelirler{% else %}Tümü{% endif %}){% endblock %}
```

3. Dynamic table header:
```html
<th>Kategori</th>
<th class="text-end">{% if entry_type == 'income' %}Toplam Gelir{% elif entry_type == 'expense' %}Toplam Gider{% else %}Toplam Tutar{% endif %}</th>
```

4. Dynamic amount color class:
```html
<td class="text-end {% if entry_type == 'income' %}text-success{% elif entry_type == 'expense' %}text-danger{% else %}fw-bold{% endif %}">
```

5. Dynamic chart title:
```javascript
title: { display: true, text: '{% if entry_type == "income" %}Kategorilere Göre Gelir Dağılımı{% elif entry_type == "expense" %}Kategorilere Göre Gider Dağılımı{% else %}Kategorilere Göre Dağılım{% endif %}', font: { size: 14 } }
```

6. Dynamic chart colors (income = green tones, expense = red tones, all = mixed):
```javascript
backgroundColor: {% if entry_type == 'income' %}['#198754', '#20c997', '#0dcaf0', '#0d6efd', '#6610f2', '#6f42c1']{% elif entry_type == 'expense' %}['#dc3545', '#fd7e14', '#ffc107', '#6c757d', '#495057', '#d63384']{% else %}['#dc3545', '#198754', '#fd7e14', '#0d6efd', '#ffc107', '#6f42c1']{% endif %}
```

---

## Task C: Financier Report — Entry Type Filter

### Files to modify:
- `routes/reports.py` — `financier()` function
- `templates/reports/financier.html`

### Route changes (`routes/reports.py`):

```python
@reports_bp.route('/reports/financier')
@login_required
def financier():
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', type=int)
    entry_type = request.args.get('entry_type', 'all')  # NEW: default to all for backward compat

    query = db.session.query(
        Financier.name,
        func.sum(TransactionPayer.amount).label('total')
    ).join(TransactionPayer).join(Transaction)

    # Apply entry_type filter
    if entry_type and entry_type != 'all':
        query = query.filter(Transaction.entry_type == entry_type)

    if year:
        query = query.filter(extract('year', Transaction.date) == year)
    if month:
        query = query.filter(extract('month', Transaction.date) == month)

    results = query.group_by(Financier.name).order_by(func.sum(TransactionPayer.amount).desc()).all()

    years = db.session.query(func.distinct(extract('year', Transaction.date))).order_by(
        extract('year', Transaction.date).desc()
    ).all()
    years = [int(y[0]) for y in years if y[0]]

    return render_template('reports/financier.html',
                           results=results, year=year, month=month, years=years,
                           entry_type=entry_type)  # NEW
```

### Template changes (`templates/reports/financier.html`):

1. Add entry_type dropdown to filter form (same as category but with `all` default)
2. Dynamic page title:
```jinja2
{% block page_title %}Finansör Raporu ({% if entry_type == 'expense' %}Giderler{% elif entry_type == 'income' %}Gelirler{% else %}Tümü{% endif %}){% endblock %}
```

3. Dynamic table header:
```html
<th>Finansör</th>
<th class="text-end">{% if entry_type == 'income' %}Toplam Gelir{% elif entry_type == 'expense' %}Toplam Gider{% else %}Toplam Tutar{% endif %}</th>
```

4. Dynamic chart title and amount color (same pattern as category)

---

## Summary of files to modify

| File | Changes |
|------|---------|
| `templates/transactions/add.html` | Add ids to payer section elements, add `changePayerLabels()` + `getPayerPlaceholder()` JS, update `addPayerRow()`, call from `toggleEntryType()` and `DOMContentLoaded` |
| `templates/transactions/edit.html` | Same JS changes as add.html |
| `routes/reports.py` | Add `entry_type` param to `category()` and `financier()` routes, pass to template |
| `templates/reports/category.html` | Add entry_type dropdown, dynamic title/header/chart |
| `templates/reports/financier.html` | Add entry_type dropdown, dynamic title/header/chart |