from pymongo import MongoClient

def start() -> MongoClient:
    client = MongoClient(DB_URI)
    return client

client = start()
db = client['nobii']
