from pyrogram import Client
from pyrogram.types import Message
from os import getcwd, sep
from defs.challenge import get_day


async def tf_msg(client: Client, message: Message):
    day = get_day(message)
    if day == 7:
        await message.reply('亲爱的旅行者：星期天所有副本都可以刷哦！', quote=True)
    else:
        path = f'{getcwd()}{sep}assets{sep}images{sep}tf{day}.png'
        await message.reply_photo(photo=path, quote=True)


async def wq_msg(client: Client, message: Message):
    day = get_day(message)
    if day == 7:
        await message.reply('亲爱的旅行者：星期天所有副本都可以刷哦！', quote=True)
    else:
        path = f'{getcwd()}{sep}assets{sep}images{sep}we{day}.png'
        await message.reply_photo(photo=path, quote=True)


async def zb_msg(client: Client, message: Message):
    await message.reply_photo(photo=f'{getcwd()}{sep}assets{sep}images{sep}zb.png', quote=True)
