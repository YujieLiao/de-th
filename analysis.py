from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import json
import time
import csv
from collections import defaultdict

consumer_conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'processed-user-consumer',
}
consumer = Consumer(consumer_conf)
topic = 'processed-user-login'
consumer.subscribe([topic])


def get_message(message):
    try:
        data = json.loads(message.value().decode('utf-8'))
        app_version_dict_new = data.get('app_version')
        locale_dict_new = data.get('locale')
        device_type_dict_new = data.get('device_type')
        
    except Exception as e:
        print(f"Error processing message: {e}")

    return app_version_dict_new, locale_dict_new, device_type_dict_new

if __name__ == "__main__":
    start_time = time.time()
    app_version_dict = defaultdict(int)
    locale_dict = defaultdict(int)
    device_type_dict = defaultdict(int)
    try:
        while True:
            msg = consumer.poll(timeout=1.0)  
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.partition} {msg.offset}")
                else:
                    raise KafkaException(msg.error())
            else:
                app_version_dict_new, locale_dict_new, device_type_dict_new = get_message(message=msg)  
                for key, value in app_version_dict_new.items():
                    app_version_dict[key] += value  
                for key, value in locale_dict_new.items():
                    locale_dict[key] += value
                for key, value in device_type_dict_new.items():
                    device_type_dict[key] += value
                most_popular_state =  max(locale_dict, key=locale_dict.get)
                print(locale_dict)
                print(device_type_dict)
                print(most_popular_state)

    finally:
        consumer.close()  
