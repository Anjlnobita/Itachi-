import threading

from NoinoiRobot.modules.sql import client, nobita as db


GBANNED_USERS_LOCK = threading.RLock()
GBAN_SETTING_LOCK = threading.RLock()
GBANNED_LIST = set()
GBANSTAT_LIST = set()


class GloballyBannedUsers:
    def __init__(self, user_id, name, reason=None):
        self.user_id = user_id
        self.name = name
        self.reason = reason

    def to_dict(self):
        return {"user_id": self.user_id, "name": self.name, "reason": self.reason}


class GbanSettings:
    def __init__(self, chat_id, enabled):
        self.chat_id = str(chat_id)
        self.setting = enabled


def gban_user(user_id, name, reason=None):
    with GBANNED_USERS_LOCK:
        user = db.gbans.find_one({"user_id": user_id})
        if not user:
            user = GloballyBannedUsers(user_id, name, reason)
            db.gbans.insert_one(user.to_dict())
        else:
            db.gbans.update_one({"user_id": user_id}, {"$set": {"name": name, "reason": reason}})
        __load_gbanned_userid_list()


def update_gban_reason(user_id, name, reason=None):
    with GBANNED_USERS_LOCK:
        user = db.gbans.find_one({"user_id": user_id})
        if not user:
            return None
        old_reason = user.get('reason')
        db.gbans.update_one({"user_id": user_id}, {"$set": {"name": name, "reason": reason}})
        return old_reason


def ungban_user(user_id):
    with GBANNED_USERS_LOCK:
        db.gbans.delete_one({"user_id": user_id})
        __load_gbanned_userid_list()


def is_user_gbanned(user_id):
    return user_id in GBANNED_LIST


def get_gbanned_user(user_id):
    return db.gbans.find_one({"user_id": user_id})


def get_gban_list():
    return [GloballyBannedUsers(**x).to_dict() for x in db.gbans.find()]


def enable_gbans(chat_id):
    with GBAN_SETTING_LOCK:
        chat = db.gban_settings.find_one({"chat_id": str(chat_id)})
        if not chat:
            chat = GbanSettings(chat_id, True)
            db.gban_settings.insert_one(chat.__dict__)
        else:
            db.gban_settings.update_one({"chat_id": str(chat_id)}, {"$set": {"setting": True}})
        if str(chat_id) in GBANSTAT_LIST:
            GBANSTAT_LIST.remove(str(chat_id))


def disable_gbans(chat_id):
    with GBAN_SETTING_LOCK:
        chat = db.gban_settings.find_one({"chat_id": str(chat_id)})
        if not chat:
            chat = GbanSettings(chat_id, False)
            db.gban_settings.insert_one(chat.__dict__)
        else:
            db.gban_settings.update_one({"chat_id": str(chat_id)}, {"$set": {"setting": False}})
        GBANSTAT_LIST.add(str(chat_id))


def does_chat_gban(chat_id):
    return str(chat_id) not in GBANSTAT_LIST


def num_gbanned_users():
    return len(GBANNED_LIST)


def __load_gbanned_userid_list():
    global GBANNED_LIST
    GBANNED_LIST = {x['user_id'] for x in db.gbans.find()}


def __load_gban_stat_list():
    global GBANSTAT_LIST
    GBANSTAT_LIST = {x['chat_id'] for x in db.gban_settings.find() if not x['setting']}


def migrate_chat(old_chat_id, new_chat_id):
    with GBAN_SETTING_LOCK:
        chat = db.gban_settings.find_one({"chat_id": str(old_chat_id)})
        if chat:
            db.gban_settings.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": new_chat_id}})


__load_gbanned_userid_list()
__load_gban_stat_list()
