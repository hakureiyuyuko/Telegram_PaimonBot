from configparser import RawConfigParser
from os import getcwd, sep
from defs.redis_load import redis, redis_status
from pyrogram import Client
from pyrogram.types import Message


async def welcome_command(client: Client, message: Message):
    # 发送欢迎消息
    await message.reply('你好！我是原神小助手 - 派蒙 。', quote=True)


async def ping_command(client: Client, message: Message):
    # 提醒在线状态
    await message.reply("poi~", quote=True)


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
    text = '<a href="https://git.io/JcbTD">PaimonBot</a> 0.2.5beta By Xtao-Labs\n\n' \
           '🔅 以下是小派蒙我学会了的功能（部分）：\n' \
           '① [武器/今日武器] 查看今日武器材料和武器\n' \
           '② [天赋/今日天赋] 查看今日天赋材料和角色\n' \
           '③ [周本] 查看周本材料和人物\n' \
           '④ [运势 (名字)] 查看今日运势\n' \
           '   💠 <code>运势 (重云)</code>\n' \
           '   💠 <code>设置运势 (重云)</code>\n' \
           '⑤ [角色查询 名字] 查看人物简介\n' \
           '   💠 <code>角色查询 重云</code>\n' \
           '⑥ [命座 名字] 查看人物命座\n' \
           '   💠 <code>命座 重云一命</code>\n' \
           '⑦ [武器查询 武器名] 查看武器资料\n' \
           '   💠 <code>武器查询 沐浴龙血的剑</code>\n' \
           '⑧ [原神黄历] 查看随机生成的原神黄历\n' \
           '⑨ [活动列表] 查看今日活动列表和祈愿列表\n' \
           '⑩ [圣遗物评分] 我也想拥有这种分数的圣遗物(切实)\n' \
           '(11) [哪里有 (资源名)] 查看资源的位置\n' \
           '(12) [资源列表] 查看原神所有资源\n' \
           '(13) [米游社] 米游社相关功能\n' \
           '   💠 <code>米游社添加（私聊）</code>\n' \
           '   💠 <code>米游社推送开启/关闭</code>\n' \
           '   💠 <code>米游社自动签到开启/关闭</code>\n' \
           '   💠 <code>米游社每月统计（群聊）</code>\n' \
           '   💠 <code>米游社签到（群聊）</code>\n' \
           '   💠 <code>米游社当前状态（群聊）</code>\n' \
           '   💠 <code>米游社绑定uid（群聊）</code>\n' \
           '   💠 <code>米游社绑定mys（群聊）</code>'
    await message.reply(text, quote=True, disable_web_page_preview=True)
