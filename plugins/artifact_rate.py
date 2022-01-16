import requests
from pyrogram import Client
from pyrogram.types import Message
from defs.artifact_rate import *
from base64 import b64encode
from os import remove


def get_format_sub_item(artifact_attr):
    msg = ""
    for i in artifact_attr["sub_item"]:
        msg += f'{i["name"]:\u3000<6} | {i["value"]}\n'
    return msg


async def artifact_rate_msg(client: Client, message: Message):
    if not message.photo:
        return await message.reply("图呢？\n*请命令将与截图一起发送", quote=True)
    msg = await message.reply("正在下载图片。。。", quote=True)
    path = await message.download()
    with open(path, "rb") as f:
        image_b64 = b64encode(f.read()).decode()
    remove(path)
    try:
        artifact_attr = await get_artifact_attr(image_b64)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return await msg.edit("连接超时")
    if 'err' in artifact_attr.keys():
        err_msg = artifact_attr["full"]["message"]
        return await msg.edit(f"发生了点小错误：\n{err_msg}")
    await msg.edit("识图成功！\n正在评分中...")
    rate_result = await rate_artifact(artifact_attr)
    if 'err' in rate_result.keys():
        err_msg = rate_result["full"]["message"]
        return await msg.edit(f"发生了点小错误：\n{err_msg}")
    format_result = f'圣遗物评分结果：\n' \
                    f'主属性：{artifact_attr["main_item"]["name"]}\n' \
                    f'{get_format_sub_item(artifact_attr)}'\
                    f'`------------------------------`\n' \
                    f'总分：{rate_result["total_percent"]}\n'\
                    f'主词条：{rate_result["main_percent"]}\n' \
                    f'副词条：{rate_result["sub_percent"]}\n' \
                    f'评分、识图均来自 genshin.pub'
    await msg.edit(format_result)
