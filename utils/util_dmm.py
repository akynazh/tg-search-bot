# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import sys
import typing
import concurrent.futures

sys.path.append('..')
import common

BASE_URL = 'https://www.dmm.co.jp'
BASE_URL_SEARCH_AV = BASE_URL + '/search/=/searchstr='
BASE_URL_TOP_STARS = BASE_URL + '/digital/videoa/-/ranking/=/type=actress'


def get_pv_by_id(id: str) -> typing.Tuple[int, str]:
    '''根据番号从 DMM 获取预览视频地址

    :param str id: 番号
    :return tuple[int, str]: 状态码和预览视频地址
    '''
    # 搜索番号
    url = BASE_URL_SEARCH_AV + id
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_mobile(),  # 手机端页面更方便爬取
    }
    code, resp = common.send_req(url=url,
                                 headers=headers,
                                 proxies=common.PROXY_DMM)
    if code != 200:
        return code, None
    soup = BeautifulSoup(resp.text, 'lxml')
    # 获取预览视频地址
    res = soup.find(class_='btn')
    if res:
        return 200, res.a['href']
    else:
        return 404, None


def get_score_by_id(id: str) -> typing.Tuple[int, str]:
    '''根据番号返回评分

    :param str id: 番号
    :return tuple[int, str]: 状态码和评分
    '''
    # 搜索番号
    url = BASE_URL_SEARCH_AV + id
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_desktop(),  # 桌面端页面更方便爬取
    }
    code, resp = common.send_req(url=url,
                                 headers=headers,
                                 proxies=common.PROXY_DMM)
    if code != 200:
        return code, resp
    soup = BeautifulSoup(resp.text, 'lxml')
    res = soup.find(class_='rate')
    if res:
        return 200, res.span.span.text
    else:
        return 404, None


def get_nice_pv_by_src(src: str) -> str:
    '''根据普通 src 获取更清晰的 src

    :param str src
    :return str: nice src
    '''
    return src.replace('_sm_', '_dmb_')


def get_top_stars(page=1) -> typing.Tuple[int, list]:
    '''根据页数获取明星排行榜某页中的明星列表

    :param int page: 页数，共 5 页，每页 20 位，共 100 位， defaults to 1
    :return tuple[int, list]: 状态码和明星列表
    '''
    url = BASE_URL_TOP_STARS + f'/page={page}/'
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_desktop(),
    }
    code, resp = common.send_req(url=url,
                                 headers=headers,
                                 proxies=common.PROXY_DMM)
    if code != 200:
        return code, None
    soup = BeautifulSoup(resp.text, 'lxml')
    res = soup.find_all(class_='data')
    if res:
        return 200, [obj.p.a.text for obj in res]
    else:
        return 404, None


def get_all_top_stars() -> typing.Tuple[int, list]:
    '''获取 DMM 排行榜前 100 名女优

    :return tuple[int, list]: 状态码和女优名称列表
    '''
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # 爬取第一到第五页数据
        futures = {
            executor.submit(get_top_stars, page): page
            for page in range(1, 6)
        }
        results = {}
        # 等待并获取数据
        for future in concurrent.futures.as_completed(futures):
            code, res = future.result()
            if code != 200:
                return 502, None
            results[futures[future]] = res
        stars = []
        for i in range(1, 6):
            stars += results[i]
        return 200, stars


if __name__ == '__main__':
    code, res = get_pv_by_id('ssni-369')
    # code, res = get_score_by_id('ssni-369')
    # code, res = get_top_stars(3)
    # code, res = get_all_top_stars()
    if code == 200: print(res)