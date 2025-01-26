import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['rss_database']
rss_collection = db['rss_feed']

INSERTION_LOCK = threading.RLock()


class RSS:
    def __init__(self, chat_id, feed_link, old_entry_link):
        self.chat_id = chat_id
        self.feed_link = feed_link
        self.old_entry_link = old_entry_link

    def __repr__(self):
        return "<RSS for chatID {} at feed_link {} with old_entry_link {}>".format(
            self.chat_id, self.feed_link, self.old_entry_link
        )


def check_url_availability(tg_chat_id, tg_feed_link):
    return list(rss_collection.find({"feed_link": tg_feed_link, "chat_id": tg_chat_id}))


def add_url(tg_chat_id, tg_feed_link, tg_old_entry_link):
    with INSERTION_LOCK:
        action = RSS(tg_chat_id, tg_feed_link, tg_old_entry_link)
        rss_collection.insert_one(action.__dict__)


def remove_url(tg_chat_id, tg_feed_link):
    with INSERTION_LOCK:
        rss_collection.delete_many({"chat_id": tg_chat_id, "feed_link": tg_feed_link})


def get_urls(tg_chat_id):
    return list(rss_collection.find({"chat_id": tg_chat_id}))


def get_all():
    return list(rss_collection.find())


def update_url(row_id, new_entry_links):
    with INSERTION_LOCK:
        rss_collection.update_one({"_id": row_id}, {"$set": {"old_entry_link": new_entry_links[0]}})
