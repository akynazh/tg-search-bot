# tg-search-bot

**一个可用于搜索各种影片磁链的电报机器人, 支持收藏, 导出记录, 自动保存磁链等操作, 可手动配置以屏蔽 NSFW 内容和代理上网。**

机器人基于 Python3 构建, 支持 Docker 一键部署, 并通过 Redis 实现了缓存功能。

机器人主要由 [akynazh](https://github.com/akynazh) 完成开发, 并结合社区力量进行了改进和优化, 感谢以下协作者:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

如果你也想为社区贡献自己的一份力量, 请查看 [TODO](https://github.com/akynazh/tg-search-bot#todo), 欢迎 issue 和 pr，可通过邮箱 [akynazh@qq.com](mailto://akynazh@qq.com)
或电报 [@jackbryant286](https://t.me/jackbryant286) 联系我。

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

编辑 `~/.tg_search_bot/config.yaml`：

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
# nsfw 1 是 | 0 否
enable_nsfw: 0
```

注：配置，记录和日志等文件存放在 `~/.tg_search_bot` 目录下。

如需使用 Pikpak 自动发送功能，需要先手动授权 [Pikpak 官方机器人](https://t.me/PikPak6_Bot)，然后在初次运行机器人时进行登录操作。

### 运行机器人

**通过 docker 运行：**

```
docker-compose up -d
```

**或通过普通方法运行：**

```
# Python >=3.10, 如果使用缓存的话需先开启 redis 服务
pip install -r requirements.txt && python3 bot.py
```
