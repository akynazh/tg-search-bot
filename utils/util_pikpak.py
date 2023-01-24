# -*- coding: UTF-8 -*-
from pyrogram import Client
import asyncio
import sys

sys.path.append('..')
import common


def send_msg(msg) -> int:
    '''发送消息到Pikpak机器人

    :param _type_ msg: 消息
    :return any: 如果失败则为 None
    '''

    async def main():
        async with Client(name=common.PATH_SESSION_FILE,
                          api_id=common.TG_API_ID,
                          api_hash=common.TG_API_HASH,
                          proxy=common.PROXY_PIKPAK) as app:
            return await app.send_message(common.PIKPAK_BOT_NAME, msg)

    try:
        return asyncio.run(main())
    except Exception as e:
        return None


if __name__ == '__main__':
    if send_msg('from tg-jav-bot'):
        print('ok')
