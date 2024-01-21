# tg-search-bot

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

**一个可用于搜索各种影片磁链的电报机器人, 支持收藏, 导出记录, 自动保存磁链等操作, 可手动配置以屏蔽 NSFW 内容和代理上网。**

机器人基于 Python3 构建, 支持 Docker 一键部署, 并通过 Redis 实现了缓存功能, 主要由 [akynazh](https://github.com/akynazh) 完成开发, 并结合社区力量进行了改进和优化, 感谢以下协作者:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://akynazh.site"><img src="https://avatars.githubusercontent.com/u/78672905?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Jack Bryant</b></sub></a><br /><a href="#maintenance-akynazh" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/z-hhh"><img src="https://avatars.githubusercontent.com/u/8455958?v=4?s=100" width="100px;" alt="zhhh"/><br /><sub><b>zhhh</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=z-hhh" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://allcontributors.org"><img src="https://avatars.githubusercontent.com/u/46410174?v=4?s=100" width="100px;" alt="All Contributors"/><br /><sub><b>All Contributors</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=all-contributors" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/JackBryant286"><img src="https://avatars.githubusercontent.com/u/113345781?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Julia</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=JackBryant286" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

如果你也想为社区贡献自己的一份力量, 请查看 [开发步骤](https://github.com/akynazh/tg-search-bot#开发步骤) 和 [TODO](https://github.com/akynazh/tg-search-bot#todo), 欢迎 issue 和 pr。

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

## 使用教程

首先需要下载本项目代码到本地，然后配置机器人，编辑 `~/.tg_search_bot/config.yaml`：

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

PS: 如需使用 Pikpak 自动发送功能，需要先手动授权 [Pikpak 官方机器人](https://t.me/PikPak6_Bot)，然后在初次运行机器人时进行登录操作。(我的 Pikpak 邀请码: 99492001, 输入可得会员)

最后运行机器人即可：(记录和日志等文件位于 `~/.tg_search_bot` 目录下)

```sh
# 方法一: 通过 docker 运行：(推荐)
docker-compose up -d
# 方法二: 通过普通方法运行:（Python >=3.10, 如果使用缓存的话需先开启 redis 服务）
pip install -r requirements.txt && python3 bot.py
```

## 开发步骤

我使用 python-3.10.9 进行开发，请使用 python <= 3.10 进行开发，另外，推荐使用 python 虚拟环境开发以避免出现一些不必要的问题。下面是一个我的开发步骤，仅供参考：

```shell
# python=3.10.9
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

接着就可以开始写代码了，完成后记得编写或运行测试实例(在 `tests/test.py` 中)。请确保测试没问题再提交代码哟～

## TODO

- 英文版本
- 影片搜索支持更多磁力网站(目前只支持了海盗湾)
- 其他你希望出现的功能...
