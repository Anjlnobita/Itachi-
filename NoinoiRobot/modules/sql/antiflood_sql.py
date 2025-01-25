import threading
from pymongo import MongoClient

DEF_COUNT = 1
DEF_LIMIT = 0
DEF_OBJ = (None, DEF_COUNT, DEF_LIMIT)

client = MongoClient('mongodb://localhost:27017/')
db = client['flood_control_db']
flood_control_collection = db['antiflood']
flood_settings_collection = db['antiflood_settings']

INSERTION_FLOOD_LOCK = threading.RLock()
INSERTION_FLOOD_SETTINGS_LOCK = threading.RLock()

CHAT_FLOOD = {}

def set_flood(chat_id, amount):
    with INSERTION_FLOOD_LOCK:
        flood = flood_control_collection.find_one({"chat_id": str(chat_id)})
        if not flood:
            flood_control_collection.insert_one({"chat_id": str(chat_id), "user_id": None, "count": DEF_COUNT, "limit": amount})
        else:
            flood_control_collection.update_one({"chat_id": str(chat_id)}, {"$set": {"limit": amount}})

        CHAT_FLOOD[str(chat_id)] = (None, DEF_COUNT, amount)

def update_flood(chat_id: str, user_id) -> bool:
    if str(chat_id) in CHAT_FLOOD:
        curr_user_id, count, limit = CHAT_FLOOD.get(str(chat_id), DEF_OBJ)

        if limit == 0:  # no antiflood
            return False

        if user_id != curr_user_id or user_id is None:  # other user
            CHAT_FLOOD[str(chat_id)] = (user_id, DEF_COUNT, limit)
            return False

        count += 1
        if count > limit:  # too many msgs, kick
            CHAT_FLOOD[str(chat_id)] = (None, DEF_COUNT, limit)
            return True

        # default -> update
        CHAT_FLOOD[str(chat_id)] = (user_id, count, limit)
        return False

def get_flood_limit(chat_id):
    return CHAT_FLOOD.get(str(chat_id), DEF_OBJ)[2]

def set_flood_strength(chat_id, flood_type, value):
    with INSERTION_FLOOD_SETTINGS_LOCK:
        curr_setting = flood_settings_collection.find_one({"chat_id": str(chat_id)})
        if not curr_setting:
            flood_settings_collection.insert_one({"chat_id": str(chat_id), "flood_type": int(flood_type), "value": value})
        else:
            flood_settings_collection.update_one({"chat_id": str(chat_id)}, {"$set": {"flood_type": int(flood_type), "value": str(value)}})

def get_flood_setting(chat_id):
    setting = flood_settings_collection.find_one({"chat_id": str(chat_id)})
    if setting:
        return setting['flood_type'], setting['value']
    else:
        return 1, "0"

def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_FLOOD_LOCK:
        flood = flood_control_collection.find_one({"chat_id": str(old_chat_id)})
        if flood:
            CHAT_FLOOD[str(new_chat_id)] = CHAT_FLOOD.get(str(old_chat_id), DEF_OBJ)
            flood_control_collection.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": str(new_chat_id)}})

def __load_flood_settings():
    global CHAT_FLOOD
    all_chats = flood_control_collection.find()
    CHAT_FLOOD = {chat['chat_id']: (None, DEF_COUNT, chat['limit']) for chat in all_chats}

__load_flood_settings()
