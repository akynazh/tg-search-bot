**A bot based on [ovnrain/javbus-api](https://github.com/ovnrain/javbus-api)**

发送给机器人一个番号，返回**Javbus地址，封面，演员，磁链**。

磁链将是被过滤的，过滤顺序：**高清，有字幕**。

过滤后磁链数目将被限制在3条以内，且附有文件大小描述，以方便选择。如果过滤过程中发现磁链数目已经为0，那么不会继续过滤，而是直接返回。

**安装过程如下：**

```
pip install pytelegrambotapi

docker pull ovnrain/javbus-api
docker run -d \
--name=javbus-api \
--restart=unless-stopped \
-p 8922:3000 \
ovnrain/javbus-api
```

在 `bot.py` 同一目录下，编辑 `credential.py`:

```
TG_CHAT_ID = '' # your telegram chat id
TG_BOT_TOKEN = '' # your telegram bot token
SERVER_URL = '' # your javbus api
```

运行你的机器人：

```
nohup python3 bot.py >/dev/null 2>&1 &
```