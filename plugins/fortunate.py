from pyrogram import Client
from pyrogram.types import Message
from defs.fortunate import get_character, get_fortunate_image
from defs.redis_load import redis_status, redis


async def fortunate_msg(client: Client, message: Message):
    # 生成运势
    uid = message.from_user.id
    name = message.text.replace('今日运势', '').replace('运势', '').strip()
    if name == '':
        if redis_status():
            try:
                name = redis.get(f'f_{uid}_name').decode()
            except AttributeError:
                name = 'random'
        else:
            name = 'random'
    else:
        name, temp = get_character(name)
        if not temp:
            await message.reply(name, quote=True)
            return
    path = get_fortunate_image(message.from_user.id, name)
    if path == '':
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>数据库离线</code>', quote=True)
        return
    if 'fortune.png' in path:
        # 开始上传
        await message.reply_photo(photo=path, quote=True)


async def set_fortunate_img(client: Client, message: Message):
    # 设置默认运势图
    uid = message.from_user.id
    name = message.text.replace('设置运势', '').strip()
    if not redis_status():
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>数据库离线</code>', quote=True)
        return
    if name == '':
        name = 'random'
    else:
        name, temp = get_character(name)
        if not temp:
            await message.reply(name, quote=True)
            return
    redis.set(f'f_{uid}_name', name)
    if name == 'random':
        name = '随机'
    await message.reply(f'设置成功，默认运势角色已设置为：<code>{name}</code>')
