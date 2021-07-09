from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters as Filters
from plugins.start import welcome_command, ping_command, help_command, leave_command
from plugins.almanac import almanac_msg
from plugins.challenge import tf_msg, wq_msg, zb_msg
from plugins.character import character_msg, mz_msg
from plugins.weapons import weapon_msg
from plugins.mys import mys_msg, promote_command
from defs.log import log


@Client.on_message(Filters.text & Filters.private)
async def process_private_msg(client: Client, message: Message):
    msg_list = message.text.split(' ')
    # 欢迎消息
    if msg_list[0] == '/start':
        await welcome_command(client, message)
    # 帮助消息
    if msg_list[0] == '/help':
        await help_command(client, message)
    # 延迟测试
    if msg_list[0] == '/ping':
        await ping_command(client, message)
    if msg_list[0] == '/leave':
        await leave_command(client, message)
    # 黄历
    if '黄历' in message.text:
        await almanac_msg(client, message)
        await log(client, message, '查询原神黄历')
    # 授权管理员
    # if msg_list[0] == '/promote':
    #    await promote_command(client, message)
    # 天赋
    if '天赋' in message.text:
        await tf_msg(client, message)
        await log(client, message, '查询角色天赋')
    # 武器查询
    if '武器资料' in message.text or '武器查询' in message.text:
        await weapon_msg(client, message)
        await log(client, message, '查询武器资料')
        return
    # 副本武器
    if '武器' in message.text:
        await wq_msg(client, message)
        await log(client, message, '查询副本武器')
    # 周本
    if message.text == '周本':
        await zb_msg(client, message)
        await log(client, message, '查询周本')
    # 角色查询
    if '角色资料' in message.text or '角色简介' in message.text or '角色查询' in message.text:
        await character_msg(client, message)
        await log(client, message, '查询角色资料')
    # 命座查询
    if '命座' in message.text:
        await mz_msg(client, message)
        await log(client, message, '查询角色命座')
    # 账号信息（cookie 过期过快  不推荐启用）
    # if '账号信息' in message.text or '用户信息' in message.text:
    #    await mys_msg(client, message)


@Client.on_message(Filters.text & Filters.group)
async def process_group_msg(client: Client, message: Message):
    text = message.text
    msg_list = text.split(' ')
    # 帮助消息
    if msg_list[0] == '/help':
        await help_command(client, message)
    # 武器查询
    if text.startswith('武器查询') or text.startswith('武器资料'):
        await weapon_msg(client, message)
        await log(client, message, '查询武器资料')
        return
    # 副本武器
    if text[-2:] == '武器':
        await wq_msg(client, message)
        await log(client, message, '查询副本武器')
    # 黄历
    if message.text == '原神黄历':
        await almanac_msg(client, message)
        await log(client, message, '查询原神黄历')
    # 天赋
    if text[-2:] == '天赋':
        await tf_msg(client, message)
        await log(client, message, '查询角色天赋')
    # 周本
    if message.text == '周本':
        await zb_msg(client, message)
        await log(client, message, '查询周本')
    # 角色查询
    if text.startswith('角色资料') or text.startswith('角色简介') or text.startswith('角色查询'):
        await character_msg(client, message)
        await log(client, message, '查询角色资料')
    # 命座查询
    if text.startswith('命座'):
        await mz_msg(client, message)
        await log(client, message, '查询角色命座')


@Client.on_message(Filters.new_chat_members)
async def send_self_intro(client: Client, message: Message):
    # 发送欢迎消息
    await message.reply('感谢邀请小派蒙到本群！\n请使用 /help 查看咱已经学会的功能。', quote=True)
    await log(client, message, '邀请入群')
