# Payer Section Redesign Plan

## Problems

1. **Payer row layout feels cramped and doesn't adapt well** for income mode ("Gelen Ödemeler"). The labeled columns (Kim/Firma, Tutar, Ödeme Yöntemi, Taksit, Not) in a single row are too tight.
2. **No delete button** on payer rows — `removePayerRow()` exists in JS but is never called. Accidentally added rows cannot be removed.

## Design: Card-Style Payer Rows

### Layout Change

Each payer row becomes a **mini-card** with:

- **Card header** row: dynamic label like "1. Ödeyen" / "1. Kişi" on the left, red ✕ delete button on the right
- **Card body** in a **2-row layout** for breathing room:
  - Row 1: Kişi/Firma select (col-5) + Tutar input (col-3) + Ödeme Yöntemi select (col-4)
  - Row 2: Taksit Sayısı (col-3, shown/hidden based on method) + Not (col-9, or col-rest)

### Delete Button

- Small `btn-outline-danger` ✕ button with `bi-x` icon, positioned in the card header
- **Hidden on the last remaining row** so at least 1 payer always exists
- For the **first/static row** in HTML template: delete button has `onclick="removePayerRow(this)"`
- For **dynamically added rows**: same button, but the first row's delete button shows/hides based on total row count

### Dynamic Labels in Card Headers

The card header text gets a class `payer-row-label` so `changePayerLabels()` can target it:

| entry_type      | Section Title     | Add Button   | Row Label   | Placeholder          |
|-----------------|-------------------|--------------|-------------|----------------------|
| expense         | Ödeme Yapanlar    | Ödeyen Ekle  | Ödeyen      | -- Kim ödedi? --     |
| income          | Gelen Ödemeler    | Kişi Ekle    | Kişi        | -- Kimden geldi? --  |
| gold_conversion | Altın Kaynağı     | Ekle         | Kaynak      | -- Kimin altını? --  |
| cash_note       | İlgili Kişiler     | Ekle         | Kişi        | -- Kim? --           |

Each row label is numbered: "1. Ödeyen", "2. Ödeyen", etc. — recalculated on add/remove.

### JS Changes

1. **`addPayerRow()`** — generates card-style HTML with header + delete button
2. **`removePayerRow(btn)`** — removes the `.payer-row` card, then updates row numbers and shows/hides delete buttons
3. **`updatePayerRowLabels()`** — new function to re-number all row labels and toggle delete button visibility
4. **`changePayerLabels()`** — calls `updatePayerRowLabels()` after changing text

### Visual Comparison

**Before** (single flat row with column labels):
```
┌─────────────────────────────────────────────────────────────────────┐
│ Kim/Firma ▼[+│ Tutar  │ Ödeme Ynt ▼[+│ Taksit │ Not            │
└─────────────────────────────────────────────────────────────────────┘
```

**After** (card with header + 2-row body):
```
┌ 1. Ödeyen                                        ✕ ┐
│ ┌──────────────────┐ ┌────────┐ ┌────────────────┐ │
│ │ Kişi/Firma ▼ [+] │ │ Tutar  │ │ Ödeme Ynt ▼[+]│ │
│ └──────────────────┘ └────────┘ └────────────────┘ │
│ ┌──────────┐ ┌──────────────────────────────────┐  │
│ │ Taksit    │ │ Not                              │  │
│ └──────────┘ └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Files to Modify

1. **`templates/transactions/add.html`** — redesign HTML + JS
2. **`templates/transactions/edit.html`** — mirror same changes

## Files Already Complete (no changes needed)

- `routes/reports.py` — entry_type filter already added
- `templates/reports/category.html` — Tür dropdown already added
- `templates/reports/financier.html` — Tür dropdown already added