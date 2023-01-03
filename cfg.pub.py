# 必填字段
TG_CHAT_ID = '' # your telegram chat id
TG_BOT_TOKEN = '' # your telegram bot token

# 可选字段：代理配置
USE_PROXY = 1 # 是否使用代理 1 是 | 0 否
# 如果不使用代理，以下四个字段不用管
PROXY_SCHEME = '' # 代理类型 http | socks5 | socks4
PROXY_ADDR_HOST = '' # IP地址
PROXY_ADDR_PORT = '' # 端口地址
PROXY_ADDR = f'{PROXY_SCHEME}://{PROXY_ADDR_HOST}:{PROXY_ADDR_PORT}' # 不用编辑该字段

# 可选字段：Pikpak配置
USE_PIKPAK = 0 # 是否使用Pikpak 1 是 | 0 否
# 如果不使用pikpak，以下三个字段不用管
PIKPAK_BOT_NAME = 'PikPak6_Bot' # 默认使用官方机器人：https://t.me/PikPak6_Bot
# 在这里申请api：https://my.telegram.org/apps
TG_API_ID = '' # telegram api id
TG_API_HASH = '' # telegram api hash