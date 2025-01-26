import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['notes_db']

NOTES_COLLECTION = db['notes']
BUTTONS_COLLECTION = db['note_urls']

NOTES_INSERTION_LOCK = threading.RLock()
BUTTONS_INSERTION_LOCK = threading.RLock()


def add_note_to_db(chat_id, note_name, note_data, msgtype, buttons=None, file=None):
    if not buttons:
        buttons = []

    with NOTES_INSERTION_LOCK:
        prev = NOTES_COLLECTION.find_one({"chat_id": str(chat_id), "name": note_name})
        if prev:
            with BUTTONS_INSERTION_LOCK:
                BUTTONS_COLLECTION.delete_many({"chat_id": str(chat_id), "note_name": note_name})
            NOTES_COLLECTION.delete_one({"chat_id": str(chat_id), "name": note_name})

        note = {
            "chat_id": str(chat_id),
            "name": note_name,
            "value": note_data or "",
            "msgtype": msgtype.value,
            "file": file
        }
        NOTES_COLLECTION.insert_one(note)

    for b_name, url, same_line in buttons:
        add_note_button_to_db(chat_id, note_name, b_name, url, same_line)


def get_note(chat_id, note_name):
    try:
        return NOTES_COLLECTION.find_one({"chat_id": str(chat_id), "name": note_name})
    finally:
        client.close()


def rm_note(chat_id, note_name):
    with NOTES_INSERTION_LOCK:
        note = NOTES_COLLECTION.find_one({"chat_id": str(chat_id), "name": note_name})
        if note:
            with BUTTONS_INSERTION_LOCK:
                BUTTONS_COLLECTION.delete_many({"chat_id": str(chat_id), "note_name": note_name})

            NOTES_COLLECTION.delete_one({"chat_id": str(chat_id), "name": note_name})
            return True
        else:
            client.close()
            return False


def get_all_chat_notes(chat_id):
    try:
        return list(NOTES_COLLECTION.find({"chat_id": str(chat_id)}).sort("name", 1))
    finally:
        client.close()


def add_note_button_to_db(chat_id, note_name, b_name, url, same_line):
    with BUTTONS_INSERTION_LOCK:
        button = {
            "chat_id": str(chat_id),
            "note_name": note_name,
            "name": b_name,
            "url": url,
            "same_line": same_line
        }
        BUTTONS_COLLECTION.insert_one(button)


def get_buttons(chat_id, note_name):
    try:
        return list(BUTTONS_COLLECTION.find({"chat_id": str(chat_id), "note_name": note_name}).sort("id"))
    finally:
        client.close()


def num_notes():
    try:
        return NOTES_COLLECTION.count_documents({})
    finally:
        client.close()


def num_chats():
    try:
        return len(NOTES_COLLECTION.distinct("chat_id"))
    finally:
        client.close()


def migrate_chat(old_chat_id, new_chat_id):
    with NOTES_INSERTION_LOCK:
        chat_notes = NOTES_COLLECTION.find({"chat_id": str(old_chat_id)})
        for note in chat_notes:
            NOTES_COLLECTION.update_one({"_id": note["_id"]}, {"$set": {"chat_id": str(new_chat_id)}})

        with BUTTONS_INSERTION_LOCK:
            chat_buttons = BUTTONS_COLLECTION.find({"chat_id": str(old_chat_id)})
            for btn in chat_buttons:
                BUTTONS_COLLECTION.update_one({"_id": btn["_id"]}, {"$set": {"chat_id": str(new_chat_id)}})

        client.close()
