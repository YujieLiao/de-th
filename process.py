from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import json
import time
import csv
from collections import defaultdict

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

def get_message(message):
    try:
        data = json.loads(message.value().decode('utf-8'))
        

        user_id = data.get('user_id')
        app_version = data.get('app_version')
        ip = data.get('ip')
        locale = data.get('locale')
        device_id = data.get('device_id')
        timestamp = time.gmtime(data.get('timestamp'))
        device_type = data.get('device_type')


        print(f"User ID: {user_id}")
        print(f"App Version: {app_version}")
        print(f"IP Address: {ip}")
        print(f"Locale: {locale}")
        print(f"Device ID: {device_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Device Type: {device_type}")
        print("-----------------------------")

    except Exception as e:
        print(f"Error processing message: {e}")

    return user_id, app_version, ip, locale, device_id, timestamp, device_type

def process_message(app_version_dict, locale_dict, device_type_dict):
    combined_dict = {
        'app_version': app_version_dict,
        'locale': locale_dict,
        'device_type': device_type_dict,
    }
    combined_json = json.dumps(obj=combined_dict)
    producer.produce('processed-user-login', value=combined_json.encode('utf-8'))

    producer.flush()
    return


if __name__ == "__main__":
    start_time = time.time()
    app_version_dict = defaultdict(int)
    locale_dict = defaultdict(int)
    device_type_dict = defaultdict(int)
    cnt = 0

    try:
        while cnt < 20:
            cnt += 1
            msg = consumer.poll(timeout=1.0)  
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.partition} {msg.offset}")
                else:
                    raise KafkaException(msg.error())
            else:
                user_id, app_version, ip, locale, device_id, timestamp, device_type = get_message(message=msg)  
                app_version_dict[app_version] += 1
                locale_dict[locale] += 1
                device_type_dict[device_type] += 1
            if cnt == 20:
                process_message(app_version_dict, locale_dict, device_type_dict)
                cnt = 0
                app_version_dict = defaultdict(int)
                locale_dict = defaultdict(int)
                device_type_dict = defaultdict(int)
    finally:
        consumer.close()  

    

    # with open('processed_data.csv', mode='w', newline='', encoding='utf-8') as file:
    #     writer = csv.DictWriter(file, fieldnames=['user_id', 'app_version', 'ip', 'locale', 'device_id', 'timestamp', 'device_type'])
    #     writer.writeheader()
    #     writer.writerows(collected_data)
