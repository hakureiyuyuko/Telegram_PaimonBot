from json.decoder import JSONDecodeError

from ci import client


async def get_url(name: str):
    res = await client.get(url=f'https://info.minigg.cn/enemies?query={name}')
    if "errcode" in res.text:
        raise JSONDecodeError("", "", 0)
    py_dict = res.json()
    return py_dict


async def get_enemies(name):
    try:
        raw_data = await get_url(name)
    except JSONDecodeError:
        return "该原魔不存在。", None
    reward = ""
    for i in raw_data["rewardpreview"]:
        reward += f"<code>   💠 {i['name']}：{(str(round(i['count'] * 100, 2)) + '%') if 'count' in i.keys() else '可能'}</code>\n"
    im = "<b>【{}】</b>\n" \
         "——{}——\n" \
         "<b>所属：</b>{}\n" \
         "<b>信息：</b>{}\n" \
         "<b>掉落物：</b>\n{}".format(raw_data["name"], raw_data["specialname"],
                                  raw_data["category"], raw_data["description"], reward)
    try:
        url = f"https://www.gamerguides.com/assets/maps/cat-icons/{raw_data['images']['nameicon']}.png"
    except KeyError:
        url = None
    return im, url
