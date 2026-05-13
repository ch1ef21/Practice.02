from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

carts = {}

os.environ['no_proxy'] = '127.0.0.1,localhost'

CATALOG_BASE_URL = "http://127.0.0.1:5001"

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    if not data:
        return jsonify({"error": "Пустой запрос"}), 400
        
    user_id = str(data.get('user_id'))
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    try:
        session = requests.Session()
        session.trust_env = False 
        
        url = f"{CATALOG_BASE_URL}/products/{product_id}"
        response = session.get(url, timeout=5)
        
        if response.status_code == 404:
            return jsonify({"error": "Товар не найден в каталоге"}), 404
        
        
        try:
            product_data = response.json()
        except Exception:
            return jsonify({
                "error": "Каталог ответил не в формате JSON",
                "received": response.text[:100] 
            }), 500

    except Exception as e:
        return jsonify({"error": "Связь с Каталогом прервана", "details": str(e)}), 503

    if user_id not in carts:
        carts[user_id] = []

    existing_item = next((item for item in carts[user_id] if item['product_id'] == product_id), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        carts[user_id].append({
            "product_id": product_id,
            "name": product_data.get('name'),
            "price": product_data.get('price'),
            "quantity": quantity
        })

    return jsonify({
        "message": "Товар успешно добавлен",
        "cart": carts[user_id]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)