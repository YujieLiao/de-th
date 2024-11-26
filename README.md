# de-th
## Kafka Data Processing Pipeline
### Overview:
This project implements a Kafka-based data processing pipeline with the following features:
Consumer 1: A kafka consumer in process.py reads raw data from the user-login topic, aggregates data in batches of 20 messages, extracting fields like app_version, locale, and device_type.
Producer: Aggregated data comes from consumer 1. Processed data is published to a new Kafka topic, processed-user-login.
Consumer 2: In analysis.py, a kafka consumer subscrib to processed-user-login topic and consume data for real-time analysis. It merges incoming aggregated data with historical data in memory for real-time analysis, such as identifying the most popular locale or app version. For further process, the data can saved to SQL database and connect to Tableau for data visualization. 

### How to run this project 
'docker-compose up' -- run the docker and you will see the row data on console.
<br> 'python process.py' -- run the consumer to consumer data from user-login topic
<br>'docker exec -it de-th-kafka-1 /bin/bash' and 'kafka-console-consumer --bootstrap-server localhost:9092 --topic processed-user-login' -- this allows you to check processed data in processed-user-login.
<br> 'kafka-console-consumer --bootstrap-server localhost:9092 --topic processed-user-login --from-beginning' -- if you want to have information from beginning
<br> 'python analysis.py' -- run the consumer to consumer data from processed-user-login to merge data with historical data for real-time analysis. It analyzes the most polular device type, most popular state, and which state has the most/lease user login. 

### Design Choices
1. Architecture
Kafka is chosen as the core messaging system due to its ability to handle real-time, high-throughput data. Docker Compose is used to orchestrate the Kafka, Zookeeper, producer, and consumer services, ensuring reproducibility. The data processing logic is implemented in Python for flexibility and ease of integration with other tools.
2. Topics
user-login: Stores raw login events.
processed-user-login: Stores processed login events, such as data enriched with locale-based aggregation or IP validation.
3. Consumer and Producer
The Kafka consumer reads messages from the user-login topic and processes them with Python. The processed messages are published to the processed-user-login topic using a Kafka producer.
4. Scalability
Kafka topics are partitioned to allow multiple consumers to process data in parallel, ensuring horizontal scalability. The pipeline leverages Kafka’s distributed nature, making it suitable for high-volume, real-time streaming.
5. Fault Tolerance
Kafka’s replication ensures durability of messages. The consumer uses an offset management strategy (auto.offset.reset='earliest') to handle restarts and avoid data loss. 

### Data Flow:
Kafka broker -> comsumer process and aggregate data with 20 messages -> aggregated data to producer processed-user-login topic -> consumer subscribe to processed-user-login and aggregate data with historical data for real-time analysis, such as most popular locale.
1. Efficiency
Batch Processing: The consumer processes messages in batches to reduce overhead and improve throughput. Instead of producing one message per input, batching (the data in processed-user-login is 20 messaged combined) reduces the number of messages in the processed-user-login topic. Downstream consumers like analysis.py handle fewer, richer messages, improving their performance and scalability. This reduce the time of IO expensive operations like SQL insert.
2. Scalability
Partitions: Kafka topics are partitioned to enable parallel processing by multiple consumers.
Consumer Groups: Multiple consumer instances can read from partitions in a coordinated manner, enabling load balancing.
Stateless Design: Processing logic is stateless, allowing it to scale horizontally.
3. Fault Tolerance
Replication Factor: Topics currently have a replication factor of 1 but it can be increased for production/distribution. 
Buffer: Kafka consumers are designed to resume consuming from the last committed offset after being restarted, provided that proper offset management is in place. This behavior depends on the consumer configuration and whether the offsets were successfully committed before the consumer was interrupted. if the consumer in process.py is broken, it can resume the last committed offset when it restarts.

### Additional Questions:
1. How would you deploy this application in production?
While Docker Compose is great for local development and testing, it lacks features for production environments. Kubernetes is better suited for production use cases where high availability, scalability, and fault tolerance are critical. Kubernetes can run and manage Kafka and Zookeeper containers, ensuring they are always available and automatically scaled when needed. Then to monitor message logs, Grafana dashboards can be used.

2. What other components would you want to add to make this production ready?
I want to increase Kafka’s replication factor to at least 3 for fault tolerance. Then use Kafka ACLs to limit access to topics based on user roles for data protection. To handle messaged that is failed to be processed, we can use Kafka Dead Letter Queue. The consumer or producer can decide to route the problematic message to a DLQ instead of retrying indefinitely or discarding it.

3. How can this application scale with a growing dataset?
Add Partitions: Increase the number of partitions for the user-login and processed-user-login topics to distribute the load.
Horizontal Scaling: Add more consumer instances in the same consumer group to process partitions in parallel.
Tuning Batch Size: Adjust max.poll.records and fetch.min.bytes for efficient batch processing.
Scalable Storage: Use cloud object storage such as AWS S3 for archiving older Kafka logs.