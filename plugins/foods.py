from pyrogram import Client
from pyrogram.types import Message
from defs.foods import get_foods


async def foods_msg(client: Client, message: Message):
    name = message.text.replace('食物查询', '').strip()
    text, url = await get_foods(name)
    if url:
        try:
            await message.reply_photo(photo=url, caption=text, quote=True)
        except:
            await message.reply(text, quote=True)
    else:
        await message.reply(text, quote=True)
