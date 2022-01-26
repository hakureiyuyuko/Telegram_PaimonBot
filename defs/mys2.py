import math
import sqlite3

from defs.db import GetAward, MysSign, GetSignInfo, GetSignList, GetDaily

avatar_json = {
    "Albedo": "阿贝多",
    "Ambor": "安柏",
    "Barbara": "芭芭拉",
    "Beidou": "北斗",
    "Bennett": "班尼特",
    "Chongyun": "重云",
    "Diluc": "迪卢克",
    "Diona": "迪奥娜",
    "Eula": "优菈",
    "Fischl": "菲谢尔",
    "Ganyu": "甘雨",
    "Hutao": "胡桃",
    "Jean": "琴",
    "Kazuha": "枫原万叶",
    "Kaeya": "凯亚",
    "Ayaka": "神里绫华",
    "Keqing": "刻晴",
    "Klee": "可莉",
    "Lisa": "丽莎",
    "Mona": "莫娜",
    "Ningguang": "凝光",
    "Noel": "诺艾尔",
    "Qiqi": "七七",
    "Razor": "雷泽",
    "Rosaria": "罗莎莉亚",
    "Sucrose": "砂糖",
    "Tartaglia": "达达利亚",
    "Venti": "温迪",
    "Xiangling": "香菱",
    "Xiao": "魈",
    "Xingqiu": "行秋",
    "Xinyan": "辛焱",
    "Yanfei": "烟绯",
    "Zhongli": "钟离",
    "Yoimiya": "宵宫",
    "Sayu": "早柚",
    "Shogun": "雷电将军",
    "Aloy": "埃洛伊",
    "Sara": "九条裟罗",
    "Kokomi": "珊瑚宫心海",
    "Shenhe": "申鹤"
}
daily_im = '''
*数据刷新可能存在一定延迟，请以当前游戏实际数据为准{}
==============
原粹树脂：{}/{}{}
每日委托：{}/{} 奖励{}领取
周本减半：{}/{}
洞天宝钱：{}
探索派遣：
总数/完成/上限：{}/{}/{}
{}'''
month_im = '''
==============
{}
UID：{}
==============
本日获取原石：{}
本日获取摩拉：{}
==============
昨日获取原石：{}
昨日获取摩拉：{}
==============
本月获取原石：{}
本月获取摩拉：{}
==============
上月获取原石：{}
上月获取摩拉：{}
==============
原石收入组成：
{}=============='''


async def award(uid):
    data = await GetAward(uid)
    nickname = data['data']['nickname']
    day_stone = data['data']['day_data']['current_primogems']
    day_mora = data['data']['day_data']['current_mora']
    lastday_stone = data['data']['day_data']['last_primogems']
    lastday_mora = data['data']['day_data']['last_mora']
    month_stone = data['data']['month_data']['current_primogems']
    month_mora = data['data']['month_data']['current_mora']
    lastmonth_stone = data['data']['month_data']['last_primogems']
    lastmonth_mora = data['data']['month_data']['last_mora']
    group_str = ''
    for i in data['data']['month_data']['group_by']:
        group_str = group_str + \
                    i['action'] + "：" + str(i['num']) + \
                    "（" + str(i['percent']) + "%）" + '\n'

    im = month_im.format(nickname, uid, day_stone, day_mora, lastday_stone, lastday_mora,
                         month_stone, month_mora, lastmonth_stone, lastmonth_mora, group_str)
    return im


# 签到函数
async def sign(uid):
    try:
        sign_data = await MysSign(uid)
        sign_info = await GetSignInfo(uid)
        sign_info = sign_info['data']
        sign_list = await GetSignList()
        status = sign_data['message']
        getitem = sign_list['data']['awards'][int(
            sign_info['total_sign_day']) - 1]['name']
        getnum = sign_list['data']['awards'][int(
            sign_info['total_sign_day']) - 1]['cnt']
        get_im = f"本次签到获得{getitem}x{getnum}"
        if status == "OK" and sign_info['is_sign']:
            mes_im = "签到成功"
        else:
            mes_im = status
        sign_missed = sign_info['sign_cnt_missed']
        im = mes_im + "!" + "\n" + get_im + "\n" + f"本月漏签次数：{sign_missed}"
    except:
        im = "签到失败，请检查Cookies是否失效。"
    return im


# 统计状态函数
async def daily(mode="push", uid=None):
    def seconds2hours(seconds: int) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    temp_list = []
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    if mode == "ask":
        c_data = ([uid, 0, 0, 0, 0, 0, 0],)
    else:
        cursor = c.execute(
            "SELECT *  FROM NewCookiesTable WHERE StatusA != ?", ("off",))
        c_data = cursor.fetchall()

    for row in c_data:
        raw_data = await GetDaily(str(row[0]))
        if raw_data["retcode"] != 0:
            temp_list.append(
                {"qid": row[2], "gid": row[3], "message": "你的推送状态有误；可能是uid绑定错误或没有在米游社打开“实时便筏”功能。"})
        else:
            dailydata = raw_data["data"]
            current_resin = dailydata['current_resin']

            current_expedition_num = dailydata['current_expedition_num']
            max_expedition_num = dailydata['max_expedition_num']
            finished_expedition_num = 0
            expedition_info: list[str] = []
            for expedition in dailydata['expeditions']:
                avatar: str = expedition['avatar_side_icon'][89:-4]
                try:
                    avatar_name: str = avatar_json[avatar]
                except KeyError:
                    avatar_name: str = avatar

                if expedition['status'] == 'Finished':
                    expedition_info.append(f"{avatar_name} 探索完成")
                    finished_expedition_num += 1
                else:
                    remained_timed: str = seconds2hours(
                        expedition['remained_time'])
                    expedition_info.append(
                        f"{avatar_name} 剩余时间{remained_timed}")

            if current_resin >= row[6] or dailydata["max_home_coin"] - dailydata[
                "current_home_coin"] <= 100 or finished_expedition_num > 0:
                tip = ''

                if current_resin >= row[6] != 0:
                    tip += "\n==============\n你的树脂快满了！"
                if dailydata["max_home_coin"] - dailydata["current_home_coin"] <= 100:
                    tip += "\n==============\n你的洞天宝钱快满了！"
                if finished_expedition_num > 0:
                    tip += "\n==============\n你有探索派遣完成了！"
                max_resin = dailydata['max_resin']
                rec_time = ''
                # print(dailydata)
                if current_resin < 160:
                    resin_recovery_time = seconds2hours(
                        dailydata['resin_recovery_time'])
                    next_resin_rec_time = seconds2hours(
                        8 * 60 - ((dailydata['max_resin'] - dailydata['current_resin']) * 8 * 60 - int(
                            dailydata['resin_recovery_time'])))
                    rec_time = f' ({next_resin_rec_time}/{resin_recovery_time})'

                finished_task_num = dailydata['finished_task_num']
                total_task_num = dailydata['total_task_num']
                is_extra_got = '已' if dailydata['is_extra_task_reward_received'] else '未'

                resin_discount_num_limit = dailydata['resin_discount_num_limit']
                used_resin_discount_num = resin_discount_num_limit - \
                                          dailydata['remain_resin_discount_num']

                coin = f'{dailydata["current_home_coin"]}/{dailydata["max_home_coin"]}'
                if dailydata["current_home_coin"] < dailydata["max_home_coin"]:
                    coin_rec_time = seconds2hours(int(dailydata["home_coin_recovery_time"]))
                    coin_add_speed = math.ceil((dailydata["max_home_coin"] - dailydata["current_home_coin"]) / (
                            int(dailydata["home_coin_recovery_time"]) / 60 / 60))
                    coin += f'（{coin_rec_time} 约{coin_add_speed}/h）'

                expedition_data = "\n".join(expedition_info)
                send_mes = daily_im.format(tip, current_resin, max_resin, rec_time, finished_task_num, total_task_num,
                                           is_extra_got, used_resin_discount_num,
                                           resin_discount_num_limit, coin, current_expedition_num,
                                           finished_expedition_num, max_expedition_num, expedition_data)

                temp_list.append(
                    {"qid": row[2], "gid": row[3], "message": send_mes})
    return temp_list
