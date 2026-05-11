from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

carts = {}

CatalogURL = "http://127.0.0.1:5001/products"

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    try:
        response = requests.get(f"{CatalogURL}/{product_id}")
        if response.status_code == 404:
            return jsonify({"error": "Товар не найден в каталоге"}), 404
        
        product_data = response.json()
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Модуль Каталога недоступен"}), 503

    if user_id not in carts:
        carts[user_id] = []

    existing_item = next((item for item in carts[user_id] if item['product_id'] == product_id), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        carts[user_id].append({
            "product_id": product_id,
            "name": product_data['name'],
            "price": product_data['price'],
            "quantity": quantity
        })

    return jsonify({
        "message": "Товар добавлен в корзину",
        "cart": carts[user_id]
    }), 200

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    user_cart = carts.get(str(user_id), [])
    return jsonify({"user_id": user_id, "items": user_cart})

if __name__ == '__main__': 
    app.run(debug=True, port=5002)