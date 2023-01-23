# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import common

BASE_URL = 'https://www.dmm.co.jp/search/=/searchstr='


def get_pv_by_id(id: str) -> str:
    '''根据番号返回预览视频地址

    :param str id: 番号
    :return str: 预览视频地址
    '''
    # 搜索番号
    url = BASE_URL + id
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_mobile(),
        # 'accept-language': 'ja-JP'
    }
    resp = common.send_req(url=url, headers=headers, proxies=common.PROXY_DMM)
    if not resp: return None
    soup = BeautifulSoup(resp.text, 'lxml')
    # 获取预览视频地址
    res = soup.find(class_='btn')
    if res: return res.a['href']


def get_nice_pv_by_src(src: str) -> str:
    '''根据普通 src 获取更清晰的 src

    :param str src
    :return str: nice src
    '''
    return src.replace('_sm_', '_dmb_')


if __name__ == '__main__':
    res = get_pv_by_id('ssni-369')
    if res: print(res)