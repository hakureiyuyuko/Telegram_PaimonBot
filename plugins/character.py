from pyrogram import Client
from pyrogram.types import Message
from defs.character import get_character, get_mz


async def character_msg(client: Client, message: Message):
    name = message.text.replace('角色资料', '').replace('角色简介', '').replace('角色查询', '').strip()
    text, url = await get_character(name)
    if url:
        await message.reply_photo(photo=url, caption=text, quote=True)
    else:
        await message.reply(text, quote=True)


async def mz_msg(client: Client, message: Message):
    name = message.text.replace('命座', '')
    text = await get_mz(name)
    await message.reply(text, quote=True)
