import socket                
import threading
import sys
import json
import random
import datetime
import time


state = False

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

# def _gen_random_temp_data():
#     temp_range = random.choices([1,2,3,4], [0.6, 0.2, 0.15, 0.05])[0]
#     if temp_range == 1:
#         return random.randint(60, 100)
#     elif temp_range == 2:
#         return random.randint(10, 59)
#     elif temp_range == 3:
#         return random.randint(101, 120)
#     else:
#         return random.randint(200, 500)

# def generate_random_data(start, end):
#     random_data = {}
#     random_data["type"] = "sensor_data"
#     content = {}
#     content["time"] = str(datetime.datetime.now())
#     content["value"] = str(_gen_random_temp_data())
#     random_data["content"] = content
#     # print(random_data['content'])
#     random_data = json.dumps(random_data)
#     return random_data
    

def receive_data(recipient_socket_address):
    data, addr = recipient_socket_address.recvfrom(1024)
    #print("Message: ", data.decode())
    return data.decode()

def send_data(sock, recipient_ip_address, recipient_port, Message):
    sock.sendto(Message.encode(), (recipient_ip_address, recipient_port))
    #print(Message)

def receive_from_gateway(sensor_socket):
    global state, poll_rate
    while True:
        gateway_data = receive_data(sensor_socket)
        message = json.loads(gateway_data)
        if message["action"] == "start":
            state = True
        elif message["action"] == "stop":
            state = False

def send_to_gateway(sensor_socket, gateway_ip_address, gateway_port, Registration_Message):
    send_data(sensor_socket, gateway_ip_address, gateway_port, Registration_Message)
    global state
    while True:
        if state:
            print("ALARM IS ON")
            time.sleep(3)
            # # Message = generate_random_data(10, 40)
            # send_data(sensor_socket, gateway_ip_address, gateway_port, Message)
            # time.sleep(poll_rate)


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
    sensor_gateway_thread.join()
    gateway_sensor_thread.join()

if __name__ == "__main__":
    main()





























