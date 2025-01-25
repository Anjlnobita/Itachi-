import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']
collection = db['chatbot_chats']

INSERTION_LOCK = threading.RLock()


def is_chat(chat_id):
    try:
        chat = collection.find_one({"chat_id": str(chat_id)})
        return chat is not None
    finally:
        client.close()


def set_ses(chat_id, ses_id, expires):
    with INSERTION_LOCK:
        autochat = collection.find_one({"chat_id": str(chat_id)})
        if not autochat:
            autochat = {"chat_id": str(chat_id), "ses_id": str(ses_id), "expires": str(expires)}
            collection.insert_one(autochat)
        else:
            collection.update_one({"chat_id": str(chat_id)}, {"$set": {"ses_id": str(ses_id), "expires": str(expires)}})


def get_ses(chat_id):
    autochat = collection.find_one({"chat_id": str(chat_id)})
    sesh = ""
    exp = ""
    if autochat:
        sesh = str(autochat['ses_id'])
        exp = str(autochat['expires'])

    client.close()
    return sesh, exp


def rem_chat(chat_id):
    with INSERTION_LOCK:
        autochat = collection.find_one({"chat_id": str(chat_id)})
        if autochat:
            collection.delete_one({"chat_id": str(chat_id)})


def get_all_chats():
    try:
        return [chat['chat_id'] for chat in collection.find({}, {"chat_id": 1})]
    finally:
        client.close()
