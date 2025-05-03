from flask import Blueprint, request, jsonify
from app import db
from app.models.transaction import Transaction
from app.services.ml_analytics import generate_cash_flow_forecast, get_expense_recommendations
from datetime import datetime, timedelta
import jwt
from functools import wraps

analytics_bp = Blueprint('analytics', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            kwargs['user_id'] = payload['user_id']
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

@analytics_bp.route('/cash-flow', methods=['GET'])
@token_required
def get_cash_flow(user_id):
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        # Default to last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    
    # Get transactions for the date range
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date.between(start_date, end_date)
    ).all()
    
    # Generate cash flow forecast
    forecast = generate_cash_flow_forecast(transactions)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'forecast': forecast
    }), 200

@analytics_bp.route('/expense-analysis', methods=['GET'])
@token_required
def get_expense_analysis(user_id):
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        # Default to last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    
    # Get expense transactions
    expenses = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).all()
    
    # Get recommendations
    recommendations = get_expense_recommendations(expenses)
    
    return jsonify({
        'expenses': [e.to_dict() for e in expenses],
        'recommendations': recommendations
    }), 200

@analytics_bp.route('/summary', methods=['GET'])
@token_required
def get_summary(user_id):
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        # Default to last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    
    # Get all transactions
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date.between(start_date, end_date)
    ).all()
    
    # Calculate summary statistics
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_cash_flow = total_income - total_expenses
    
    # Group by category
    category_totals = {}
    for t in transactions:
        if t.category not in category_totals:
            category_totals[t.category] = {'income': 0, 'expense': 0}
        category_totals[t.category][t.transaction_type] += t.amount
    
    return jsonify({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_cash_flow': net_cash_flow,
        'category_totals': category_totals
    }), 200 