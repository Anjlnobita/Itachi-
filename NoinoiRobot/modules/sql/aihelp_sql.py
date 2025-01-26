import threading
from NoinoiRobot.modules.sql import client, nobita as collection

INSERTION_LOCK = threading.RLock()

def is_chat(chat_id):
    chat = collection.find_one({"chat_id": str(chat_id)})
    return chat is not None

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
    if autochat:
        return str(autochat['ses_id']), str(autochat['expires'])
    return "", ""

def rem_chat(chat_id):
    with INSERTION_LOCK:
        collection.delete_one({"chat_id": str(chat_id)})

def get_all_chats():
    return [chat['chat_id'] for chat in collection.find({}, {"chat_id": 1})]
