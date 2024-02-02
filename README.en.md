# tg-search-bot

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

**A Telegram robot that can be used to search for various video magnet links. It supports operations such as collection, exporting records, and automatically saving magnet links. It can be manually configured to block NSFW content and proxy Internet access.**

The robot is built based on Python3, supports one-click deployment with Docker, and implements caching functions through Redis.

## Function introduction

The following functions are sorted by development completion time, and new functions will be continuously added in the future.

-   Supports obtaining basic video information and magnet links - 2022/11/25
-   Support configuration proxy - 2022/11/26
-   Support filtering magnet links (uncensored => hd => subtitle)- 2022/11/26
-   Support allowing robots to automatically save optimal magnet links to Pikpak - 2022/12/29
-   Support getting preview video and full video - 2022/12/31
-   Support obtaining video screenshots - 2023/01/01
-   Support collection of actors and videos - 2023/01/04
-   Support deployment via docker - 2023/01/08
-   Supports obtaining actor rankings and film ratings - 2023/01/20
-   Supports random access to high-scoring videos and latest videos - 2023/01/25
-   Support obtaining actors’ Chinese names through Wikipedia - 2023/02/18
-   Support translation of Japanese titles - 2023/02/18
-   Support searching for actors - 2023/02/18
-   Support caching through redis - 2023/03/17

## Tutorial

First, you need to download the project code locally, then configure the robot and edit`~/.tg_search_bot/config.yaml`：

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

PS: If you want to use Pikpak’s automatic sending function, you need to authorize it manually first.[Pikpak official robot](https://t.me/PikPak6_Bot), and then log in when running the robot for the first time. (My Pikpak invitation code: 99492001, enter to get membership)

Finally, run the robot: (files such as records and logs are located in`~/.tg_search_bot`Under contents)

```sh
# 方法一: 通过 docker 运行：(推荐)
docker-compose up -d
# 方法二: 通过普通方法运行:（Python >=3.10, 如果使用缓存的话需先开启 redis 服务）
pip install -r requirements.txt && python3 bot.py
```

## Development steps

I use python-3.10.9 for development. Please use python &lt;= 3.10 for development. In addition, it is recommended to use python virtual environment development to avoid unnecessary problems. The following are my development steps for reference only:

```shell
# python=3.10.9
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

Then you can start writing code. When you are done, remember to write or run a test instance (in`tests/test.py`middle). Please make sure there is no problem with the test before submitting the code~

## ALL

-   English version
-   Video search supports more magnetic websites (currently only The Pirate Bay is supported)
-   Other features you would like to see appear...

## Acknowledgments

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

If you also want to contribute to the community, please check out[ALL](https://github.com/akynazh/tg-search-bot#todo), and based on[Development steps](https://github.com/akynazh/tg-search-bot#开发步骤)For development, issues and PRs are welcome.
