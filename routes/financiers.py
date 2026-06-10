from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.financier import Financier
from models.transaction import TransactionPayer
from app import db

financiers_bp = Blueprint('financiers', __name__)


def require_admin():
    if not current_user.is_admin:
        flash('Bu sayfaya sadece yönetici erişebilir.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


@financiers_bp.route('/financiers', methods=['GET', 'POST'])
@login_required
def list():
    error = require_admin()
    if error:
        return error

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name', '').strip()
            if not name:
                flash('Finansör adı zorunludur.', 'danger')
            elif Financier.query.filter_by(name=name).first():
                flash(f'"{name}" finansörü zaten mevcut.', 'warning')
            else:
                db.session.add(Financier(name=name))
                db.session.commit()
                flash(f'"{name}" finansörü eklendi.', 'success')

        elif action == 'edit':
            fin_id = request.form.get('id', type=int)
            name = request.form.get('name', '').strip()
            financier = Financier.query.get_or_404(fin_id)
            if not name:
                flash('Finansör adı zorunludur.', 'danger')
            else:
                existing = Financier.query.filter(Financier.name == name, Financier.id != fin_id).first()
                if existing:
                    flash(f'"{name}" adında başka bir finansör zaten var.', 'warning')
                else:
                    financier.name = name
                    db.session.commit()
                    flash(f'"{name}" finansörü güncellendi.', 'success')

        elif action == 'delete':
            fin_id = request.form.get('id', type=int)
            financier = Financier.query.get_or_404(fin_id)
            payer_count = TransactionPayer.query.filter_by(financier_id=fin_id).count()
            if payer_count > 0:
                flash(f'"{financier.name}" finansörüne bağlı {payer_count} ödeme kaydı var. Önce onları taşıyın.', 'danger')
            else:
                db.session.delete(financier)
                db.session.commit()
                flash(f'"{financier.name}" finansörü silindi.', 'success')

        return redirect(url_for('financiers.list'))

    financiers = Financier.query.order_by(Financier.name).all()
    # Count transactions per financier
    counts = {}
    for f in financiers:
        counts[f.id] = TransactionPayer.query.filter_by(financier_id=f.id).count()

    return render_template('financiers/list.html', financiers=financiers, counts=counts)


@financiers_bp.route('/financiers/quick_add', methods=['POST'])
@login_required
def quick_add():
    error = require_admin()
    if error:
        return jsonify(success=False, error='Yetkisiz erişim'), 403

    name = request.form.get('name', '').strip()
    if not name:
        return jsonify(success=False, error='Ad zorunludur.'), 400
    if Financier.query.filter_by(name=name).first():
        return jsonify(success=False, error=f'"{name}" zaten mevcut.'), 400

    f = Financier(name=name)
    db.session.add(f)
    db.session.commit()
    return jsonify(success=True, id=f.id, name=f.name)
