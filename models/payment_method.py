from app import db


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(32), unique=True, nullable=False)
    has_installments = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    @staticmethod
    def seed_defaults():
        from app import db as database
        defaults = [
            ('Nakit', 'cash', False, 1),
            ('Kredi Kartı Peşin', 'credit_card_single', False, 2),
            ('Kredi Kartı Taksitli', 'credit_card_installment', True, 3),
            ('Altın', 'gold', False, 4),
            ('Havale/EFT', 'transfer', False, 5),
        ]
        for name, slug, has_inst, order in defaults:
            if not PaymentMethod.query.filter_by(slug=slug).first():
                database.session.add(PaymentMethod(
                    name=name, slug=slug,
                    has_installments=has_inst, order=order
                ))
        database.session.commit()

    def __repr__(self):
        return f'<PaymentMethod {self.name}>'
