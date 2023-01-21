# 必填字段

# your telegram chat id
TG_CHAT_ID = ''
 # your telegram bot token
TG_BOT_TOKEN = ''

# 可选字段：关于代理的配置

# 是否使用代理 1 是 | 0 否
USE_PROXY = 1
 # 访问 DMM 是否使用代理 1 是 | 0 否 （该字段的值由自己决定，与 USE_PROXY 无关）
USE_PROXY_DMM = 1
# 如果不使用代理，以下三个字段不用管
# 代理类型 http | socks5 | socks4
PROXY_SCHEME = ''
# IP 地址
PROXY_ADDR_HOST = ''
# 端口地址
PROXY_ADDR_PORT = ''
# 不用编辑该字段
PROXY_ADDR = f'{PROXY_SCHEME}://{PROXY_ADDR_HOST}:{PROXY_ADDR_PORT}'

# 可选字段：关于自动发送磁链到 Pikpak 的配置

# 是否使用 Pikpak 自动发送功能 1 是 | 0 否
USE_PIKPAK = 0
# 如果不使用 pikpak 自动发送功能，以下三个字段不用管
# 默认使用官方机器人：https://t.me/PikPak6_Bot
PIKPAK_BOT_NAME = 'PikPak6_Bot'
# 在这里申请 api：https://my.telegram.org/apps
# telegram api id
TG_API_ID = ''
# telegram api hash
TG_API_HASH = ''