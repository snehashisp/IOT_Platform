from confluent_kafka import Producer
import json

class TopicPublisher:
    
    def __init__(self, config = "Configs/platform_configs.json"):
        with open(config, 'r') as fp:
            configs = json.load(fp)
            self.producer = Producer({"bootstrap.servers":configs["kafka_host"]})
    
    def publish(self, topic, message, partition = None):
        #print(topic, message)
        if partition:
            self.producer.produce(topic, message.encode(), partition = partition)
        else:
            self.producer.produce(topic, message.encode())
        self.producer.poll(0)