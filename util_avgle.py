# -*- coding: UTF-8 -*-
import requests
import cfg

BASE_URL = 'https://api.avgle.com'
proxies = {}
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}


def get_video_by_id(id: str) -> dict:
    '''从avgle获取预览视频

    :param str id: 番号
    :return dict: 完整视频链接和预览视频链接
    {
        'fv': '', # 完整视频链接
        'pv': ''  # 预览视频链接
    }
    '''
    # 初始化数据
    page = 0
    limit = 3
    url = f'{BASE_URL}/v1/jav/{id}/{page}?limit={limit}'
    # 获取视频
    resp = requests.get(url, proxies=proxies)
    if resp.status_code == 200 and resp.json()['success']:
        videos = resp.json()['response']['videos']
        if videos != []:
            res = {'fv': '', 'pv': ''}
            for video in videos:
                fv_url = video['video_url'].strip()
                pv_url = video['preview_video_url'].strip()
                if res['fv'] == '' and fv_url != '': res['fv'] = fv_url
                if res['pv'] == '' and pv_url != '': res['pv'] = pv_url
            return res


if __name__ == '__main__':
    res = None
    res = get_video_by_id('ssni-497')
    if res: print(res)