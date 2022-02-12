import asyncio
import random
import re
import sqlite3
import traceback

from pyrogram import Client
from pyrogram.types import Message

from defs.db2 import deal_ck, selectDB, OpenPush, CheckDB, connectDB, deletecache
from defs.mihoyo import sign, daily, draw_pic, draw_wordcloud, award

from ci import scheduler, app, admin_id
from defs.redis_load import redis

SUPERUSERS = [admin_id]


async def mihoyo_msg(client: Client, message: Message):
    text = message.text.replace("mihoyo", "")
    userid = message.from_user.id
    if '添加' in text:
        try:
            mes = text.replace('添加', '').strip()
            if not mes:
                return await message.reply_text("获取 Cookie 请登录：https://account.mihoyo.com/#/login 后按F12运行\n<code>var cookie=document.cookie;var ask=confirm('Cookie:'+cookie+'\\n\\nDo you want to copy the cookie to the clipboard?');if(ask==true){copy(cookie);msg=cookie}else{msg='Cancel'}</code>\n然后点击OK即可", quote=True)
            await deal_ck(mes, userid)
            await message.reply(f'添加Cookies成功！\n'
                                f'Cookies属于个人重要信息，如果你是在不知情的情况下添加，'
                                f'请马上修改mihoyo账户密码，保护个人隐私！\n'
                                f'<code>=============</code>\n'
                                f'如果需要【开启自动签到】和【开启推送】还需要使用命令 '
                                f'<code>mihoyo绑定uid</code>绑定你的uid。\n'
                                f'例如：<code>mihoyo绑定uid123456789</code>。')
        except Exception as e:
            traceback.print_exc()
            await message.reply(f'校验失败！请输入正确的Cookies！获取 Cookie 请参考：'
                                f'[link](https://github.com/thesadru/'
                                f'genshinstats/tree/master#how-can-i-get-my-cookies)', quote=True)
    elif '推送' in text:
        try:
            uid = await selectDB(userid, mode="uid")
            if '开启' in text:
                im = await OpenPush(int(uid[0]), userid, "on", "StatusA")
                await message.reply(im, quote=True)
            else:
                im = await OpenPush(int(uid[0]), userid, "off", "StatusA")
                await message.reply(im, quote=True)
        except Exception as e:
            traceback.print_exc()
            await message.reply("未找到uid绑定记录。", quote=True)
    elif '自动签到' in text:
        try:
            uid = await selectDB(userid, mode="uid")
            if '开启' in text:
                im = await OpenPush(int(uid[0]), userid, "on", "StatusB")
                await message.reply(im, quote=True)
            else:
                im = await OpenPush(int(uid[0]), userid, "off", "StatusA")
                await message.reply(im, quote=True)
        except Exception as e:
            traceback.print_exc()
            await message.reply("未找到uid绑定记录。", quote=True)
    elif "每月统计" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            im = await award(uid)
            await message.reply(im, quote=True)
        except Exception as e:
            traceback.print_exc()
            await message.reply('未找到绑定信息', quote=True)
    elif "签到" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            im = await sign(uid)
            await message.reply(im, quote=True)
        except Exception as e:
            traceback.print_exc()
            await message.reply('未找到绑定信息', quote=True)
    elif "效验全部" in text:
        im = await CheckDB()
        await message.reply(im, quote=True)
    elif "当前状态" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            mes = await daily("ask", uid)
            im = mes[0]['message']
        except Exception as e:
            traceback.print_exc()
            im = "没有找到绑定信息。"
        await message.reply(im, quote=True)
    elif "绑定uid" in text:
        uid = text.replace("绑定uid", "")  # str
        await connectDB(message.from_user.id, uid)
        await message.reply('绑定uid成功！', quote=True)
    elif "绑定mys" in text:
        mys = text.replace("绑定mys", "")  # str
        await connectDB(message.from_user.id, None, mys)
        await message.reply('绑定米游社id成功！', quote=True)


async def mihoyo_qun_msg(client: Client, message: Message):
    text = message.text.replace("mihoyo", "")

    qid = message.from_user.id
    at = message.reply_to_message
    if "自动签到" in text:
        try:
            if at and qid in SUPERUSERS:
                qid = at.from_user.id
            elif at and qid not in SUPERUSERS:
                return await message.reply("你没有权限。")
            gid = message.chat.id
            uid = await selectDB(qid, mode="uid")
            if "开启" in text:
                im = await OpenPush(int(uid[0]), message.from_user.id, str(gid), "StatusB")
                await message.reply(im, quote=True)
            elif "关闭" in text:
                im = await OpenPush(int(uid[0]), message.from_user.id, "off", "StatusB")
                await message.reply(im)
        except Exception as e:
            traceback.print_exc()
            await message.reply("未绑定uid信息！")
    elif "推送" in text:
        try:
            if at and qid in SUPERUSERS:
                qid = at.from_user.id
            elif at and qid not in SUPERUSERS:
                return await message.reply("你没有权限。")
            gid = message.chat.id
            uid = await selectDB(qid, mode="uid")
            if "开启" in text:
                im = await OpenPush(int(uid[0]), message.from_user.id, str(gid), "StatusA")
                await message.reply(im, quote=True)
            elif "关闭" in text:
                im = await OpenPush(int(uid[0]), message.from_user.id, "off", "StatusA")
                await message.reply(im)
        except Exception as e:
            traceback.print_exc()
            await message.reply("未绑定uid信息！")
    elif "每月统计" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            im = await award(uid)
            await message.reply(im)
        except Exception as e:
            traceback.print_exc()
            await message.reply('未找到绑定信息')
    elif "签到" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            im = await sign(uid)
            await message.reply(im)
        except Exception as e:
            traceback.print_exc()
            await message.reply('未找到绑定信息')
    elif "效验全部" in text:
        im = await CheckDB()
        await message.reply(im)
    elif "当前状态" in text:
        try:
            uid = await selectDB(message.from_user.id, mode="uid")
            uid = uid[0]
            mes = await daily("ask", uid)
            im = mes[0]['message']
        except Exception as e:
            traceback.print_exc()
            im = "没有找到绑定信息。"
        await message.reply(im)
    elif "绑定uid" in text:
        uid = text.replace("绑定uid", "")  # str
        await connectDB(message.from_user.id, uid)
        await message.reply('绑定uid成功！')
    elif "绑定mys" in text:
        mys = text.replace("绑定mys", "")  # str
        await connectDB(message.from_user.id, None, mys)
        await message.reply('绑定米游社id成功！')
    elif "查询" in text:
        try:
            at = message.reply_to_message
            if at:
                qid = at.from_user.id
                nickname = at.from_user.first_name
                uid = await selectDB(qid)
            else:
                nickname = message.from_user.first_name
                uid = await selectDB(message.from_user.id)
            nickname = nickname if len(nickname) < 10 else (nickname[:10] + "...")
            if uid:
                if "词云" in text:
                    try:
                        im = await draw_wordcloud(uid[0], message, uid[1])
                        if im.find(".jpg") != -1:
                            await message.reply_photo(im)
                        else:
                            await message.reply(im)
                    except Exception as e:
                        await message.reply("获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。".format(e))
                        traceback.print_exc()
                else:
                    try:
                        bg = await draw_pic(uid[0], message, nickname=nickname, mode=uid[1])
                        if bg.find(".") != -1:
                            await message.reply_photo(bg)
                        else:
                            await message.reply(bg)
                    except Exception as e:
                        await message.reply("获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。".format(e))
                        traceback.print_exc()
            else:
                await message.reply('未找到绑定记录！')
        except Exception as e:
            traceback.print_exc()
            await message.reply("发生错误 {},请检查后台输出。".format(e))
    elif "mys" in text:
        try:
            try:
                uid = re.findall(r"\d+", text)[0]  # str
            except IndexError:
                return await message.reply("米游社 id 格式错误！")
            nickname = message.from_user.first_name
            nickname = nickname if len(nickname) < 10 else (nickname[:10] + "...")
            try:
                im = await draw_pic(uid, message, nickname=nickname, mode=3)
                if im.find(".") != -1:
                    await message.reply_photo(im)
                else:
                    await message.reply(im)
            except Exception as e:
                await message.reply("获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。".format(e))
                traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
            await message.reply("发生错误 {},请检查后台输出。".format(e))
    elif "全部重签" in text and message.from_user.id in SUPERUSERS:
        try:
            await message.reply("已开始执行")
            await daily_sign_2()
        except Exception as e:
            traceback.print_exc()
            await message.reply("发生错误 {},请检查后台输出。".format(e))


# 每隔一小时检测树脂是否超过设定值
@scheduler.scheduled_job('interval', hours=1)
async def push_2():
    daily_data = await daily()
    if daily_data is not None:
        for i in daily_data:
            # 过滤重复推送
            data = i['message'].split('==============')
            if len(data) > 2:
                text = "".join(data[1:-1])
                data = redis.get("daily_" + str(i['qid']))
                if data:
                    if text == data.decode():
                        continue
                redis.set("daily_" + str(i['qid']), text)

            if i['gid'] == "on":
                await app.send_message(int(i['qid']), i['message'])
            else:
                await app.send_message(int(i['gid']), f"[NOTICE {i['qid']}](tg://user?id={i['qid']})" + "\n" +
                                       i['message'])
    else:
        pass


# 每日零点半进行 mihoyo 签到
@scheduler.scheduled_job('cron', hour='0', minute="30")
async def daily_sign_2():
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    cursor = c.execute(
        "SELECT *  FROM NewCookiesTable WHERE StatusB != ?", ("off",))
    c_data = cursor.fetchall()
    temp_list = []

    for row in c_data:
        if row[4] == "on":
            try:
                im = await sign(str(row[0]))
                await app.send_message(int(row[2]), im)
            except Exception as e:
                traceback.print_exc()
        else:
            im = await sign(str(row[0]))
            message = f"[NOTICE {row[2]}](tg://user?id={row[2]})\n\n{im}"
            for i in temp_list:
                if row[4] == i["push_group"]:
                    i["push_message"] = i["push_message"] + "\n" + message
                    break
            else:
                temp_list.append({"push_group": row[4], "push_message": message})
        await asyncio.sleep(6 + random.randint(0, 2))

    for i in temp_list:
        try:
            await app.send_message(int(i["push_group"]), i["push_message"])
        except Exception as e:
            traceback.print_exc()
        await asyncio.sleep(3 + random.randint(0, 2))


# 每日零点清空cookies使用缓存
@scheduler.scheduled_job('cron', hour='0')
async def delete_2():
    deletecache()
