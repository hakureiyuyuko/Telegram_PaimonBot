from pyrogram import Client
from pyrogram.types import Message
from defs.artifacts import get_artifacts


async def artifacts_msg(client: Client, message: Message):
    name = message.text.replace('圣遗物详情', '').strip()
    text, url = await get_artifacts(name)
    if url:
        await message.reply_photo(photo=url, caption=text, quote=True)
    else:
        await message.reply(text, quote=True)
