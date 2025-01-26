# Fixing the TypeError in the code

import threading
import time
from typing import Union

from NoinoiRobot.modules.sql import client
from NoinoiRobot.modules.sql import nobita as CONNECTION_HISTORY_COLLECTION
from NoinoiRobot.modules.sql import nobita as CHAT_ACCESS_COLLECTION
from NoinoiRobot.modules.sql import nobita as CONNECTION_COLLECTION

CHAT_ACCESS_LOCK = threading.RLock()
CONNECTION_INSERTION_LOCK = threading.RLock()
CONNECTION_HISTORY_LOCK = threading.RLock()

HISTORY_CONNECT = {}

class ChatAccessConnectionSettings:
    def __init__(self, chat_id, allow_connect_to_chat):
        self.chat_id = str(chat_id)
        self.allow_connect_to_chat = bool(allow_connect_to_chat)

    def __repr__(self):
        return "<Chat access settings ({}) is {}>".format(
            self.chat_id, self.allow_connect_to_chat
        )

class Connection:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = str(chat_id)

class ConnectionHistory:
    def __init__(self, user_id, chat_id, chat_name, conn_time):
        self.user_id = user_id
        self.chat_id = str(chat_id)
        self.chat_name = str(chat_name)
        self.conn_time = int(conn_time)

    def __repr__(self):
        return "<connection user {} history {}>".format(self.user_id, self.chat_id)

def allow_connect_to_chat(chat_id: Union[str, int]) -> bool:
    chat_setting = CHAT_ACCESS_COLLECTION.find_one({"chat_id": str(chat_id)})
    return chat_setting['allow_connect_to_chat'] if chat_setting else False

def set_allow_connect_to_chat(chat_id: Union[int, str], setting: bool):
    with CHAT_ACCESS_LOCK:
        chat_setting = CHAT_ACCESS_COLLECTION.find_one({"chat_id": str(chat_id)})
        if not chat_setting:
            chat_setting = ChatAccessConnectionSettings(chat_id, setting)
            CHAT_ACCESS_COLLECTION.insert_one(chat_setting.__dict__)
        else:
            CHAT_ACCESS_COLLECTION.update_one(
                {"chat_id": str(chat_id)},
                {"$set": {"allow_connect_to_chat": setting}}
            )

def connect(user_id, chat_id):
    with CONNECTION_INSERTION_LOCK:
        CONNECTION_COLLECTION.delete_one({"user_id": int(user_id)})
        connect_to_chat = Connection(int(user_id), chat_id)
        CONNECTION_COLLECTION.insert_one(connect_to_chat.__dict__)
        return True

def get_connected_chat(user_id):
    return CONNECTION_COLLECTION.find_one({"user_id": int(user_id)})

def disconnect(user_id):
    with CONNECTION_INSERTION_LOCK:
        disconnect = CONNECTION_COLLECTION.find_one({"user_id": int(user_id)})
        if disconnect:
            CONNECTION_COLLECTION.delete_one({"user_id": int(user_id)})
            return True
        return False

def add_history_conn(user_id, chat_id, chat_name):
    global HISTORY_CONNECT
    with CONNECTION_HISTORY_LOCK:
        conn_time = int(time.time())
        if HISTORY_CONNECT.get(int(user_id)):
            counting = CONNECTION_HISTORY_COLLECTION.count_documents({"user_id": int(user_id)})
            getchat_id = {HISTORY_CONNECT[int(user_id)][x]["chat_id"]: x for x in HISTORY_CONNECT[int(user_id)]}
            if chat_id in getchat_id:
                todeltime = getchat_id[str(chat_id)]
                CONNECTION_HISTORY_COLLECTION.delete_one({"user_id": int(user_id), "chat_id": str(chat_id)})
                HISTORY_CONNECT[int(user_id)].pop(todeltime)
            elif counting >= 5:
                todel = list(HISTORY_CONNECT[int(user_id)])
                todel.reverse()
                todel = todel[4:]
                for x in todel:
                    chat_old = HISTORY_CONNECT[int(user_id)][x]["chat_id"]
                    CONNECTION_HISTORY_COLLECTION.delete_one({"user_id": int(user_id), "chat_id": str(chat_old)})
                    HISTORY_CONNECT[int(user_id)].pop(x)
        else:
            HISTORY_CONNECT[int(user_id)] = {}
        CONNECTION_HISTORY_COLLECTION.delete_one({"user_id": int(user_id), "chat_id": str(chat_id)})
        history = ConnectionHistory(int(user_id), str(chat_id), chat_name, conn_time)
        CONNECTION_HISTORY_COLLECTION.insert_one(history.__dict__)
        HISTORY_CONNECT[int(user_id)][conn_time] = {
            "chat_name": chat_name,
            "chat_id": str(chat_id),
        }

def get_history_conn(user_id):
    return HISTORY_CONNECT.get(int(user_id), {})

def clear_history_conn(user_id):
    global HISTORY_CONNECT
    todel = list(HISTORY_CONNECT[int(user_id)])
    for x in todel:
        chat_old = HISTORY_CONNECT[int(user_id)][x]["chat_id"]
        CONNECTION_HISTORY_COLLECTION.delete_one({"user_id": int(user_id), "chat_id": str(chat_old)})
        HISTORY_CONNECT[int(user_id)].pop(x)
    return True

def __load_user_history():
    global HISTORY_CONNECT
    qall = CONNECTION_HISTORY_COLLECTION.find()
    HISTORY_CONNECT = {}
    for x in qall:
        if x['user_id'] not in HISTORY_CONNECT:
            HISTORY_CONNECT[x['user_id']] = {}
        HISTORY_CONNECT[x['user_id']][x['conn_time']] = {
            "chat_name": x['chat_name'],
            "chat_id": x['chat_id'],
        }

__load_user_history()
