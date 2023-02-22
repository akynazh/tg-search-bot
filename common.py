# -*- coding: UTF-8 -*-
import os
import random
import requests
import typing
import logging
from bs4 import BeautifulSoup
from anti_useragent import UserAgent
import cfg

# 文件存储目录位置
PATH_ROOT = os.path.expanduser('~') + '/.tg_jav_bot'
if not os.path.exists(PATH_ROOT):
    os.mkdir(PATH_ROOT)
# 日志文件位置
PATH_LOG_FILE = PATH_ROOT + '/log.txt'
# 记录文件位置
PATH_RECORD_FILE = PATH_ROOT + '/record.json'
# my_account.session 文件位置
PATH_SESSION_FILE = PATH_ROOT + '/my_account'
# 全局代理变量
PROXY = {}
# DMM 代理变量
PROXY_DMM = {}
# PIKPAK 代理变量
PROXY_PIKPAK = {}
# 代理地址
PROXY_ADDR = f'{cfg.PROXY_SCHEME}://{cfg.PROXY_ADDR_HOST}:{cfg.PROXY_ADDR_PORT}'
if cfg.USE_PROXY == 1:
    PROXY = {'http': PROXY_ADDR, 'https': PROXY_ADDR}
    PROXY_PIKPAK = {
        'scheme': cfg.PROXY_SCHEME,
        'hostname': cfg.PROXY_ADDR_HOST,
        'port': int(cfg.PROXY_ADDR_PORT),
    }
if cfg.USE_PROXY_DMM == 1:
    PROXY_DMM = {'http': PROXY_ADDR, 'https': PROXY_ADDR}
# TG 对话 ID
TG_CHAT_ID = cfg.TG_CHAT_ID
# TG 机器人 Token
TG_BOT_TOKEN = cfg.TG_BOT_TOKEN
# 是否使用 Pikpak 自动发送功能
USE_PIKPAK = cfg.USE_PIKPAK
# TG API ID
TG_API_ID = cfg.TG_API_ID
# TG API HASH
TG_API_HASH = cfg.TG_API_HASH
# 项目地址
PROJECT_ADDRESS = 'https://github.com/akynazh/tg-jav-bot'
# 默认使用官方机器人：https://t.me/PikPak6_Bot
PIKPAK_BOT_NAME = 'PikPak6_Bot'
# Japan Wiki
BASE_URL_JAPAN_WIKI = 'https://ja.wikipedia.org/wiki'
# 联系作者
CONTACT_AUTHOR = 'https://t.me/jackbryant286'
# 请求超时时间
TIMEOUT_SECONDS = 3


class Logger:
    '''日志记录器
    '''

    def __init__(self, log_level):
        '''初始化日志记录器

        :param _type_ log_level: 记录级别
        '''
        self.logger = logging.getLogger()
        self.logger.addHandler(self.get_file_handler(PATH_LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        return file_handler


# 初始化日志记录器
LOG = Logger(log_level=logging.INFO).logger


def ua_mobile() -> str:
    '''返回手机端 UserAgent

    :return str: 手机端 UserAgent
    '''
    c = random.randint(0, 1)
    if c == 0:
        return UserAgent().android
    else:
        return UserAgent().iphone


def ua_desktop() -> str:
    '''返回桌面端 UserAgent

    :return str: 桌面端 UserAgent
    '''
    c = random.randint(0, 1)
    if c == 0:
        return UserAgent(platform='windows').random
    else:
        return UserAgent(platform='mac').random


def ua() -> str:
    '''随机返回 UserAgent

    :return str: UserAgent
    '''
    return UserAgent().random


def write_html(resp: requests.Response, file='t.html'):
    '''将 requests.Response.text 写入文件

    :param requests.Response resp
    :param str file: 文件名, defaults to 't.html'
    '''
    with open(file, 'w') as f:
        f.write(resp.text)


def send_req(
        url,
        proxies=PROXY,
        headers={'user-agent': ua()}) -> typing.Tuple[int, requests.Response]:
    '''发送请求

    :param _type_ url: 地址
    :param _type_ proxies: 代理, 默认读取配置的全局代理
    :param dict headers: 请求头, 默认使用随机请求头
    :return tuple[int, requests.Response] 状态码和请求返回值
    关于状态码：
    200：成功
    404：未找到
    502：网络问题
    '''
    try:
        resp = requests.get(url, proxies=proxies, headers=headers, timeout=TIMEOUT_SECONDS)
        if resp.status_code != 200:
            return 404, None
        return 200, resp
    except Exception as e:
        LOG.error(e)
        return 502, None


def get_soup(resp: requests.Response) -> BeautifulSoup:
    '''从请求结果得到 soup

    :param requests.Response resp: 请求结果
    :return BeautifulSoup
    '''
    return BeautifulSoup(resp.text, 'lxml')


if __name__ == '__main__':
    # print(ua())
    # print(ua_mobile())
    print(ua_desktop())