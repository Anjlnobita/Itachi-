import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
rules_collection = db['rules']

INSERTION_LOCK = threading.RLock()


class Rules:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.rules = ""

    def __repr__(self):
        return "<Chat {} rules: {}>".format(self.chat_id, self.rules)


def set_rules(chat_id, rules_text):
    with INSERTION_LOCK:
        rules = rules_collection.find_one({"chat_id": str(chat_id)})
        if not rules:
            rules = Rules(str(chat_id))
            rules_collection.insert_one({"chat_id": rules.chat_id, "rules": rules_text})
        else:
            rules_collection.update_one({"chat_id": str(chat_id)}, {"$set": {"rules": rules_text}})


def get_rules(chat_id):
    rules = rules_collection.find_one({"chat_id": str(chat_id)})
    ret = ""
    if rules:
        ret = rules['rules']
    return ret


def num_chats():
    return rules_collection.distinct("chat_id").count()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = rules_collection.find_one({"chat_id": str(old_chat_id)})
        if chat:
            rules_collection.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": str(new_chat_id)}})
