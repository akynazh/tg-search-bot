**2022-12-29更新：集成了PikPak并添加了代理功能。**

**2022-12-18更新：添加了分类查询功能。**

**2022-12-05更新：添加了正则匹配番号功能。**

**2022-11-28更新：添加了记录查询历史功能，可通过/record查询历史记录。**

---

**A bot based on [ovnrain/javbus-api](https://github.com/ovnrain/javbus-api)**

发送给机器人一个番号，返回**Javbus地址，封面，演员，磁链**。

磁链将是被过滤的，过滤顺序：**高清，有字幕**。

过滤后磁链数目将被限制在3条以内，且附有文件大小描述，以方便选择。

如果发现某一次过滤后磁链数目已经为0，那么会直接返回过滤前的条目。

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

在 `bot.py` 同一目录下，编辑 `cfg.py`:

```
TG_CHAT_ID = '' # your telegram chat id
TG_BOT_TOKEN = '' # your telegram bot token
SERVER_URL = '' # your javbus api
```

运行你的机器人：

```
nohup python3 bot.py >/dev/null 2>&1 &
```