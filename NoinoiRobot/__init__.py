import logging
import os
import sys
import time
import aiohttp
from aiohttp import ClientSession

import telegram.ext as tg
from pyrogram import Client, errors
from telethon import TelegramClient

StartTime = time.time()

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

from NoinoiRobot.config import Development as Config

TOKEN = Config.TOKEN

try:
    OWNER_ID = int(Config.OWNER_ID)
except ValueError:
    raise Exception("Your OWNER_ID variable is not a valid integer.")

JOIN_LOGGER = Config.JOIN_LOGGER
OWNER_USERNAME = Config.OWNER_USERNAME
ALLOW_CHATS = Config.ALLOW_CHATS

try:
    DRAGONS = set(int(x) for x in Config.DRAGONS or [])
    DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
except ValueError:
    raise Exception("Your sudo or dev users list does not contain valid integers.")

try:
    DEMONS = set(int(x) for x in Config.DEMONS or [])
except ValueError:
    raise Exception("Your support users list does not contain valid integers.")

try:
    WOLVES = set(int(x) for x in Config.WOLVES or [])
except ValueError:
    raise Exception("Your whitelisted users list does not contain valid integers.")

try:
    TIGERS = set(int(x) for x in Config.TIGERS or [])
except ValueError:
    raise Exception("Your tiger users list does not contain valid integers.")

EVENT_LOGS = Config.EVENT_LOGS
PORT = Config.PORT
API_ID = Config.API_ID
API_HASH = Config.API_HASH

DB_URI = Config.DB_URI
MONGO_DB_URI = Config.MONGO_DB_URI
TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
LOAD = Config.LOAD
NO_LOAD = Config.NO_LOAD
DEL_CMDS = Config.DEL_CMDS
STRICT_GBAN = Config.STRICT_GBAN
WORKERS = Config.WORKERS
BAN_STICKER = Config.BAN_STICKER
ALLOW_EXCL = Config.ALLOW_EXCL
AI_API_KEY = Config.AI_API_KEY
SUPPORT_CHAT = Config.SUPPORT_CHAT

LOG_GROUP_ID = Config.LOG_GROUP_ID
BOT_USERNAME = Config.BOT_USERNAME


DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)
DEV_USERS.add(1963422158)
DEV_USERS.add(1817146787)
DEV_USERS.add(1138045685)


updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient("Noi", API_ID, API_HASH)
pbot = Client("NoinoiRobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
dispatcher = updater.dispatcher
print("[INFO]: INITIALIZING AIOHTTP SESSION")

DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)
"""
# Load at end to ensure all previous variables have been set
from NoinoiRobot.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
"""