import threading
from NoinoiRobot.modules.sql import client, nobita as STICKERS_FILTERS_COLLECTION
from NoinoiRobot.modules.sql import nobita as STICKER_SETTINGS_COLLECTION

STICKERS_FILTER_INSERTION_LOCK = threading.RLock()
CHAT_STICKERS = {}
CHAT_BLSTICK_BLACKLISTS = {}

def add_to_stickers(chat_id, trigger):
    with STICKERS_FILTER_INSERTION_LOCK:
        stickers_filt = {
            'chat_id': str(chat_id),
            'trigger': trigger
        }
        STICKERS_FILTERS_COLLECTION.update_one(stickers_filt, {'$setOnInsert': stickers_filt}, upsert=True)
        CHAT_STICKERS.setdefault(str(chat_id), set()).add(trigger)

def rm_from_stickers(chat_id, trigger):
    with STICKERS_FILTER_INSERTION_LOCK:
        if STICKERS_FILTERS_COLLECTION.find_one({'chat_id': str(chat_id), 'trigger': trigger}):
            CHAT_STICKERS.get(str(chat_id), set()).discard(trigger)
            STICKERS_FILTERS_COLLECTION.delete_one({'chat_id': str(chat_id), 'trigger': trigger})
            return True
        return False

def get_chat_stickers(chat_id):
    return CHAT_STICKERS.get(str(chat_id), set())

def num_stickers_filters():
    return STICKERS_FILTERS_COLLECTION.count_documents({})

def num_stickers_chat_filters(chat_id):
    return STICKERS_FILTERS_COLLECTION.count_documents({'chat_id': str(chat_id)})

def num_stickers_filter_chats():
    return STICKERS_FILTERS_COLLECTION.distinct('chat_id')

def set_blacklist_strength(chat_id, blacklist_type, value):
    with STICKERS_FILTER_INSERTION_LOCK:
        curr_setting = STICKER_SETTINGS_COLLECTION.find_one({'chat_id': str(chat_id)})
        if not curr_setting:
            curr_setting = {
                'chat_id': str(chat_id),
                'blacklist_type': int(blacklist_type),
                'value': value
            }
            STICKER_SETTINGS_COLLECTION.insert_one(curr_setting)
        else:
            STICKER_SETTINGS_COLLECTION.update_one({'chat_id': str(chat_id)}, {'$set': {
                'blacklist_type': int(blacklist_type),
                'value': str(value)
            }})

        CHAT_BLSTICK_BLACKLISTS[str(chat_id)] = {
            "blacklist_type": int(blacklist_type),
            "value": value,
        }

def get_blacklist_setting(chat_id):
    return CHAT_BLSTICK_BLACKLISTS.get(str(chat_id), {"blacklist_type": 1, "value": "0"})

def __load_CHAT_STICKERS():
    global CHAT_STICKERS
    for chat_id in STICKERS_FILTERS_COLLECTION.distinct('chat_id'):
        CHAT_STICKERS[chat_id] = set()
    for x in STICKERS_FILTERS_COLLECTION.find():
        CHAT_STICKERS[x['chat_id']].add(x['trigger'])

def __load_chat_stickerset_blacklists():
    global CHAT_BLSTICK_BLACKLISTS
    for x in STICKER_SETTINGS_COLLECTION.find():
        CHAT_BLSTICK_BLACKLISTS[x['chat_id']] = {
            "blacklist_type": x['blacklist_type'],
            "value": x['value'],
        }

def migrate_chat(old_chat_id, new_chat_id):
    with STICKERS_FILTER_INSERTION_LOCK:
        for filt in STICKERS_FILTERS_COLLECTION.find({'chat_id': str(old_chat_id)}):
            STICKERS_FILTERS_COLLECTION.update_one({'_id': filt['_id']}, {'$set': {'chat_id': str(new_chat_id)}})

__load_CHAT_STICKERS()
__load_chat_stickerset_blacklists()
