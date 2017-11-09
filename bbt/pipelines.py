from pymongo import MongoClient
from scrapy.conf import settings


class MongoDBPipeline(object):
    def __init__(self):
        connection = MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        self.collection.update(
            {'title': item['title']}, dict(item), upsert=True)
        return item
