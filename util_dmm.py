# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import common
import concurrent.futures

BASE_URL = 'https://www.dmm.co.jp'
BASE_URL_SEARCH_AV = BASE_URL + '/search/=/searchstr='
BASE_URL_TOP_STARS = BASE_URL + '/digital/videoa/-/ranking/=/type=actress'


def get_pv_by_id(id: str) -> str:
    '''根据番号返回预览视频地址

    :param str id: 番号
    :return str: 预览视频地址
    '''
    # 搜索番号
    url = BASE_URL_SEARCH_AV + id
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_mobile(),
    }
    resp = common.send_req(url=url, headers=headers, proxies=common.PROXY_DMM)
    if not resp: return None
    soup = BeautifulSoup(resp.text, 'lxml')
    # 获取预览视频地址
    res = soup.find(class_='btn')
    if res: return res.a['href']


def get_score_by_id(id: str) -> str:
    '''根据番号返回评分

    :param str id: 番号
    :return str: 评分
    '''
    # 搜索番号
    url = BASE_URL_SEARCH_AV + id
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_desktop(),
    }
    resp = common.send_req(url=url, headers=headers, proxies=common.PROXY_DMM)
    if not resp: return None
    soup = BeautifulSoup(resp.text, 'lxml')
    res = soup.find(class_='rate')
    return res.span.span.text


def get_nice_pv_by_src(src: str) -> str:
    '''根据普通 src 获取更清晰的 src

    :param str src
    :return str: nice src
    '''
    return src.replace('_sm_', '_dmb_')


def get_top_stars(page=1) -> list:
    '''根据页数获取明星排行榜某页中的明星列表

    :param int page: 页数，共5页，每页20位，共100位 defaults to 1
    :return list: 明星列表
    '''
    url = BASE_URL_TOP_STARS + f'/page={page}/'
    headers = {
        'cookie': 'age_check_done=1;',
        'user-agent': common.ua_desktop(),
    }
    resp = common.send_req(url=url, headers=headers, proxies=common.PROXY_DMM)
    if not resp: return None
    soup = BeautifulSoup(resp.text, 'lxml')
    res = soup.find_all(class_='data')
    return [obj.p.a.text for obj in res]


def get_all_top_stars() -> list:
    '''获取dmm排行榜前100名女优

    :return list: 女优名称列表
    '''
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(get_top_stars, page): page
            for page in range(1, 6)
        }
        results = {}
        for future in concurrent.futures.as_completed(futures):
            try:
                results[futures[future]] = future.result()
            except Exception:
                return None
        stars = []
        for i in range(1, 6):
            stars += results[i]
        return stars


if __name__ == '__main__':
    # res = get_pv_by_id('ssni-369')
    # res = get_score_by_id('ssni-369')
    # res = get_top_stars(3)
    res = get_all_top_stars()
    if res: print(res)