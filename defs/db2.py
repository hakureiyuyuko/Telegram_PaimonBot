import sqlite3
import re
import traceback
from datetime import datetime
from shutil import copyfile
import genshinstats as gs


async def cookiesDB(uid, Cookies, qid):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS NewCookiesTable
    (UID INT PRIMARY KEY     NOT NULL,
    Cookies         TEXT,
    QID         INT,
    StatusA     TEXT,
    StatusB     TEXT,
    StatusC     TEXT,
    NUM         INT,
    Extra       TEXT);''')

    c.execute('''CREATE TABLE IF NOT EXISTS CookiesCache
            (UID TEXT PRIMARY KEY,
            MYSID         TEXT,
            Cookies       TEXT);''')

    cursor = c.execute("SELECT * from NewCookiesTable WHERE UID = ?", (uid,))
    c_data = cursor.fetchall()
    if len(c_data) == 0:
        c.execute("INSERT OR IGNORE INTO NewCookiesTable (Cookies,UID,StatusA,StatusB,StatusC,NUM,QID) \
            VALUES (?, ?,?,?,?,?,?)", (Cookies, uid, "off", "off", "off", 140, qid))
    else:
        c.execute("UPDATE NewCookiesTable SET Cookies = ? WHERE UID=?", (Cookies, uid))

    conn.commit()
    conn.close()


async def deal_ck(mes, qid):
    aid = re.search(r"ltuid=(\d*)", mes)
    mysid_data = aid.group(0).split('=')
    mysid = mysid_data[1]
    cookie = ';'.join(filter(lambda x: x.split('=')[0] in [
        "ltuid", "ltoken"], [i.strip() for i in mes.split(';')]))
    data = await GetMysInfo(mysid, cookie)
    if data:
        uid = data[0]['uid']
    else:
        # 未绑定游戏账号
        uid = 888888888

    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()

    test = c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name = 'CookiesCache'")
    if test == 0:
        pass
    else:
        try:
            c.execute("DELETE from CookiesCache where uid=? or mysid = ?", (uid, mysid))
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

    await cookiesDB(uid, cookie, qid)


async def GetMysInfo(mysid, ck):
    try:
        gs.set_cookie(ck)
        data = gs.get_uid_from_hoyolab_uid(mysid)
        if data:
            return gs.get_game_accounts()
        else:
            return None
    except gs.errors.NotLoggedIn:
        raise gs.errors.NotLoggedIn
    except Exception as e:
        traceback.print_exc()
        print("米游社信息读取Api失败！")


async def selectDB(userid, mode="auto"):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  FROM UIDDATA WHERE USERID = ?", (userid,))
    for row in cursor:
        if mode == "auto":
            if row[0]:
                if row[2]:
                    return [row[2], 3]
                elif row[1]:
                    return [row[1], 2]
                else:
                    return None
            else:
                return None
        elif mode == "uid":
            return [row[1], 2]
        elif mode == "mys":
            return [row[2], 3]


async def OpenPush(uid, qid, status, mode):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    cursor = c.execute("SELECT * from NewCookiesTable WHERE UID = ?", (uid,))
    c_data = cursor.fetchall()
    if len(c_data) != 0:
        try:
            c.execute("UPDATE NewCookiesTable SET {s} = ?,QID = ? WHERE UID=?".format(s=mode), (status, qid, uid))
            conn.commit()
            conn.close()
            return "成功！"
        except:
            return "未找到Ck绑定记录。"
    else:
        return "未找到Ck绑定记录。"


async def OwnerCookies(uid):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    try:
        cursor = c.execute("SELECT *  FROM NewCookiesTable WHERE UID = ?", (uid,))
        c_data = cursor.fetchall()
        cookies = c_data[0][1]
    except:
        return
    return cookies


async def GetAward(Uid):
    try:
        gs.set_cookie(await OwnerCookies(Uid))
        return gs.fetch_endpoint("https://hk4e-api-os.mihoyo.com/event/ysledgeros/month_info",
                                 params=dict(uid=Uid, region=gs.utils.recognize_server(Uid),
                                             month=datetime.now().month, lang='zh=cn'))
    except:
        traceback.print_exc()
        print("访问失败，请重试！")


async def MysSign(Uid):
    try:
        gs.set_cookie(await OwnerCookies(Uid))
        data = gs.claim_daily_reward(Uid, lang='zh-cn')
        if data:
            return data
        else:
            return gs.get_daily_reward_info()
    except:
        print("签到失败，请重试")


async def CheckDB():
    str = ''
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    cursor = c.execute("SELECT UID,Cookies  from NewCookiesTable")
    c_data = cursor.fetchall()
    for row in c_data:
        try:
            aid = re.search(r"ltuid=(\d*)", row[1])
            mysid_data = aid.group(0).split('=')
            mysid = mysid_data[1]
            mys_data = await GetMysInfo(mysid, row[1])
            str = str + f"uid{row[0]}/mysid{mysid}的Cookies是正常的！\n"
        except:
            str = str + f"uid{row[0]}的Cookies是异常的！已删除该条Cookies！\n"
            c.execute("DELETE from NewCookiesTable where UID=?", (row[0],))
            test = c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name = 'CookiesCache'")
            if test == 0:
                pass
            else:
                c.execute("DELETE from CookiesCache where Cookies=?", (row[1],))
    conn.commit()
    conn.close()
    return str


async def GetDaily(Uid):
    try:
        gs.set_cookie(await OwnerCookies(Uid))
        return gs.get_notes(Uid, lang='zh-cn')
    except Exception as e:
        traceback.print_exc()
        print("访问每日信息失败，请重试！")


async def connectDB(userid, uid=None, mys=None):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS UIDDATA
        (USERID INT PRIMARY KEY     NOT NULL,
        UID         TEXT,
        MYSID       TEXT);''')

    c.execute("INSERT OR IGNORE INTO UIDDATA (USERID,UID,MYSID) \
    VALUES (?, ?,?)", (userid, uid, mys))

    if uid:
        c.execute("UPDATE UIDDATA SET UID = ? WHERE USERID=?", (uid, userid))
    if mys:
        c.execute("UPDATE UIDDATA SET MYSID = ? WHERE USERID=?", (mys, userid))

    conn.commit()
    conn.close()


def deletecache():
    try:
        conn = sqlite3.connect('ID_DATA_OR.db')
        c = conn.cursor()
        c.execute("DROP TABLE CookiesCache")
        c.execute("UPDATE NewCookiesTable SET Extra = ? WHERE Extra=?", (None, "limit30"))
        copyfile("ID_DATA_OR.db", "ID_DATA_OR_bak.db")
        c.execute('''CREATE TABLE IF NOT EXISTS CookiesCache
        (UID TEXT PRIMARY KEY,
        MYSID         TEXT,
        Cookies       TEXT);''')
        conn.commit()
        conn.close()
    except:
        print("\nerror\n")

    try:
        conn = sqlite3.connect('ID_DATA_OR.db')
        c = conn.cursor()
        c.execute("UPDATE UseridDict SET lots=NULL")
        conn.commit()
        conn.close()
    except:
        print("\nerror\n")


def functionRegex(value, patter):
    c_pattern = re.compile(r"ltuid={}".format(patter))
    return c_pattern.search(value) is not None


def cacheDB(uid, mode=1, mys=None):
    use = ''
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS CookiesCache
        (UID TEXT PRIMARY KEY,
        MYSID         TEXT,
        Cookies       TEXT);''')
    if mode == 2:
        cursor = c.execute("SELECT *  FROM CookiesCache WHERE MYSID = ?", (uid,))
        c_data = cursor.fetchall()
    else:
        if mys:
            cursor = c.execute("SELECT *  FROM CookiesCache WHERE MYSID = ?", (mys,))
            c_data = cursor.fetchall()
        else:
            cursor = c.execute("SELECT *  FROM CookiesCache WHERE UID = ?", (uid,))
            c_data = cursor.fetchall()

    if len(c_data) == 0:
        if mode == 2:
            conn.create_function("REGEXP", 2, functionRegex)
            cursor = c.execute("SELECT *  FROM NewCookiesTable WHERE REGEXP(Cookies, ?)", (uid,))
            d_data = cursor.fetchall()
        else:
            cursor = c.execute("SELECT *  FROM NewCookiesTable WHERE UID = ?", (uid,))
            d_data = cursor.fetchall()

        if len(d_data) != 0:
            if d_data[0][7] != "error":
                use = d_data[0][1]
                if mode == 1:
                    c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)", (use, uid))
                elif mode == 2:
                    c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                            VALUES (?, ?)", (use, uid))
            else:
                cookiesrow = c.execute("SELECT * FROM NewCookiesTable WHERE Extra IS NULL ORDER BY RANDOM() LIMIT 1")
                e_data = cookiesrow.fetchall()
                if len(e_data) != 0:
                    if mode == 1:
                        c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                                VALUES (?, ?)", (e_data[0][1], uid))
                    elif mode == 2:
                        c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                                VALUES (?, ?)", (e_data[0][1], uid))
                    use = e_data[0][1]
                else:
                    return "没有可以使用的Cookies！"
        else:
            cookiesrow = c.execute("SELECT * FROM NewCookiesTable WHERE Extra IS NULL ORDER BY RANDOM() LIMIT 1")
            e_data = cookiesrow.fetchall()
            if len(e_data) != 0:
                if mode == 1:
                    c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)", (e_data[0][1], uid))
                elif mode == 2:
                    c.execute("INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                            VALUES (?, ?)", (e_data[0][1], uid))
                use = e_data[0][1]
            else:
                return "没有可以使用的Cookies！"
    else:
        use = c_data[0][2]
        if mys:
            try:
                c.execute("UPDATE CookiesCache SET UID = ? WHERE MYSID=?", (uid, mys))
            except:
                c.execute("UPDATE CookiesCache SET MYSID = ? WHERE UID=?", (mys, uid))

    conn.commit()
    conn.close()
    return use


async def GetSpiralAbyssInfo(Uid, ck, Schedule_type="1"):
    try:
        gs.set_cookie(ck),
        return gs.get_spiral_abyss(Uid)
    except Exception as e:
        traceback.print_exc()
        print("深渊信息读取Api失败！")


def errorDB(ck, err):
    conn = sqlite3.connect('ID_DATA_OR.db')
    c = conn.cursor()
    if err == "error":
        c.execute("UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?", ("error", ck))
    elif err == "limit30":
        c.execute("UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?", ("limit30", ck))


async def GetInfo(Uid, ck):
    try:
        gs.set_cookie(ck)
        return gs.get_user_stats(Uid, lang='zh-cn')
    except Exception as e:
        traceback.print_exc()
        print("米游社基础信息读取Api失败！")
