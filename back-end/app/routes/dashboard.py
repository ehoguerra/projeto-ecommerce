from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order import Order, OrderItem
from models.cart_item import CartItem
from models.product import Product, Category
from models.user import User
from extensions import db, roles
from utils.decorators import account_activated_required

bp = Blueprint('dashboard', __name__)


@bp.route('/orders', methods=['POST'])
@account_activated_required
def all_orders():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    orders = Order.query.all()
    orders_data = []
    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        items_data = [{"product_id": item.product_id, "quantity": item.quantity} for item in items]
        orders_data.append({
            "order_id": order.id,
            "created_at": order.created_at,
            "items": items_data
        })
    if not orders_data:
        return jsonify({"msg": "No orders found"}), 404

    return jsonify(orders_data), 200

@bp.route('/users', methods=['GET'])
@account_activated_required
def all_users():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    users = User.query.all()
    users_data = [{"id": user.id, "email": user.email} for user in users]
    if not users_data:
        return jsonify({"msg": "No users found"}), 404

    return jsonify(users_data), 200

@bp.route('/products', methods=['GET'])
@account_activated_required
def all_products():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403
    
    # Fetch all products
    products = Product.query.all()
    products_data = [{"id": product.id, "name": product.name, "price": product.price} for product in products]
    if not products_data:
        return jsonify({"msg": "No products found"}), 404
    
    # Fetch in how many carts each product is present
    product_cart_counts = db.session.query(
        CartItem.product_id,
        db.func.count(CartItem.id).label('cart_count')
    ).group_by(CartItem.product_id).all()

    product_cart_counts_dict = {item.product_id: item.cart_count for item in product_cart_counts}

    for product in products_data:
        product["cart_count"] = product_cart_counts_dict.get(product["id"], 0)

    return jsonify(products_data), 200

@bp.route('/products/<int:product_id>', methods=['GET'])
@account_activated_required
def get_product(product_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    product = Product.query.get_or_404(product_id)
    result = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category.name if product.category else None,
        'image_url': product.image_url
    }
    return jsonify(result), 200

@bp.route('/categories', methods=['GET'])
@account_activated_required
def all_categories():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    categories = Category.query.all()
    categories_data = [{"id": category.id, "name": category.name} for category in categories]
    if not categories_data:
        return jsonify({"msg": "No categories found"}), 404

    return jsonify(categories_data), 200

@bp.route('/categories', methods=['POST'])
@account_activated_required
def create_category():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({"msg": "Missing category name"}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({"msg": "Category created successfully"}), 201

# 


@bp.route('/results', methods=['GET'])
@account_activated_required
def results():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"msg": "Unauthorized"}), 401
    if current_user.role not in roles:
        return jsonify({"msg": "Forbidden"}), 403

    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    total_sales = db.session.query(db.func.sum(OrderItem.quantity)).scalar() or 0

    results_data = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_sales": total_sales
    }

    return jsonify(results_data), 200