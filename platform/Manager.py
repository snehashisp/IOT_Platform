# import sys
# import os
# sys.path.append(os.getcwd() + "/..")
import json
from confluent_kafka import Producer, Consumer, OFFSET_END
from confluent_kafka.admin import NewPartitions, AdminClient
from API.Registry import *
from API.DatabaseIngestor import *
from threading import *
from API.TopicPublisher import *
import API.Sensor as Sensor

class MessageExec:

    def __init__(self, config = "Configs/platform_configs.json"):
        with open(config, 'r') as fp:
            configs = json.load(fp)
            self._admin_topic = configs["admin_topic"]
            self._topic_publisher = TopicPublisher(config)
            self._registry = Registry(config)
        self.ingestor = DatabaseIngestor(config)

    def _new_sensor(self, content):
        self._topic_publisher.publish(self._admin_topic, json.dumps(content))
        print("New Sensor Registering ip", content['ip_port'])

    def _add_db_endpoint(self, sensor_data):
        sensor = Sensor.Sensor(**sensor_data)
        self.ingestor.add_connection(sensor)
        print("Added New Db endpoint ", sensor.ip_port, sensor.configs['db_endpoint'])

    def _new_sensor_config(self, sensor_data):
        sensor = Sensor.Sensor(**sensor_data)
        self._registry.addSensor(sensor)
        #print(content)
        db_ep = sensor_data["configs"].get("db_endpoint", None)
        if db_ep != None and db_ep != "None":
            self.ingestor.add_connection(sensor)
        print("Added New Sensor Configuration ", sensor_data['ip_port'], sensor_data['configs'])
    
    def _remove_db_endpoint(self, sensor_data):
        sensor = Sensor.Sensor(**sensor_data)
        self.ingestor.remove_connection(sensor)


    def exec(self, message):
        message = json.loads(message)
        if message["type"] == "new_sensor":
            self._new_sensor(message["content"])
        elif message["type"] == "new_sensor_config":
            self._new_sensor_config(message["content"])
        elif message["type"] == "remove_db_endpoint":
            self._remove_db_endpoint(message["db_endpoint"])
        elif message["type"] == "add_db_endpoint":
            self._add_db_endpoint(message["sensor_data"])

class Manager:

    def _kafkaAssign(self):
        consumer_assigned = False
        def flush(consumer, partition):
            nonlocal consumer_assigned
            for p in partition:
                p.offset = OFFSET_END
            consumer.assign(partition)
            consumer_assigned = True

        self.kafka_consumer.subscribe([self.manager_topic], on_assign = flush)
        while not consumer_assigned:
            self.kafka_consumer.poll(1)

    def _configuire_topic(self, configs):
        admin_client = AdminClient({'bootstrap.servers':configs['kafka_host']})
        sensor_topic_partitions = NewPartitions(configs['sensor_manager_topic'], int(configs['sensor_manager_topic_partitions']))
        admin_client.create_partitions([sensor_topic_partitions])

    def _get_data(self):
        message = self.kafka_consumer.poll(self._response_timeout)
        if message != None and not message.error():
            return message.value().decode()
        return None

    def _manager_consumer_thread(self):
        while self._status:
            message = self._get_data()
            #print(message)
            if message != None:
                #pass
                self.message_executor.exec(message)

    def __init__(self, config = "Configs/platform_configs.json"):
        self.message_executor = MessageExec(config)
        with open(config, 'r') as fp:
            configs = json.load(fp)
            self.manager_topic = configs["sensor_manager_topic"]
            self._configuire_topic(configs)
            self.kafka_consumer = Consumer({
                "bootstrap.servers": configs['kafka_host'],
                "group.id": "sensor_manager",
                "auto.offset.reset":'latest'
            })
            self._kafkaAssign()
            self._response_timeout = configs["sensor_manager_response_timeout"]
            print("Subscribed to sensor_manager")

    def start(self):
        self._status = True
        self.manager_thread = threading.Thread(target=self._manager_consumer_thread)
        self.manager_thread.start()
        print("Manager polling thread started")

    def stop(self):
        self._status = False
        self.manager_thread.join()
        self.kafka_consumer.close()


if __name__ == "__main__":
    manager = Manager()
    manager.start()
