from flask import Flask, request, jsonify
import requests
import os
import integrationLib.rabbitmq_helper as rabbitmq_helper

app = Flask(__name__)
integration = rabbitmq_helper.IntegrationService()

carts = {}

CATALOG_BASE_URL = os.getenv("CATALOG_BASE_URL", "http://127.0.0.1:5001")

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    if not data:
        return jsonify({"error": "Пустой запрос"}), 400
        
    user_id = str(data.get('user_id'))
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    try:
        url = f"{CATALOG_BASE_URL}/products/{product_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 404:
            return jsonify({"error": "товар не найден в каталоге"}), 404
        
        product_data = response.json()

    except Exception as e:
        return jsonify({"error": "связь с Каталогом прервана", "details": str(e)}), 503

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

    integration.publish_message(queue_name="cart_events", message={
        "user_id": user_id,
        "product_id": product_id,
        "action": "add_to_cart"
    })

    return jsonify({"message": "товар добавлен", "cart": carts[user_id]}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)