import cfg
import random
from anti_useragent import UserAgent

UA = UserAgent()

PROXY = {}
if cfg.USE_PROXY == 1:
    PROXY = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}

PROXY_DMM = {}
if cfg.USE_PROXY_DMM == 1:
    PROXY_DMM = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}

def ua_mobile() -> str:
    c = random.randint(0, 1)
    if c == 0:
        return UA.android
    else:
        return UA.iphone


def ua() -> str:
    return UA.random


if __name__ == '__main__':
    # print(ua_mobile())
    # print(ua())
    print(PROXY)