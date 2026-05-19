from flask import Flask, request, jsonify
import uuid
import integrationLib.rabbitmq_helper as rabbitmq_helper
from models import OrderRepository

app = Flask(__name__)
integration = rabbitmq_helper.IntegrationService()
db_set_orders = OrderRepository()

@app.route('/orders/create', methods=['POST'])
def create_order():
    data = request.json
    if not data:
        return jsonify({"error": "Пустой запрос"}), 400

    user_id = data.get('user_id')
    items = data.get('items', [])

    order_id = str(uuid.uuid4())

    try:
        db_set_orders.add(order_id=order_id, user_id=user_id, status='Created')
    except Exception as e:
        return jsonify({"error": "Не удалось сохранить заказ в БД", "details": str(e)}), 500

    order_event = {
        "order_id": order_id,
        "user_id": user_id,
        "items": items,
        "status": "Created"
    }

    integration.publish_message(queue_name="order_events", message=order_event)

    return jsonify({
        "message": "Заказ успешно создан и сохранен в БД",
        "order_id": order_id,
        "status": "Created"
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)