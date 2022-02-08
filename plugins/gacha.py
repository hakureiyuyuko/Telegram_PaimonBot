import traceback
from datetime import timedelta
from asyncio import sleep

from pyrogram import Client
from pyrogram.types import Message
from defs.gacha.utils import filter_list, cache
from defs.gacha.gacha_info import gacha_info_list, gacha_info
from defs.gacha.wish import wish, gacha_type_by_name
from defs.gacha.wish_ui import wish_ui


async def gacha_msg(client: Client, message: Message):
    try:
        gacha_type, gacha_name, gacha_data = await handle_msg(client, message)
    except Exception as e:
        if str(e).find("不存在此卡池") != -1:
           return await message.reply(str(e))
        else:
            traceback.print_exc()
            return await message.reply("出现错误，请联系管理员")
    wish_info = await wish(message.from_user.id, gacha_type, gacha_data).ten()
    img = await wish_ui.ten_to_img(wish_info)
    msg = await message.reply_photo(img)
    await sleep(60)
    await msg.delete()


async def handle_msg(client: Client, message: Message):
    msg = message.text.replace("抽卡", "").strip() or '限定'
    if msg == '2':
        msg = '限定2'
    gacha_type = gacha_type_by_name(msg)
    if not gacha_type:
        raise Exception('不存在此卡池: %s' % msg)
    gacha_name, gacha_data = await gacha_pool(gacha_type=gacha_type)
    return gacha_type, gacha_name, gacha_data


@cache(ttl=timedelta(hours=24))
async def gacha_pool(gacha_type):
    data = await gacha_info_list()
    f = lambda x: x.gacha_type == gacha_type
    gacha_data = sorted(filter_list(data, f), key=lambda x: x.end_time)[-1]
    gacha_id = gacha_data.gacha_id
    gacha_name = gacha_data.gacha_name
    gacha_type = gacha_data.gacha_type
    gacha_data = await gacha_info(gacha_id)
    return gacha_name, gacha_data
