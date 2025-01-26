import threading
from NoinoiRobot.modules.sql import client, nobita as db

CLEANER_CHAT_SETTINGS = threading.RLock()
CLEANER_CHAT_LOCK = threading.RLock()
CLEANER_GLOBAL_LOCK = threading.RLock()

CLEANER_CHATS = {}
GLOBAL_IGNORE_COMMANDS = set()

def set_cleanbt(chat_id, is_enable):
    with CLEANER_CHAT_SETTINGS:
        db.cleaner_bluetext_chat_setting.update_one(
            {"chat_id": str(chat_id)},
            {"$set": {"is_enable": is_enable}},
            upsert=True
        )
        CLEANER_CHATS.setdefault(str(chat_id), {"setting": False, "commands": set()})
        CLEANER_CHATS[str(chat_id)]["setting"] = is_enable

def chat_ignore_command(chat_id, ignore):
    ignore = ignore.lower()
    with CLEANER_CHAT_LOCK:
        if str(chat_id) not in CLEANER_CHATS:
            CLEANER_CHATS.setdefault(str(chat_id), {"setting": False, "commands": set()})
        if ignore not in CLEANER_CHATS[str(chat_id)]["commands"]:
            CLEANER_CHATS[str(chat_id)]["commands"].add(ignore)
            db.cleaner_bluetext_chat_ignore_commands.insert_one({"chat_id": str(chat_id), "command": ignore})
            return True
    return False

def chat_unignore_command(chat_id, unignore):
    unignore = unignore.lower()
    with CLEANER_CHAT_LOCK:
        if str(chat_id) in CLEANER_CHATS and unignore in CLEANER_CHATS[str(chat_id)]["commands"]:
            CLEANER_CHATS[str(chat_id)]["commands"].remove(unignore)
            db.cleaner_bluetext_chat_ignore_commands.delete_one({"chat_id": str(chat_id), "command": unignore})
            return True
    return False

def global_ignore_command(command):
    command = command.lower()
    with CLEANER_GLOBAL_LOCK:
        if command not in GLOBAL_IGNORE_COMMANDS:
            GLOBAL_IGNORE_COMMANDS.add(command)
            db.cleaner_bluetext_global_ignore_commands.insert_one({"command": str(command)})
            return True
    return False

def global_unignore_command(command):
    command = command.lower()
    with CLEANER_GLOBAL_LOCK:
        if command in GLOBAL_IGNORE_COMMANDS:
            GLOBAL_IGNORE_COMMANDS.remove(command)
            db.cleaner_bluetext_global_ignore_commands.delete_one({"command": str(command)})
            return True
    return False

def is_command_ignored(chat_id, command):
    return command.lower() in GLOBAL_IGNORE_COMMANDS or (str(chat_id) in CLEANER_CHATS and command.lower() in CLEANER_CHATS[str(chat_id)]["commands"])

def is_enabled(chat_id):
    return str(chat_id) in CLEANER_CHATS and CLEANER_CHATS[str(chat_id)]["setting"]

def get_all_ignored(chat_id):
    LOCAL_IGNORE_COMMANDS = CLEANER_CHATS.get(str(chat_id), {"commands": set()})["commands"]
    return GLOBAL_IGNORE_COMMANDS, LOCAL_IGNORE_COMMANDS

def __load_cleaner_list():
    global GLOBAL_IGNORE_COMMANDS
    global CLEANER_CHATS

    GLOBAL_IGNORE_COMMANDS = {x['command'] for x in db.cleaner_bluetext_global_ignore_commands.find()}
    for x in db.cleaner_bluetext_chat_setting.find():
        CLEANER_CHATS.setdefault(x['chat_id'], {"setting": False, "commands": set()})
        CLEANER_CHATS[x['chat_id']]["setting"] = x['is_enable']
    for x in db.cleaner_bluetext_chat_ignore_commands.find():
        CLEANER_CHATS.setdefault(x['chat_id'], {"setting": False, "commands": set()})
        CLEANER_CHATS[x['chat_id']]["commands"].add(x['command'])

__load_cleaner_list()
