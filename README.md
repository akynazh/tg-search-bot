# tg-jav-bot

**基于Javbus和Avgle并集成Pikpak的一个番号查询机器人。**

## 功能简介

**主要功能：**

发送给机器人一条含有番号的消息，机器人会正则匹配所有符合规则的番号，然后进行搜索。如果番号存在并搜索到结果，则将返回番号对应AV的**封面，标题，日期，演员，磁链等**。

**附加功能：**

- 支持**过滤**磁链（过滤顺序：**高清，有字幕**）
- 支持让机器人自动将**最优磁链**发送到**pikpak**（随机获取时不会自动发送）
- 支持获取**在线视频**功能
- 支持获取**截图**功能
- 支持**代理**功能
- 支持**收藏演员和番号**功能
- 支持**随机获取**影片功能
- 支持**日志记录**功能
- 支持**搜索演员**功能

## 使用教程

### 安装依赖

前提：已经安装Python3（>=3.7）。

```
git clone https://github.com/akynazh/tg-jav-bot.git
pip install -r requirements.txt
cd tg-jav-bot
```

### 填写配置

将 `cfg.pub.py` 重命名为 `cfg.py` 并根据提示编辑:

```
# 必填字段
TG_CHAT_ID = '' # your telegram chat id
TG_BOT_TOKEN = '' # your telegram bot token

# 可选字段：关于代理的配置
USE_PROXY = 0 # 是否使用代理 1 是 | 0 否
# 如果不使用代理，以下四个字段不用管
PROXY_SCHEME = '' # 代理类型 http | socks5 | socks4
PROXY_ADDR_HOST = '' # IP地址
PROXY_ADDR_PORT = '' # 端口地址
PROXY_ADDR = f'{PROXY_SCHEME}://{PROXY_ADDR_HOST}:{PROXY_ADDR_PORT}' # 不用编辑该字段

# 可选字段：关于自动发送磁链到Pikpak的配置
USE_PIKPAK = 0 # 是否使用Pikpak 1 是 | 0 否
# 如果不使用pikpak，以下三个字段不用管
PIKPAK_BOT_NAME = 'PikPak6_Bot' # 默认使用官方机器人：https://t.me/PikPak6_Bot
# 在这里申请api：https://my.telegram.org/apps
TG_API_ID = '' # telegram api id
TG_API_HASH = '' # telegram api hash
```

### 运行机器人

```
nohup python3 bot.py >/dev/null 2>&1 &
```

### 番号规则

- 大部分：字母 + “-” +数字
- 东京热：“n”或“k” + 数字
- 加勒比：六位数字 + “-” + 数字
- 1pondo/10mume：六位数字 + “_” + 数字
- FC2：“fc2-ppv-” + 数字
- MGSTAGE：数字 + 字母 + “-” + 数字