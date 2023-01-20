# -*- coding: UTF-8 -*-
import requests
import common
from bs4 import BeautifulSoup

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
    resp = requests.get(url=url, headers=headers, proxies=common.PROXY)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'lxml')
    # 获取预览视频地址
    res = soup.find(class_='btn')
    if not res:
        return None
    video_src = res.a['href']
    # video_src = video_src.replace('_sm_', '_dmb_')
    return video_src


if __name__ == '__main__':
    res = get_pv_by_id('ssni-369')
    if res: print(res)