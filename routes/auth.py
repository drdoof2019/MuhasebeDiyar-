from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, Permission
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash(f'Hoş geldiniz, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/seed-admin')
def seed_admin():
    """Run once to create the default admin user."""
    import os
    if User.query.filter_by(username='admin').first():
        return 'Admin zaten var!'
    admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    admin = User(username='admin', full_name='Yönetici', is_admin=True, is_active=True)
    admin.set_password(admin_password)
    from models.category import Category
    from models.financier import Financier
    from models.payment_method import PaymentMethod
    db.session.add(admin)
    db.session.commit()
    Category.seed_defaults()
    Financier.seed_defaults()
    PaymentMethod.seed_defaults()
    return 'Admin kullanıcısı ve varsayılan referans verileri olusturuldu.'
