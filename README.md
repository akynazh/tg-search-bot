# tg-jav-bot

**一个基于 Javbus，Sukebei，Avgle，Dmm，Javlibrary 并集成了 Pikpak 的万能 Telegram 番号查询机器人。**

该项目持续更新，如果发现代码存在问题（特别是爬虫失效了）或者需要其他新的功能，欢迎提 issue 或者参与到本项目中 ~

plus: 由于有较多无关紧要的 issue 出现，在此声明，如果你是：【不懂技术 / 没有服务器 / 没有日本 IP（只针对 dmm 爬虫） / 懒得折腾 / 想定制机器人】这一类人，可以通过邮箱 akynazh@qq.com 或 电报 [@jackbryant286](https://t.me/jackbryant286) 联系我（保证价格低廉，便捷快速）。

## 功能简介

**主要功能：**

发送给机器人一条含有番号的消息，机器人会匹配并通过 Javbus 和 Sukebei 搜索消息中所有符合“字母-数字”格式的番号（其它格式的番号可通过 /av 命令查找）。如果搜索到结果，将返回番号对应 AV 的封面，标题，日期，演员，磁链等。

**附加功能：**

- 支持收藏演员和番号
- 支持过滤磁链（过滤顺序：高清，有字幕）
- 支持配置代理
- 支持通过 Javbus 获取截图
- 支持通过 Javbus 搜索演员，获取演员最新 AV，随机获取演员 AV
- 支持让机器人自动将最优磁链发送到 Pikpak（随机获取时不会自动发送）
- 支持通过 Dmm 获取预览视频，女优排行榜，AV 评分 （由于 DMM 限制，只支持日本 IP）
- 支持通过 Avgle 获取预览视频和完整视频
- 支持通过 Javlibrary 各种排行榜随机获取番号

注：记录和日志等文件生成位置在 `~/.tg_jav_bot` 目录下。

**部分结果展示：**

![部分结果展示](res.png)

## 使用教程

### 一、下载代码

```
git clone https://github.com/akynazh/tg-jav-bot.git
cd tg-jav-bot
```

### 二、安装依赖

如果使用 docker 部署，可以跳过该步骤。

前提：系统已经安装 Python3（>=3.7）

```
pip install -r requirements.txt
```

注：`requirements.txt` 配置使用了国内镜像源，如需取消该设定，可以删除 `requirements.txt` 中的第一行内容：

```
-i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 三、配置机器人

将 `cfg.pub.py` 重命名为 `cfg.py` 并根据提示编辑:

```
# 必填字段

# TG 对话 ID
TG_CHAT_ID = ''
# TG 机器人 Token
TG_BOT_TOKEN = ''

# 可选字段：关于代理的配置

# 是否使用代理 1 是 | 0 否
USE_PROXY = 0
# 访问 Dmm 是否使用代理 1 是 | 0 否 （该字段的值由自己决定，与 USE_PROXY 无关）
USE_PROXY_DMM = 0
# 如果不使用代理，以下三个字段不用管
# 代理类型 http | socks5 | socks4
PROXY_SCHEME = 'http'
# IP 地址
PROXY_ADDR_HOST = '127.0.0.1'
# 端口地址
PROXY_ADDR_PORT = '7890'

# 可选字段：关于自动发送磁链到 Pikpak 的配置

# 是否使用 Pikpak 自动发送功能 1 是 | 0 否
USE_PIKPAK = 0
# 如果不使用 Pikpak 自动发送功能，以下两个字段不用管（在这里申请 API：https://my.telegram.org/apps）
# TG API ID
TG_API_ID = ''
# TG API HASH
TG_API_HASH = ''
```

如需使用 Pikpak 自动发送功能，需要先生成 `my_account.session` 文件，运行如下命令：

```
python3 util_pikpak.py
```

接着需要在控制台中完成登录操作，登录成功即可生成 `my_account.session` 文件。

### 四、运行机器人

如果不是通过 docker 部署，运行如下命令：

```
nohup python3 bot.py >/dev/null 2>&1 &
```

如果通过 docker 部署，运行如下命令：（前提：安装了 docker 和 docker-compose ）

```
docker-compose up -d
```
