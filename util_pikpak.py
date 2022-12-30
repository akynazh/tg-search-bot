# -*- coding: UTF-8 -*-
from pyrogram import Client
import asyncio
import cfg

TG_API_ID = cfg.TG_API_ID
TG_API_HASH = cfg.TG_API_HASH
SESSION_FILE_NAME = "my_account"
proxy = {}
if cfg.USE_PROXY == 1:
    proxy = {
        "scheme": cfg.PROXY_SCHEME,
        "hostname": cfg.PROXY_ADDR_HOST,
        "port": int(cfg.PROXY_ADDR_PORT),
    }


def send_msg(msg):
    pikpak_bot_name = cfg.PIKPAK_BOT_NAME

    async def main():
        async with Client(
            name=SESSION_FILE_NAME, api_id=TG_API_ID, api_hash=TG_API_HASH, proxy=proxy
        ) as app:
            await app.send_message(pikpak_bot_name, msg)

    asyncio.run(main())


if __name__ == "__main__":
    send_msg("test")
