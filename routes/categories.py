from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.category import Category
from app import db

categories_bp = Blueprint('categories', __name__)


def require_admin():
    if not current_user.is_admin:
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


@categories_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def list():
    error = require_admin()
    if error:
        return error

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name', '').strip()
            cat_type = request.form.get('type', 'expense')
            if not name:
                flash('Kategori adı zorunludur.', 'danger')
            elif Category.query.filter_by(name=name).first():
                flash(f'"{name}" kategorisi zaten mevcut.', 'warning')
            else:
                db.session.add(Category(name=name, type=cat_type))
                db.session.commit()
                flash(f'"{name}" kategorisi eklendi.', 'success')

        elif action == 'edit':
            cat_id = request.form.get('id', type=int)
            name = request.form.get('name', '').strip()
            cat_type = request.form.get('type', 'expense')
            category = Category.query.get_or_404(cat_id)
            if not name:
                flash('Kategori adı zorunludur.', 'danger')
            else:
                existing = Category.query.filter(Category.name == name, Category.id != cat_id).first()
                if existing:
                    flash(f'"{name}" adında başka bir kategori zaten var.', 'warning')
                else:
                    category.name = name
                    category.type = cat_type
                    db.session.commit()
                    flash(f'"{name}" kategorisi güncellendi.', 'success')

        elif action == 'delete':
            cat_id = request.form.get('id', type=int)
            category = Category.query.get_or_404(cat_id)
            txn_count = category.transactions.count()
            if txn_count > 0:
                flash(f'"{category.name}" kategorisine bağlı {txn_count} işlem var. Önce onları taşıyın.', 'danger')
            else:
                db.session.delete(category)
                db.session.commit()
                flash(f'"{category.name}" kategorisi silindi.', 'success')

        return redirect(url_for('categories.list'))

    categories = Category.query.order_by(Category.type, Category.name).all()
    # Count transactions per category
    counts = {}
    for c in categories:
        counts[c.id] = c.transactions.count()

    return render_template('categories/list.html', categories=categories, counts=counts)


@categories_bp.route('/categories/quick_add', methods=['POST'])
@login_required
def quick_add():
    error = require_admin()
    if error:
        return jsonify(success=False, error='Yetkisiz erişim'), 403

    name = request.form.get('name', '').strip()
    cat_type = request.form.get('type', 'expense')
    if not name:
        return jsonify(success=False, error='Ad zorunludur.'), 400
    if Category.query.filter_by(name=name).first():
        return jsonify(success=False, error=f'"{name}" zaten mevcut.'), 400

    cat = Category(name=name, type=cat_type)
    db.session.add(cat)
    db.session.commit()
    return jsonify(success=True, id=cat.id, name=cat.name, type=cat.type)
