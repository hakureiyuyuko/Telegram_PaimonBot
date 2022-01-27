from json.decoder import JSONDecodeError

from ci import client


async def get_url(name: str):
    res = await client.get(url=f'https://info.minigg.cn/foods?query={name}')
    if "errcode" in res.text:
        raise JSONDecodeError("", "", 0)
    py_dict = res.json()
    return py_dict


async def get_foods(name):
    try:
        data = await get_url(name)
    except JSONDecodeError:
        return "该食物不存在。", None
    # 可能为材料名称
    if isinstance(data, list):
        data = [f"<code>{i}</code>" for i in data]
        im = f"材料 <b>{name}</b> 可以制作的食物有：{'、'.join(data)}\n"
        return im, None
    food_im = '''<b>【{}】 {}</b>
【食物类型】 {}
【食物类别】 {}
【效果】 {}
【介绍】 {}
【材料】
{}'''
    ingredients = ""
    food_temp = {}
    for i in data["ingredients"]:
        if i["name"] not in food_temp:
            food_temp[i["name"]] = i["count"]
        else:
            food_temp[i["name"]] = food_temp[i["name"]] + i["count"]
    for i in food_temp:
        ingredients += "<code>   💠 " + i + " " + str(food_temp[i]) + "</code>\n"
    ingredients = ingredients[:-1]
    im = food_im.format(data["name"], "★" * int(data["rarity"]), data["foodtype"], data["foodfilter"],
                        data["effect"], data["description"], ingredients)
    try:
        url = f"https://api.ambr.top/assets/UI/{data['images']['nameicon']}.png"
    except KeyError:
        url = None
    return im, url
