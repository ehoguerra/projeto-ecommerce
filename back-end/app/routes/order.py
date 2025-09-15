from flask import Flask, jsonify, Blueprint, request
from extensions import db, jwt, cors
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order import Order, OrderItem
from models.cart_item import CartItem
from models.product import Product
from utils.decorators import account_activated_required

order_bp = Blueprint('orders', __name__, url_prefix='/orders')

@order_bp.route('/checkout', methods=['POST'])
@account_activated_required
def create_order():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    data = request.get_json()
    cart_items = data.get('cart_items', [])

    if not cart_items:
        return jsonify({"msg": "No items to order"}), 400

    order = Order(user_id=current_user['id'])
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if not product:
            continue

        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=item['quantity'])
        db.session.add(order_item)

    db.session.commit()

    return jsonify({"msg": "Order created", "order_id": order.id}), 201

@order_bp.route('/', methods=['GET'])
@account_activated_required
def get_orders():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    orders = Order.query.filter_by(user_id=current_user['id']).all()
    orders_data = []
    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        items_data = [{"product_id": item.product_id, "quantity": item.quantity} for item in items]
        orders_data.append({
            "order_id": order.id,
            "created_at": order.created_at,
            "items": items_data
        })

    return jsonify(orders_data), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
@account_activated_required
def get_order(order_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    order = Order.query.filter_by(id=order_id, user_id=current_user['id']).first()
    if not order:
        return jsonify({"msg": "Order not found"}), 404

    items = OrderItem.query.filter_by(order_id=order.id).all()
    items_data = [{"product_id": item.product_id, "quantity": item.quantity} for item in items]

    order_data = {
        "order_id": order.id,
        "created_at": order.created_at,
        "items": items_data
    }

    return jsonify(order_data), 200
