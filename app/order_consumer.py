import pika
import json
import os
import sys
import time

def process_checkout_event(ch, method, properties, body):
    try:
        order_payload = json.loads(body)
        user_id = order_payload.get('user_id')
        print(f" [Orders Worker] Получено событие order_checkout для пользователя {user_id}", flush=True)
        
        
        time.sleep(0.5) 
        print(f" [Orders Worker] Заказ для пользователя {user_id} успешно сохранен в БД.", flush=True)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Ошибка при обработке события заказа: {e}", file=sys.stderr, flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    print("Запуск Асинхронного Воркера Заказов...", flush=True)
    time.sleep(10)
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    
    channel.queue_declare(queue='order_checkout', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='order_checkout', on_message_callback=process_checkout_event)
    
    print(" [*] Воркер заказов готов к приему асинхронных checkout-событий...", flush=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()