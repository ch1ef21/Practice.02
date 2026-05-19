from flask import Flask, jsonify, abort
from models import ProductRepository
app = Flask(__name__)

db_set_products = ProductRepository()

@app.route('/products', methods=['GET'])
def get_products():
    products = db_set_products.get_all()
    return jsonify({"products": products})

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db_set_products.get_by_id(product_id)
    if not product is None:
        return jsonify({'error': 'Товар не найден'}), 404
    return jsonify(product), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)