import json
import time
import sys
import os
import pika
from models import ProductRepository

db_set_products = ProductRepository()

def reply_to_orders(ch, status, order_id, user_id):
    """Отправка ответа (события) обратно в сервис заказов"""
    reply_queue = 'order_saga_replies'
    ch.queue_declare(queue=reply_queue, durable=True)
    
    reply_message = {
        'order_id': order_id,
        'user_id': user_id,
        'saga_status': status
    }
    
    ch.basic_publish(
        exchange='',
        routing_key=reply_queue,
        body=json.dumps(reply_message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f" [Saga] Отправлен ответ в Сагу: {status} для Заказа {order_id}", flush=True)

def process_order_event(ch, method, properties, body):
    try:
        event_data = json.loads(body)
        order_id = event_data.get('order_id')
        user_id = event_data.get('user_id')
        items = event_data.get('items', [])
        
        print(f" [Saga] Шаг 2: Проверка и списание для заказа {order_id}", flush=True)
        
        success = True
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            product = db_set_products.get_by_id(product_id)
            if not product or product['stock'] < quantity:
                print(f" [Saga] КРИТИЧЕСКИЙ СБОЙ: Нет товара {product_id} на складе!", flush=True)
                success = False
                break
            
            for attempt in range(3):
                try:
                    db_set_products.reduce_stock(product_id, quantity)
                    break
                except Exception as db_err:
                    if attempt == 2: raise db_err
                    time.sleep(1) 
                    
        if success:
            print(f" [Saga] Склад подтвержден для заказа {order_id}", flush=True)
            reply_to_orders(ch, 'SUCCESS', order_id, user_id)
        else:
            print(f" [Saga] Склад отклонен для заказа {order_id}. Инициируем откат!", flush=True)
            reply_to_orders(ch, 'REJECTED', order_id, user_id)
            
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Ошибка Саги на стороне Воркера: {e}", file=sys.stderr, flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    print("Запуск Сага-Воркера Каталога...", flush=True)
    time.sleep(10)
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    channel.queue_declare(queue='order_events', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='order_events', on_message_callback=process_order_event)
    
    print(" [*] Сага-Воркер ждет шага распределенной транзакции...", flush=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()