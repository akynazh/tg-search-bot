# tg-search-bot

**一个用于查询与收藏演员和影片的机器人, 可自动保存磁链到 Pikpak。**

欢迎 issue 和 pr，可通过邮箱 [akynazh@qq.com](mailto://akynazh@qq.com) 或电报 [@jackbryant286](https://t.me/jackbryant286) 联系我。

## 功能简介

以下功能按开发完成时间进行排序，后续有新功能将持续补充。

- 支持获取影片基本信息和磁链 - 2022/11/25
- 支持配置代理 - 2022/11/26
- 支持过滤磁链 (uncensored => hd => subtitle)- 2022/11/26
- 支持让机器人自动将最优磁链保存到 Pikpak - 2022/12/29
- 支持获取预览视频和完整视频 - 2022/12/31
- 支持获取影片截图 - 2023/01/01
- 支持收藏演员和影片 - 2023/01/04
- 支持通过 docker 部署 - 2023/01/08
- 支持获取演员排行榜，影片评分 - 2023/01/20
- 支持随机获取高分影片和最新影片 - 2023/01/25
- 支持通过维基百科获取演员中文名 - 2023/02/18
- 支持翻译日文标题 - 2023/02/18
- 支持搜索演员 - 2023/02/18
- 支持通过 redis 进行缓存 - 2023/03/17

## TODO 

- 英文版本

## 使用教程

首先需要下载本项目代码到本地。

### 配置机器人

编辑 `~/.tg_jav_bot/config.yaml`：

```yaml
# TG 对话 ID
tg_chat_id: 
# TG 机器人 Token
tg_bot_token: 
# 全局是否使用代理 1 是 | 0 否
use_proxy: 
# 访问 dmm 时是否使用代理，如果全局使用代理，则忽略该字段 1 是 | 0 否
use_proxy_dmm: 
# 代理服务器地址，如果不使用代理，则忽略该字段
proxy_addr: 
# 是否使用 Pikpak 自动发送功能 1 是 | 0 否
use_pikpak: 
# 配置 TG API，如果不使用 Pikpak 自动发送功能，则忽略以下两个字段，可在这里申请 API: https://my.telegram.org/apps
tg_api_id: 
tg_api_hash: 
# 是否使用缓存 1 是 | 0 否
use_cache: 
# redis 地址，如果不使用缓存，则忽略以下两个字段
redis_host: 
redis_port: 
```

注：配置，记录和日志等文件存放在 `~/.tg_jav_bot` 目录下。

如需使用 Pikpak 自动发送功能，需要先手动授权 [Pikpak 官方机器人](https://t.me/PikPak6_Bot)，然后在初次运行机器人时进行登录操作。

### 运行机器人

**通过 docker 运行：**

```
docker-compose up -d
```

**或通过普通方法运行：**

```
# Python >=3.7, 如果使用缓存的话需先开启 redis 服务
pip install -r requirements.txt && python3 bot.py
```

### 更新机器人

首先拉取最新代码。

接着，如果是使用 docker 进行部署，则重新构建镜像并运行即可，参考命令：

```
docker-compose down && docker-compose up -d --build
```

如果是使用普通方法部署，则需要先更新 jvav 这个包，然后再运行机器人。([jvav](https://github.com/akynazh/jvav) 是从本项目分离出的一个子项目，现作为本项目的包依赖，同时服务于更多应用)
