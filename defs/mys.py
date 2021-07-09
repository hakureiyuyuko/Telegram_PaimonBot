import hashlib, json, string, random, time
from os import getcwd, sep
from httpx import AsyncClient
from PIL import Image, ImageDraw, ImageFont, ImageFilter

working_dir = getcwd()
mhyVersion = "2.7.0"
with open("cookie.txt", mode='r') as r:
    cookie = r.read()


def md5(text):
    temp = hashlib.md5()
    temp.update(text.encode())
    return temp.hexdigest()


def DSGet():
    n = "fd3ykrh7o1j54g581upo1tvpam0dsgtf"
    i = str(int(time.time()))
    f = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t=" + i + "&r=" + f)
    return i + "," + f + "," + c


async def GetInfo(uid, server_id="cn_gf01"):
    if uid[0] == '5':
        server_id = "cn_qd01"
    try:
        async with AsyncClient() as client:
            req = await client.get(
                url=f"https://api-takumi.mihoyo.com/game_record/genshin/api/index?server={server_id}&role_id={uid}",
                headers={
                    'Accept': 'application/json, text/plain, */*',
                    'DS': DSGet(),
                    'Origin': 'https://webstatic.mihoyo.com',
                    'x-rpc-app_version': mhyVersion,
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, '
                                  'like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                    'x-rpc-client_type': '2',
                    'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,en-US;q=0.8',
                    'X-Requested-With': 'com.mihoyo.hyperion',
                    "Cookie": cookie})
            data = json.loads(req.text)
            return data
    except ConnectionError:
        raise ConnectionError


async def circle_corner(img, radii):
    circle = Image.new('L', (radii * 2, radii * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)

    img = img.convert("RGBA")
    w, h = img.size

    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))

    img.putalpha(alpha)
    return img


def ys_font(size):
    return ImageFont.truetype(f'{working_dir}{sep}assets{sep}fonts{sep}yuan_shen.ttf', size=size, encoding="utf-8")


async def draw_pic(uid):
    raw_data = await GetInfo(uid)
    if raw_data["retcode"] != 0:
        if raw_data["retcode"] == 10001:
            raise ConnectionRefusedError
        return None
    # 读取用户角色
    raw_data = raw_data['data']
    bg_path = f'{working_dir}{sep}assets{sep}images{sep}bg_1.jpg'
    char1_id = raw_data['avatars'][0]['id']
    char2_id = raw_data['avatars'][1]['id']
    char3_id = raw_data['avatars'][2]['id']
    char4_id = raw_data['avatars'][3]['id']
    char5_id = raw_data['avatars'][4]['id']
    char6_id = raw_data['avatars'][5]['id']

    char1 = f'{working_dir}{sep}assets{sep}characters{sep}{char1_id}.png'
    char2 = f'{working_dir}{sep}assets{sep}characters{sep}{char2_id}.png'
    char3 = f'{working_dir}{sep}assets{sep}characters{sep}{char3_id}.png'
    char4 = f'{working_dir}{sep}assets{sep}characters{sep}{char4_id}.png'
    char5 = f'{working_dir}{sep}assets{sep}characters{sep}{char5_id}.png'
    char6 = f'{working_dir}{sep}assets{sep}characters{sep}{char6_id}.png'
    area = (0, 0, 680, 750)
    # 加载背景
    img = Image.open(bg_path).crop(area)
    im_blur = img.filter(ImageFilter.GaussianBlur)
    base_img = Image.new("RGB", img.size, (255, 255, 255))
    canvas_img = Image.new("RGB", (int(img.size[0] * 0.95), int(img.size[1] * 0.98)), "black")
    paste_box_x = base_img.size[0] - canvas_img.size[0]
    paste_box_y = base_img.size[1] - canvas_img.size[1]
    paste_box = (int(paste_box_x / 2), int(paste_box_y / 2))
    base_img.paste(canvas_img, paste_box)
    img_canvas = Image.blend(im_blur, base_img, 0.2)

    text_draw = ImageDraw.Draw(img_canvas)
    # 上左部背景
    ava_holder = Image.open(f'{working_dir}{sep}assets{sep}images{sep}ba.png').resize((200, 200), Image.BILINEAR)
    # 上中部背景
    id_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}level.png").resize((250, 155),
                                                                                     Image.BILINEAR).convert("RGBA")
    # 上右部背景
    level_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}level2.png").resize((180, 180), "RGBA")
    # 中部大背景
    p1_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}p1.png").resize((600, 300),
                                                                                  Image.BILINEAR).convert("RGBA")
    # cover_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}cover.png").convert("RGBA").resize((105, 105),
    # Image.BILINEAR)
    # 默认头像
    ava_img = Image.open(f'{working_dir}{sep}assets{sep}images{sep}ava.png').resize((127, 127), Image.BILINEAR)
    bar = Image.open(f"{working_dir}{sep}assets{sep}images{sep}bar.png").convert("RGBA").resize((580, 40),
                                                                                                Image.BILINEAR)
    wind_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}wind.png").convert("RGBA")
    earth_img = Image.open(f"{working_dir}{sep}assets{sep}images{sep}earth.png").convert("RGBA")

    char1_img = Image.open(char1).convert("RGBA").resize((95, 95), Image.BILINEAR)
    char2_img = Image.open(char2).convert("RGBA").resize((95, 95), Image.BILINEAR)
    char3_img = Image.open(char3).convert("RGBA").resize((95, 95), Image.BILINEAR)
    char4_img = Image.open(char4).convert("RGBA").resize((95, 95), Image.BILINEAR)
    char5_img = Image.open(char5).convert("RGBA").resize((95, 95), Image.BILINEAR)
    char6_img = Image.open(char6).convert("RGBA").resize((95, 95), Image.BILINEAR)

    ava_rad = await circle_corner(ava_img, 15)
    img_canvas.paste(ava_holder, (15, 20), ava_holder)
    img_canvas.paste(ava_rad, (50, 55), ava_rad)
    img_canvas.paste(id_img, (210, 45), id_img)
    img_canvas.paste(level_img, (465, 30), level_img)
    img_canvas.paste(p1_img, (41, 230), p1_img)
    img_canvas.paste(bar, (45, 480), bar)
    img_canvas.paste(wind_img, (308, 240), wind_img)
    img_canvas.paste(earth_img, (480, 245), earth_img)
    img_canvas.paste(char1_img, (40, 540), char1_img)
    img_canvas.paste(char2_img, (140, 540), char2_img)
    img_canvas.paste(char3_img, (240, 540), char3_img)
    img_canvas.paste(char4_img, (340, 540), char4_img)
    img_canvas.paste(char5_img, (440, 540), char5_img)
    img_canvas.paste(char6_img, (540, 540), char6_img)

    text_draw.text((240, 80), "账号信息", 'lightcyan', ys_font(23))
    text_draw.text((230, 80), f'UID {uid}', 'lightcyan', ys_font(25))
    if uid[0] == "1":
        text_draw.text((230, 130), "服务器 天空岛", 'lightcyan', ys_font(25))
    else:
        text_draw.text((220, 130), "服务器 世界树", 'lightcyan', ys_font(25))
    text_draw.text((520, 90), "XX 级", (0, 0, 0), ys_font(30))
    text_draw.text((510, 125), "世界等级 X", (0, 0, 0), ys_font(18))

    wind_num = raw_data['stats']['anemoculus_number']
    earth_num = raw_data['stats']['geoculus_number']

    char_data = raw_data["avatars"]

    text_draw.text((80, 245), '活跃天数   ' + str(raw_data['stats']['active_day_number']), (0, 0, 0), ys_font(23))
    text_draw.text((80, 285), '成就解锁   ' + str(raw_data['stats']['achievement_number']), (0, 0, 0), ys_font(23))
    text_draw.text((80, 325), '华丽宝箱   ' + str(raw_data['stats']['luxurious_chest_number']), (0, 0, 0), ys_font(23))
    text_draw.text((80, 365), '珍贵宝箱   ' + str(raw_data['stats']['precious_chest_number']), (0, 0, 0), ys_font(23))
    text_draw.text((80, 405), '精致宝箱   ' + str(raw_data['stats']['exquisite_chest_number']), (0, 0, 0), ys_font(23))
    text_draw.text((80, 445), '普通宝箱   ' + str(raw_data['stats']['common_chest_number']), (0, 0, 0), ys_font(23))
    text_draw.text((250, 485), '深境螺旋  ' + raw_data['stats']['spiral_abyss'], 'lightcyan', ys_font(25))
    text_draw.text((320, 365), f'风神瞳\n{wind_num}/66', (0, 0, 0), ys_font(27))
    text_draw.text((490, 365), f'岩神瞳\n{earth_num}/131', (0, 0, 0), ys_font(27))
    text_draw.text((60, 640),
                   f'{char_data[0]["name"]}\nLv.{str(char_data[0]["level"])}\n好感等级{str(char_data[0]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((156, 640),
                   f'{char_data[1]["name"]}\nLv.{str(char_data[1]["level"])}\n好感等级{str(char_data[1]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((254, 640),
                   f'{char_data[2]["name"]}\nLv.{str(char_data[2]["level"])}\n好感等级{str(char_data[2]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((352, 640),
                   f'{char_data[3]["name"]}\nLv.{str(char_data[3]["level"])}\n好感等级{str(char_data[3]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((450, 640),
                   f'{char_data[4]["name"]}\nLv.{str(char_data[4]["level"])}\n好感等级{str(char_data[4]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((548, 640),
                   f'{char_data[5]["name"]}\nLv.{str(char_data[5]["level"])}\n好感等级{str(char_data[5]["fetter"])}',
                   'lightcyan', ys_font(17))
    text_draw.text((55, 715), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'lightcyan', ys_font(18))

    img_canvas.save(f'{working_dir}{sep}temp{sep}mys.png', format='png')
    return f'{working_dir}{sep}temp{sep}mys.png'
