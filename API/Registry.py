# import os
# import sys
# sys.path.append(os.getcwd() + "/..")
import pymongo
import API.Sensor as Sensor
import json

class Registry:

    def __init__(self, config = "Configs/platform_configs.json"):
        with open(config, "r") as fp:
            configs = json.load(fp)
            client = pymongo.MongoClient(configs["sensor_mongo_client"])
            registry_db = client[configs["sensor_registry_db"]]
            self.registry = registry_db["sensor_registry_collection"]
            self.gateway_collection = registry_db["gateway_collection"]
    
    def _create_filter(self, filter):
        filter_dict = {}
        for key, val in filter.items():
            if key in ['name','location','geolocation']:
                filter_dict.update({"configs." + key:val})
                continue
            if key == 'actions':
                filter_dict.update({"actions":{"$in":val}})
                continue
            if key == 'domain':
                filter_dict.update({"gateway.domain":val})
                continue
            filter_dict.update({key:val})
        #print(filter_dict)
        return filter_dict
    
    def _create_updates(self, updates):
        update_dict = {}
        for key, val in updates.items():
            update_dict.update({"configs." + key:val})
        return {"$set":update_dict}

    def addSensor(self, new_sensor):
        self.registry.insert(new_sensor.__dict__)
        #print("Adding new sensor", new_sensor.__dict__)

    def addGateway(self, new_gateway):
        self.gateway_collection.insert(new_gateway)

    def getSensor(self, filters):
        sensor_list = []
        for sensor_info in self.registry.find(self._create_filter(filters)):
            sensor_list.append(Sensor.Sensor(**sensor_info))
        return sensor_list
    
    def setSensorConfig(self, filter, updates):
        self.registry.update(self._create_filter(filter), self._create_updates(updates), multi = True)
    
    def getGateways(self):
        return list(self.gateway_collection.find())