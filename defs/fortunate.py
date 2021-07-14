import json, time, secrets
from defs.character import nic2name, get_json, auto_correct, montage_result
from os import getcwd, sep
from PIL import Image, ImageDraw, ImageFont
from json.decoder import JSONDecodeError
from defs.redis_load import redis_status, redis


def get_character(name: str):
    # 角色常见昵称转换为官方角色名
    nick_name = nic2name(name)
    try:
        if nick_name == '旅行者':
            return "派蒙这里不支持旅行者哦。", None
        get_json(nick_name)
        return nick_name, 'ok'
    except JSONDecodeError:
        correct_result = auto_correct(nick_name)
        if correct_result is None:
            return f"派蒙这里没找到 <code>{name}</code> ，可能是派蒙的错，可能是你输入的名字不正确哦。", None
        else:
            if len(correct_result) > 1:
                return f"派蒙这里没找到 <code>{name}</code> ，你是要搜索如下的角色吗?\n{montage_result(correct_result)}", None
            elif len(correct_result) < 1:
                return f"派蒙这里没找到 <code>{name}</code> ，可能是派蒙的错，可能是你输入的名字不正确哦。", None
            else:
                return f"派蒙这里没找到 <code>{name}</code> ，你是要搜索 <code>{correct_result[0]}</code> 吗", None


def get_img_path(name: str):
    data = ['迪奥娜', '芭芭拉', '魈', '重云', '行秋', '凯亚', '雷泽', '温迪', '班尼特', '迪卢克', '砂糖', '北斗', '菲谢尔',
            '诺艾尔', '香菱', '达达利亚', '丽莎', '安伯', '七七', '琴', '凝光', '莫娜', '刻晴', '可莉', '钟离', '辛焱',
            '阿贝多']
    if name == 'random':
        secret_generator = secrets.SystemRandom()
        index = secret_generator.randint(0, len(data) - 1)
        return f'{getcwd()}{sep}assets{sep}img{sep}frame_{index + 1}.jpg'
    return f'{getcwd()}{sep}assets{sep}img{sep}frame_{data.index(name) + 1}.jpg'


def copy_writing(uid):
    p = f"{getcwd()}{sep}assets{sep}data{sep}fortunate.json"
    with open(p, "r", encoding="utf-8") as f:
        content = json.loads(f.read())
    secret_generator = secrets.SystemRandom()
    index = secret_generator.randint(0, len(content["fortunate"]) - 1)
    text = json.dumps(content["fortunate"][index])
    redis.set(f'f_{uid}_txt', text)
    redis.set(f'f_{uid}', time.strftime("%Y-%m-%d"))
    return content["fortunate"][index]


def getTitle(structure):
    p = f"{getcwd()}{sep}assets{sep}data{sep}goodLuck.json"
    with open(p, "r", encoding="utf-8") as f:
        content = json.loads(f.read())
    for i in content["types_of"]:
        if i["good-luck"] == structure["good-luck"]:
            return i["name"]


def drawing(img_path, text):
    resources = f"{getcwd()}{sep}assets{sep}fonts{sep}"
    fonts_path = {
        "title": f"{resources}Mamelon.otf",
        "text": f"{resources}sakura.ttf",
    }
    img = Image.open(img_path)
    # Draw title
    draw = ImageDraw.Draw(img)
    title = getTitle(text)
    text = text["content"]
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    tt_front = ImageFont.truetype(fonts_path["title"], font_size)
    font_length = tt_front.getsize(title)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=tt_front,
    )
    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    tt_front = ImageFont.truetype(fonts_path["text"], font_size)
    result = decrement(text)
    if not result[0]:
        return
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        text_vertical = vertical(result[i + 1])
        x = int(
            image_font_center[0]
            + (result[0] - 2) * font_size / 2
            + (result[0] - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), text_vertical, fill=color, font=tt_front)
    # Save
    img.save(f'temp{sep}fortune.png')
    return f'temp{sep}fortune.png'


def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    number_of_slices = 1
    while length > cardinality:
        number_of_slices += 1
        length -= cardinality
    result.append(number_of_slices)
    # Optimize for two columns
    space = " "
    length = len(text)
    if number_of_slices == 2:
        if length % 2 == 0:
            # even
            fill_in = space * int(9 - length / 2)
            return [
                number_of_slices,
                text[: int(length / 2)] + fill_in,
                fill_in + text[int(length / 2):],
            ]
        else:
            # odd number
            fill_in = space * int(9 - (length + 1) / 2)
            return [
                number_of_slices,
                text[: int((length + 1) / 2)] + fill_in,
                fill_in + space + text[int((length + 1) / 2):],
            ]
    for i in range(0, number_of_slices):
        if i == number_of_slices - 1 or number_of_slices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality: (i + 1) * cardinality])
    return result


def vertical(txt):
    lists = []
    for s in txt:
        lists.append(s)
    return "\n".join(lists)


def get_fortunate_image(uid, name):
    # 判断是否需要重新生成，无 redis 不生成。
    if redis_status():
        try:
            date = redis.get(f'f_{uid}').decode()
        except AttributeError:
            date = None
        if not date == time.strftime("%Y-%m-%d"):
            text = copy_writing(uid)
            img = get_img_path(name)
            drawing(img, text)
            return f'{getcwd()}{sep}temp{sep}fortune.png'
        else:
            text = json.loads(redis.get(f'f_{uid}_txt').decode())
            img = get_img_path(name)
            drawing(img, text)
        return f'{getcwd()}{sep}temp{sep}fortune.png'
    else:
        return ''
