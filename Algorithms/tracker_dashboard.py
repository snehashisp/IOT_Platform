from API.sensor_api import *
import sys
import pygame
import time

circle_rad = 5
restrict_rad = 40
colors = {"healthy":(0, 0, 255), "infected":(255, 0, 0), "recovered":(0, 255, 0), "dead":(125,125,125), 'restricted': (0,255,255)}
tracking_set = {}
dead_set = {}
vdim, hdim = 500, 400
stats_vpos = 400

location = sys.argv[1]
logging_location = sys.argv[2]

pygame.init()
display = pygame.display.set_mode((hdim, vdim))
display_refresh = 60
pygame.font.init() 
font_size = 15
myfont = pygame.font.SysFont('Comic Sans MS', font_size)

infected, recovered = {}, set()

print("Initiating Tracking ")
sensors = getSensor({'location':location})
for sensor in sensors:
    tracking_set[sensor.ip_port] = sensor.getDatabaseRetriever()#(sensor.configs['name'], skip_assign = False)
    print("Initializing " + sensor.configs['name'])

print("Starting Tracking")
for sensor in sensors:
    sensor.doAction('start')

def log(sensor):
    with open(logging_location + "/" + sensor.configs["name"], 'w+') as fp:
        movement_logs = sensor.getDatabaseRetriever().retrieve({"Count":100})
        for log in movement_logs:
            fp.write("|".join(["Time:" + log["time"], "Location:" + log['value']['location'], 'Status:' + log['value']['status']]) + "\n")

def send_restrict_message(pos):
    for sensor in sensors:
        if sensor.ip_port not in dead_set:
            sensor.doAction('restrict', pos)

def send_release_message(pos):
    for sensor in sensors:
        if sensor.ip_port not in dead_set:
            sensor.doAction('release', pos)

def render_stats():
    infected_text = myfont.render('Infected: ' + str(len(infected)), False, (255, 0, 0))
    dead_text = myfont.render('Dead: ' + str(len(dead_set)), False, (125, 125, 125))
    recovered_text = myfont.render('Recovered: ' + str(len(recovered)), False, (0, 255, 0))
    rem = len(sensors) - len(infected) - len(dead_set) - len(recovered)
    healthy_text = myfont.render('Healthy: ' + str(rem), False, (0, 0, 255))
    vpos = 0
    for text in [infected_text, dead_text, recovered_text, healthy_text]:
        display.blit(text, (0, stats_vpos + vpos))
        vpos += font_size + 3




def track_and_update():
    for sensor in sensors:
        if sensor.ip_port in tracking_set:
            info = tracking_set[sensor.ip_port].retrieve()#(batchsize = 1, total_time = 0.01)
            # print(info)
            if info == []:
                continue
            info = info[0]['value']
            x, y = info['location'][1:-1].split(',')
            pos = (int(x), int(y))
            if info['status'] == 'dead':
                print(sensor.configs["name"] + " Died ")
                tracking_set.pop(sensor.ip_port)
                dead_set[sensor.ip_port] = pos
                send_release_message(infected[sensor.ip_port])
                try:
                    infected.pop(sensor.ip_port)
                except:
                    pass
                sensor.doAction('stop')
                log(sensor)
            elif info['status'] == 'infected' and sensor.ip_port not in infected:
                print(sensor.configs["name"] + " got infected ")
                send_restrict_message(pos)
                infected[sensor.ip_port] = pos
            elif info['status'] == 'recovered' and sensor.ip_port not in recovered:
                print(sensor.configs["name"] + " recoverd ")
                send_release_message(infected[sensor.ip_port])
                try:
                    infected.pop(sensor.ip_port)
                except:
                    pass
                recovered.add(sensor.ip_port)
            status = info['status']
        elif sensor.ip_port in dead_set:
            pos = dead_set[sensor.ip_port]
            status = 'dead'
        pygame.draw.circle(display, colors[status], (int(pos[0]), int(pos[1])), circle_rad)
    for pos in infected.values():
        pygame.draw.circle(display, colors['restricted'], (int(pos[0]), int(pos[1])), restrict_rad, 2)
    render_stats()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    total_time = 1/display_refresh
    tn = time.time()
    track_and_update()
    # display.fill((0,0,0))
    pygame.display.update()
    rem_time = total_time - (time.time() - tn)
    if rem_time > 0:
        time.sleep(rem_time)
    display.fill((0,0,0))





