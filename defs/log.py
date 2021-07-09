from configparser import RawConfigParser
from os import getcwd, sep
from pyrogram import Client
from pyrogram.types import Message


config = RawConfigParser()
config.read(f"{getcwd()}{sep}config.ini")
channel_id: int = 0
channel_id = config.get("basic", "channel_id", fallback=channel_id)


async def log(client: Client, message: Message, mode):
    if not channel_id == 0:
        chat = message.chat
        cid = chat.id
        uid = message.from_user.id
        if chat.type == 'private':
            cname = chat.first_name
        else:
            cname = chat.title
        if chat.username:
            cname = f'<a href="https://t.me/{chat.username}">{cname}</a>'
        else:
            cname = f'<code>{cname}</code>'
        if mode == '邀请入群':
            text = '#Paimon #join \n'
        else:
            text = '#Paimon #message \n'
        text += f'群组 ID：<code>{cid}</code>\n' \
                f'群组名称：{cname}\n' \
                f'用户 ID：<code>{uid}</code>\n' \
                f'执行操作：<code>{mode}</code>'
        await client.send_message(channel_id, text, disable_notification=True, disable_web_page_preview=True)
