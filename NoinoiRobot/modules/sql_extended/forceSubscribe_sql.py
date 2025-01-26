from NoinoiRobot.modules.sql import client, nobita as collection





class ForceSubscribe:
    def __init__(self, chat_id, channel):
        self.chat_id = chat_id
        self.channel = channel


def fs_settings(chat_id):
    try:
        return collection.find_one({"chat_id": chat_id})
    except:
        return None


def add_channel(chat_id, channel):
    adder = collection.find_one({"chat_id": chat_id})
    if adder:
        collection.update_one({"chat_id": chat_id}, {"$set": {"channel": channel}})
    else:
        adder = ForceSubscribe(chat_id, channel)
        collection.insert_one(adder.__dict__)


def disapprove(chat_id):
    collection.delete_one({"chat_id": chat_id})
