import difflib, json, re, requests
from os import getcwd, sep
from xpinyin import Pinyin
from json.decoder import JSONDecodeError

working_dir = getcwd()


def nic2name(name):
    with open(f"{working_dir}{sep}assets{sep}data{sep}nickname.json", 'r', encoding='utf-8') as f:
        all_name = json.load(f)
        f.close()
    for i in all_name:
        for x in i.values():
            if name in x:
                return x[0]
    return name


# def repl(match):
#     content = re.sub(" ", "",match.group(0))
#     length = len(content) - 1
#     result = ''
#     if content[0] == '[':
#         result = '[""'
#         length -= 1
#
#     after = ','
#     if content[-1] == ']':
#         length -= 1
#         after += '""]'
#
#     return result + (',""' * length) + after


def get_json(name: str) -> dict:
    if name not in ["空", "荧"]:
        name = nic2name(name)
    res = requests.get(f'https://info.minigg.cn/characters?query={name}')
    if "errcode" in res.text:
        raise JSONDecodeError("", "", 0)
    py_dict = res.json()
    return py_dict


def get_json_mz(name: str) -> dict:
    name = nic2name(name)
    res = requests.get(f'https://info.minigg.cn/constellations?query={name}')
    if "errcode" in res.text:
        raise JSONDecodeError("", "", 0)
    py_dict = res.json()
    return py_dict


def num_to_char(num):
    """数字转中文."""
    num = str(num)
    num_dict = {"0": u"零", "1": u"一", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
    list_num = list(num)
    shu = []
    for i in list_num:
        shu.append(num_dict[i])
    new_str = "".join(shu)
    return new_str


def char_to_char(char):
    char_dict = {"零": u"0", "一": u"1", "二": u"2", "三": u"3", "四": u"4", "五": u"5", "六": u"6", "七": u"7", "八": u"8",
                 "九": u"9"}
    list_num = list(char)
    shu = []
    for i in list_num:
        shu.append(char_dict[i])
    new_str = "".join(shu)
    return int(new_str)


def get_character(name: str):
    # 角色常见昵称转换为官方角色名
    nick_name = name
    if name not in ["空", "荧"]:
        nick_name = nic2name(name)
    try:
        data = get_json(nick_name)
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
    result = f"<b>{nick_name}</b>\n" \
             f"<b>稀有度：</b>{data['rarity']}\n" \
             f"<b>命之座：</b>{data['constellation']}\n" \
             f"<b>所属：</b>{data['affiliation']}\n" \
             f"<b>突破加成：</b>{data['substat']}\n" \
             f"<b>武器类型：</b>{data['weapontype']}\n" \
             f"<b>生日：</b>{data['birthday']}\n" \
             f"<b>神之眼/心：</b>{data['element']}\n" \
             f"<b>称号：</b>{data['title']}\n" \
             f"<b>CV：</b>{data['cv']['chinese']}\n" \
             f"<b>简介：</b>{data['description']}"
    try:
        url = data["images"]["cover1"]
    except KeyError:
        url = data["images"]["icon"]
    return result, url


async def get_mz(name_mz: str) -> str:
    name_mz = name_mz.replace(" ", "")
    try:
        name = re.findall(r'(.*)([零一二三四五六七八九0123456789]{1})命', name_mz)[0][0]
        name = nic2name(name)
    except IndexError:
        name = name_mz
        name = nic2name(name)
    try:
        num = int(re.search(r'\d{1,5}', name_mz).group(0))
    except AttributeError:
        try:
            num = char_to_char(re.findall(r'(.*)([零一二三四五六七八九0123456789]{1})命', name_mz)[0][1])
        except IndexError:
            num = -1
    try:
        data = get_json_mz(name)
    except:
        return f"派蒙这没有 <code>{name}</code> ，可能是官方资料没有该资料，可能是你输入的名字不正确哦。"
    result = ''
    if num == -1:
        n = 1
        for i in range(6):
            try:
                result = result + f"{num_to_char(n)}命{data['c{}'.format(n)]['name']}：" \
                                  f"{data['c{}'.format(n)]['effect'].replace('*', '')}\n"
            except KeyError:
                break
            n = n + 1
        return f'{name}' + '\n' + result
    elif 0 < num < 7:
        try:
            return f'{name}的' + f"{num_to_char(num)}命{data['c{}'.format(num)]['name']}：" \
                       f"{data['c{}'.format(num)]['effect'].replace('*', '')}\n"
        except KeyError:
            return f"查询错误!你家 <code>{name}</code> 有 <code>{num}</code> 命？？"
    elif num == 0:
        return "你搁这原地tp呢？"
    else:
        return f"查询错误!你家 <code>{name}</code> 有 <code>{num}</code> 命？？"


def auto_correct(name: str) -> list:
    with open(f"{working_dir}{sep}assets{sep}data{sep}character_index.json", "r", encoding="utf-8") as f:
        character_index = json.loads(f.read())
    input_pin_yin_list = Pinyin().get_pinyin(name).split("-")
    result_cache = []
    result = []
    for index_name in character_index:
        true_name = list(index_name.keys())[0]
        for input_pin_yin in input_pin_yin_list:
            for true_pin_yin in index_name[true_name]:
                if difflib.SequenceMatcher(None, true_pin_yin, input_pin_yin).quick_ratio() >= 1:
                    result_cache.append(true_name)
        if difflib.SequenceMatcher(None, true_name, name).quick_ratio() >= 0.3:
            result_cache.append(true_name)
    for result_repeat in result_cache:
        if result_cache.count(result_repeat) > 1 and result_repeat not in result:
            result.append(result_repeat)
    return result


def montage_result(correct_result: list) -> str:
    cause = correct_result[0]
    for i in range(1, len(correct_result)):
        cause = cause + "\n" + correct_result[i]
    return cause
