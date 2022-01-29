from defs.gacha.utils import Dict
from ci import client

BASE_URL = 'https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/%s'


async def gacha_info_list():
    res = await client.get(BASE_URL % 'gacha/list.json')
    json_data = res.json(object_hook=Dict)

    if json_data.retcode != 0:
        raise Exception(json_data.message)

    return json_data.data.list


async def gacha_info(gacha_id):
    res = await client.get(BASE_URL % gacha_id + '/zh-cn.json')

    if res.status_code != 200:
        raise Exception("error gacha_id: %s" % gacha_id)

    return res.json(object_hook=Dict)
