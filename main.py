import logging
from configparser import RawConfigParser
from pyrogram import Client


# 日志记录
logging.basicConfig(level=logging.INFO)
# 读取配置文件
config = RawConfigParser()
config.read("config.ini")
bot_token: str = ""
bot_token = config.get("basic", "bot_token", fallback=bot_token)
# 初始化客户端
app = Client("bot", bot_token=bot_token)
app.run()
