import asyncio
from pyrogram import Client
import cfg
# pip3 install -U tgcrypto # boost speed

api_id = cfg.TG_API_ID
api_hash = cfg.TG_API_HASH
my_proxy = {}
if cfg.USE_PROXY == 1:
    my_proxy = {
        "scheme": cfg.PROXY_SCHEME,
        "hostname": cfg.PROXY_ADDR_HOST,
        "port": int(cfg.PROXY_ADDR_PORT),
    }
session_file = 'my_account'

def send_msg(name, msg):
    async def main():
        async with Client(session_file, api_id, api_hash, proxy=my_proxy) as app:
            await app.send_message(name, msg)
    asyncio.run(main())
    
# send_msg('@PikPak6_Bot', 'test')