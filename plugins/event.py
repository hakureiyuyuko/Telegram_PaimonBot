from pyrogram import Client
from pyrogram.types import Message
from defs.event import get_event_image
from defs.redis_load import redis


async def event_msg(client: Client, message: Message):
    # 活动列表
    text = '旅行者你好，这是提瓦特大陆今日份的活动列表。'
    path = get_event_image()
    if 'event.jpg' in path:
        # 开始上传
        msg = await message.reply_document(document=path, caption=text, quote=True)
        # 缓存 file_id
        redis.set('event_file_id', msg.document.file_id)
    else:
        await message.reply_document(document=path, caption=text, quote=True)
