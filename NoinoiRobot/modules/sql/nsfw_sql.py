import threading

from NoinoiRobot.modules.sql import client, nobita as nsfw_chats_collection



#   |----------------------------------|
#   |   
#   |        Kang with Credits         |
#   |----------------------------------|



INSERTION_LOCK = threading.RLock()

def is_nsfw(chat_id):
    try:
        chat = nsfw_chats_collection.find_one({"chat_id": str(chat_id)})
        if chat:
            return True
        else:
            return False
    finally:
        client.close()

def set_nsfw(chat_id):
    with INSERTION_LOCK:
        nsfwchat = nsfw_chats_collection.find_one({"chat_id": str(chat_id)})
        if not nsfwchat:
            nsfw_chats_collection.insert_one({"chat_id": str(chat_id)})

def rem_nsfw(chat_id):
    with INSERTION_LOCK:
        nsfwchat = nsfw_chats_collection.find_one({"chat_id": str(chat_id)})
        if nsfwchat:
            nsfw_chats_collection.delete_one({"chat_id": str(chat_id)})

def get_all_nsfw_chats():
    try:
        return [chat['chat_id'] for chat in nsfw_chats_collection.find({}, {"_id": 0, "chat_id": 1})]
    finally:
        client.close()
