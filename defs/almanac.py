import json, time, secrets
from os import getcwd, sep
from PIL import Image, ImageDraw, ImageFont
from defs.redis_load import redis, redis_status

working_dir = getcwd()
FONT_PATH = f'{working_dir}{sep}assets{sep}fonts{sep}ZhuZiAWan-2.ttc'
almanac_conf_data = {}
chinese = {"0": "", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}


def month_to_chinese(month: str):
    # 把日期数字转成中文数字
    m = int(month)
    if m < 10:
        return chinese[month[-1]]
    elif m < 20:
        return "十" + chinese[month[-1]]
    else:
        return chinese[month[0]] + "十" + chinese[month[-1]]


def load_data():
    # 载入黄历数据
    global almanac_conf_data
    with open(f'{working_dir}{sep}assets{sep}data{sep}almanac.json', 'r', encoding='UTF-8') as f:
        almanac_conf_data = json.load(f)
    if redis_status():
        redis.set('almanac', '')


load_data()


def seed_random_list(data_list: list):
    # 使用随机种子随机选择列表中的元素，相同的种子和列表将返回同样的输出
    secret_generator = secrets.SystemRandom()
    index = secret_generator.randint(0, len(data_list) - 1)
    return data_list[index]


def generate_almanac():
    # 生成黄历图片到 data 文件夹
    offset = 1
    today_luck = []
    data_list = list(almanac_conf_data.keys())

    while len(today_luck) < 6:
        # 随机6个不同的运势放到 today_luck
        r = seed_random_list(data_list)
        if r in today_luck:
            offset += 1
        else:
            today_luck.append(r)

    # 加载背景图片
    back = Image.open(f"{working_dir}{sep}assets{sep}images{sep}almanac_back.png")

    # 读取日期
    year = time.strftime("%Y")
    month = month_to_chinese(time.strftime("%m")) + "月"
    day = month_to_chinese(time.strftime("%d")) + "日"

    # 绘图
    draw = ImageDraw.Draw(back)
    draw.text((118, 165), year, fill="#8d7650ff", font=ImageFont.truetype(FONT_PATH, size=30), anchor="mm",
              align="center")
    draw.text((260, 165), day, fill="#f7f8f2ff", font=ImageFont.truetype(FONT_PATH, size=35), anchor="mm",
              align="center")
    draw.text((410, 165), month, fill="#8d7650ff", font=ImageFont.truetype(FONT_PATH, size=30), anchor="mm",
              align="center")

    buff = Image.new("RGBA", (325, 160))
    debuff = Image.new("RGBA", (325, 160))

    buff_draw = ImageDraw.Draw(buff)
    debuff_draw = ImageDraw.Draw(debuff)

    for i in range(3):
        buff_name = today_luck[i]
        debuff_name = today_luck[(i + 3)]

        buff_effect = seed_random_list(almanac_conf_data[buff_name]["buff"])
        debuff_effect = seed_random_list(almanac_conf_data[debuff_name]["debuff"])

        buff_draw.text((0, i * 53), buff_name, fill="#756141ff", font=ImageFont.truetype(FONT_PATH, size=25))
        debuff_draw.text((0, i * 53), debuff_name, fill="#756141ff", font=ImageFont.truetype(FONT_PATH, size=25))

        buff_draw.text((0, i * 53 + 28), buff_effect, fill="#b5b3acff", font=ImageFont.truetype(FONT_PATH, size=19))
        debuff_draw.text((0, i * 53 + 28), debuff_effect, fill="#b5b3acff", font=ImageFont.truetype(FONT_PATH, size=19))

    back.paste(buff, (150, 230), buff)
    back.paste(debuff, (150, 400), debuff)

    back.save(f'{working_dir}{sep}temp{sep}almanac.png', format='PNG')

    # 更新缓存的黄历的更新日期
    if redis_status():
        redis.set('almanac', time.strftime("%Y-%m-%d"))


def get_almanac_image():
    # 判断是否需要重新生成黄历，无 redis 不生成。
    if redis_status():
        try:
            date = redis.get('almanac').decode()
        except AttributeError:
            date = None
        if not date == time.strftime("%Y-%m-%d"):
            generate_almanac()
            return f'{working_dir}{sep}temp{sep}almanac.png'
        else:
            return redis.get('almanac_file_id').decode()
    else:
        return ''
