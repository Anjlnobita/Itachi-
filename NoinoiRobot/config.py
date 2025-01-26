import json
import os


def get_user_list(config, key):
    with open("{}/Noi/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]



class Config(object):
    LOGGER = True
    

    API_ID = 20650066
    API_HASH = "7a4f8ed638f1369a40693574c2835217"


    TOKEN = "7970949227:AAHHqi_yNrnpN4w0criBvVri_YX6D1BmUKg"

    OWNER_ID = 6777860063

    OWNER_USERNAME = "anjlnobita"


    SUPPORT_CHAT = "anime_societyy"

    JOIN_LOGGER = (
        -1002372313866
    )

    EVENT_LOGS = (
        -1002372313866
    ) 
    MONGO_DB_URI = "mongodb+srv://anjlnobita:tCUPU9Ty1FFvLumv@cluster0.appf0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    DB_URI = "mongodb+srv://anjlnobita:tCUPU9Ty1FFvLumv@cluster0.appf0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    LOAD = []
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    WEBHOOK = False
    INFOPIC = True
    URL = None

    SPAMWATCH_API = "29sw~FuIbphLGXWd38AYb6VnlJ86DKKfnjWHS91VlpUUSyzpHoVlZWxQ0F4P_ZTy"  

    SPAMWATCH_SUPPORT_CHAT = "@anime_societyy"

   
    DRAGONS = get_user_list("", "1963422158")
    
    DEV_USERS = get_user_list("", "1963422158")
    
    DEMONS = get_user_list("", "1963422158")
    
    TIGERS = get_user_list("", "1963422158")

    WOLVES = get_user_list("", "1963422158")

    DONATION_LINK = None  
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True
    STRICT_GBAN = True
    WORKERS = (
        8  
    )
    BAN_STICKER = ""  
    ALLOW_EXCL = True

    CASH_API_KEY = (
        "V7NS1NBFEL4X24L6"
    )

    TIME_API_KEY = "2AS711XS1O9B"

    WALL_API = (
        "awoo"
    )

    AI_API_KEY = "awoo"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []

    SPAMMERS = None

class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
