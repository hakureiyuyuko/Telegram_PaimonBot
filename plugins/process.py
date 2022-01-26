from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters as Filters
from plugins.start import welcome_command, ping_command, help_command, leave_command
from plugins.almanac import almanac_msg
from plugins.challenge import tf_msg, wq_msg, zb_msg
from plugins.character import character_msg, mz_msg
from plugins.event import event_msg
from plugins.weapons import weapon_msg
from plugins.fortunate import fortunate_msg, set_fortunate_img
from plugins.artifact_rate import artifact_rate_msg
from plugins.query_resource_points import inquire_resource_points, inquire_resource_list
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
    if '活动列表' in message.text:
        await event_msg(client, message)
        await log(client, message, '查询活动列表')
    # 授权管理员
    # if msg_list[0] == '/promote':
    #    await promote_command(client, message)
    # 天赋
    if '天赋' in message.text:
        await tf_msg(client, message)
        await log(client, message, '查询天赋副本')
    # # 武器查询
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
    # # 角色查询
    if '角色资料' in message.text or '角色简介' in message.text or '角色查询' in message.text:
        await character_msg(client, message)
        await log(client, message, '查询角色资料')
    # # 命座查询
    if '命座' in message.text:
        await mz_msg(client, message)
        await log(client, message, '查询角色命座')
    # 设置运势
    if '设置运势' in message.text:
        await set_fortunate_img(client, message)
        await log(client, message, '设置运势角色')
        return
    # 运势查询
    if '运势' in message.text:
        await fortunate_msg(client, message)
        await log(client, message, '查询今日运势')
    # 圣遗物评分
    if '圣遗物评分' in message.text:
        await message.reply("图呢？\n*请将命令与截图一起发送", quote=True)
    # 资源查询
    if '哪里有' in message.text:
        await inquire_resource_points(client, message)
        await log(client, message, '查询地图资源')
    # 资源列表
    if '资源列表' in message.text:
        await inquire_resource_list(client, message)
        await log(client, message, '查询资源列表')
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
    # # 武器查询
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
    if message.text == '活动列表':
        await event_msg(client, message)
        await log(client, message, '查询活动列表')
    # 天赋
    if text[-2:] == '天赋':
        await tf_msg(client, message)
        await log(client, message, '查询天赋副本')
    # 周本
    if message.text == '周本':
        await zb_msg(client, message)
        await log(client, message, '查询周本')
    # # 角色查询
    if text.startswith('角色资料') or text.startswith('角色简介') or text.startswith('角色查询'):
        await character_msg(client, message)
        await log(client, message, '查询角色资料')
    # # 命座查询
    if text.startswith('命座'):
        await mz_msg(client, message)
        await log(client, message, '查询角色命座')
    # 运势查询
    if text.startswith('运势') or text.startswith('今日运势'):
        await fortunate_msg(client, message)
        await log(client, message, '查询今日运势')
    # 设置运势
    if text.startswith('设置运势'):
        await set_fortunate_img(client, message)
        await log(client, message, '设置运势角色')
    # 圣遗物评分
    if text.startswith('圣遗物评分'):
        await message.reply("图呢？\n*请将命令与截图一起发送")
    # 资源查询
    if text.startswith('哪里有') or text.endswith('哪里有'):
        await inquire_resource_points(client, message)
        await log(client, message, '查询地图资源')
    # 资源列表
    if text.startswith('资源列表'):
        await inquire_resource_list(client, message)
        await log(client, message, '查询资源列表')


@Client.on_message(Filters.photo)
async def process_photo(client: Client, message: Message):
    text = message.caption if message.caption else ""

    if text.startswith('圣遗物评分'):
        await artifact_rate_msg(client, message)
        await log(client, message, '圣遗物评分')


@Client.on_message(Filters.new_chat_members)
async def send_self_intro(client: Client, message: Message):
    # 发送欢迎消息
    if message.new_chat_members[0].is_self:
        await message.reply('感谢邀请小派蒙到本群！\n请使用 /help 查看咱已经学会的功能。', quote=True)
        await log(client, message, '邀请入群')
