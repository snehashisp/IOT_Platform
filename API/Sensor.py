
from API.DatabaseRetriever import *
from API.KafkaRetriever import *
from API.TopicPublisher import *
import json

class Sensor(object):
    
    _action_publisher = TopicPublisher()
    _sensor_instance_map = {}

    def __new__(cls, **kwargs):
        #print(kwargs)
        if kwargs['ip_port'] in Sensor._sensor_instance_map:
            return Sensor._sensor_instance_map[kwargs['ip_port']]
        else:
            return super(Sensor, cls).__new__(cls)

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        Sensor._sensor_instance_map[kwargs['ip_port']] = self


    def getDatabaseRetriever(self):
        return DatabaseRetriever(self.configs["db_endpoint"])
    
    def getKafkaRetriever(self, user):
        sensor_topic = "_".join(self.ip_port.split('.'))
        return KafkaRetriever(sensor_topic , user)
    
    def _construct_action_message(self, action, value = None):
        message = json.dumps({
            "ip_port": self.ip_port,
            "message": {
                "action": action,
                "value": str(value)
            }
        })
        return message

    def doAction(self, action, value = None):
        if action in self.actions:
            sensor_gateway_topic = self.gateway["domain"]
            Sensor._action_publisher.publish(sensor_gateway_topic, self._construct_action_message(action, value))


