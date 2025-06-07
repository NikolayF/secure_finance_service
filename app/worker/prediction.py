import pika
import os



def prediction_worker(queue_name: str):
    rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
    connection_params = pika.ConnectionParameters(
    host=rabbitmq_host, 
    port=os.environ.get('RABBITMQ_PORT', 5672),  
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=os.environ.get('RABBITMQ_USER'), 
        password=os.environ.get('RABBITMQ_PASS')
    ),
    heartbeat=30,
    blocked_connection_timeout=2
    )
    
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)

    return channel
    