# -*- coding: UTF-8 -*-
import cfg
import requests

BASE_URL = 'https://api.avgle.com'
proxies = {}
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}


def get_video(id: str) -> dict:
    '''avgle.com获取预览视频

    :param str id: 番号
    :return dict: 完整视频链接和预览视频链接
    {
        'fv': '', # 完整视频链接
        'pv': ''  # 预览视频链接
    }
    '''
    page = 0
    limit = 3
    url = f'{BASE_URL}/v1/jav/{id}/{page}?limit={limit}'

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


def get_pv(id: str) -> str:
    '''获取预览视频

    :param str id: 番号
    :return str: 链接地址
    '''
    video = get_video(id)
    if video and video['pv'] != '': return video['pv']


def get_fv(id: str) -> str:
    '''获取完整视频

    :param str id: 番号
    :return str: 链接地址
    '''
    video = get_video(id)
    if video and video['fv'] != '': return video['fv']


if __name__ == '__main__':
    v = get_video('ipx-369')
    if v: print(v)
