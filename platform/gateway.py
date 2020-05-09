import socket                
import ipaddress
import threading
import sys
import json
import sys
from confluent_kafka import Producer, Consumer, KafkaError

#There is only one thread running for the consumer
#Producer is running on the main thread.

# Steps:
# 1. Sensors will register by communicating to gateway.
#    Sensors communicate with gateway via socket programming[TCP or UDP]?
#    Sensors will provide metadata(ip, port included in metadata).
#    Each sensor's unique ID will be "Sensor's IP:Sensor's port".
# 2. Gateway's responsibility is to publish this meta_data to the sensor's topic.
#    Sensor's topic will be "Sensor's IP:Sensor's port"
# 3. Infrastructure will communicate to gateway via gateway topic.
#    Gateway's topic will be "Gateway's IP"

class Gateway:

    def create_producer(self):
        p = Producer({'bootstrap.servers': self.kafka_port})
        return p

    def create_consumer(self):
        c = Consumer({'bootstrap.servers': self.kafka_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
        return c

    def start_kafka(self):
        p = self.create_producer()
        c = self.create_consumer()
        return p, c

    def get_gateway_dict(self):
        gateway_dict = {}
        gateway_dict["ip"] = self.gateway_ip
        gateway_dict["domain"] = self.gateway_domain_name
        return gateway_dict

    def __init__(self, gateway_domain_name = "default", port = 6745, config = "Configs/platform_configs.json"):
        
        with open(config, 'r') as fp:
            configs = json.load(fp)

        # ***************UDP****************************
        #hostname = socket.gethostname()
        #self.gateway_ip = socket.gethostbyname(hostname)
        self.gateway_ip = "0.0.0.0"
        self.gateway_port = port
        self.gateway_domain_name = gateway_domain_name
        self.gateway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gateway_sock.bind((self.gateway_ip, self.gateway_port))
        self.gateway_dict = self.get_gateway_dict()
        self.sensor_manager_topic = configs['sensor_manager_topic']

        # **************Kafka***************************

        self.consumer_status = True
        self.gateway_topic_name = str(self.gateway_domain_name)
        self.kafka_port = configs['kafka_host']
        self.p, self.c = self.start_kafka()

    # *********************************************************************************************
    
    def get_sensor_id(self, sensor_ip, sensor_port):
        sensor_id = sensor_ip + "_" + str(sensor_port)
        return sensor_id
    
    # ****************************Kafka functions**************************************************

    def kafka_send_message(self, recipient_topic_name, message):
        self.p.produce(recipient_topic_name, message.encode('utf-8'))
        self.p.poll(0)
    
    def kafka_receive_message(self, consumer_topic_name):
        self.c.subscribe([consumer_topic_name])
        msg = self.c.poll(0.01)
        if msg is not None:
            msg = msg.value().decode('utf-8')
        return msg
    
    def add_info_to_metadata(self, sensor_metadata_dict, sensor_id):
        sensor_metadata_dict["content"]["ip_port"] = sensor_id
        sensor_metadata_dict["content"]["gateway"] = self.gateway_dict
        updated_sensor_metadata = json.dumps(sensor_metadata_dict)
        return updated_sensor_metadata
    
    def publish_to_sensor_manager(self, sensor_metadata_dict, sensor_id):
        updated_sensor_metadata = self.add_info_to_metadata(sensor_metadata_dict, sensor_id)
        #print(updated_sensor_metadata)
        self.kafka_send_message(self.sensor_manager_topic, updated_sensor_metadata)
    
    def publish_to_sensor_topic(self, sensor_data, sensor_topic):
        #print("sensor_topic", sensor_topic)
        self.kafka_send_message(sensor_topic, sensor_data)
    
    # ****************************Kafka functions**************************************************



    # ****************************UDP functions**************************************************

    def udp_receive_data(self):
        data, addr = self.gateway_sock.recvfrom(1024)
        message = data.decode()
        sensor_ip = addr[0]
        sensor_port = addr[1]
        return  message, sensor_ip, sensor_port

    def udp_send_data(self, recipient_ip_address, recipient_port, Message):
        self.gateway_sock.sendto(Message.encode(), (recipient_ip_address, recipient_port))

    def receive_from_sensor(self):
        while True:
            sensor_data, sensor_ip, sensor_port = self.udp_receive_data()
            #print(sensor_data, sensor_ip, sensor_port)
            sensor_id = self.get_sensor_id(sensor_ip, sensor_port)
            sensor_topic = "_".join(sensor_id.split('.'))
            sensor_metadata_dictionary = json.loads(sensor_data)
            message_type = sensor_metadata_dictionary["type"]
            
            if(message_type == "new_sensor"):
                self.publish_to_sensor_manager(sensor_metadata_dictionary, sensor_id)
            else:
                self.publish_to_sensor_topic(json.dumps(sensor_metadata_dictionary['content']), sensor_topic)


    def send_to_sensor(self, sensor_ip_address, sensor_port, Message):
        self.udp_send_data(sensor_ip_address, sensor_port, Message)

    # ****************************UDP functions**************************************************



    # **********************Sensor -> Gateway -> Infrastructure(Sensor's Topic)********************

    def sensor_gateway_recv_thread_init(self):
        self.receive_from_sensor()

    def start_sensor_gateway_recv_thread(self):
        t1 = threading.Thread(target=self.sensor_gateway_recv_thread_init, args=())
        t1.start()
        return t1 

    # **********************Sensor -> Gateway -> Infrastructure(Sensor's Topic)********************

# Gateway_topic data format:
# {
# "ip_port": self.ip_port,
# "action": action,
# "value": str(value)
# }

def extract_ip_port(sensor_ip_port):
    sensor_ip_port = sensor_ip_port.split('_')
    sensor_ip = sensor_ip_port[0]
    sensor_port = sensor_ip_port[1]
    return sensor_ip, int(sensor_port)

def get_gateway_info():
    domain = "default"
    port = 6745
    try:
        domain = sys.argv[1]
        port = int(sys.argv[2])
    except:
        pass
    return domain, port

def main():
    
    domain, port = get_gateway_info()
    g = Gateway(domain, port)

    sensor_gateway_recv_thread = g.start_sensor_gateway_recv_thread()
    while True:
        message = g.kafka_receive_message(g.gateway_topic_name)
        if message is None:
            continue
        #print("Kafka message for gateway: ", message)
        message_dict = json.loads(message)
        sensor_ip_port = message_dict["ip_port"]
        sensor_ip, sensor_port = extract_ip_port(sensor_ip_port)
        message = message_dict["message"]
        g.send_to_sensor(sensor_ip, sensor_port, json.dumps(message))
        #print("Sent kafka message to sensor")

    sensor_gateway_recv_thread.join()


if __name__ == "__main__":
    main()