import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']

INSERTION_LOCK = threading.RLock()


class UserInfo:
    def __init__(self, user_id, info):
        self.user_id = user_id
        self.info = info

    def __repr__(self):
        return "<User info %d>" % self.user_id


class UserBio:
    def __init__(self, user_id, bio):
        self.user_id = user_id
        self.bio = bio

    def __repr__(self):
        return "<User info %d>" % self.user_id


def get_user_me_info(user_id):
    userinfo = db.userinfo.find_one({"user_id": user_id})
    if userinfo:
        return userinfo['info']
    return None


def set_user_me_info(user_id, info):
    with INSERTION_LOCK:
        userinfo = db.userinfo.find_one({"user_id": user_id})
        if userinfo:
            db.userinfo.update_one({"user_id": user_id}, {"$set": {"info": info}})
        else:
            userinfo = UserInfo(user_id, info)
            db.userinfo.insert_one(userinfo.__dict__)


def get_user_bio(user_id):
    userbio = db.userbio.find_one({"user_id": user_id})
    if userbio:
        return userbio['bio']
    return None


def set_user_bio(user_id, bio):
    with INSERTION_LOCK:
        userbio = db.userbio.find_one({"user_id": user_id})
        if userbio:
            db.userbio.update_one({"user_id": user_id}, {"$set": {"bio": bio}})
        else:
            userbio = UserBio(user_id, bio)
            db.userbio.insert_one(userbio.__dict__)
