from flask import Flask, Blueprint, request, jsonify, make_response
from extensions import db, jwt, cors
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.user import User
from models.product import Product
from models.cart_item import Cart, CartItem
from utils.decorators import account_activated_required


cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/', methods=['POST'])
@account_activated_required
def add_to_cart():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    # Logic to add the item to the cart
    cart = Cart.query.filter_by(user_id=current_user['id']).first()
    if not cart:
        cart = Cart(user_id=current_user['id'])
        db.session.add(cart)
        db.session.commit()
    cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({"msg": "Item added to cart"}), 201

@cart_bp.route('/<int:item_id>', methods=['DELETE'])
@account_activated_required
def remove_from_cart(item_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    cart = Cart.query.filter_by(user_id=current_user['id']).first()
    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return jsonify({"msg": "Item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({"msg": "Item removed from cart"}), 200

@cart_bp.route('/', methods=['GET'])
@account_activated_required
def view_cart():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    cart = Cart.query.filter_by(user_id=current_user['id']).first()
    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    return jsonify({"cart_items": [item.to_dict() for item in cart_items]}), 200

@cart_bp.route('/<int:item_id>', methods=['PUT'])
@account_activated_required
def update_cart_item(item_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    
    data = request.get_json()
    quantity = data.get('quantity')

    if quantity is None or quantity < 1:
        remove_from_cart(item_id)
        return jsonify({"msg": "Item removed from cart"}), 200

    # Update the item in the cart
    cart = Cart.query.filter_by(user_id=current_user['id']).first()
    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return jsonify({"msg": "Item not found"}), 404
    if cart_item.product.stock < quantity:
        return jsonify({"msg": "Insufficient stock"}), 400
    if cart_item.quantity == quantity:
        return jsonify({"msg": "No changes made"}), 200

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({"msg": "Item updated"}), 200