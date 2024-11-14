# app/routes/api.py
from flask import Blueprint, jsonify
from app.services.exchange_service import get_exchange_rates

api_bp = Blueprint('api', __name__)

@api_bp.route('/exchange-rates')
def exchange_rates():
    result = get_exchange_rates()
    if result['success']:
        return jsonify(result)
    return jsonify(result), 500