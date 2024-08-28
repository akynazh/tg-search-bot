# tg-search-bot

A Telegram bot that can be used to search for various video magnet links. It supports operations such as collection, exporting records, and automatically saving magnet links. It can be manually configured to block NSFW content and proxy Internet access.

The bot is built based on Python3, supports one-click deployment with Docker, and implements caching functions through Redis.

## Functions

The following functions are sorted by development completion time, and new functions will be continuously added in the future.

- Supports obtaining basic video information and magnet links - 2022/11/25
- Support configuration proxy - 2022/11/26
- Support allowing bot to automatically save optimal magnet links to Pikpak - 2022/12/29
- Support getting preview video and full video - 2022/12/31
- Support obtaining video screenshots - 2023/01/01
- Support collection of actors and videos - 2023/01/04
- Support deployment via docker - 2023/01/08
- Supports obtaining actor rankings and film ratings - 2023/01/20
- Supports random access to high-scoring videos and latest videos - 2023/01/25
- Support searching for actors - 2023/02/18
- Support caching through redis - 2023/03/17

## Tutorial

First, you need to download the code, then configure the bot and edit `~/.tg_search_bot/config.yaml`：

```yaml
# required, your telegram chat id
tg_chat_id: 
# required, your telegram bot token
tg_bot_token: 
# required, global proxy, 1 yes | 0 no
use_proxy: 
# optional, proxy server address, required if use_proxy == 1
proxy_addr: 
# your telegram api id
tg_api_id: 
# your telegram api hash
tg_api_hash: 
# your redis host
redis_host: 
# your redis port
redis_port: 
# optional, your redis password, empty by default when using docker
redis_password: 
# required, enable nsfw or not, 1 yes | 0 no
enable_nsfw: 0
```

PS: To use Pikpak’s automatic sending function, you need to authorize it manually first: [Pikpak official bot](https://t.me/PikPak6_Bot), and then log in when running the bot for the first time.

Finally, run the bot: (files such as records and logs are located in `~/.tg_search_bot`)

```sh
# op1. docker-compose
docker-compose up -d
# op2. simple way (Python >=3.9)
pip install -r requirements.txt && python3 bot.py
```

## Development

I use python-3.9.13 for development. Please use python <= 3.9 for development. In addition, it is recommended to use python virtual environment development to avoid unnecessary problems. The following are my development steps for reference only:

```shell
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
~/.pyenv/versions/3.9.13/bin/python -m venv .venv
source ./.venv/bin/activate
pip3 install -r requirements.txt
```

Then you can start writing code. When you are done, remember to write or run a test instance (in `tests/test.py`). Please make sure there is no problem with the test before submitting the code.

## Thanks

<a href="https://www.jetbrains.com/">
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains Logo (Main) logo." style="width: 200px;"></a>

Thanks to JetBrains for their support to this project!
