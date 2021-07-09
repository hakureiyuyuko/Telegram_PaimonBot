from pyrogram import Client
from pyrogram.types import Message
from defs.weapons import get_weapon


async def weapon_msg(client: Client, message: Message):
    name = message.text.replace('武器查询', '').replace('武器资料', '').strip()
    text, url = await get_weapon(name)
    if url:
        await message.reply_photo(photo=url, caption=text, quote=True)
    else:
        await message.reply(text, quote=True)
