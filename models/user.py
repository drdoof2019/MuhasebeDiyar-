from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    permissions = db.relationship('Permission', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_permissions(self):
        if self.is_admin:
            return {
                'can_view_transactions': True,
                'can_add_transaction': True,
                'can_edit_transaction': True,
                'can_delete_transaction': True,
                'can_view_reports': True,
                'can_manage_users': True,
            }
        if self.permissions:
            return self.permissions.to_dict()
        return {
            'can_view_transactions': False,
            'can_add_transaction': False,
            'can_edit_transaction': False,
            'can_delete_transaction': False,
            'can_view_reports': False,
            'can_manage_users': False,
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    can_view_transactions = db.Column(db.Boolean, default=True)
    can_add_transaction = db.Column(db.Boolean, default=False)
    can_edit_transaction = db.Column(db.Boolean, default=False)
    can_delete_transaction = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=True)
    can_manage_users = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'can_view_transactions': self.can_view_transactions,
            'can_add_transaction': self.can_add_transaction,
            'can_edit_transaction': self.can_edit_transaction,
            'can_delete_transaction': self.can_delete_transaction,
            'can_view_reports': self.can_view_reports,
            'can_manage_users': self.can_manage_users,
        }
