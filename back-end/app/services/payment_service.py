# Integration with payment gateways

from flask import jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from utils.decorators import account_activated_required
from extensions import db
from datetime import datetime, timedelta


def call_mercado_pago_api(user_id, amount, cpf):
    # Expirating date for the payment
    time_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    expiration_date = (datetime.now() + timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    if not user.account_activated:
        return jsonify({"msg": "Account not activated"}), 403


    # Mercado Pago API 
    api = "https://api.mercadopago.com/v1/payments"
    headers = {
        "X-Idempotency-Key": user_id,
    }
    body = {
        "description": "Payment for order",
        "date_of_expiration": expiration_date,
        "transaction_amount": amount,
        "payer": {
            "email": user.email,
            "identification": {
                "type": "CPF",
                "number": cpf
            },
            "first_name": user.fname,
            "entity_type": "individual",
            "type": "customer"
        },

    }

@jwt_required()
@account_activated_required
def process_payment(user_id, amount, payment_method, cpf):
    # Get selected payment method
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    if not user.account_activated:
        return jsonify({"msg": "Account not activated"}), 403
    
    if payment_method == 'mercado_pago':
        # Call Mercado Pago API to process payment
        response = call_mercado_pago_api(user_id, amount, cpf)
        return response
    else:
        return jsonify({"msg": "Unsupported payment method"}), 400