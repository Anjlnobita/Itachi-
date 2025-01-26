import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['NoinoiRobot']

INSERTION_LOCK = threading.RLock()

def ensure_bot_in_db():
    with INSERTION_LOCK:
        bot = {
            "user_id": dispatcher.bot.id,
            "username": dispatcher.bot.username
        }
        db.users.update_one({"user_id": bot["user_id"]}, {"$set": bot}, upsert=True)

def update_user(user_id, username, chat_id=None, chat_name=None):
    with INSERTION_LOCK:
        user = db.users.find_one({"user_id": user_id})
        if not user:
            user = {
                "user_id": user_id,
                "username": username
            }
            db.users.insert_one(user)
        else:
            db.users.update_one({"user_id": user_id}, {"$set": {"username": username}})

        if chat_id and chat_name:
            chat = db.chats.find_one({"chat_id": str(chat_id)})
            if not chat:
                chat = {
                    "chat_id": str(chat_id),
                    "chat_name": chat_name
                }
                db.chats.insert_one(chat)
            else:
                db.chats.update_one({"chat_id": str(chat_id)}, {"$set": {"chat_name": chat_name}})

            member = db.chat_members.find_one({"chat": str(chat_id), "user": user_id})
            if not member:
                chat_member = {
                    "chat": str(chat_id),
                    "user": user_id
                }
                db.chat_members.insert_one(chat_member)

def get_userid_by_name(username):
    try:
        return list(db.users.find({"username": {"$regex": f"^{username}$", "$options": "i"}}))
    finally:
        client.close()

def get_name_by_userid(user_id):
    try:
        return db.users.find_one({"user_id": int(user_id)})
    finally:
        client.close()

def get_chat_members(chat_id):
    try:
        return list(db.chat_members.find({"chat": str(chat_id)}))
    finally:
        client.close()

def get_all_chats():
    try:
        return list(db.chats.find())
    finally:
        client.close()

def get_all_users():
    try:
        return list(db.users.find())
    finally:
        client.close()

def get_user_num_chats(user_id):
    try:
        return db.chat_members.count_documents({"user": int(user_id)})
    finally:
        client.close()

def get_user_com_chats(user_id):
    try:
        chat_members = list(db.chat_members.find({"user": int(user_id)}))
        return [i['chat'] for i in chat_members]
    finally:
        client.close()

def num_chats():
    try:
        return db.chats.count_documents({})
    finally:
        client.close()

def num_users():
    try:
        return db.users.count_documents({})
    finally:
        client.close()

def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        db.chats.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": str(new_chat_id)}})

        chat_members = list(db.chat_members.find({"chat": str(old_chat_id)}))
        for member in chat_members:
            db.chat_members.update_one({"_id": member["_id"]}, {"$set": {"chat": str(new_chat_id)}})

def del_user(user_id):
    with INSERTION_LOCK:
        curr = db.users.find_one({"user_id": user_id})
        if curr:
            db.users.delete_one({"user_id": user_id})
            db.chat_members.delete_many({"user": user_id})
            return True
    return False

def rem_chat(chat_id):
    with INSERTION_LOCK:
        chat = db.chats.find_one({"chat_id": str(chat_id)})
        if chat:
            db.chats.delete_one({"chat_id": str(chat_id)})
