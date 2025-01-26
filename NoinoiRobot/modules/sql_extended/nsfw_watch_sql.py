from NoinoiRobot.modules.sql import client, nobita as nsfwatch_collection





class Nsfwatch:
    def __init__(self, chat_id):
        self.chat_id = chat_id


def add_nsfwatch(chat_id: str):
    nsfws = Nsfwatch(str(chat_id))
    nsfwatch_collection.insert_one(vars(nsfws))


def rmnsfwatch(chat_id: str):
    nsfwm = nsfwatch_collection.find_one({"chat_id": str(chat_id)})
    if nsfwm:
        nsfwatch_collection.delete_one({"chat_id": str(chat_id)})


def get_all_nsfw_enabled_chat():
    stark = list(nsfwatch_collection.find())
    return stark


def is_nsfwatch_indb(chat_id: str):
    s__ = nsfwatch_collection.find_one({"chat_id": str(chat_id)})
    if s__:
        return str(s__['chat_id'])
