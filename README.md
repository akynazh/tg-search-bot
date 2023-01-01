# tg-jav-bot

**基于Javbus和Avgle并集成Pikpak的一个番号查询机器人。**

## 功能简介

- 发送给机器人一个番号，返回**封面，演员，磁链**
- 可以记录查找成功的番号消息
- 可以过滤磁链（过滤顺序：**高清，有字幕**）
- 可以让机器人自动将最优磁链发送到**pikpak**
- 支持**代理**功能
- 支持**在线视频**功能

## 使用教程

前提：已经安装Python3（>=3.7）。

```
git clone https://github.com/akynazh/tg-jav-bot.git
pip install -r requirements.txt
```

将 `cfg.pub.py` 重命名为 `cfg.py` 并根据提示编辑:

```
TG_CHAT_ID = '' # your telegram chat id
TG_BOT_TOKEN = '' # your telegram bot token

USE_PROXY = 1 # 是否使用代理 1 是 | 0 否
# 如果不使用代理，以下四个字段不用管
PROXY_SCHEME = '' # 代理类型 http | socks5 | socks4
PROXY_ADDR_HOST = '' # IP地址
PROXY_ADDR_PORT = '' # 端口地址
PROXY_ADDR = f'{PROXY_SCHEME}://{PROXY_ADDR_HOST}:{PROXY_ADDR_PORT}' # 不用编辑该字段

USE_PIKPAK = 1 # 1 yes | 0 no
# 如果不使用pikpak，以下三个字段不用管
PIKPAK_BOT_NAME = 'PikPak6_Bot' # 默认使用官方机器人：https://t.me/PikPak6_Bot
# 在这里申请api：https://my.telegram.org/apps
TG_API_ID = '' # telegram api id
TG_API_HASH = '' # telegram api hash
```

运行你的机器人：

```
cd tg-jav-bot
nohup python3 bot.py >/dev/null 2>&1 &
```

## 更新记录

- 2022-12-31更新：添加了在线视频功能。

- 2022-12-30更新：自主定制爬虫，无需再依赖[javbus-api](https://github.com/ovnrain/javbus-api)。

- 2022-12-29更新：集成了PikPak并添加了代理功能。

- 2022-11-28更新：添加了记录查询历史功能。