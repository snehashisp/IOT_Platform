from API.sensor_api import *
import sys
import os
sys.path.append(os.getcwd())

sensor_name = sys.argv[1]
sensor = getSensor({"name":sensor_name})[0]
sensor.doAction('start')
kafka_retriever = sensor.getKafkaRetriever('test_user')
wait_time = sensor.specifications['poll_rate']
continous_ones = 0
while True:
    data = kafka_retriever.retrieve(batchsize = 1, total_time = wait_time)[0]
    reading = int(data['value'])
    #print(reading)
    if reading == 0:
        continous_ones = 0
    else:
        continous_ones += 1
    if continous_ones > 60:
        #notify security office using action and notification manager
        print("Someone might be accessing location " + sensor.configs['location'] + " illegally")
