from app import db


class Financier(db.Model):
    __tablename__ = 'financiers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    @staticmethod
    def seed_defaults():
        from app import db as database
        defaults = ['Hasan', 'Babam', 'Annem', 'Dükkan', 'Altın', 'Diğer']
        for name in defaults:
            if not Financier.query.filter_by(name=name).first():
                database.session.add(Financier(name=name))
        database.session.commit()

    def __repr__(self):
        return f'<Financier {self.name}>'
