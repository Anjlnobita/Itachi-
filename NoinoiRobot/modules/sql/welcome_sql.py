import random
import threading
from typing import Union

from NoinoiRobot.modules.sql import client, nobita as db



DEFAULT_WELCOME = "Hey {first}, how are you?"
DEFAULT_GOODBYE = "Nice knowing ya!"

DEFAULT_WELCOME_MESSAGES = [
    "{first} is here!",
    "Ready player {first}",
    "Genos, {first} is here.",
    "A wild {first} appeared.",
    "{first} came in like a Lion!",
    "{first} has joined your party.",
]

DEFAULT_GOODBYE_MESSAGES = [
    "{first} will be missed.",
    "{first} just went offline.",
    "{first} has left the lobby.",
    "{first} has left the clan.",
    "{first} has left the game.",
    "{first} has fled the area.",
    "{first} is out of the running.",
]


INSERTION_LOCK = threading.RLock()

class Welcome:
    def __init__(self, chat_id, should_welcome=True, should_goodbye=True):
        self.chat_id = chat_id
        self.should_welcome = should_welcome
        self.should_goodbye = should_goodbye
        self.custom_content = None
        self.custom_welcome = random.choice(DEFAULT_WELCOME_MESSAGES)
        self.welcome_type = "text"
        self.custom_leave = random.choice(DEFAULT_GOODBYE_MESSAGES)
        self.leave_type = "text"
        self.clean_welcome = None

    def save(self):
        db.welcome_pref.update_one({'chat_id': self.chat_id}, {'$set': self.__dict__}, upsert=True)

class WelcomeButtons:
    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = chat_id
        self.name = name
        self.url = url
        self.same_line = same_line

    def save(self):
        db.welcome_urls.update_one({'chat_id': self.chat_id, 'name': self.name}, {'$set': self.__dict__}, upsert=True)

class GoodbyeButtons:
    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = chat_id
        self.name = name
        self.url = url
        self.same_line = same_line

    def save(self):
        db.leave_urls.update_one({'chat_id': self.chat_id, 'name': self.name}, {'$set': self.__dict__}, upsert=True)

class WelcomeMute:
    def __init__(self, chat_id, welcomemutes):
        self.chat_id = chat_id
        self.welcomemutes = welcomemutes

    def save(self):
        db.welcome_mutes.update_one({'chat_id': self.chat_id}, {'$set': self.__dict__}, upsert=True)

class WelcomeMuteUsers:
    def __init__(self, user_id, chat_id, human_check):
        self.user_id = user_id
        self.chat_id = chat_id
        self.human_check = human_check

    def save(self):
        db.human_checks.update_one({'user_id': self.user_id, 'chat_id': self.chat_id}, {'$set': self.__dict__}, upsert=True)

class CleanServiceSetting:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.clean_service = True

    def save(self):
        db.clean_service.update_one({'chat_id': self.chat_id}, {'$set': self.__dict__}, upsert=True)

def welcome_mutes(chat_id):
    return db.welcome_mutes.find_one({'chat_id': chat_id})

def set_welcome_mutes(chat_id, welcomemutes):
    with INSERTION_LOCK:
        welcome_mute = WelcomeMute(chat_id, welcomemutes)
        welcome_mute.save()

def set_human_checks(user_id, chat_id):
    with INSERTION_LOCK:
        human_check = WelcomeMuteUsers(user_id, chat_id, True)
        human_check.save()

def get_human_checks(user_id, chat_id):
    return db.human_checks.find_one({'user_id': user_id, 'chat_id': chat_id})

def get_welc_pref(chat_id):
    welc = db.welcome_pref.find_one({'chat_id': chat_id})
    if welc:
        return welc['should_welcome'], welc['custom_welcome'], welc['custom_content'], welc['welcome_type']
    return True, DEFAULT_WELCOME, None, "text"

def set_clean_welcome(chat_id, clean_welcome):
    with INSERTION_LOCK:
        welcome = db.welcome_pref.find_one({'chat_id': chat_id})
        if welcome:
            welcome['clean_welcome'] = clean_welcome
            db.welcome_pref.update_one({'chat_id': chat_id}, {'$set': welcome})
        else:
            new_welcome = Welcome(chat_id)
            new_welcome.clean_welcome = clean_welcome
            new_welcome.save()

def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = db.welcome_pref.find_one({'chat_id': old_chat_id})
        if chat:
            chat['chat_id'] = new_chat_id
            db.welcome_pref.update_one({'chat_id': old_chat_id}, {'$set': chat})

        chat_buttons = db.welcome_urls.find({'chat_id': old_chat_id})
        for btn in chat_buttons:
            btn['chat_id'] = new_chat_id
            db.welcome_urls.update_one({'chat_id': old_chat_id, 'name': btn['name']}, {'$set': btn})

        goodbye_buttons = db.leave_urls.find({'chat_id': old_chat_id})
        for btn in goodbye_buttons:
            btn['chat_id'] = new_chat_id
            db.leave_urls.update_one({'chat_id': old_chat_id, 'name': btn['name']}, {'$set': btn})
