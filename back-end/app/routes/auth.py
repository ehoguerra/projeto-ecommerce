from extensions import db, migrate, jwt, cors
from models.user import User
from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.decorators import account_activated_required
from itsdangerous import URLSafeTimedSerializer
from services.email_service import account_activation_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    fname = data.get('fname')
    surname = data.get('surname')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    unique_id = str(uuid4())
    new_user = User(id=unique_id, fname=fname, surname=surname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    

    token = create_access_token(identity={'id': new_user.id, 'email': new_user.email})

    #Generate activation token
    activation_token = URLSafeTimedSerializer('secret_key').dumps(new_user.id)

    account_activation_email(new_user.email, activation_token, fname)

    resp = make_response(jsonify({"msg": "User created successfully"}), 201)
    resp.set_cookie('access_token', token, httponly=True, samesite='Strict', secure=True, max_age=60*60*24*7)
    return resp

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad email or password"}), 401

    # Verificar se a conta está ativada
    if not user.account_activated:
        return jsonify({"msg": "Account not activated. Please check your email to activate your account."}), 403

    access_token = create_access_token(identity={'id': user.id, 'email': user.email, 'is_admin': user.is_admin})
    resp = make_response(jsonify({"msg": "Login successful"}), 200)
    resp.set_cookie('access_token', access_token, httponly=True, samesite='Strict', secure=True, max_age=60*60*24*7)
    return resp

@auth_bp.route('/refresh', methods=['GET'])
@account_activated_required
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    resp = make_response(jsonify({"msg": "Token refreshed"}), 200)
    resp.set_cookie('access_token', new_token, httponly=True, samesite='Strict', secure=True, max_age=60*60*24*7)
    return resp

@auth_bp.route('/logout', methods=['POST'])
@account_activated_required
def logout():
    resp = make_response(jsonify({"msg": "Logout successful"}), 200)
    resp.delete_cookie('access_token')
    return resp

@auth_bp.route('/activate-account/<token>', methods=['GET'])
def activate_account(token):
    """Rota para ativar conta de usuário usando um token"""
    try:
        user_id = URLSafeTimedSerializer('secret_key').loads(token, max_age=3600)  # Token válido por 1 hora
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "Invalid activation token"}), 400
        
        if user.account_activated:
            return jsonify({"msg": "Account already activated"}), 200
        
        user.account_activated = True
        db.session.commit()
        
        return jsonify({"msg": "Account activated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": "Invalid activation token"}), 400

@auth_bp.route('/resend-activation', methods=['POST'])
@jwt_required()
def resend_activation():
    """Rota para reenviar email de ativação"""
    current_user_data = get_jwt_identity()
    user = User.query.get(current_user_data['id'])
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if user.account_activated:
        return jsonify({"msg": "Account already activated"}), 200

    activation_token = URLSafeTimedSerializer('secret_key').dumps(user.id)
    try:
        account_activation_email(user.email, activation_token, user.fname)
    except Exception as e:
        return jsonify({"msg": "Failed to send activation email"}), 500

    return jsonify({"msg": "Activation email sent successfully"}), 200