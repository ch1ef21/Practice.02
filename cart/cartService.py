from flask import Flask, request, jsonify
import requests
import os
import integrationLib.rabbitmq_helper as rabbitmq_helper
from mapping.order_mapper import map_cart_to_order
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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


@app.route('/cart/checkout', methods=['POST'])
def checkout():
    data = request.json
    user_id = str(data.get('user_id'))

    user_cart = carts.get(user_id)
    if not user_cart:
        return jsonify({"error": "Корзина пуста"}), 400

    order_payload = map_cart_to_order(user_id, user_cart)

    try:
        integration.publish_message(
            queue_name="order_checkout", 
            message=order_payload
        )
        
        carts[user_id] = []
        
        return jsonify({
            "status": "accepted",
            "message": "Запрос на оформление заказа принят и поставлен в очередь обработки"
        }), 202

    except Exception as e:
        return jsonify({
            "error": "Не удалось отправить заказ в шину сообщений", 
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)