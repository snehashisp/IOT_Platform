import socket                
import threading
import sys
import json
import random
import datetime
import time
import math


state = False
poll_rate = 0.2
height, width = 400, 400

current_angle = int(random.uniform(0, 360))
step_distance = 4
move_duration_max = 5
pos = (random.randint(0, width), random.randint(0, height))
move_duration = random.randint(1, move_duration_max)


person_status = "healthy"
default_infection_chance = 0.03
infection_multiplier = 3
death_chance = 0.01
infection_duration = 20

avoid_radius = 40
avoid_centres = set()

def udp_init():
    sensor_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sensor_sock

# sensor data format (gateway sends this to sensor topic (ip_port of sensor))
# {
#     "type": "sensor_data",
#     "content": {
#         "time": "...", \\get time using datetime.datetime.utcnow()
#         "value": "..." \\generate value randomly
#     }
# }

def _check_danger(nx, ny):
    global avoid_centres, avoid_radius
    for centres in avoid_centres:
        if (centres[0] - nx)**2 + (centres[1] - ny)**2 < avoid_radius**2:
            # print("Inside Centre", centres)
            return True
    return False

def _check_boundary(nx, ny):
    if nx < 0 or nx > width or ny < 0 or ny > height:
        return True
    return False

def _move():
    global current_angle, move_duration, move_duration_max, pos, step_distance
    if person_status in ['healthy', 'recovered'] and not _check_danger(pos[0], pos[1]):
        while True:
            nx, ny = pos[0] + step_distance * math.cos(current_angle * (math.pi/180)), pos[1] + step_distance * math.sin(current_angle * (math.pi/180))
            # print(nx, ny, current_angle)
            if _check_danger(nx, ny) or _check_boundary(nx, ny) or move_duration < 0:
                current_angle = int(random.uniform(0, 360))
                if move_duration < 0:
                    move_duration = random.randint(1, move_duration_max)
            else:
                break
        # print(nx, ny, current_angle)
        pos = (int(nx), int(ny))
        move_duration -= 1*poll_rate

def _update_person_status():
    global state
    while True:
        if state:
            global person_status, infection_duration, death_chance, infection_multiplier, default_infection_chance
            if person_status != "dead":
                if person_status == "healthy":
                    ic = default_infection_chance
                    if _check_danger(pos[0], pos[1]):
                        ic *= infection_multiplier
                    if random.uniform(0, 1) < ic:
                        person_status = "infected"
                if person_status == "infected":
                    if infection_duration <= 0:
                        person_status = "recovered"
                    else:
                        if random.uniform(0, 1) < death_chance:
                            person_status = "dead"
                        infection_duration -= 1
        time.sleep(1)



def generate_random_data(start, end):
    random_data = {}
    random_data["type"] = "sensor_data"
    content = {}
    content["time"] = str(datetime.datetime.now())
    _move()
    global person_status, pos
    content["value"] = {"location":str(pos), "status":person_status}
    random_data["content"] = content
    # print(random_data['content'])
    random_data = json.dumps(random_data)
    return random_data
    

def receive_data(recipient_socket_address):
    data, addr = recipient_socket_address.recvfrom(1024)
    print("Message: ", data.decode())
    return data.decode()

def send_data(sock, recipient_ip_address, recipient_port, Message):
    sock.sendto(Message.encode(), (recipient_ip_address, recipient_port))
    #print(Message)

def receive_from_gateway(sensor_socket):
    global state, poll_rate, avoid_centres
    while True:
        gateway_data = receive_data(sensor_socket)
        message = json.loads(gateway_data)
        if message["action"] == "print":
            print(message["value"])
        elif message["action"] == "start":
            state = True
        elif message["action"] == "stop":
            state = False
        elif message["action"] == "poll_rate":
            poll_rate = float(message["value"])
        elif message["action"] == "restrict":
            x, y = message["value"][1:-1].split(',')
            avoid_centres.add((int(x), int(y)))
            print("Avoiding Centres", avoid_centres)
        elif message["action"] == "release":
            x, y = message["value"][1:-1].split(',')
            avoid_centres.discard((int(x), int(y)))
            print("Avoiding Centres", avoid_centres)

def send_to_gateway(sensor_socket, gateway_ip_address, gateway_port, Registration_Message):
    send_data(sensor_socket, gateway_ip_address, gateway_port, Registration_Message)
    global state
    while True:
        if state:
            Message = generate_random_data(10, 40)
            # print(Message)
            send_data(sensor_socket, gateway_ip_address, gateway_port, Message)
            time.sleep(poll_rate)


def sensor_gateway_thread_init(sensor_socket, gateway_ip_address, gateway_port, Message):
    send_to_gateway(sensor_socket, gateway_ip_address, gateway_port, Message)


def gateway_sensor_thread_init(sensor_socket_address):
    receive_from_gateway(sensor_socket_address)

def start_sensor_gateway_thread(sensor_socket, gateway_ip_address, gateway_port, Message):
    t1 = threading.Thread(target=sensor_gateway_thread_init, args=(sensor_socket, gateway_ip_address, gateway_port, Message, ))
    t1.start()
    #print("t1 started")
    return t1

def start_gateway_sensor_thread(sensor_socket_address):
    t2 = threading.Thread(target=gateway_sensor_thread_init, args=(sensor_socket_address, ))
    t2.start()
    #print("t2 started")
    return t2

def get_gateway_details():
    gateway_ip_address = "127.0.0.1"
    gateway_port = 6745
    return gateway_ip_address, gateway_port

def get_sensor_info(sensor_file_name):
    with open(sensor_file_name, 'r') as fp:
        sensor_data = json.load(fp)
    #sensor_data = json.dumps(sensor_data)
    poll_rate = int(sensor_data['specifications']['poll_rate'])
    return sensor_data

def create_init_message(sensor_data):
    init_message = {
        "type":"new_sensor",
        "content":sensor_data
    }
    return json.dumps(init_message)

def main():
    sensor_config_file_name = sys.argv[1]
    sensor_data = create_init_message(get_sensor_info(sensor_config_file_name))
    sensor_sock = udp_init()
    gateway_ip_address, gateway_port = get_gateway_details()
    sensor_gateway_thread = start_sensor_gateway_thread(sensor_sock, gateway_ip_address, gateway_port, sensor_data)
    gateway_sensor_thread = start_gateway_sensor_thread(sensor_sock)
    threading.Thread(target = _update_person_status).start()
    sensor_gateway_thread.join()
    gateway_sensor_thread.join()

if __name__ == "__main__":

    main()





























