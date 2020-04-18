from confluent_kafka import Producer, Consumer, OFFSET_END
import string
import random
import json

admin_topic = 'admin_topic'
sensor_topic = 'sensor_manager'
kafka_consumer = Consumer({
    "bootstrap.servers":"localhost:9092",
    "group.id":"10",
    "auto.offset.reset":"latest"
})
kafka_producer = Producer({
    "bootstrap.servers":"localhost:9092"
})

def get_configs(new_sensor):
    print("New Sensor Registered", json.dumps(new_sensor, indent=4))
    configs = {}
    configs['name'] = input("Enter Name ")
    configs['location'] = input("Enter Location ")
    configs['geolocation'] = input("Enter Geolocation ")
    configs['db_endpoint'] = input("Enter DB ingestion endpoint (send None for no endpont) ")
    return configs

    
def _kafkaAssign():
    consumer_assigned = False
    global kafka_consumer
    def flush(consumer, partition):
        nonlocal consumer_assigned
        for p in partition:
            p.offset = OFFSET_END
        consumer.assign(partition)
        consumer_assigned = True


    kafka_consumer.subscribe([admin_topic], on_assign = flush)
    while not consumer_assigned:
        kafka_consumer.poll(1)

kafka_consumer.subscribe([admin_topic])
_kafkaAssign()
print("Simple Command Line User Started")
while True:
    message = kafka_consumer.poll(0)
    if message != None and not message.error():
        # random_config = gen_random_configs()
        sensor_meta = json.loads(message.value().decode())
        user_config = get_configs(sensor_meta)
        new_sensor = {'type':"new_sensor_config", "content":sensor_meta}
        new_sensor['content']['configs'] = user_config
        # print("New Sensor Config", new_sensor)
        kafka_producer.produce(sensor_topic, json.dumps(new_sensor))



