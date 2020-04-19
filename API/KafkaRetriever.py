from confluent_kafka import Producer, Consumer, OFFSET_END
import json
import pymongo 
from datetime import datetime

class KafkaRetriever():

    def __init__(self, sensor_kafka_endpoint, user_id, config = "Configs/platform_configs.json"):

        with open(config, "r") as fp:
            configs = json.load(fp)
            kafka_host = configs["kafka_host"]
            self.kafka_consumer = Consumer({
                "bootstrap.servers": kafka_host,
                "group.id": user_id,
                "auto.offset.reset":'earliest'
            })
            self.kafka_topic = sensor_kafka_endpoint
            self._default_batchsize = configs["default_count_returned"]
            self._kafkaAssign()

    def _kafkaAssign(self):
        consumer_assigned = False
        def flush(consumer, partition):
            nonlocal consumer_assigned
            for p in partition:
                p.offset = OFFSET_END
            consumer.assign(partition)
            consumer_assigned = True


        self.kafka_consumer.subscribe([self.kafka_topic], on_assign = flush)
        while not consumer_assigned:
            self.kafka_consumer.poll(1)

    def _get_data(self, response_timeout):
        message = self.kafka_consumer.poll(timeout = response_timeout)
        if message != None and not message.error():
            return message.value().decode()
        return None

    def retrieve(self, batchsize = None, total_time = 1.0):
        if batchsize == None:
            batchsize = self._default_batchsize
        data = []
        while batchsize and total_time > 0:
            time_now = datetime.utcnow()
            message = self._get_data(total_time)
            if message != None:
                data.append(json.loads(message))
                batchsize -= 1
            total_time -= (datetime.utcnow() - time_now).seconds
        return data

    def close(self):
        self.kafka_consumer.close()

    def __del__(self):
        self.close()
