from API.sensor_api import *
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime
import threading 
sys.path.append(os.getcwd())

temp_sensor_name = sys.argv[1]
data_duration = 300
if len(sys.argv) == 3:
    data_duration = int(sys.argv[2])

temp_sensor = getSensor({"name":temp_sensor_name})[0]
temp_sensor.doAction('start')

kafka_retriever = temp_sensor.getKafkaRetriever('test_user')
db_retriever = temp_sensor.getDatabaseRetriever()
wait_time = temp_sensor.specifications['poll_rate']

alarm_sensor = getSensor({'location':temp_sensor.configs['location'], 'type':'alarm'})[0]

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

coord = []
def animate(i):
    global coord
    xar = []
    yar = []
    for i, c in enumerate(coord):
        xar.append(i)
        yar.append(c)
    ax1.clear()
    ax1.plot(xar,yar)

ani = animation.FuncAnimation(fig, animate, interval=1000)

def run_alarm_thread():
    while True:
        data = kafka_retriever.retrieve(batchsize = 1, total_time = wait_time)[0]
        reading = int(data['value'])
        if reading > 200:
            alarm_sensor.doAction('start')
            break

def plot_data_thread(duration):
    filters = {}
    global coord
    while True:
        time_now = datetime.datetime.now()
        filters['StartTime'] = str(time_now - datetime.timedelta(seconds = duration))
        filters['EndTime'] = str(time_now)
        filters['Count'] = int(duration/wait_time)
        data = reversed(db_retriever.retrieve(filters))
        coord = []
        for d in data:
            coord.append(int(d['value']))
        #print(coord)
        time.sleep(wait_time)

alarm_thread = threading.Thread(target = run_alarm_thread)
data_thread = threading.Thread(target = plot_data_thread, args = (data_duration, ))
alarm_thread.start()
data_thread.start()
plt.show()

