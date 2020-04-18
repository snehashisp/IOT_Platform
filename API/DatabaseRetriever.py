import json
import datetime
import pymongo

class DatabaseRetriever():

    def __init__(self, sensor_db_endpoint, config = "Configs/platform_configs.json"):
        with open(config, 'r') as fp:
            configs = json.load(fp)
            self.default_count = configs["default_count_returned"]
            client = pymongo.MongoClient(configs["sensor_mongo_client"])
            sensor_db = client[configs["sensor_data_db"]]
            self.collection = sensor_db[sensor_db_endpoint]
    
    def _get_time_filter(self, filter):
        time_filter = {"time":{}}
        if "StartTime" in filter:
            time_filter["time"]["$gt"] = filter["StartTime"]
        if "EndTime" in filter:
            time_filter["time"]["$lt"] = filter["EndTime"]
        return {"$match":time_filter}

    def _get_aggregation(self, aggregations):
        params = {"_id":"null"}
        for aggr in aggregations:
            params.update({aggr:{'$' + aggr: {'$toInt':'$value'}}})
        return {"$group":params}

    def _construct_query_pipeline(self, count, time_filter = None, aggregations = None):
        query_pipeline = []
        if time_filter:
            query_pipeline.append(time_filter)
        if aggregations:
            query_pipeline.append(aggregations)
        query_pipeline.append({"$sort":{"time":-1}})
        query_pipeline.append({"$limit":count})
        return query_pipeline

    def retrieve(self, filter = None, aggregations = None):
        count, time_filter = self.default_count, None
        if filter and 'Count' in filter:
            count = filter['Count']
        if filter and ('StartTime' in filter or 'EndTime' in filter):
            time_filter = self._get_time_filter(filter)
        if aggregations:
            aggregations = self._get_aggregation(aggregations)
        query_pipeline = self._construct_query_pipeline(count, time_filter, aggregations)
        return list(self.collection.aggregate(query_pipeline))
 
