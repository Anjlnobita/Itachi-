import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['approval_db']
approvals_collection = db['approval']

APPROVE_INSERTION_LOCK = threading.RLock()

class Approvals:
    def __init__(self, chat_id, user_id):
        self.chat_id = str(chat_id)  # ensure string
        self.user_id = user_id

    def __repr__(self):
        return "<Approve %s>" % self.user_id


def approve(chat_id, user_id):
    with APPROVE_INSERTION_LOCK:
        approve_user = Approvals(str(chat_id), user_id)
        approvals_collection.insert_one(approve_user.__dict__)


def is_approved(chat_id, user_id):
    try:
        return approvals_collection.find_one({"chat_id": str(chat_id), "user_id": user_id})
    finally:
        client.close()


def disapprove(chat_id, user_id):
    with APPROVE_INSERTION_LOCK:
        disapprove_user = approvals_collection.find_one({"chat_id": str(chat_id), "user_id": user_id})
        if disapprove_user:
            approvals_collection.delete_one({"chat_id": str(chat_id), "user_id": user_id})
            return True
        else:
            client.close()
            return False


def list_approved(chat_id):
    try:
        return list(approvals_collection.find({"chat_id": str(chat_id)}).sort("user_id", 1))
    finally:
        client.close()
