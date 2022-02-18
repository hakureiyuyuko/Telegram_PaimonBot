from ci import admin_id
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

HELP_MSG_PRE = '<a href="https://git.io/JcbTD">PaimonBot</a> 0.3.8beta By Xtao-Labs\n\n' \
               '🔅 以下是小派蒙我学会了的功能（部分）：\n'
HELP_MSG = """① [武器/今日武器] 查看今日武器材料和武器
② [天赋/今日天赋] 查看今日天赋材料和角色
③ [周本] 查看周本材料和人物
④ [运势 (名字)] 查看今日运势
   💠 <code>运势 (重云)</code>
   💠 <code>设置运势 (重云)</code>
⑤ [角色查询 名字] 查看人物简介
   💠 <code>角色查询 重云</code>
⑥ [命座 名字] 查看人物命座
   💠 <code>命座 重云一命</code>
⑦ [武器查询 武器名] 查看武器资料
   💠 <code>武器查询 沐浴龙血的剑</code>
⑧ [原魔查询 原魔名] 查看原魔资料
   💠 <code>原魔查询 丘丘人</code>
⑨ [食物查询 食物/食材名] 查看食物资料
   💠 <code>食物查询 甜甜花/甜甜花酿鸡</code>
⑩ [圣遗物查询 圣遗物套装名] 查看圣遗物套装资料
   💠 <code>圣遗物查询 逆飞的流星</code>
======
(11) [抽卡] 抽卡
   💠 <code>抽卡</code>
   💠 <code>抽卡 2</code>
   💠 <code>抽卡 武器</code>
   💠 <code>抽卡 常驻</code>
(12) [原神黄历] 查看随机生成的原神黄历
(13) [活动列表] 查看今日活动列表和祈愿列表
(14) [圣遗物评分] 我也想拥有这种分数的圣遗物(切实)
(15) [哪里有 (资源名)] 查看资源的位置
(16) [资源列表] 查看原神所有资源（私聊）
(17) [猜语音] 和群友一起玩猜语音小游戏吧！（群聊）
   💠 <code>猜语音</code>
   💠 <code>猜语音 无尽模式</code>
(18) [米游社/hoyolab] 米游社/hoyolab相关功能
   💠 <a href="https://telegra.ph/PaimonBot-02-18">点击查看</a>"""


async def welcome_command(client: Client, message: Message):
    # 发送欢迎消息
    await message.reply('你好！我是原神小助手 - 派蒙 。', quote=True)


async def ping_command(client: Client, message: Message):
    # 提醒在线状态
    await message.reply("poi~", quote=True)


async def leave_command(client: Client, message: Message):
    # 退出群组
    chat_id = message.text.split()[-1]
    # 权限检查
    if message.from_user.id == admin_id:
        return
    try:
        await client.leave_chat(chat_id)
        await message.reply('成功执行退出群组命令。')
    except Exception as e:
        await message.reply(f'错误：\n{e}')


async def help_command(client: Client, message: Message):
    text = HELP_MSG_PRE + HELP_MSG.split("\n======\n")[0]
    await message.reply(text, quote=True, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("下一页", callback_data="help_1")],
        ]))


async def help_callback(client: Client, query: CallbackQuery):
    data = query.data.replace("help_", "")
    try:
        data = int(data)
    except ValueError:
        data = 1
    text = HELP_MSG_PRE + HELP_MSG.split("\n======\n")[data]
    await query.message.edit(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("上一页" if data else "下一页",
                                  callback_data="help_0" if data else "help_1")],
        ]))
