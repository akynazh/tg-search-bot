# -*- coding: UTF-8 -*-
import random
import requests
import logging
import os
from anti_useragent import UserAgent
import cfg

PATH_ROOT = os.path.expanduser('~') + '/.tg_jav_bot'
if not os.path.exists(PATH_ROOT):
    os.mkdir(PATH_ROOT)
PATH_LOG_FILE = PATH_ROOT + '/log.txt'
UA = UserAgent()
PROXY = {}
if cfg.USE_PROXY == 1:
    PROXY = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}
PROXY_DMM = {}
if cfg.USE_PROXY_DMM == 1:
    PROXY_DMM = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}


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


LOG = Logger(log_level=logging.INFO).logger


def ua_mobile() -> str:
    c = random.randint(0, 1)
    if c == 0:
        return UA.android
    else:
        return UA.iphone


def ua() -> str:
    return UA.random


def send_req(url,
             proxies=PROXY,
             headers={'user-agent': ua()}) -> requests.Response:
    '''发送请求

    :param _type_ url: 地址
    :param _type_ proxies: 代理, 默认读取配置的全局代理
    :param dict headers: 请求头, 默认使用随机请求头
    :return requests.Response
    '''
    resp = requests.get(url, proxies=proxies, headers=headers)
    if resp.status_code == 200:
        return resp


if __name__ == '__main__':
    print(ua_mobile())