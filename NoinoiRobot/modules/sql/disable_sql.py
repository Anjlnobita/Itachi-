import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
disabled_commands_collection = db['disabled_commands']

DISABLE_INSERTION_LOCK = threading.RLock()
DISABLED = {}

class Disable:
    def __init__(self, chat_id, command):
        self.chat_id = chat_id
        self.command = command

    def __repr__(self):
        return "Disabled cmd {} in {}".format(self.command, self.chat_id)

def disable_command(chat_id, disable):
    with DISABLE_INSERTION_LOCK:
        disabled = disabled_commands_collection.find_one({"chat_id": str(chat_id), "command": disable})

        if not disabled:
            DISABLED.setdefault(str(chat_id), set()).add(disable)

            disabled_command = Disable(str(chat_id), disable)
            disabled_commands_collection.insert_one(disabled_command.__dict__)
            return True

        return False

def enable_command(chat_id, enable):
    with DISABLE_INSERTION_LOCK:
        disabled = disabled_commands_collection.find_one({"chat_id": str(chat_id), "command": enable})

        if disabled:
            if enable in DISABLED.get(str(chat_id)):  # sanity check
                DISABLED.setdefault(str(chat_id), set()).remove(enable)

            disabled_commands_collection.delete_one({"chat_id": str(chat_id), "command": enable})
            return True

        return False

def is_command_disabled(chat_id, cmd):
    return str(cmd).lower() in DISABLED.get(str(chat_id), set())

def get_all_disabled(chat_id):
    return DISABLED.get(str(chat_id), set())

def num_chats():
    return disabled_commands_collection.distinct("chat_id")

def num_disabled():
    return disabled_commands_collection.count_documents({})

def migrate_chat(old_chat_id, new_chat_id):
    with DISABLE_INSERTION_LOCK:
        chats = disabled_commands_collection.find({"chat_id": str(old_chat_id)})
        for chat in chats:
            disabled_commands_collection.update_one({"_id": chat["_id"]}, {"$set": {"chat_id": str(new_chat_id)}})

        if str(old_chat_id) in DISABLED:
            DISABLED[str(new_chat_id)] = DISABLED.get(str(old_chat_id), set())

def __load_disabled_commands():
    global DISABLED
    all_chats = disabled_commands_collection.find()
    for chat in all_chats:
        DISABLED.setdefault(chat['chat_id'], set()).add(chat['command'])

__load_disabled_commands()
