from pyrogram import Client
from pyrogram.types import Message

from ci import guess_time
from defs.guess_voice import Guess


async def guess_voice(client: Client, message: Message):
    text = message.text.replace("猜语音", "")
    guess = Guess(message.chat.id, time=guess_time)
    if text == "排行榜":
        return await message.reply(await guess.get_rank(client, message))
    if text == "停止":
        if guess.is_start():
            return await guess.end_game(True)
    if guess.is_start():
        return await message.reply('游戏正在进行中哦')
    guess.set_start()
    if text == "无尽模式":
        guess.set_forever()
        await message.reply(f'即将发送一段原神语音，将在 <b>{guess_time}秒</b> 后公布答案。\n'
                            f'目前处于<b>无尽模式</code>，游戏将只能通过 <code>猜语音停止</code> 来结束。')
    else:
        await message.reply(f'即将发送一段原神语音，将在 <b>{guess_time}秒</b> 后公布答案')
    try:
        await guess.start()
    except Exception as e:
        guess.set_end()
        await message.reply("出现未知错误,请联系管理员")


async def process_guess(client: Client, message: Message):
    msg = message.text
    guess = Guess(message.chat.id, time=guess_time)
    if guess.is_start():
        await guess.add_answer(message.from_user.id, msg)
