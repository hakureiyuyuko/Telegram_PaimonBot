import os
import random
import datetime
import json
import traceback
from os.path import exists

from apscheduler.triggers.date import DateTrigger
from pyrogram import Client
from pyrogram.types import Message
from sqlitedict import SqliteDict

from ci import scheduler, app

data_path = os.path.join("assets", "voice")


def init_db(db_dir, db_name) -> SqliteDict:
    return SqliteDict(os.path.join(db_dir, db_name),
                      encode=json.dumps,
                      decode=json.loads,
                      autocommit=True)


def get_chars(data: list) -> list:
    data_ = []
    for i in data:
        char_name = i.split(" ")[0]
        if char_name not in data_:
            data_.append(i.split(" ")[0])
    return data_


def get_key_list(data: list, key: str) -> list:
    # 获取包含key的数据
    data_ = []
    for i in data:
        if key in i:
            data_.append(i)
    return data_


def choice_voice(data: list) -> str:
    long_key = ['感兴趣的见闻', '关于神之眼', '生日', '爱好', '讨厌的食物', '想要了解', '有什么想要分享',
                '突破的感觉', '喜欢的食物', '烦恼', '角色待机', '角色死亡']
    data_ = []
    for i in data:
        for k in long_key:
            if k in i:
                data_.append(i)
    if not data_:
        return ""
    return random.choice(data_)


user_db = init_db('temp', 'guess_voice.sqlite')
process = {}


with open(os.path.join(data_path, 'character.json'), 'r', encoding="utf-8") as f:
    character_json: dict = json.loads(f.read())


def char_name_by_name(name):
    names = character_json.keys()
    # 是否就是正确的名字
    if name in names:
        return name
    #
    for item in names:
        nickname = character_json[item]
        if name in nickname:
            return item
    return name


class Guess:
    time: int
    group_id: int
    group = {}
    retry_count = 0

    def __init__(self, group_id: int, time=30):
        self.time = time
        self.group_id = group_id
        self.group = process.get(self.group_id)

    def is_start(self):
        if not self.group:
            return False
        return self.group['start']

    def set_start(self):
        process[self.group_id] = {'start': True}

    def set_end(self):
        process[self.group_id] = {}

    async def start(self):
        if exists(f"assets{os.sep}voice{os.sep}voice.json"):
            with open(f"assets{os.sep}voice{os.sep}voice.json", "r", encoding='utf-8') as f:
                mys_list_raw = json.load(f)
        else:
            return "没有找到声音数据"
        mys_list = list(mys_list_raw.keys())
        if not mys_list:
            return "没有找到声音数据"
        chars = get_chars(mys_list)
        answer = random.choice(chars)
        file_id = get_key_list(mys_list, answer)
        file_id = choice_voice(file_id)
        if not file_id:
            return "没有找到声音数据"

        # 记录答案
        process[self.group_id] = {
            'start': True,
            'answer': answer,
            'ok': set()
        }

        job_id = str(self.group_id) + '_guess_voice'
        if scheduler.get_job(job_id, 'default'):
            scheduler.remove_job(job_id, 'default')

        now = datetime.datetime.now()
        notify_time = now + datetime.timedelta(seconds=self.time)
        scheduler.add_job(self.end_game, trigger=DateTrigger(notify_time),
                          id=job_id,
                          misfire_grace_time=60,
                          coalesce=True,
                          jobstore='default',
                          max_instances=1)

        print('答案: ' + answer)
        return mys_list_raw[file_id]

    async def end_game(self):
        self.group = process.get(self.group_id)

        ok_list = list(process[self.group_id]['ok'])
        if len(ok_list) > 1:  # 只允许1个人猜对
            return
        if not ok_list:
            msg = '还没有人猜中呢'
        else:
            msg = '回答正确的人: ' + ' '.join([f"[{qq}](tg://user?id={qq})" for qq in ok_list])
        msg = '正确答案是 %s\n%s' % (self.group['answer'], msg)
        try:
            await app.send_message(self.group_id, msg)
        except Exception as e:
            traceback.print_exc()

        # 清理记录
        process[self.group_id] = {}

        # 记录到数据库给之后奖励做处理
        user_group = user_db.get(self.group_id, {})
        if not user_group:
            user_db[self.group_id] = {}

        for user in ok_list:
            info = user_group.get(str(user), {'count': 0})
            info['count'] += 1
            user_group[user] = info
        user_db[self.group_id] = user_group

    # 只添加正确的答案
    async def add_answer(self, qq: int, msg: str):
        if self.group.get('answer') and char_name_by_name(msg) == self.group['answer']:
            process[self.group_id]['ok'].add(qq)
            job_id = str(self.group_id)
            if scheduler.get_job(job_id + '_guess_voice', 'default'):
                scheduler.remove_job(job_id + '_guess_voice', 'default')
            await self.end_game()

    # 获取排行榜
    async def get_rank(self, client: Client, message: Message):
        user_list = user_db.get(self.group_id, {})

        user_list = sorted(user_list.items(), key=lambda v: v[1]['count'])
        user_list.reverse()
        num = 0
        msg = '本群猜语音排行榜：'
        for user, data in user_list[:10]:
            try:
                user = (await client.get_users(int(user))).first_name
            except:
                user = str(user)
            num += 1
            msg += f"\n第{num}名: {user}, 猜对{data['count']}次"
        return msg
