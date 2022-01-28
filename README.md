# Telegram_PaimonBot

一个用于查询原神信息的 Telegram bot 。

![](https://img.shields.io/badge/license-GPL3.0-%23373737.svg) ![https://python.org](https://img.shields.io/badge/python-3.6%2B-blue.svg) ![https://github.com/pyrogram/pyrogram/](https://img.shields.io/badge/Pyrogram-asyncio-green.svg) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/e1fa3655218f4edaa14db099c5ab2823)](https://www.codacy.com/gh/Xtao-Labs/Telegram_PaimonBot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Xtao-Labs/Telegram_PaimonBot&amp;utm_campaign=Badge_Grade)

Bot 实例: [@Genshin_All_Info_Bot](https://t.me/Genshin_All_Info_Bot)

## 安装

- [@BotFather](https://t.me/botfather) 申请 Bot Token 
- [Obtaining Telegram API ID](https://core.telegram.org/api/obtaining_api_id) 申请 API ID 与 API Hash
- 拉取项目
  ```bash
  git clone https://github.com/Xtao-Labs/Telegram_PaimonBot.git
  cd Telegram_PaimonBot
  ```
- 安装依赖
  ```bash
  python3 -m pip install -r requirements.txt
  ```
- 修改配置文件
  ```bash
  cp config.ini.example config.ini
  nano config.ini
  ``` 
  `api_id` 为第二步申请的 API ID
  `api_hash` 为第二步申请的 API Hash
  `bot_token` 为第一步申请的 Bot Token 
  `admin` 为 bot 管理员账号 id ，可以不修改。
  `channel_id` 为 bot 日志记录频道 id ，可以不修改。
  
- 开始运行
  ```bash
  python3 main.py
  ``` 
- 配置进程守护


## 特别感谢

[genshinstats](https://github.com/thesadru/genshinstats/)

[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)

[Genshin_Impact_bot](https://github.com/H-K-Y/Genshin_Impact_bot)

[PaimonBot](https://github.com/XiaoMiku01/PaimonBot)

[YuanShen_User_Info](https://github.com/Womsxd/YuanShen_User_Info)

