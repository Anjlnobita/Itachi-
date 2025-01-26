import threading

from NoinoiRobot.modules.sql import client, nobita as afk_collection




INSERTION_LOCK = threading.RLock()

AFK_USERS = {}


def is_afk(user_id):
    return user_id in AFK_USERS


def check_afk_status(user_id):
    return afk_collection.find_one({"user_id": user_id})


def set_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = afk_collection.find_one({"user_id": user_id})
        if not curr:
            afk_collection.insert_one({"user_id": user_id, "reason": reason, "is_afk": True})
        else:
            afk_collection.update_one({"user_id": user_id}, {"$set": {"is_afk": True}})

        AFK_USERS[user_id] = reason


def rm_afk(user_id):
    with INSERTION_LOCK:
        curr = afk_collection.find_one({"user_id": user_id})
        if curr:
            if user_id in AFK_USERS:  # sanity check
                del AFK_USERS[user_id]

            afk_collection.delete_one({"user_id": user_id})
            return True

        return False


def toggle_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = afk_collection.find_one({"user_id": user_id})
        if not curr:
            afk_collection.insert_one({"user_id": user_id, "reason": reason, "is_afk": True})
        elif curr['is_afk']:
            afk_collection.update_one({"user_id": user_id}, {"$set": {"is_afk": False}})
        else:
            afk_collection.update_one({"user_id": user_id}, {"$set": {"is_afk": True}})


def __load_afk_users():
    global AFK_USERS
    all_afk = afk_collection.find({"is_afk": True})
    AFK_USERS = {user['user_id']: user['reason'] for user in all_afk}


__load_afk_users()
