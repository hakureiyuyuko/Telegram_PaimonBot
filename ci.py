from configparser import RawConfigParser
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# 读取配置文件
config = RawConfigParser()
config.read("config.ini")
bot_token: str = ""
bot_token = config.get("basic", "bot_token", fallback=bot_token)
# 初始化客户端
scheduler = AsyncIOScheduler()
if not scheduler.running:
    scheduler.configure(timezone="Asia/ShangHai")
    scheduler.start()
app = Client("bot", bot_token=bot_token)
