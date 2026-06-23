from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import User, Permission
from app import db

users_bp = Blueprint('users', __name__)

ALL_PERMS = [
    'can_view_transactions',
    'can_add_transaction',
    'can_edit_transaction',
    'can_delete_transaction',
    'can_view_reports',
    'can_manage_users',
]


def _is_all_perms(form):
    return all(p in form for p in ALL_PERMS)


def require_admin():
    if not current_user.is_admin:
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


def require_manage_users():
    if not current_user.get_permissions().get('can_manage_users'):
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


@users_bp.route('/users')
@login_required
def list():
    error = require_manage_users()
    if error: return error

    users = User.query.order_by(User.username).all()
    return render_template('users/list.html', users=users)


@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create():
    error = require_manage_users()
    if error: return error

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if not username or not full_name or not password:
            flash('Tüm alanları doldurun.', 'danger')
            return render_template('users/create.html')

        if password != password_confirm:
            flash('Şifreler eşleşmiyor.', 'danger')
            return render_template('users/create.html')

        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
            return render_template('users/create.html')

        is_admin = _is_all_perms(request.form)
        user = User(username=username, full_name=full_name, is_admin=is_admin, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Set permissions
        perm = Permission(
            user_id=user.id,
            can_view_transactions='can_view_transactions' in request.form,
            can_add_transaction='can_add_transaction' in request.form,
            can_edit_transaction='can_edit_transaction' in request.form,
            can_delete_transaction='can_delete_transaction' in request.form,
            can_view_reports='can_view_reports' in request.form,
            can_manage_users='can_manage_users' in request.form,
        )
        db.session.add(perm)
        db.session.commit()
        flash(f'{full_name} kullanıcısı oluşturuldu.', 'success')
        return redirect(url_for('users.list'))

    return render_template('users/create.html')


@users_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    error = require_manage_users()
    if error: return error

    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()

        password = request.form.get('password', '')
        if password:
            password_confirm = request.form.get('password_confirm', '')
            if password != password_confirm:
                flash('Şifreler eşleşmiyor.', 'danger')
                return render_template('users/edit.html', user=user)
            user.set_password(password)

        user.is_active = 'is_active' in request.form

        is_admin = _is_all_perms(request.form)

        # Prevent demoting the last admin
        if user.is_admin and not is_admin:
            from models.user import User as UserModel
            admin_count = UserModel.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                flash('Son yöneticiyi düşüremezsiniz.', 'danger')
                return render_template('users/edit.html', user=user)

        user.is_admin = is_admin

        # Ensure Permission row exists (seeded admin may have none)
        if not user.permissions:
            user.permissions = Permission(user_id=user.id)
            db.session.add(user.permissions)

        user.permissions.can_view_transactions = 'can_view_transactions' in request.form
        user.permissions.can_add_transaction = 'can_add_transaction' in request.form
        user.permissions.can_edit_transaction = 'can_edit_transaction' in request.form
        user.permissions.can_delete_transaction = 'can_delete_transaction' in request.form
        user.permissions.can_view_reports = 'can_view_reports' in request.form
        user.permissions.can_manage_users = 'can_manage_users' in request.form

        db.session.commit()
        flash(f'{user.full_name} güncellendi.', 'success')
        return redirect(url_for('users.list'))

    return render_template('users/edit.html', user=user)
