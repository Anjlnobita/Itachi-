import threading
from typing import Union
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['reporting_db']

CHAT_LOCK = threading.RLock()
USER_LOCK = threading.RLock()


def chat_should_report(chat_id: Union[str, int]) -> bool:
    try:
        chat_setting = db.chat_report_settings.find_one({"chat_id": str(chat_id)})
        if chat_setting:
            return chat_setting.get("should_report", False)
        return False
    finally:
        client.close()


def user_should_report(user_id: int) -> bool:
    try:
        user_setting = db.user_report_settings.find_one({"user_id": user_id})
        if user_setting:
            return user_setting.get("should_report", True)
        return True
    finally:
        client.close()


def set_chat_setting(chat_id: Union[int, str], setting: bool):
    with CHAT_LOCK:
        chat_setting = db.chat_report_settings.find_one({"chat_id": str(chat_id)})
        if not chat_setting:
            chat_setting = {"chat_id": str(chat_id), "should_report": setting}
            db.chat_report_settings.insert_one(chat_setting)
        else:
            db.chat_report_settings.update_one(
                {"chat_id": str(chat_id)},
                {"$set": {"should_report": setting}}
            )


def set_user_setting(user_id: int, setting: bool):
    with USER_LOCK:
        user_setting = db.user_report_settings.find_one({"user_id": user_id})
        if not user_setting:
            user_setting = {"user_id": user_id, "should_report": setting}
            db.user_report_settings.insert_one(user_setting)
        else:
            db.user_report_settings.update_one(
                {"user_id": user_id},
                {"$set": {"should_report": setting}}
            )


def migrate_chat(old_chat_id, new_chat_id):
    with CHAT_LOCK:
        chat_notes = db.chat_report_settings.find({"chat_id": str(old_chat_id)})
        for note in chat_notes:
            db.chat_report_settings.update_one(
                {"chat_id": str(old_chat_id)},
                {"$set": {"chat_id": str(new_chat_id)}}
            )
