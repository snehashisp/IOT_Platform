from API.Registry import Registry
from API.DatabaseIngestor import DatabaseIngestor
from API.Sensor import Sensor

config = "Configs/platform_configs.json"
registry = Registry(config)
ingestor = DatabaseIngestor(config)

def _authenticate(sensor, user_id):
    #code for authenticating sensors using the authentication api
    return True

def getSensor(filter_query, user_id = None):
    authenticated_sensors = []
    for sensor in registry.getSensor(filter_query):
        if _authenticate(sensor, user_id):
            authenticated_sensors.append(sensor)
    return authenticated_sensors

def _invoke_updates(config_changes):
    for sensor in Sensor._sensor_instance_map.values():
        for config, value in config_changes.items():
            sensor.doAction(config, value)
            if config == 'db_endpoint':
                if value == '':
                    ingestor.remove_connection(sensor)
                else:
                    ingestor.add_connection(sensor)

def _update_existing_sensors():
    for ip_port in Sensor._sensor_instance_map.keys():
        print(ip_port)
        registry.getSensor({'ip_port':ip_port})

def setSensorConfig(filter_query, config_params, user_id = None):
    sensors = registry.getSensor(filter_query)
    for sens in sensors:
        if not _authenticate(sens, user_id):
            raise Exception("Authorization not granted for some sensor")
    registry.setSensorConfig(filter_query, config_params)
    _update_existing_sensors()
    _invoke_updates(config_params)




