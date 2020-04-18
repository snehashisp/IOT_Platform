from API.sensor_api import *
import sys
import os
sys.path.append(os.getcwd())

sensor_name = sys.argv[1]
sensor = getSensor({"name":sensor_name})[0]
sensor.doAction('start')
kafka_retriever = sensor.getKafkaRetriever('test_user')
wait_time = sensor.specifications['poll_rate']
while True:
    data = kafka_retriever.retrieve(batchsize = 1, total_time = wait_time + 5)[0]
    reading = int(data['value'])
    if reading > 10 and reading < 59:
        sensor.doAction('print', 'LOW_TEMP ' + str(reading))
    elif reading > 60 and reading < 100:
        sensor.doAction('print', 'NORMAL_TEMP ' + str(reading))
    elif reading > 101 and reading < 120:
        sensor.doAction('print', 'HIGH_TEMP ' + str(reading))
