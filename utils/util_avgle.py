# -*- coding: UTF-8 -*-
import sys
import typing

sys.path.append('..')
import common

BASE_URL = 'https://api.avgle.com'


def get_video_by_id(id: str) -> typing.Tuple[int, dict]:
    '''根据番号从 avgle 获取视频
    :param str id: 番号
    :return tuple[int, dict]: 状态码，视频链接
    视频链接：
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
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    if resp.json()['success']:
        videos = resp.json()['response']['videos']
        if videos != []:
            for video in videos:
                fv_url = video['video_url'].strip()
                pv_url = video['preview_video_url'].strip()
                if res['fv'] == '' and fv_url != '': res['fv'] = fv_url
                if res['pv'] == '' and pv_url != '': res['pv'] = pv_url
        return code, res
    else:
        return 404, None


def get_pv_by_id(id: str) -> typing.Tuple[int, str]:
    '''根据番号从 avgle 获取预览视频
    :param str id: 番号
    :return tuple[int, str]: 状态码，预览视频链接
    '''
    code, res = get_video_by_id(id)
    if code != 200:
        return code, None
    if res['pv'] != '':
        return 200, res['pv']
    else:
        return 404, None


def get_fv_by_id(id: str) -> typing.Tuple[int, str]:
    '''根据番号从 avgle 获取完整视频
    :param str id: 番号
    :return tuple[int, str]: 状态码，完整视频链接
    '''
    code, res = get_video_by_id(id)
    if code != 200:
        return code, None
    if res['pv'] != '':
        return 200, res['fv']
    else:
        return 404, None


if __name__ == '__main__':
    # code, res = get_fv_by_id('ssni-497')
    # code, res = get_pv_by_id('ssni-497')
    code, res = get_pv_by_id('fc2-ppv-1901670')
    if code == 200:
        print(res)