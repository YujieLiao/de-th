from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import json
import time
import csv

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'consumer_gp1',
    'auto.offset.reset': 'earliest'
}

producer_conf = {
    'bootstrap.servers': 'localhost:29092',  
}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)

consumer.subscribe(['user-login'])

def process_message(message):
    try:
        # Deserialize the JSON message
        data = json.loads(message.value().decode('utf-8'))
        
        # Extract fields from the message
        user_id = data.get('user_id')
        app_version = data.get('app_version')
        ip = data.get('ip')
        locale = data.get('locale')
        device_id = data.get('device_id')
        timestamp = data.get('timestamp')
        device_type = data.get('device_type')

        collected_data.append({
            'user_id': user_id,
            'app_version': app_version,
            'ip': ip,
            'locale': locale,
            'device_id': device_id,
            'timestamp': timestamp,
            'device_type': device_type
        })

        # Process the data (printing in this example)
        print(f"User ID: {user_id}")
        print(f"App Version: {app_version}")
        print(f"IP Address: {ip}")
        print(f"Locale: {locale}")
        print(f"Device ID: {device_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Device Type: {device_type}")
        print("-----------------------------")

        new_message = json.dumps({
            'user_id': user_id,
            'app_version': app_version,
            'ip': ip,
            'locale': locale,
            'device_id': device_id,
            'timestamp': timestamp,
            'device_type': device_type
        })

        producer.produce('processed-user-login', value=new_message)
        producer.flush()

    except Exception as e:
        print(f"Error processing message: {e}")

start_time = time.time()
collected_data = []
try:
    while time.time() - start_time < 60:
        msg = consumer.poll(timeout=1.0)  # Poll for new messages
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.partition} {msg.offset}")
            else:
                raise KafkaException(msg.error())
        else:
            process_message(message=msg)  # Process each message

finally:
    consumer.close()  # Ensure the consumer is closed after finishing

with open('processed_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['user_id', 'app_version', 'ip', 'locale', 'device_id', 'timestamp', 'device_type'])
    writer.writeheader()
    writer.writerows(collected_data)
