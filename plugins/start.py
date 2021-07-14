from configparser import RawConfigParser
from os import getcwd, sep
from defs.redis_load import redis, redis_status
from pyrogram import Client
from pyrogram.types import Message


async def welcome_command(client: Client, message: Message):
    # 发送欢迎消息
    await message.reply('你好！我是原神小助手 - 派蒙 。')


async def ping_command(client: Client, message: Message):
    # 提醒在线状态
    await message.reply("poi~")


async def leave_command(client: Client, message: Message):
    # 退出群组
    chat_id = message.text.split()[-1]
    # 权限检查
    uid = str(message.from_user.id)
    config = RawConfigParser()
    config.read(f"{getcwd()}{sep}config.ini")
    admin_str: str = "777000"
    admin_str = config.get("basic", "admin", fallback=admin_str)
    admins = admin_str.split('|')
    if redis_status():
        admin = redis.get('mys')
        if admin:
            admins.extend(admin.split('|'))
    if uid not in admins:
        return
    try:
        await client.leave_chat(chat_id)
        await message.reply('成功执行退出群组命令。')
    except Exception as e:
        await message.reply(f'错误：\n{e}')


async def help_command(client: Client, message: Message):
    text = '<a href="https://git.io/JcbTD">PaimonBot</a> 0.1.1beta By Xtao-Labs\n\n' \
           '🔅 以下是小派蒙我学会了的功能（部分）：\n' \
           '1️⃣ [武器/今日武器] 查看今日武器材料和武器\n' \
           '2️⃣ [天赋/今日天赋] 查看今日天赋材料和角色\n' \
           '3️⃣ [周本] 查看周本材料和人物\n' \
           '4️⃣ [武器查询 武器名] 查看武器资料\n' \
           '   💠 <code>武器查询 沐浴龙血的剑</code>\n' \
           '5️⃣ [角色查询 名字] 查看人物简介\n' \
           '   💠 <code>角色查询 重云</code>\n' \
           '6️⃣ [命座 名字] 查看人物命座\n' \
           '   💠 <code>命座 重云一命</code>\n' \
           '7️⃣ [运势 (名字)] 查看今日运势\n' \
           '   💠 <code>运势 (重云)</code>\n' \
           '   💠 <code>设置运势 (重云)</code>\n' \
           '8️⃣ [原神黄历] 查看随机生成的原神黄历'
    await message.reply(text, quote=True, disable_web_page_preview=True)
