from pyrogram import Client
from pyrogram.types import Message
from defs.enemies import get_enemies


async def enemies_msg(client: Client, message: Message):
    name = message.text.replace('原魔查询', '').strip()
    text, url = await get_enemies(name)
    if url:
        try:
            await message.reply_photo(photo=url, caption=text, quote=True)
        except:
            await message.reply(text, quote=True)
    else:
        await message.reply(text, quote=True)
