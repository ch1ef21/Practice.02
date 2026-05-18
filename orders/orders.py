from flask import Flask, request, jsonify
import uuid
from datetime import datetime
# Импортируем наш общий сервис
from integrationLib.rabbitmq_helper import IntegrationService

app = Flask(__name__)
integration = IntegrationService()

@app.route('/orders/create', methods=['POST'])
def create_order():
    data = request.json
    user_id = data.get('user_id')
    items = data.get('items')

    if not user_id or not items:
        return jsonify({"error": "Неполные данные заказа"}), 400

    order_id = str(uuid.uuid4())
    
    order_event = {
        "order_id": order_id,
        "user_id": user_id,
        "items": items,
        "status": "Created",
        "timestamp": datetime.now().isoformat()
    }

    try:
        integration.publish_message(queue_name='order_events', message=order_event)
    except Exception as e:
        return jsonify({"error": f"Ошибка интеграции: {str(e)}"}), 500

    return jsonify({
        "message": "Заказ создан и отправлен в очередь",
        "order_id": order_id
    }), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)