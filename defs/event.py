import time
import datetime
import os
from requests import get
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from defs.redis_load import redis_status, redis


def ys_font(size):
    return ImageFont.truetype(f"assets{os.sep}fonts{os.sep}ZhuZiAWan-2.ttc", size=size)


def generate_event():
    # 生成图片到 temp 文件夹
    TEXT_PATH = f"assets{os.sep}event"
    raw_data = get(
        "https://hk4e-api.mihoyo.com/common/hk4e_cn/announcement/api/getAnnList?game=hk4e&game_biz=hk4e_cn&lang=zh-cn"
        "&bundle_id=hk4e_cn&platform=pc&region=cn_gf01&level=55&uid=100000000").json()
    now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    raw_time_data = get(
        "https://api-takumi.mihoyo.com/event/bbs_activity_calendar/getActList?"
        "time={}&game_biz=ys_cn&page=1&tag_id=0".format(now_time)).json()

    data = raw_data["data"]["list"][1]["list"]

    event_data = {"gacha_event": [], "normal_event": [], "other_event": []}
    for k in data:
        for i in raw_time_data["data"]["act_list"]:
            if i["name"] == k["title"]:
                k["act_begin_time"] = i["act_begin_time"]
                k["act_end_time"] = i["act_end_time"]
            elif "神铸赋形" in k["title"] and "神铸赋形" in i["name"]:
                k["act_begin_time"] = i["act_begin_time"]
                k["act_end_time"] = i["act_end_time"]
            elif "传说任务" in k["title"]:
                k["act_begin_time"] = k["start_time"]
                k["act_end_time"] = "永久开放"
            elif k["subtitle"] in i["name"]:
                k["act_begin_time"] = i["act_begin_time"]
                k["act_end_time"] = i["act_end_time"]
            else:
                k["act_begin_time"] = "{}-{}-{} {}".format(k["start_time"].split()[0].split("-")[0],
                                                           k["start_time"].split()[0].split("-")[1],
                                                           str(int(k["start_time"].split()[0].split("-")[2]) + 2),
                                                           "10:00:00(?)")
                k["act_end_time"] = k["end_time"]

        if "冒险助力礼包" in k["title"] or "纪行" in k["title"]:
            continue
        # if "角色试用" in k["title"] or "传说任务" in k["title"]:
        #    event_data['other_event'].append(k)
        elif k["tag_label"] == "扭蛋":
            event_data['gacha_event'].append(k)
        elif k["tag_label"] == "活动":
            event_data['normal_event'].append(k)

    # base_h = 900 + ((1 + (len(event_data['normal_event'])+len(event_data['other_event'])))//2)*390 +
    # ((1 + len(event_data['gacha_event']))//2)*533
    base_h = 600 + len(event_data['normal_event']) * (390 + 90) + len(event_data['gacha_event']) * (533 + 90)
    base_img = Image.new(mode="RGB", size=(1080, base_h), color=(237, 217, 195))

    event1_path = os.path.join(TEXT_PATH, "event_1.png")
    event2_path = os.path.join(TEXT_PATH, "event_2.png")
    # event3_path = os.path.join(TEXT_PATH,"event_3.png")
    event1 = Image.open(event1_path)
    event2 = Image.open(event2_path)
    # event3 = Image.open(event3_path)

    base_img.paste(event1, (0, 0), event1)
    # base_img.paste(event2,(0,300+((1+len(event_data['normal_event']))//2)*390),event2)
    base_img.paste(event2, (0, len(event_data['normal_event']) * (390 + 90) + 300), event2)
    # base_img.paste(event3,(0,600+((1+len(event_data['normal_event']))//2)*390 + ((1 +
    # len(event_data['gacha_event']))//2)*533),event3)

    time_img1 = Image.new(mode="RGB", size=(1080, len(event_data['normal_event']) * (390 + 90)),
                          color=(237, 130, 116))
    time_img2 = Image.new(mode="RGB", size=(1080, len(event_data['gacha_event']) * (533 + 90)),
                          color=(237, 130, 116))
    base_img.paste(time_img1, (0, 300))
    base_img.paste(time_img2, (0, 600 + len(event_data['normal_event']) * (390 + 90)))
    base_draw = ImageDraw.Draw(base_img)
    for index, value in enumerate(event_data['normal_event']):
        img = Image.open(BytesIO(get(value["banner"]).content))
        base_draw.text((540, 300 + 45 + 390 + (390 + 90) * index + 1),
                       value["act_begin_time"] + " —— " + value["act_end_time"], (255, 255, 255), ys_font(42),
                       anchor="mm")
        # base_img.paste(img,((index%2)*1080,300 + 390*(index//2)))
        base_img.paste(img, (0, 300 + (390 + 90) * index))

    for index, value in enumerate(event_data['gacha_event']):
        img = Image.open(BytesIO(get(value["banner"]).content))
        base_draw.text((540, 600 + 45 + (390 + 90) * len(event_data['normal_event']) + 533 + index * (533 + 90)),
                       value["act_begin_time"] + " —— " + value["act_end_time"], (255, 255, 255), ys_font(42),
                       anchor="mm")
        # base_img.paste(img,((index%2)*1080,600 + ((1 + len(event_data['normal_event']))//2)*390 +
        # 533*(index//2)))
        base_img.paste(img, (0, 600 + (390 + 90) * len(event_data['normal_event']) + index * (533 + 90)))
    # for index,value in enumerate(event_data['other_event']):
    #    img = Image.open(BytesIO(get(value["banner"]).content))
    #    base_img.paste(img,((index%2)*1080,900 + ((1 + len(event_data['normal_event']))//2)*390 +
    #    ((1 + len(event_data['gacha_event']))//2)*533 + 390*(index//2)))

    base_img = base_img.convert('RGB')
    base_img.save(f'temp{os.sep}event.jpg', format='JPEG', subsampling=0, quality=90)

    # 更新缓存的日程的更新日期
    if redis_status():
        redis.set('event', time.strftime("%Y-%m-%d"))


def get_event_image():
    # 判断是否需要重新生成事件，无 redis 每次生成。
    if redis_status():
        try:
            date = redis.get('event').decode()
        except AttributeError:
            date = None
        if not date == time.strftime("%Y-%m-%d"):
            generate_event()
            return f'temp{os.sep}event.jpg'
        else:
            return redis.get('event_file_id').decode()
    else:
        generate_event()
        return f'temp{os.sep}event.jpg'
