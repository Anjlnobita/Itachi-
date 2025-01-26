from NoinoiRobot.modules.sql import client, nobita as nightmode_collection




class Nightmode:
    def __init__(self, chat_id):
        self.chat_id = chat_id


def add_nightmode(chat_id: str):
    nightmoddy = Nightmode(str(chat_id))
    nightmode_collection.insert_one(nightmoddy.__dict__)


def rmnightmode(chat_id: str):
    nightmode_collection.delete_one({'chat_id': str(chat_id)})


def get_all_chat_id():
    return list(nightmode_collection.find({}, {'_id': 0, 'chat_id': 1}))


def is_nightmode_indb(chat_id: str):
    result = nightmode_collection.find_one({'chat_id': str(chat_id)})
    return str(result['chat_id']) if result else None
