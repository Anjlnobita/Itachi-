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
        global CHAT_STICKERS
        if CHAT_STICKERS.get(str(chat_id), set()) == set():
            CHAT_STICKERS[str(chat_id)] = {trigger}
        else:
            CHAT_STICKERS.get(str(chat_id), set()).add(trigger)

def rm_from_stickers(chat_id, trigger):
    with STICKERS_FILTER_INSERTION_LOCK:
        stickers_filt = STICKERS_FILTERS_COLLECTION.find_one({'chat_id': str(chat_id), 'trigger': trigger})
        if stickers_filt:
            if trigger in CHAT_STICKERS.get(str(chat_id), set()):  # sanity check
                CHAT_STICKERS.get(str(chat_id), set()).remove(trigger)

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
        global CHAT_BLSTICK_BLACKLISTS
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
    setting = CHAT_BLSTICK_BLACKLISTS.get(str(chat_id))
    if setting:
        return setting["blacklist_type"], setting["value"]
    else:
        return 1, "0"

def __load_CHAT_STICKERS():
    global CHAT_STICKERS
    chats = STICKERS_FILTERS_COLLECTION.distinct('chat_id')
    for chat_id in chats:
        CHAT_STICKERS[chat_id] = []
    
    all_filters = STICKERS_FILTERS_COLLECTION.find()
    for x in all_filters:
        CHAT_STICKERS[x['chat_id']].append(x['trigger'])
    
    CHAT_STICKERS = {x: set(y) for x, y in CHAT_STICKERS.items()}

def __load_chat_stickerset_blacklists():
    global CHAT_BLSTICK_BLACKLISTS
    chats_settings = STICKER_SETTINGS_COLLECTION.find()
    for x in chats_settings:
        CHAT_BLSTICK_BLACKLISTS[x['chat_id']] = {
            "blacklist_type": x['blacklist_type'],
            "value": x['value'],
        }

def migrate_chat(old_chat_id, new_chat_id):
    with STICKERS_FILTER_INSERTION_LOCK:
        chat_filters = STICKERS_FILTERS_COLLECTION.find({'chat_id': str(old_chat_id)})
        for filt in chat_filters:
            STICKERS_FILTERS_COLLECTION.update_one({'_id': filt['_id']}, {'$set': {'chat_id': str(new_chat_id)}})

__load_CHAT_STICKERS()
__load_chat_stickerset_blacklists()
