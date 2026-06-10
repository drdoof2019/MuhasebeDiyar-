from app import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    entry_type = db.Column(db.String(16), nullable=False, default='expense')
    # expense, income, gold_conversion, cash_note
    description = db.Column(db.String(512), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    gold_grams = db.Column(db.Float, nullable=True)
    note = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payers = db.relationship('TransactionPayer', backref='transaction',
                             lazy='joined', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='transactions')

    @property
    def financier_summary(self):
        """Return a summary string like: Hasan: 13.310TL + Babam: 120.000TL (kart 6 taksit)"""
        parts = []
        for p in self.payers:
            method_str = ''
            if p.payment_method == 'credit_card_single':
                method_str = ' (kart peşin)'
            elif p.payment_method == 'credit_card_installment':
                method_str = f' (kart {p.installment_count} taksit)'
            elif p.payment_method == 'gold':
                method_str = ' (altın)'
            parts.append(f'{p.financier.name}: {p.amount:,.0f}TL{method_str}')
        return ', '.join(parts)

    @property
    def gold_grams_display(self):
        if self.gold_grams:
            return f'{self.gold_grams} gr'
        return ''

    def __repr__(self):
        return f'<Transaction {self.entry_type} {self.description[:30]} {self.total_amount}TL>'


class TransactionPayer(db.Model):
    __tablename__ = 'transaction_payers'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    financier_id = db.Column(db.Integer, db.ForeignKey('financiers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(32), nullable=False, default='cash')
    # cash, credit_card_single, credit_card_installment, gold, transfer
    installment_count = db.Column(db.Integer, nullable=True)
    installment_start_date = db.Column(db.Date, nullable=True)
    note = db.Column(db.String(256), nullable=True)

    financier = db.relationship('Financier', lazy='joined')

    def __repr__(self):
        return f'<Payer {self.financier.name} {self.amount}TL>'
