from pyrogram import Client
from pyrogram.types import Message
from configparser import RawConfigParser
from os import getcwd, sep
from defs.mys import draw_pic
from defs.redis_load import redis, redis_status


async def mys_msg(client: Client, message: Message):
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
    # 生成用户信息
    uid = message.text.replace('账号信息', '').replace('用户信息', '').strip()
    try:
        path = await draw_pic(uid)
    except ConnectionRefusedError:
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>ConnectionRefusedError</code>', quote=True)
        return
    except ConnectionError:
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>ConnectionError</code>', quote=True)
        return
    if path:
        # 上传图片
        await message.reply_photo(photo=path, quote=True)
    else:
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>ConnectionError</code>', quote=True)


async def promote_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply('你需要回复一个用户才能授权 Ta 管理员权限。', quote=True)
        return
    uid = str(message.reply_to_message.from_user.id)
    if redis_status():
        # 读取数据
        admin = redis.get('mys').decode()
        if admin:
            admins = admin.split('|')
        else:
            admins = []
        if len(message.text.split(' ')) >= 2:
            # 列出所有管理员
            if len(admins) > 0:
                await message.reply('管理员列表：\n{" ".join(admins)}', quote=True)
                return
            else:
                await message.reply('当前暂无管理员。', quote=True)
                return
        if uid in admins:
            admins.remove(uid)
            mode = False
        else:
            admins.append(uid)
            mode = True
        # 写入数据
        admin = '|'.join(admins)
        redis.set('mys', admin)
        text = f'移除管理员 {uid} 成功。'
        if mode:
            text = f'添加管理员 {uid} 成功。'
        await message.reply(text, quote=True)
        return
