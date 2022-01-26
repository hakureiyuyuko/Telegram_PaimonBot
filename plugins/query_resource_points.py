from pyrogram import Client
from pyrogram.errors import PhotoInvalidDimensions
from pyrogram.types import Message
from os import sep
from defs.query_resource_points import get_resource_map_mes, get_resource_list_mes, init_point_list_and_map

init_resource_map = False


async def inquire_resource_points(client: Client, message: Message):
    global init_resource_map
    if not init_resource_map:
        await init_point_list_and_map()
        init_resource_map = True
    resource_name = message.text.replace("哪里有", "").strip()
    if resource_name == "":
        return await message.reply("没有想好要找的资源吗？试试 `资源列表`", quote=True)
    text = await get_resource_map_mes(resource_name)
    if text.find("没有") != -1:
        return await message.reply(text, quote=True)
    try:
        await message.reply_photo(f"temp{sep}map.jpg", caption=text, quote=True)
    except PhotoInvalidDimensions:
        await message.reply_document(f"temp{sep}map.jpg", caption=text, quote=True)


async def inquire_resource_list(client: Client, message: Message):
    global init_resource_map
    if not init_resource_map:
        await init_point_list_and_map()
        init_resource_map = True
    text = get_resource_list_mes()
    await message.reply(text, quote=True)
