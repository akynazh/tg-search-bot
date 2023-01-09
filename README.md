# tg-jav-bot

**一个基于Javbus，Sukebei，Avgle并集成Pikpak的TG番号查询机器人。**

## 功能简介

**主要功能：**

发送给机器人一条含有番号的消息，机器人会匹配并搜索消息中所有符合 **“字母-数字”** 格式的番号（其它格式的番号可通过 **/av** 命令查找）。如果搜索到结果，将返回番号对应AV的 **封面，标题，日期，演员，磁链** 等。

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

如果通过docker部署可以跳过该步骤。该步骤完成的前提是已经安装Python3（>=3.7）。

```
git clone https://github.com/akynazh/tg-jav-bot.git
pip install -r requirements.txt
cd tg-jav-bot
```

注：`requirements.txt` 配置使用了国内镜像源，如需取消该设定，可以删除 `requirements.txt` 中的第一行内容：

```
-i https://pypi.tuna.tsinghua.edu.cn/simple
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
USE_PIKPAK = 0 # 是否使用Pikpak自动发送功能 1 是 | 0 否
# 如果不使用pikpak自动发送功能，以下三个字段不用管
PIKPAK_BOT_NAME = 'PikPak6_Bot' # 默认使用官方机器人：https://t.me/PikPak6_Bot
# 在这里申请api：https://my.telegram.org/apps
TG_API_ID = '' # telegram api id
TG_API_HASH = '' # telegram api hash
```

注：如需使用Pikpak自动发送功能，需要先生成 `my_account.session` 文件，运行如下命令：

```
python3 util_pikpak.py
```

接着需要在控制台中完成登录操作，即可生成 `my_account.session` 文件。

### 运行机器人

```
nohup python3 bot.py >/dev/null 2>&1 &
```

如果通过docker部署：（前提：安装了docker和docker-compose）

```
docker-compose up -d
```