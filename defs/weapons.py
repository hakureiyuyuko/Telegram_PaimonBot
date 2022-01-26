import difflib, json, requests, yaml, re
from os import getcwd, sep
from xpinyin import Pinyin
from json.decoder import JSONDecodeError
from defs.character import repl

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/89.0.4389.82 Safari/537.36"}
working_dir = getcwd()
with open(f"{working_dir}{sep}assets{sep}data{sep}weapon.json", 'r', encoding='utf-8') as f:
    weapon_all = json.load(f)
weapon_type = {1: "单手剑", 2: "双手剑", 3: "弓", 4: "法器", 5: "长枪"}


def get_url(name: str):
    res = requests.get(url=f'https://api.minigg.cn/weapons?query={name}', headers=headers)
    if res.text == "undefined\n":
        raise JSONDecodeError("", "", 0)
    py_dict = yaml.safe_load(re.sub(r'\[? *(, *)+\]?', repl, res.text))
    return py_dict


async def get_weapon(name: str):
    for i in weapon_all:
        if name in i['name']:
            try:
                url = (get_url(i['name'][0]))["images"]["image"]
            except (JSONDecodeError, KeyError):
                url = None
            text = f"<b>{i['name'][0]}</b> {'★' * i['star']}\n" \
                   f"<b>类型：</b>{weapon_type[i['type']]}\n" \
                   f"<b>1级基础攻击力：</b>{i['basic_attack']}\n" \
                   f"<b>满级基础攻击力：</b>{i['max_attack']}\n" \
                   f"<b>满级副属性：</b>{i['max_attribute']}\n" \
                   f"<b>技能：</b>{i['skill']}"
            return text, url
    try:
        data = get_url(str(name))
        text = f"<b>{data['name']}</b> {'★' * int(data['rarity'])}\n" \
               f"<b>类型：</b>{data['weapontype']}\n" \
               f"<b>1级基础攻击力：</b>{data['baseatk']}\n" \
               f"<b>副属性：</b>{data['substat']}\n" \
               f"<b>描述：</b>{data['description']}"
        try:
            url = data["images"]["image"]
        except KeyError:
            url = None
        return text, url
    except (JSONDecodeError, KeyError):
        pass
    correct_result = auto_correct(name)
    if len(correct_result) > 1:
        return f"派蒙这里没找到武器 <code>{name}</code> ，你是要搜索如下的武器吗?\n{montage_result(correct_result)}", None
    elif len(correct_result) < 1:
        return "没有找到该武器,派蒙也米有办法！是不是名字错了？", None
    else:
        return f"派蒙这里没找到武器 <code>{name}</code> ，你是要搜索 <code>{correct_result[0]}</code> 吗？", None


def auto_correct(name: str) -> list:
    with open(f"{working_dir}{sep}assets{sep}data{sep}weapon_index.json", "r", encoding="utf-8") as weapon_index_file:
        character_index = json.loads(weapon_index_file.read())
    input_pin_yin_list = Pinyin().get_pinyin(name).split("-")
    result_cache = []
    result = []
    for index_name in character_index:
        true_name = list(index_name.keys())[0]
        for input_pin_yin in input_pin_yin_list:
            for true_pin_yin in index_name[true_name]:
                if difflib.SequenceMatcher(None, true_pin_yin, input_pin_yin).quick_ratio() >= 1:
                    result_cache.append(true_name)
        if difflib.SequenceMatcher(None, true_name, name).quick_ratio() >= 0.8:
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
