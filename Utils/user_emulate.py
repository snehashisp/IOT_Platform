from confluent_kafka import Producer, Consumer, OFFSET_END
import string
import random
import json
import sys

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

name, loc, gloc, db = None, None, None, None
try:
    name = sys.argv[sys.argv.index('-n') + 1]
except:
    pass
try:
    loc = sys.argv[sys.argv.index('-l') + 1]
except:
    pass
try:
    gloc = sys.argv[sys.argv.index('-g') + 1]
except:
    pass
try:
    db = sys.argv[sys.argv.index('-d') + 1]
except:
    pass

def gen_random_string(length):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length)) 
    return str(res)

def gen_random_configs(length = 5):
    configs = {}
    global name, loc, gloc, db
    configs["name"] = gen_random_string(length) if name == None else name
    configs["location"] = gen_random_string(length) if loc == None else loc
    configs["geolocation"] = ",".join(random.choices([str(i) for i in range(100)], k = 2)) if gloc == None else gloc
    configs["db_endpoint"] = gen_random_string(length) if db == None else db
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
while True:
    message = kafka_consumer.poll(0)
    if message != None and not message.error():
        random_config = gen_random_configs()
        sensor_meta = json.loads(message.value().decode())
        print("New Sensor", sensor_meta)
        new_sensor = {'type':"new_sensor_config", "content":sensor_meta}
        new_sensor['content']['configs'] = random_config
        print("New Sensor Config", new_sensor)
        kafka_producer.produce(sensor_topic, json.dumps(new_sensor))



