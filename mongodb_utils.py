from pymongo import MongoClient


# Replace the URI string with your MongoDB deployment's connection string.
uri = "mongodb://localhost:27017/"


class MongoDBClient:
    def __init__(self, uri="mongodb://localhost:27017/"):
        """
        Initialize the MongoDB client.

        :param uri: MongoDB connection URI
        """
        self.client = MongoClient(uri)
        self.db = self.client['academicworld']

    def find(self, database, collection, query, projection=None):
        return list(self.db[collection].find(query, projection))

    def aggregate(self, database, collection, pipeline):
        return list(self.db[collection].aggregate(pipeline))

    def update_one(self, database, collection, query, new_values):
        self.db[collection].update_one(query, new_values)