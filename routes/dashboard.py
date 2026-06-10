from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.transaction import Transaction
from models.category import Category
from models.financier import Financier
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = datetime.utcnow().date()
    current_month = today.month
    current_year = today.year
    month_start = datetime(current_year, current_month, 1).date()

    # Current month totals
    month_expenses = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.date >= month_start,
        Transaction.entry_type == 'expense'
    ).scalar() or 0

    month_income = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.date >= month_start,
        Transaction.entry_type == 'income'
    ).scalar() or 0

    month_gold = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.date >= month_start,
        Transaction.entry_type == 'gold_conversion'
    ).scalar() or 0

    # Yearly totals
    year_start = datetime(current_year, 1, 1).date()
    year_expenses = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.date >= year_start,
        Transaction.entry_type == 'expense'
    ).scalar() or 0

    year_income = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.date >= year_start,
        Transaction.entry_type == 'income'
    ).scalar() or 0

    # All time totals
    all_expenses = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.entry_type == 'expense'
    ).scalar() or 0

    all_income = db.session.query(func.sum(Transaction.total_amount)).filter(
        Transaction.entry_type == 'income'
    ).scalar() or 0

    # Recent transactions
    recent = Transaction.query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(20).all()

    # Cash register balance (income - expense)
    cash_balance = all_income - all_expenses

    return render_template('dashboard/index.html',
                         month_expenses=month_expenses,
                         month_income=month_income,
                         month_gold=month_gold,
                         year_expenses=year_expenses,
                         year_income=year_income,
                         all_expenses=all_expenses,
                         all_income=all_income,
                         cash_balance=cash_balance,
                         recent=recent)
