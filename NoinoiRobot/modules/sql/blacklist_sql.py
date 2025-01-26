
"""

import threading


from NoinoiRobot.modules.sql import client, nobita as BLACKLIST_FILTERS_COLLECTION

from NoinoiRobot.modules.sql import nobita as BLACKLIST_SETTINGS_COLLECTION




BLACKLIST_FILTER_INSERTION_LOCK = threading.RLock()
BLACKLIST_SETTINGS_INSERTION_LOCK = threading.RLock()

CHAT_BLACKLISTS = {}
CHAT_SETTINGS_BLACKLISTS = {}


def add_to_blacklist(chat_id, trigger):
    with BLACKLIST_FILTER_INSERTION_LOCK:
        blacklist_filt = {'chat_id': str(chat_id), 'trigger': trigger}
        BLACKLIST_FILTERS_COLLECTION.update_one(blacklist_filt, {'$setOnInsert': blacklist_filt}, upsert=True)
        
        global CHAT_BLACKLISTS
        if CHAT_BLACKLISTS.get(str(chat_id), set()) == set():
            CHAT_BLACKLISTS[str(chat_id)] = {trigger}
        else:
            CHAT_BLACKLISTS.get(str(chat_id), set()).add(trigger)


def rm_from_blacklist(chat_id, trigger):
    with BLACKLIST_FILTER_INSERTION_LOCK:
        blacklist_filt = BLACKLIST_FILTERS_COLLECTION.find_one({'chat_id': str(chat_id), 'trigger': trigger})
        if blacklist_filt:
            if trigger in CHAT_BLACKLISTS.get(str(chat_id), set()):  # sanity check
                CHAT_BLACKLISTS.get(str(chat_id), set()).remove(trigger)

            BLACKLIST_FILTERS_COLLECTION.delete_one({'chat_id': str(chat_id), 'trigger': trigger})
            return True

        return False


def get_chat_blacklist(chat_id):
    return CHAT_BLACKLISTS.get(str(chat_id), set())


def num_blacklist_filters():
    return BLACKLIST_FILTERS_COLLECTION.count_documents({})


def num_blacklist_chat_filters(chat_id):
    return BLACKLIST_FILTERS_COLLECTION.count_documents({'chat_id': str(chat_id)})


def num_blacklist_filter_chats():
    return len(CHAT_BLACKLISTS)


def set_blacklist_strength(chat_id, blacklist_type, value):
    with BLACKLIST_SETTINGS_INSERTION_LOCK:
        global CHAT_SETTINGS_BLACKLISTS
        curr_setting = BLACKLIST_SETTINGS_COLLECTION.find_one({'chat_id': str(chat_id)})
        if not curr_setting:
            curr_setting = {'chat_id': str(chat_id), 'blacklist_type': int(blacklist_type), 'value': value}
            BLACKLIST_SETTINGS_COLLECTION.insert_one(curr_setting)
        else:
            BLACKLIST_SETTINGS_COLLECTION.update_one({'chat_id': str(chat_id)}, {'$set': {'blacklist_type': int(blacklist_type), 'value': str(value)}})

        CHAT_SETTINGS_BLACKLISTS[str(chat_id)] = {
            "blacklist_type": int(blacklist_type),
            "value": value,
        }


def get_blacklist_setting(chat_id):
    setting = CHAT_SETTINGS_BLACKLISTS.get(str(chat_id))
    if setting:
        return setting["blacklist_type"], setting["value"]
    else:
        return 1, "0"


def __load_chat_blacklists():
    global CHAT_BLACKLISTS
    chats = BLACKLIST_FILTERS_COLLECTION.distinct('chat_id')
    for chat_id in chats:
        CHAT_BLACKLISTS[chat_id] = []
    
    all_filters = BLACKLIST_FILTERS_COLLECTION.find()
    for x in all_filters:
        CHAT_BLACKLISTS[x['chat_id']].append(x['trigger'])

    CHAT_BLACKLISTS = {x: set(y) for x, y in CHAT_BLACKLISTS.items()}


def __load_chat_settings_blacklists():
    global CHAT_SETTINGS_BLACKLISTS
    chats_settings = BLACKLIST_SETTINGS_COLLECTION.find()
    for x in chats_settings:
        CHAT_SETTINGS_BLACKLISTS[x['chat_id']] = {
            "blacklist_type": x['blacklist_type'],
            "value": x['value'],
        }


def migrate_chat(old_chat_id, new_chat_id):
    with BLACKLIST_FILTER_INSERTION_LOCK:
        chat_filters = BLACKLIST_FILTERS_COLLECTION.find({'chat_id': str(old_chat_id)})
        for filt in chat_filters:
            BLACKLIST_FILTERS_COLLECTION.update_one({'_id': filt['_id']}, {'$set': {'chat_id': str(new_chat_id)}})


__load_chat_blacklists()
__load_chat_settings_blacklists()


"""
