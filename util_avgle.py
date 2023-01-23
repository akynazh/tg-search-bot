# -*- coding: UTF-8 -*-
import common

BASE_URL = 'https://api.avgle.com'


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
    res = {'fv': '', 'pv': ''}
    # 获取视频
    resp = common.send_req(url)
    if resp.json()['success']:
        videos = resp.json()['response']['videos']
        if videos != []:
            for video in videos:
                fv_url = video['video_url'].strip()
                pv_url = video['preview_video_url'].strip()
                if res['fv'] == '' and fv_url != '': res['fv'] = fv_url
                if res['pv'] == '' and pv_url != '': res['pv'] = pv_url
    return res


def get_pv_by_id(id: str) -> str:
    res = get_video_by_id(id)
    if res['pv'] != '': 
        return res['pv']


def get_fv_by_id(id: str) -> str:
    res = get_video_by_id(id)
    if res['fv'] != '': 
        return res['fv']


if __name__ == '__main__':
    # res = get_fv_by_id('ssni-497')
    # res = get_pv_by_id('ssni-497')
    res = get_pv_by_id('fc2-ppv-1901670')
    if res: print(res)