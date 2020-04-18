import threading
import json
import pymongo
import requests
import re


class DatabaseIngestor:

    def __init__(self, config = "Configs/platform_configs.json"):
        with open(config, 'r') as fp:
            configs = json.load(fp)
            self._connector_addr = configs['kafka_connect']
            self._connector_name = configs['connector_name']
            self._url = self._connector_addr + '/connectors/' + self._connector_name + '/config'
    
    def _get_configs(self):
        response = requests.get(self._url)
        if response.status_code == 200:
            return json.loads(response.text)
        raise Exception("Kafka Connect Error getting config" + response.status_code)
    
    def _put_configs(self, new_config):
        response = requests.put(self._url, headers = {'Content-Type':'application/json'}, data = json.dumps(new_config))
        if response.status_code != 200:
            raise Exception("Kafka Connect Error setting sonfig" + response.status_code)
    
    def add_connection(self, sensor):
        current_configs = self._get_configs()
        sensor_topic = "_".join(sensor.ip_port.split('.'))
        if sensor_topic not in current_configs['topics']:
            current_configs['topics'] += "," + sensor_topic
        current_configs['topic.override.' + sensor_topic + ".collection"] = sensor.configs['db_endpoint']
        self._put_configs(current_configs)
    
    def remove_connection(self, sensor):
        current_configs = self._get_configs()
        sensor_topic = "_".join(sensor.ip_port.split('.'))
        if sensor_topic in current_configs['topics']:
            new_topics = re.sub(sensor_topic + ',', '', current_configs['topics'])
            new_topics = re.sub(',' + sensor_topic, '', new_topics)
            current_configs['topics'] = new_topics
            current_configs.pop('topic.override.' + sensor_topic + ".collection")
            self._put_configs(current_configs)

            

