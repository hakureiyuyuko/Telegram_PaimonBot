from configparser import RawConfigParser
import pyromod.listen
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from httpx import AsyncClient, get
# 读取配置文件
config = RawConfigParser()
config.read("config.ini")
bot_token: str = ""
admin_id: int = 0
bot_token = config.get("basic", "bot_token", fallback=bot_token)
admin_id = config.getint("basic", "admin", fallback=admin_id)
guess_time = 30  # 猜语音游戏持续时间
""" Init httpx client """
# 使用自定义 UA
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}
client = AsyncClient(timeout=10.0, headers=headers)
me = get(f"https://api.telegram.org/bot{bot_token}/getme").json()
# 初始化客户端
scheduler = AsyncIOScheduler()
if not scheduler.running:
    scheduler.configure(timezone="Asia/ShangHai")
    scheduler.start()
app = Client("bot", bot_token=bot_token)
