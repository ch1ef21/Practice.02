from flask import Flask, request, jsonify
import pika
import json
import uuid
from datetime import datetime

app = Flask(__name__)

def send_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='order_events', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='order_events',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  
        )
    )
    connection.close()

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
        send_to_queue(order_event)
    except Exception as e:
        return jsonify({"error": f"Ошибка RabbitMQ: {str(e)}"}), 500

    return jsonify({
        "message": "Заказ создан и отправлен в очередь на обработку",
        "order_id": order_id
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=3000)