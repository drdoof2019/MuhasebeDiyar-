from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.transaction import Transaction, TransactionPayer
from models.category import Category
from models.financier import Financier
from app import db
from datetime import datetime
from sqlalchemy import func

transactions_bp = Blueprint('transactions', __name__)


def check_permission(perm):
    perms = current_user.get_permissions()
    return perms.get(perm, False)


@transactions_bp.route('/transactions')
@login_required
def list():
    if not check_permission('can_view_transactions'):
        flash('İşlemleri görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard.index'))

    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Filters
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    entry_type = request.args.get('entry_type', '')
    category_id = request.args.get('category_id', type=int)
    financier_id = request.args.get('financier_id', type=int)
    search = request.args.get('search', '').strip()

    # Sorting
    sort = request.args.get('sort', 'date')
    order = request.args.get('order', 'desc')
    allowed_sorts = {
        'date': Transaction.date,
        'description': Transaction.description,
        'entry_type': Transaction.entry_type,
        'category': Category.name,
        'amount': Transaction.total_amount,
    }
    sort_column = allowed_sorts.get(sort, Transaction.date)
    if order == 'asc':
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    query = Transaction.query

    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    if entry_type:
        query = query.filter(Transaction.entry_type == entry_type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if financier_id:
        query = query.join(Transaction.payers).filter(TransactionPayer.financier_id == financier_id)
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))
    if financier_id and search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))

    if financier_id:
        query = query.join(Transaction.payers).filter(TransactionPayer.financier_id == financier_id)
        if search:
            query = query.filter(Transaction.description.ilike(f'%{search}%'))

    # Always join category for sorting by category name
    if sort == 'category':
        query = query.join(Category)

    query = query.order_by(sort_column, Transaction.id.desc())

    transactions = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.order_by(Category.name).all()
    financiers = Financier.query.order_by(Financier.name).all()

    return render_template('transactions/list.html',
                         transactions=transactions,
                         categories=categories,
                         financiers=financiers,
                         date_from=date_from,
                         date_to=date_to,
                         entry_type=entry_type,
                         category_id=category_id,
                         financier_id=financier_id,
                         search=search,
                         sort=sort,
                         order=order)


@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add():
    if not check_permission('can_add_transaction'):
        flash('İşlem ekleme yetkiniz yok.', 'danger')
        return redirect(url_for('transactions.list'))

    categories = Category.query.order_by(Category.name).all()
    financiers = Financier.query.order_by(Financier.name).all()
    from models.payment_method import PaymentMethod
    payment_methods = PaymentMethod.query.order_by(PaymentMethod.order).all()
    from datetime import date
    today_date = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Geçerli bir tarih giriniz.', 'danger')
            return render_template('transactions/add.html', categories=categories, financiers=financiers)

        entry_type = request.form.get('entry_type', 'expense')
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        if not category_id:
            category_id = None
        gold_grams = request.form.get('gold_grams', type=float)
        note = request.form.get('note', '').strip()

        if not description:
            flash('Açıklama zorunludur.', 'danger')
            return render_template('transactions/add.html', categories=categories, financiers=financiers)

        # Calculate total from payers
        total_amount = 0
        payer_data = []

        payer_ids = request.form.getlist('payer_financier_id[]')
        payer_amounts = request.form.getlist('payer_amount[]')
        payer_methods = request.form.getlist('payer_method[]')
        payer_installments = request.form.getlist('payer_installment_count[]')
        payer_notes = request.form.getlist('payer_note[]')

        for i in range(len(payer_ids)):
            if i < len(payer_amounts) and payer_amounts[i]:
                try:
                    amount = float(payer_amounts[i])
                    if amount > 0:
                        fid = int(payer_ids[i])
                        method = payer_methods[i] if i < len(payer_methods) else 'cash'
                        inst = int(payer_installments[i]) if i < len(payer_installments) and payer_installments[i] else None
                        pnote = payer_notes[i] if i < len(payer_notes) else ''
                        total_amount += amount
                        payer_data.append({
                            'financier_id': fid,
                            'amount': amount,
                            'method': method,
                            'installments': inst,
                            'note': pnote
                        })
                except (ValueError, TypeError):
                    pass

        transaction = Transaction(
            date=date,
            entry_type=entry_type,
            description=description,
            category_id=category_id,
            total_amount=total_amount,
            gold_grams=gold_grams,
            note=note,
            created_by=current_user.id
        )
        db.session.add(transaction)
        db.session.flush()

        for pd_item in payer_data:
            payer = TransactionPayer(
                transaction_id=transaction.id,
                financier_id=pd_item['financier_id'],
                amount=pd_item['amount'],
                payment_method=pd_item['method'],
                installment_count=pd_item['installments'],
                note=pd_item['note']
            )
            db.session.add(payer)

        db.session.commit()
        flash('İşlem başarıyla kaydedildi.', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('transactions/add.html', categories=categories,
                         financiers=financiers, payment_methods=payment_methods,
                         today_date=today_date)


@transactions_bp.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not check_permission('can_edit_transaction'):
        flash('İşlem düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('transactions.list'))

    transaction = Transaction.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()
    financiers = Financier.query.order_by(Financier.name).all()
    from models.payment_method import PaymentMethod
    payment_methods = PaymentMethod.query.order_by(PaymentMethod.order).all()

    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            transaction.date = date
        except (ValueError, TypeError):
            flash('Geçerli bir tarih giriniz.', 'danger')
            return render_template('transactions/edit.html', transaction=transaction,
                                 categories=categories, financiers=financiers,
                                 payment_methods=payment_methods)

        transaction.entry_type = request.form.get('entry_type', 'expense')
        transaction.description = request.form.get('description', '').strip()
        transaction.category_id = request.form.get('category_id', type=int)
        if not transaction.category_id:
            transaction.category_id = None
        transaction.gold_grams = request.form.get('gold_grams', type=float)
        transaction.note = request.form.get('note', '').strip()

        # Remove existing payers
        TransactionPayer.query.filter_by(transaction_id=transaction.id).delete()

        total_amount = 0
        payer_ids = request.form.getlist('payer_financier_id[]')
        payer_amounts = request.form.getlist('payer_amount[]')
        payer_methods = request.form.getlist('payer_method[]')
        payer_installments = request.form.getlist('payer_installment_count[]')
        payer_notes = request.form.getlist('payer_note[]')

        for i in range(len(payer_ids)):
            if i < len(payer_amounts) and payer_amounts[i]:
                try:
                    amount = float(payer_amounts[i])
                    if amount > 0:
                        fid = int(payer_ids[i])
                        method = payer_methods[i] if i < len(payer_methods) else 'cash'
                        inst = int(payer_installments[i]) if i < len(payer_installments) and payer_installments[i] else None
                        pnote = payer_notes[i] if i < len(payer_notes) else ''
                        total_amount += amount
                        db.session.add(TransactionPayer(
                            transaction_id=transaction.id,
                            financier_id=fid,
                            amount=amount,
                            payment_method=method,
                            installment_count=inst,
                            note=pnote
                        ))
                except (ValueError, TypeError):
                    pass

        transaction.total_amount = total_amount
        db.session.commit()
        flash('İşlem güncellendi.', 'success')
        return redirect(url_for('transactions.list'))

    return render_template('transactions/edit.html', transaction=transaction,
                         categories=categories, financiers=financiers,
                         payment_methods=payment_methods)


@transactions_bp.route('/transactions/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not check_permission('can_delete_transaction'):
        flash('İşlem silme yetkiniz yok.', 'danger')
        return redirect(url_for('transactions.list'))

    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem silindi.', 'info')
    return redirect(url_for('transactions.list'))
