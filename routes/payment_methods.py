from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.payment_method import PaymentMethod
from models.transaction import TransactionPayer
from app import db
import re

payment_methods_bp = Blueprint('payment_methods', __name__)


def require_admin():
    if not current_user.is_admin:
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


def require_add_transaction():
    if not current_user.get_permissions().get('can_add_transaction'):
        return jsonify(success=False, error='Yetkisiz erişim'), 403
    return None


def generate_slug(name):
    tr_map = {'ı': 'i', 'ü': 'u', 'ö': 'o', 'ş': 's', 'ç': 'c', 'ğ': 'g',
              'İ': 'i', 'Ü': 'u', 'Ö': 'o', 'Ş': 's', 'Ç': 'c', 'Ğ': 'g'}
    for k, v in tr_map.items():
        name = name.replace(k, v)
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    slug = slug.strip('_')
    return slug


@payment_methods_bp.route('/payment_methods', methods=['GET', 'POST'])
@login_required
def list():
    error = require_admin()
    if error:
        return error

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name', '').strip()
            has_installments = request.form.get('has_installments') == 'on'
            if not name:
                flash('Ödeme yöntemi adı zorunludur.', 'danger')
            else:
                slug = generate_slug(name)
                if PaymentMethod.query.filter_by(slug=slug).first():
                    flash(f'"{name}" benzeri bir ödeme yöntemi zaten var.', 'warning')
                else:
                    max_order = db.session.query(db.func.max(PaymentMethod.order)).scalar() or 0
                    db.session.add(PaymentMethod(
                        name=name, slug=slug,
                        has_installments=has_installments,
                        order=max_order + 1
                    ))
                    db.session.commit()
                    flash(f'"{name}" ödeme yöntemi eklendi.', 'success')
        elif action == 'edit':
            pm_id = request.form.get('id', type=int)
            name = request.form.get('name', '').strip()
            has_installments = request.form.get('has_installments') == 'on'
            pm = PaymentMethod.query.get_or_404(pm_id)
            if not name:
                flash('Ödeme yöntemi adı zorunludur.', 'danger')
            else:
                new_slug = generate_slug(name)
                existing = PaymentMethod.query.filter(
                    PaymentMethod.slug == new_slug,
                    PaymentMethod.id != pm_id
                ).first()
                if existing:
                    flash(f'"{name}" adında başka bir ödeme yöntemi zaten var.', 'warning')
                else:
                    pm.name = name
                    pm.slug = new_slug
                    pm.has_installments = has_installments
                    db.session.commit()
                    flash(f'"{name}" ödeme yöntemi güncellendi.', 'success')
        elif action == 'delete':
            pm_id = request.form.get('id', type=int)
            pm = PaymentMethod.query.get_or_404(pm_id)
            payer_count = TransactionPayer.query.filter_by(payment_method=pm.slug).count()
            if payer_count > 0:
                flash(f'"{pm.name}" yöntemine bağlı {payer_count} ödeme kaydı var. Önce onları taşıyın.', 'danger')
            else:
                db.session.delete(pm)
                db.session.commit()
                flash(f'"{pm.name}" ödeme yöntemi silindi.', 'success')
        return redirect(url_for('payment_methods.list'))

    methods = PaymentMethod.query.order_by(PaymentMethod.order).all()
    counts = {}
    for m in methods:
        counts[m.id] = TransactionPayer.query.filter_by(payment_method=m.slug).count()
    return render_template('payment_methods/list.html', methods=methods, counts=counts)


@payment_methods_bp.route('/payment_methods/quick_add', methods=['POST'])
@login_required
def quick_add():
    error = require_add_transaction()
    if error:
        return jsonify(success=False, error='Yetkisiz erişim'), 403

    name = request.form.get('name', '').strip()
    has_installments = request.form.get('has_installments') == 'on'
    if not name:
        return jsonify(success=False, error='Ad zorunludur.'), 400

    slug = generate_slug(name)
    if PaymentMethod.query.filter_by(slug=slug).first():
        return jsonify(success=False, error=f'"{name}" zaten mevcut.'), 400

    max_order = db.session.query(db.func.max(PaymentMethod.order)).scalar() or 0
    pm = PaymentMethod(name=name, slug=slug, has_installments=has_installments, order=max_order + 1)
    db.session.add(pm)
    db.session.commit()
    return jsonify(success=True, id=pm.id, name=pm.name, slug=pm.slug, has_installments=pm.has_installments)
