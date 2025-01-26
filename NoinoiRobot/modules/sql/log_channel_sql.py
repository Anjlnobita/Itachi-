import threading

from NoinoiRobot.modules.sql import client, nobita as collection


LOGS_INSERTION_LOCK = threading.RLock()

CHANNELS = {}


def set_chat_log_channel(chat_id, log_channel):
    with LOGS_INSERTION_LOCK:
        res = collection.find_one({"chat_id": str(chat_id)})
        if res:
            collection.update_one({"chat_id": str(chat_id)}, {"$set": {"log_channel": log_channel}})
        else:
            collection.insert_one({"chat_id": str(chat_id), "log_channel": str(log_channel)})

        CHANNELS[str(chat_id)] = log_channel


def get_chat_log_channel(chat_id):
    return CHANNELS.get(str(chat_id))


def stop_chat_logging(chat_id):
    with LOGS_INSERTION_LOCK:
        res = collection.find_one({"chat_id": str(chat_id)})
        if res:
            if str(chat_id) in CHANNELS:
                del CHANNELS[str(chat_id)]

            log_channel = res['log_channel']
            collection.delete_one({"chat_id": str(chat_id)})
            return log_channel


def num_logchannels():
    return collection.distinct("chat_id").count()


def migrate_chat(old_chat_id, new_chat_id):
    with LOGS_INSERTION_LOCK:
        chat = collection.find_one({"chat_id": str(old_chat_id)})
        if chat:
            collection.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": str(new_chat_id)}})
            if str(old_chat_id) in CHANNELS:
                CHANNELS[str(new_chat_id)] = CHANNELS.get(str(old_chat_id))


def __load_log_channels():
    global CHANNELS
    all_chats = collection.find()
    CHANNELS = {chat['chat_id']: chat['log_channel'] for chat in all_chats}


__load_log_channels()
