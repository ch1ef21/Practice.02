from flask import Flask, jsonify, abort

app = Flask(__name__)

products = [
    {"id": 1, "name": "Смартфон ", "price": 15000, "stock": 10},
    {"id": 2, "name": "Игровой руль ", "price": 25000, "stock": 5},
    {"id": 3, "name": "Видеокарта ", "price": 12000, "stock": 0},
    {"id": 4, "name": "Видеокарта №2", "price": 125000, "stock": 100},
    {"id": 5, "name": "Монитор ", "price": 14000, "stock": 104},
]

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({"products": products})

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        abort(404, description="товар не найден")
    return jsonify(product)

if __name__ == '__main__':
    app.run(debug=True, port=5001)