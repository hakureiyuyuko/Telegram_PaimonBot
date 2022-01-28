import asyncio
import hashlib
import string
import time
import uuid
import requests
import random
# md5计算


def md5(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


# 随机文本
def random_text(num: int) -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, num))


# 时间戳
def timestamp() -> int:
    return int(time.time())


# 获取请求Header里的DS 当web为true则生成网页端的DS
def get_ds() -> str:
    n = "fd3ykrh7o1j54g581upo1tvpam0dsgtf"
    i = str(timestamp())
    r = random_text(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return f"{i},{r},{c}"


# 生成一个device id
def get_device_id(ck) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, ck)).replace(
        '-', '').upper()


class MihoyoBbs:
    def __init__(self, ck):
        if "login_ticket" not in ck:
            raise Exception("Cookie 缺失 login_ticket")
        if "stoken" not in ck:
            # 登录操作
            temp_Cookies = ck.split(";")
            for i in temp_Cookies:
                if i.split("=")[0] == "login_ticket":
                    self.mihoyobbs_Login_ticket = i.split("=")[1]
                if i.split("=")[0] == "account_id":
                    self.mihoyobbs_Stuid = i.split("=")[1]
            # 直接拿cookie里面的Uid
            data = requests.get(url="https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket"
                                    "?login_ticket={}&token_types=3&"
                                    "uid={}".format(self.mihoyobbs_Login_ticket, self.mihoyobbs_Stuid)).json()
            try:
                self.mihoyobbs_Stoken = data["data"]["list"][0]["token"]
            except TypeError:
                raise Exception("Cookie 缺失 login_ticket")
        else:
            temp_Cookies = ck.split(";")
            for i in temp_Cookies:
                if i.split("=")[0] == "account_id":
                    self.mihoyobbs_Stuid = i.split("=")[1]
                if i.split("=")[0] == "stoken":
                    self.mihoyobbs_Stoken = i.split("=")[1]
        self.headers = {
            "DS": get_ds(),
            "cookie": f"stuid={self.mihoyobbs_Stuid};stoken={self.mihoyobbs_Stoken}",
            "x-rpc-client_type": "2",
            "x-rpc-app_version": "2.7.0",
            "x-rpc-sys_version": "6.0.1",
            "x-rpc-channel": "mihoyo",
            "x-rpc-device_id": get_device_id(ck),
            "x-rpc-device_name": random_text(random.randint(1, 10)),
            "x-rpc-device_model": "Mi 10",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com",
            "User-Agent": "okhttp/4.8.0"
        }
        self.Task_do = {
            "bbs_Sign": False,
            "bbs_Read_posts": False,
            "bbs_Read_posts_num": 3,
            "bbs_Like_posts": False,
            "bbs_Like_posts_num": 5,
            "bbs_Share": False
        }
        self.Today_getcoins = 0
        self.Today_have_getcoins = 0
        self.Have_coins = 0
        self.Get_taskslist()
        # 如果这三个任务都做了就没必要获取帖子了
        if self.Task_do["bbs_Read_posts"] and self.Task_do["bbs_Share"]:
            pass
        else:
            self.postsList = self.get_list()

    # 获取任务列表，用来判断做了哪些任务
    def Get_taskslist(self):
        # log.info("正在获取任务列表")
        req = requests.get(url="https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState", headers=self.headers)
        data = req.json()
        if "err" in data["message"] or data["retcode"] == -100:
            # log.error("获取任务列表失败，你的cookie可能已过期，请重新设置cookie。")
            raise Exception("获取任务列表失败，你的cookie可能已过期，请重新设置cookie。")
        else:
            self.Today_getcoins = data["data"]["can_get_points"]
            self.Today_have_getcoins = data["data"]["already_received_points"]
            self.Have_coins = data["data"]["total_points"]
            # 如果当日可获取米游币数量为0直接判断全部任务都完成了
            if self.Today_getcoins == 0:
                self.Task_do["bbs_Sign"] = True
                self.Task_do["bbs_Read_posts"] = True
                self.Task_do["bbs_Like_posts"] = True
                self.Task_do["bbs_Share"] = True
            else:
                # 如果第0个大于或等于62则直接判定任务没做
                if data["data"]["states"][0]["mission_id"] >= 62:
                    # log.info(f"新的一天，今天可以获得{Today_getcoins}个米游币")
                    pass
                else:
                    # log.info(f"似乎还有任务没完成，今天还能获得{Today_getcoins}")
                    for i in data["data"]["states"]:
                        # # 58是讨论区签到
                        # if i["mission_id"] == 58:
                        #     if i["is_get_award"]:
                        #         self.Task_do["bbs_Sign"] = True
                        # 59是看帖子
                        if i["mission_id"] == 59:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Read_posts"] = True
                            else:
                                self.Task_do["bbs_Read_posts_num"] -= i["happened_times"]
                        # 60是给帖子点赞
                        # elif i["mission_id"] == 60:
                        #     if i["is_get_award"]:
                        #         self.Task_do["bbs_Like_posts"] = True
                        #     else:
                        #         self.Task_do["bbs_Like_posts_num"] -= i["happened_times"]
                        # 61是分享帖子
                        elif i["mission_id"] == 61:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Share"] = True
                                # 分享帖子，是最后一个任务，到这里了下面都是一次性任务，直接跳出循环
                                break

    # 获取帖子列表
    def get_list(self) -> list:
        temp_list = []
        # log.info("正在获取帖子列表......")
        req = requests.get(url="https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id="
                               "5&is_good=false&is_hot=false&page_size=20&sort_type=1", headers=self.headers)
        data = req.json()
        for n in range(5):
            temp_list.append([data["data"]["list"][n]["post"]["post_id"], data["data"]["list"][n]["post"]["subject"]])
        # log.info("已获取{}个帖子".format(len(temp_list)))
        return temp_list

    # 看帖子
    async def read_posts(self):
        if self.Task_do["bbs_Read_posts"]:
            pass
            # log.info("看帖任务已经完成过了~")
        else:
            # log.info("正在看帖......")
            for i in range(self.Task_do["bbs_Read_posts_num"]):
                req = requests.get(
                    url="https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}".format(self.postsList[i][0]),
                    headers=self.headers)
                data = req.json()
                if data["message"] == "OK":
                    pass
                    # log.debug("看帖：{} 成功".format(self.postsList[i][1]))
                await asyncio.sleep(random.randint(1, 2))

    # 分享操作
    async def share_post(self):
        if self.Task_do["bbs_Share"]:
            pass
            # log.info("分享任务已经完成过了~")
        else:
            # log.info("正在执行分享任务......")
            for i in range(3):
                req = requests.get(
                    url="https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1".format(
                        self.postsList[0][0]), headers=self.headers)
                data = req.json()
                if data["message"] == "OK":
                    # log.debug("分享：{} 成功".format(self.postsList[0][1]))
                    # log.info("分享任务执行成功......")
                    break
                else:
                    # log.debug(f"分享任务执行失败，正在执行第{i+2}次，共3次")
                    await asyncio.sleep(random.randint(1, 2))
