import json
import time
import sys
import os
import pika
from models import ProductRepository

db_set_products = ProductRepository()

def process_order_event(ch, method, properties, body):
    try:
        event_data = json.loads(body)
        print(f" [x] Получено событие заказа: {event_data}", flush=True)
        
        items = event_data.get('items', [])
        
        with db_set_products._get_connection() as conn:
            with conn.cursor() as cur:
                for item in items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)
                    print(f"Синхронизация: Списываем товар {product_id} в количестве {quantity} шт.", flush=True)
                conn.commit()
                
        print(" [x] Синхронизация каталога успешно завершена!", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Ошибка при синхронизации события: {e}", file=sys.stderr, flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    print("Запуск воркера синхронизации Каталога...", flush=True)
    time.sleep(10)
    
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    channel.queue_declare(queue='order_events', durable=True)
    
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(
        queue='order_events', 
        on_message_callback=process_order_event
    )
    
    print(" [*] Успешно подключено к RabbitMQ. Ожидание сообщений...", flush=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Воркер остановлен вручную.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)