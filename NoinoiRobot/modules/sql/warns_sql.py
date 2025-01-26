import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['warns_db']

WARN_INSERTION_LOCK = threading.RLock()
WARN_FILTER_INSERTION_LOCK = threading.RLock()
WARN_SETTINGS_LOCK = threading.RLock()

WARN_FILTERS = {}

class Warns:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = str(chat_id)
        self.num_warns = 0
        self.reasons = []

    def __repr__(self):
        return "<{} warns for {} in {} for reasons {}>".format(
            self.num_warns, self.user_id, self.chat_id, self.reasons
        )

class WarnFilters:
    def __init__(self, chat_id, keyword, reply):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.reply = reply

    def __repr__(self):
        return "<Permissions for %s>" % self.chat_id

class WarnSettings:
    def __init__(self, chat_id, warn_limit=3, soft_warn=False):
        self.chat_id = str(chat_id)
        self.warn_limit = warn_limit
        self.soft_warn = soft_warn

    def __repr__(self):
        return "<{} has {} possible warns.>".format(self.chat_id, self.warn_limit)

def warn_user(user_id, chat_id, reason=None):
    with WARN_INSERTION_LOCK:
        warned_user = db.warns.find_one({"user_id": user_id, "chat_id": str(chat_id)})
        if not warned_user:
            warned_user = Warns(user_id, str(chat_id))
            db.warns.insert_one(warned_user.__dict__)
        else:
            warned_user['num_warns'] += 1
            if reason:
                warned_user['reasons'].append(reason)

            db.warns.update_one(
                {"user_id": user_id, "chat_id": str(chat_id)},
                {"$set": warned_user}
            )

        return warned_user['num_warns'], warned_user['reasons']

def remove_warn(user_id, chat_id):
    with WARN_INSERTION_LOCK:
        warned_user = db.warns.find_one({"user_id": user_id, "chat_id": str(chat_id)})
        if warned_user and warned_user['num_warns'] > 0:
            warned_user['num_warns'] -= 1
            warned_user['reasons'].pop()
            db.warns.update_one(
                {"user_id": user_id, "chat_id": str(chat_id)},
                {"$set": warned_user}
            )
            return True
        return False

def reset_warns(user_id, chat_id):
    with WARN_INSERTION_LOCK:
        db.warns.update_one(
            {"user_id": user_id, "chat_id": str(chat_id)},
            {"$set": {"num_warns": 0, "reasons": []}}
        )

def get_warns(user_id, chat_id):
    warned_user = db.warns.find_one({"user_id": user_id, "chat_id": str(chat_id)})
    if not warned_user:
        return None
    return warned_user['num_warns'], warned_user['reasons']

def add_warn_filter(chat_id, keyword, reply):
    with WARN_FILTER_INSERTION_LOCK:
        warn_filt = WarnFilters(str(chat_id), keyword, reply)
        db.warn_filters.insert_one(warn_filt.__dict__)

        if keyword not in WARN_FILTERS.get(str(chat_id), []):
            WARN_FILTERS[str(chat_id)] = sorted(
                WARN_FILTERS.get(str(chat_id), []) + [keyword],
                key=lambda x: (-len(x), x),
            )

def remove_warn_filter(chat_id, keyword):
    with WARN_FILTER_INSERTION_LOCK:
        db.warn_filters.delete_one({"chat_id": str(chat_id), "keyword": keyword})
        if keyword in WARN_FILTERS.get(str(chat_id), []):
            WARN_FILTERS[str(chat_id)].remove(keyword)
            return True
        return False

def get_chat_warn_triggers(chat_id):
    return WARN_FILTERS.get(str(chat_id), set())

def get_chat_warn_filters(chat_id):
    return list(db.warn_filters.find({"chat_id": str(chat_id)}))

def get_warn_filter(chat_id, keyword):
    return db.warn_filters.find_one({"chat_id": str(chat_id), "keyword": keyword})

def set_warn_limit(chat_id, warn_limit):
    with WARN_SETTINGS_LOCK:
        curr_setting = db.warn_settings.find_one({"chat_id": str(chat_id)})
        if not curr_setting:
            curr_setting = WarnSettings(chat_id, warn_limit=warn_limit)
            db.warn_settings.insert_one(curr_setting.__dict__)
        else:
            curr_setting['warn_limit'] = warn_limit
            db.warn_settings.update_one(
                {"chat_id": str(chat_id)},
                {"$set": curr_setting}
            )

def set_warn_strength(chat_id, soft_warn):
    with WARN_SETTINGS_LOCK:
        curr_setting = db.warn_settings.find_one({"chat_id": str(chat_id)})
        if not curr_setting:
            curr_setting = WarnSettings(chat_id, soft_warn=soft_warn)
            db.warn_settings.insert_one(curr_setting.__dict__)
        else:
            curr_setting['soft_warn'] = soft_warn
            db.warn_settings.update_one(
                {"chat_id": str(chat_id)},
                {"$set": curr_setting}
            )

def get_warn_setting(chat_id):
    setting = db.warn_settings.find_one({"chat_id": str(chat_id)})
    if setting:
        return setting['warn_limit'], setting['soft_warn']
    else:
        return 3, False

def num_warns():
    return db.warns.count_documents({})

def num_warn_chats():
    return db.warns.distinct("chat_id")

def num_warn_filters():
    return db.warn_filters.count_documents({})

def num_warn_chat_filters(chat_id):
    return db.warn_filters.count_documents({"chat_id": str(chat_id)})

def num_warn_filter_chats():
    return db.warn_filters.distinct("chat_id")

def __load_chat_warn_filters():
    global WARN_FILTERS
    chats = db.warn_filters.distinct("chat_id")
    for chat_id in chats:
        WARN_FILTERS[chat_id] = []

    all_filters = list(db.warn_filters.find())
    for x in all_filters:
        WARN_FILTERS[x['chat_id']].append(x['keyword'])

    WARN_FILTERS = {
        x: sorted(set(y), key=lambda i: (-len(i), i))
        for x, y in WARN_FILTERS.items()
    }

def migrate_chat(old_chat_id, new_chat_id):
    with WARN_INSERTION_LOCK:
        db.warns.update_many(
            {"chat_id": str(old_chat_id)},
            {"$set": {"chat_id": str(new_chat_id)}}
        )

    with WARN_FILTER_INSERTION_LOCK:
        db.warn_filters.update_many(
            {"chat_id": str(old_chat_id)},
            {"$set": {"chat_id": str(new_chat_id)}}
        )
        old_warn_filt = WARN_FILTERS.get(str(old_chat_id))
        if old_warn_filt is not None:
            WARN_FILTERS[str(new_chat_id)] = old_warn_filt
            del WARN_FILTERS[str(old_chat_id)]

    with WARN_SETTINGS_LOCK:
        db.warn_settings.update_many(
            {"chat_id": str(old_chat_id)},
            {"$set": {"chat_id": str(new_chat_id)}}
        )

__load_chat_warn_filters()
