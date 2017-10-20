
from pymongo import MongoClient

class DBClient:

    def __init__(self):
        pass

    def get_user(self, id):
        pass

    def create_user(self, user_dict):
        pass

class MongoDBClient(DBClient):

    def __init__(self):
        self.client = MongoClient('0.0.0.0', 27017)

    def get_user(self, id):
        users = self.client.db.users
        user = users.find_one({"id": id})
        return user

    def create_user(self, user_dict):
        users = self.client.db.users
        user = users.insert_one(user_dict)
        return user
