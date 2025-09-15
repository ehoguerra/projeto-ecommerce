from flask import Flask, jsonify, make_response, request, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from models.product import Product, Category
from extensions import db, migrate, jwt, cors, roles
from uuid import uuid4
from utils.decorators import account_activated_required

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    pagination = Product.query.paginate(page=page, per_page=limit)
    products = pagination.items
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'category': product.category.name if product.category else None,
            'image_url': product.image_url
        })
    return jsonify(result), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
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

@products_bp.route('/products', methods=['POST'])
@account_activated_required
def create_product():
    current_user = get_jwt_identity()
    if not current_user or current_user.role not in roles:
        return jsonify({"msg": "Admin privilege required"}), 403
    if 'image' not in request.files:
        return jsonify({"msg": "No image file provided"}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    if image.filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
        return jsonify({"msg": "Invalid image file type"}), 400
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join('static', 'images', filename)
        image.save(image_path)
        image_url = url_for('static', filename=os.path.join('images', filename), _external=True)
    else:
        return jsonify({"msg": "Invalid image file"}), 400
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')
    category_id = data.get('category_id')
    image_url = data.get('image_url')

    if not all([name, description, price, stock, category_id, image_url]):
        return jsonify({"msg": "Missing data"}), 400
    
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({"msg": "Category not found"}), 404

    new_product = Product(
        id=str(uuid4()),
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        image_url=image_url
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"msg": "Product created successfully", "id": new_product.id}), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@account_activated_required
def update_product(product_id):
    current_user = get_jwt_identity()
    if not current_user or current_user.role not in roles:
        return jsonify({"msg": "Admin privilege required"}), 403
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.category_id = data.get('category_id', product.category_id)
    product.image_url = data.get('image_url', product.image_url)
    category = Category.query.filter_by(id=product.category_id).first()
    if not category:
        return jsonify({"msg": "Category not found"}), 404
    if not product.image_url:
        product.image_url = 'default_image_url'
    db.session.add(product)
    db.session.flush()  # Ensure the product is updated before committing
    db.session.refresh(product)  # Refresh the product instance to get the latest data
    db.session.commit()
    return jsonify({"msg": "Product updated successfully"}), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@account_activated_required
def delete_product(product_id):
    current_user = get_jwt_identity()
    if not current_user or current_user.role not in roles:
        return jsonify({"msg": "Admin privilege required"}), 403
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Product deleted successfully"}), 200

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(result), 200

@products_bp.route('/products/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    result = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category.name if product.category else None,
        'image_url': product.image_url
    } for product in products]
    return jsonify(result), 200