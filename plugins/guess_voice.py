from pyrogram import Client
from pyrogram.types import Message

from ci import guess_time
from defs.guess_voice import Guess


async def guess_voice(client: Client, message: Message):
    text = message.text.replace("原神猜语音", "")
    guess = Guess(message.chat.id, time=guess_time)
    if text == "排行榜":
        return await message.reply(await guess.get_rank(client, message))
    if guess.is_start():
        return await message.reply('游戏正在进行中哦')
    guess.set_start()
    await message.reply(f'即将发送一段原神语音,将在 <b>{guess_time}秒</b> 后公布答案')
    try:
        msg = await guess.start()
        if msg == "没有找到声音数据":
            await message.reply(msg)
        else:
            await client.send_voice(message.chat.id, msg)
    except Exception as e:
        guess.set_end()
        await message.reply("出现未知错误,请联系管理员")


async def process_guess(client: Client, message: Message):
    msg = message.text
    guess = Guess(message.chat.id, time=guess_time)
    if guess.is_start():
        await guess.add_answer(message.from_user.id, msg)
