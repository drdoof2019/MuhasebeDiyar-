from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    type = db.Column(db.String(16), nullable=False, default='expense')  # expense, income, both

    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'

    @staticmethod
    def seed_defaults():
        from app import db as database
        defaults = [
            ('Kira', 'expense'),
            ('Elektrik/Tedaş', 'expense'),
            ('Su', 'expense'),
            ('Yakıt', 'expense'),
            ('Yemek', 'expense'),
            ('Malzeme', 'expense'),
            ('Ekipman', 'expense'),
            ('Nakliye', 'expense'),
            ('Kargo', 'expense'),
            ('Vergi', 'expense'),
            ('Oda/Meslek Kaydı', 'expense'),
            ('Muhasebe', 'expense'),
            ('Tabela/Reklam', 'expense'),
            ('Dikiş/İplik', 'expense'),
            ('Hırdavat', 'expense'),
            ('Servis Geliri', 'income'),
            ('Diğer Gelir', 'income'),
        ]
        for name, cat_type in defaults:
            if not Category.query.filter_by(name=name).first():
                database.session.add(Category(name=name, type=cat_type))
        database.session.commit()
