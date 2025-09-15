from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def account_activated_required(f):
    """Decorator para verificar se a conta do usuário está ativada"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_data = get_jwt_identity()
        if not current_user_data:
            return jsonify({"msg": "Unauthorized"}), 401
        
        # Buscar o usuário no banco para verificar se a conta está ativada
        user = User.query.get(current_user_data['id'])
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        if not user.account_activated:
            return jsonify({"msg": "Account not activated. Please check your email to activate your account."}), 403
        
        return f(*args, **kwargs)
    return decorated_function
