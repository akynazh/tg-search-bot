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


def send_msg(msg) -> bool:
    '''发送消息到Pikpak机器人

    :param _type_ msg: 消息
    :return bool: 是否发送成功
    '''
    async def main():
        async with Client(
            name=SESSION_FILE_NAME, api_id=TG_API_ID, api_hash=TG_API_HASH, proxy=proxy
        ) as app:
            return await app.send_message(cfg.PIKPAK_BOT_NAME, msg)
    res = asyncio.run(main())
    if res: return True
    return False


if __name__ == "__main__":
    if send_msg("test"):
        print('ok')