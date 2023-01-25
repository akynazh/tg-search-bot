# -*- coding: UTF-8 -*-
import sys
import typing

sys.path.append('..')
import common

BASE_URL = 'https://sukebei.nyaa.si'


def sort_magnets(magnets: list) -> list:
    # 统一单位为 MB
    for magnet in magnets:
        size = magnet['size']
        gb_idx = size.lower().find('gib')
        mb_idx = size.lower().find('mib')
        if gb_idx != -1:  # 单位为 GB
            magnet['size_no_unit'] = float(size[:gb_idx]) * 1024
        elif mb_idx != -1:  # 单位为 MB
            magnet['size_no_unit'] = float(size[:mb_idx])
    # 根据 size_no_unit 大小排序
    magnets = sorted(magnets, key=lambda m: m['size_no_unit'], reverse=True)
    return magnets


def get_av_by_id(id: str,
                 is_nice: bool,
                 magnet_max_count=100) -> typing.Tuple[int, dict]:
    '''通过 sukebei 获取番号对应 av

    :param str id: 番号
    :param bool is_nice: 是否过滤磁链
    :param int magnet_max_count: 过滤后磁链的最大数目
    :return tuple[int, dict]: 状态码和 av
    av格式:
    {
        'id': '',      # 番号
        'title': '',   # 标题
        'img': '',     # 封面地址 | sukebei 不支持
        'date': '',    # 发行日期 | sukebei 不支持
        'tags': '',    # 标签 | sukebei 不支持
        'stars': [],   # 演员 | sukebei 不支持
        'magnets': [], # 磁链
    }
    磁链格式:
    {
        'link': '', # 链接
        'size': '', # 大小
        'hd': '0',  # 是否高清 0 否 | 1 是 | sukebei 不支持
        'zm': '0',   # 是否有字幕 0 否 | 1 是 | sukebei 不支持
        'size_no_unit': 浮点值 # 去除单位后的大小值，用于排序，当要求过滤磁链时会存在该字段
    }
    演员格式: | sukebei 不支持
    {
        'name': '', # 演员名称
        'link': ''    # 演员链接
    }
    '''
    # 初始化数据
    av = {
        'id': id,
        'title': '',
        'img': '',
        'date': '',
        'tags': '',
        'stars': [],
        'magnets': [],
    }
    # 查找av
    url = f'{BASE_URL}?q={id}'
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    # 获取soup
    soup = common.get_soup(resp)
    torrent_list = soup.find(class_='torrent-list')
    if not torrent_list:
        return 404, None
    # 开始解析
    trs = torrent_list.tbody.find_all('tr')
    if not trs:
        return 404, None
    try:
        for i, tr in enumerate(trs):
            tds = tr.find_all('td')
            magnet = {
                'link': '',  # 链接
                'size': '',  # 大小
                'hd': '0',  # 是否高清 0 否 | 1 是
                'zm': '0'  # 是否有字幕 0 否 | 1 是
            }
            for j, td in enumerate(tds):
                if j == 1:  # 获取标题
                    title = td.a.text
                    if i == 0: av['title'] = title
                if j == 2:  # 获取磁链
                    magnet['link'] = td.find_all('a')[-1]['href']
                if j == 3:  # 获取大小
                    magnet['size'] = td.text
            av['magnets'].append(magnet)
        # 过滤番号
        if is_nice:
            magnets = av['magnets']
            if len(magnets) > magnet_max_count:
                magnets = magnets[0:magnet_max_count]
            magnets = sort_magnets(magnets)
            av['magnets'] = magnets
    except Exception:
        return 404, av
    return 200, av


if __name__ == '__main__':
    res = get_av_by_id(id='fc2-ppv-880652', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='880652', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='siro-3352', is_nice=True, magnet_max_count=3)
    if res: print(res)