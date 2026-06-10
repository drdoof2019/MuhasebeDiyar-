from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models.transaction import Transaction, TransactionPayer
from models.category import Category
from models.financier import Financier
from app import db
from datetime import datetime
from sqlalchemy import func, extract

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports/monthly')
@login_required
def monthly():
    year = request.args.get('year', datetime.utcnow().year, type=int)

    months_data = []
    for m in range(1, 13):
        expenses = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == m,
            Transaction.entry_type == 'expense'
        ).scalar() or 0

        income = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == m,
            Transaction.entry_type == 'income'
        ).scalar() or 0

        gold = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == m,
            Transaction.entry_type == 'gold_conversion'
        ).scalar() or 0

        months_data.append({
            'month': m,
            'expenses': expenses,
            'income': income,
            'gold': gold,
            'net': income - expenses,
            'total_gold_grams': db.session.query(func.sum(Transaction.gold_grams)).filter(
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == m,
                Transaction.entry_type == 'gold_conversion'
            ).scalar() or 0
        })

    # Get available years
    years = db.session.query(func.distinct(extract('year', Transaction.date))).order_by(
        extract('year', Transaction.date).desc()
    ).all()
    years = [int(y[0]) for y in years if y[0]]

    if year not in years:
        years = [year] + years

    return render_template('reports/monthly.html', months_data=months_data, year=year, years=years)


@reports_bp.route('/reports/yearly')
@login_required
def yearly():
    # Get distinct years
    year_rows = db.session.query(
        extract('year', Transaction.date).label('year')
    ).group_by(extract('year', Transaction.date)).order_by(
        extract('year', Transaction.date).desc()
    ).all()

    yearly_data = []
    for (year,) in year_rows:
        year = int(year)
        expenses = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            Transaction.entry_type == 'expense'
        ).scalar() or 0
        income = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            Transaction.entry_type == 'income'
        ).scalar() or 0
        gold = db.session.query(func.sum(Transaction.total_amount)).filter(
            extract('year', Transaction.date) == year,
            Transaction.entry_type == 'gold_conversion'
        ).scalar() or 0
        yearly_data.append({
            'year': year,
            'expenses': expenses,
            'income': income,
            'gold': gold,
        })

    return render_template('reports/yearly.html', yearly_data=yearly_data)


@reports_bp.route('/reports/category')
@login_required
def category():
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', type=int)
    entry_type = request.args.get('entry_type', 'all')

    query = db.session.query(
        Category.name,
        func.sum(Transaction.total_amount).label('total')
    ).join(Transaction)

    if entry_type and entry_type != 'all':
        query = query.filter(Transaction.entry_type == entry_type)

    if year:
        query = query.filter(extract('year', Transaction.date) == year)
    if month:
        query = query.filter(extract('month', Transaction.date) == month)

    results = query.group_by(Category.name).order_by(func.sum(Transaction.total_amount).desc()).all()

    years = db.session.query(func.distinct(extract('year', Transaction.date))).order_by(
        extract('year', Transaction.date).desc()
    ).all()
    years = [int(y[0]) for y in years if y[0]]

    return render_template('reports/category.html', results=results, year=year, month=month,
                           years=years, entry_type=entry_type)


@reports_bp.route('/reports/financier')
@login_required
def financier():
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', type=int)
    entry_type = request.args.get('entry_type', 'all')

    query = db.session.query(
        Financier.name,
        func.sum(TransactionPayer.amount).label('total')
    ).join(TransactionPayer).join(Transaction)

    if entry_type and entry_type != 'all':
        query = query.filter(Transaction.entry_type == entry_type)

    if year:
        query = query.filter(extract('year', Transaction.date) == year)
    if month:
        query = query.filter(extract('month', Transaction.date) == month)

    results = query.group_by(Financier.name).order_by(func.sum(TransactionPayer.amount).desc()).all()

    years = db.session.query(func.distinct(extract('year', Transaction.date))).order_by(
        extract('year', Transaction.date).desc()
    ).all()
    years = [int(y[0]) for y in years if y[0]]

    return render_template('reports/financier.html', results=results, year=year, month=month,
                           years=years, entry_type=entry_type)


@reports_bp.route('/reports/gold')
@login_required
def gold():
    gold_transactions = Transaction.query.filter(
        Transaction.entry_type == 'gold_conversion'
    ).order_by(Transaction.date.desc()).all()

    total_grams = sum(t.gold_grams or 0 for t in gold_transactions)
    total_tl = sum(t.total_amount or 0 for t in gold_transactions)

    return render_template('reports/gold.html',
                         gold_transactions=gold_transactions,
                         total_grams=total_grams,
                         total_tl=total_tl)


@reports_bp.route('/reports/cash-register')
@login_required
def cash_register():
    # Simple cash register: running balance of income - expense
    transactions = Transaction.query.filter(
        Transaction.entry_type.in_(['income', 'expense'])
    ).order_by(Transaction.date.asc(), Transaction.id.asc()).all()

    running_data = []
    balance = 0
    for t in transactions:
        if t.entry_type == 'income':
            change = t.total_amount
        else:
            change = -t.total_amount
        balance += change
        running_data.append({
            'date': t.date,
            'description': t.description,
            'entry_type': t.entry_type,
            'amount': t.total_amount,
            'change': change,
            'balance': balance
        })

    return render_template('reports/cash_register.html', running_data=running_data)
