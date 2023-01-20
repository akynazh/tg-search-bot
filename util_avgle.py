# -*- coding: UTF-8 -*-
import requests
import common

BASE_URL = 'https://api.avgle.com'


def get_fv_by_id(id: str) -> str:
    '''从avgle获取番号对应视频地址

    :param str id: 番号
    :return str: 视频地址
    '''
    # 初始化数据
    page = 0
    limit = 3
    url = f'{BASE_URL}/v1/jav/{id}/{page}?limit={limit}'
    # 获取视频
    resp = requests.get(url, proxies=common.PROXY)
    if resp.status_code == 200 and resp.json()['success']:
        videos = resp.json()['response']['videos']
        if videos != []:
            for video in videos:
                fv_url = video['video_url'].strip()
                if fv_url != '':
                    return fv_url


if __name__ == '__main__':
    res = get_fv_by_id('ssni-497')
    if res: print(res)