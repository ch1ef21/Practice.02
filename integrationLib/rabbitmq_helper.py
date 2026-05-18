import pika
import json
import os

class IntegrationService:
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')

    def publish_message(self, queue_name: str, message: dict):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
            channel = connection.channel()

            channel.queue_declare(queue=queue_name, durable=True)
            
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2, 
                )
            )
            print(f" [integration] отправлено в очередь '{queue_name}': {message}")
            connection.close()
            
        except Exception as e:
            print(f" [integration] ошибка сети RabbitMQ: {e}")