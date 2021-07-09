from pyrogram import Client
from pyrogram.types import Message
from defs.almanac import get_almanac_image
from defs.redis_load import redis


async def almanac_msg(client: Client, message: Message):
    # 生成黄历
    text = '旅行者你好，这是提瓦特大陆今日份的黄历。'
    path = get_almanac_image()
    if path == '':
        await message.reply('派蒙与提瓦特大陆的连接遇到了一点问题：<code>数据库离线</code>', quote=True)
        return
    if 'almanac.png' in path:
        # 开始上传
        msg = await message.reply_photo(photo=path, caption=text, quote=True)
        # 缓存 file_id
        redis.set('almanac_file_id', msg.photo.file_id)
    else:
        await message.reply_photo(photo=path, caption=text, quote=True)
