# -*- coding: UTF-8 -*-
import re
import random
import sys
import typing

sys.path.append('..')
import common

BASE_URL = 'https://www.javbus.com'
# BASE_URL = 'https://www.seejav.me'
HOME_MAX_PAGE = 100


def get_max_page(url: str) -> typing.Tuple[int, int]:
    '''获取最大页数（只适用于不超过 10 页的页面）

    :param str url: 页面地址
    :return tuple[int, int]: 状态码和最大页数
    '''
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    soup = common.get_soup(resp)
    tag_pagination = soup.find(class_='pagination pagination-lg')
    # 如果没有分页块则只有第一页
    if not tag_pagination:
        return 200, 1
    try:
        tags_li = tag_pagination.find_all('li')
        return 200, int(tags_li[len(tags_li) - 2].a.text)
    except Exception:
        return 404, None


def get_id_from_page(base_page_url: str, page=-1) -> typing.Tuple[int, str]:
    '''从 av 列表页面获取一个番号

    :param str base_page: 基础页地址，也是第一页地址
    :param int page: 用于指定爬取哪一页的数据，默认值为 -1，表示随机获取某一页
    :return tuple[int, str]: 状态码和番号
    '''
    # 准备 url 地址
    url = ''
    if page != -1:
        url = f'{base_page_url}/{page}'
    else:
        code, max_page = get_max_page(base_page_url)
        if code != 200:
            return code, None
        url = f'{base_page_url}/{random.randint(1, max_page)}'
    # 开始获取番号
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    ids = []
    soup = common.get_soup(resp)
    tags = soup.find_all(class_='movie-box')
    if not tags:
        return 404, None
    try:
        for tag in tags:
            id_link = tag['href']
            id = id_link[id_link.rfind('/') + 1:]
            ids.append(id)
        if ids != []:
            return 200, random.choice(ids)
        else:
            return 404, None
    except Exception:
        return 404, None


def get_id_from_home(page=-1) -> typing.Tuple[int, str]:
    '''从 javbus 主页获取一个番号

    :param int page: 用于指定爬取哪一页的数据，默认值为 -1，表示随机获取某一页
    :return tuple[int, str]: 状态码和番号
    '''
    if page == -1:
        page = random.randint(1, HOME_MAX_PAGE)
    return get_id_from_page(base_page_url=BASE_URL + '/page', page=page)


def get_id_by_star_name(star_name: str, page=-1) -> typing.Tuple[int, str]:
    '''根据演员名称获取一个番号

    :param str star_name: 演员名称
    :param int page: 用于指定爬取哪一页的数据，默认值为 -1，表示随机获取某一页
    :return tuple[int, str]: 状态码和番号
    '''
    return get_id_from_page(base_page_url=f'{BASE_URL}/search/{star_name}',
                            page=page)


def get_id_by_star_id(star_id: str, page=-1) -> typing.Tuple[int, str]:
    '''根据演员编号获取一个番号

    :param str star_id: 演员编号
    :param int page: 用于指定爬取哪一页的数据，默认值为 -1，表示随机获取某一页
    :return tuple[int, str]: 状态码和番号
    '''
    return get_id_from_page(base_page_url=f'{BASE_URL}/star/{star_id}',
                            page=page)


def get_samples_by_id(id: str) -> typing.Tuple[int, list]:
    '''根据番号获取截图

    :param str id: 番号
    :return tuple[int, list]: 状态码和截图列表
    '''
    # 初始化数据
    samples = []
    url = f'{BASE_URL}/{id}'
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    # 获取soup
    soup = common.get_soup(resp)
    # 获取截图
    sample_tags = soup.find_all(class_='sample-box')
    if not sample_tags:
        return 404, None
    try:
        for tag in sample_tags:
            sample_link = tag['href']
            if sample_link.find('https') == -1:
                sample_link = BASE_URL + sample_link
            samples.append(sample_link)
        if samples == []:
            return 404, None
        return 200, samples
    except Exception:
        return 404, None


def get_nice_magnets(magnets: list, prop: str, expect_val: any) -> list:
    '''过滤磁链列表

    :param list magnets: 要过滤的磁链列表
    :param str prop: 过滤属性
    :param any expect_val: 过滤属性的期望值
    :return list: 过滤后的磁链列表
    '''
    # 已经无法再过滤
    if len(magnets) == 0:
        return []
    if len(magnets) == 1:
        return magnets
    # 开始过滤
    magnets_nice = []
    for magnet in magnets:
        if magnet[prop] == expect_val:
            magnets_nice.append(magnet)
    # 如果过滤后已经没了，返回原来磁链列表
    if len(magnets_nice) == 0:
        return magnets
    return magnets_nice


def sort_magnets(magnets: list) -> list:
    '''根据大小排列磁链列表

    :param list magnets: 磁链列表
    :return list: 排列好的磁链列表
    '''
    # 统一单位为 MB
    for magnet in magnets:
        size = magnet['size']
        gb_idx = size.lower().find('gb')
        mb_idx = size.lower().find('mb')
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
    '''通过 javbus 获取番号对应 av

    :param str id: 番号
    :param bool is_nice: 是否过滤磁链
    :param int magnet_max_count: 过滤后磁链的最大数目
    :return tuple[int, dict]: 状态码和 av
    av格式:
    {
        'id': '',      # 番号
        'title': '',   # 标题
        'img': '',     # 封面地址
        'date': '',    # 发行日期
        'tags': '',    # 标签
        'stars': [],   # 演员
        'magnets': [], # 磁链
    }
    磁链格式:
    {
        'link': '', # 链接
        'size': '', # 大小
        'hd': '0',  # 是否高清 0 否 | 1 是
        'zm': '0',   # 是否有字幕 0 否 | 1 是
        'size_no_unit': 浮点值 # 去除单位后的大小值，用于排序，当要求过滤磁链时会存在该字段
    }
    演员格式:
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
    url = f'{BASE_URL}/{id}'
    code, resp = common.send_req(url)
    if code != 200:
        return code, None
    # 获取soup和html
    soup = common.get_soup(resp)
    html = soup.prettify()
    # 获取封面和标题
    big_image = soup.find(class_='bigImage')
    img = None
    if big_image:
        img = big_image['href']
        if img.find('http') == -1:
            av['img'] = BASE_URL + img
            av['title'] = big_image.img['title']
    # 提取更多信息
    try:
        paras = soup.find(class_='col-md-3 info').find_all('p')
        for i, p in enumerate(paras):
            # 获取发行日期
            if p.text.find('發行日期:') != -1:
                av['date'] = ''.join(
                    p.text.replace('發行日期:', '').replace('"', '').split())
            # 获取标签
            elif p.text.find('類別:') != -1:
                tags = paras[i + 1].find_all('a')
                for tag in tags:
                    av['tags'] += ''.join(tag.text.split()) + ' '
                av['tags'] = av['tags'].strip()
            # 获取演员
            elif i == len(paras) - 1:
                tags = p.find_all('a')
                for tag in tags:
                    star = {'name': '', 'link': ''}
                    star['name'] = ''.join(tag.text.split())
                    star['link'] = tag['href']
                    av['stars'].append(star)
    except Exception:
        pass
    # 获取uc
    uc_pattern = re.compile(r'var uc = .*?;')
    match = uc_pattern.findall(html)
    uc = None
    if match:
        uc = match[0].replace('var uc = ', '').replace(';', '')
    # 获取gid
    gid_pattern = re.compile(r'var gid = .*?;')
    match = gid_pattern.findall(html)
    gid = None
    if match:
        gid = match[0].replace('var gid = ', '').replace(';', '')
    # 如果不存在磁链则直接返回
    if not uc and not gid:
        return 200, av
    # 得到磁链的ajax请求地址
    url = f'{BASE_URL}/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&uc={uc}'
    headers = {
        'user-agent': common.ua(),
        'referer': f'{BASE_URL}/{id}',
    }
    # 发送请求获取含磁链页
    code, resp = common.send_req(url=url, headers=headers)
    # 如果不存在磁链或请求失败则直接返回
    if code != 200:
        return 200, av
    soup = common.get_soup(resp)
    trs = soup.find_all('tr')
    if not trs:
        return 200, av
    # 解析页面获取磁链
    try:
        for tr in trs:
            i = 0
            magnet = {'link': '', 'hd': '0', 'zm': '0'}
            for td in tr:
                if td.string:
                    continue
                i += 1
                magnet['link'] = td.a['href']
                if i % 3 == 1:
                    links = td.find_all('a')
                    for link in links:
                        text = link.text.strip()
                        if text == '高清':
                            magnet['hd'] = '1'
                        elif text == '字幕':
                            magnet['zm'] = '1'
                if i % 3 == 2:
                    magnet['size'] = td.a.text.strip()
            if magnet['link'] != '':
                av['magnets'].append(magnet)
        if is_nice:
            magnets = av['magnets']
            magnets = get_nice_magnets(magnets, 'hd', expect_val='1')  # 过滤高清
            magnets = get_nice_magnets(magnets, 'zm', expect_val='1')  # 过滤有字幕
            magnets = sort_magnets(magnets)  # 从大到小排序
            if len(magnets) > magnet_max_count:
                magnets = magnets[0:magnet_max_count]
            av['magnets'] = magnets
    except Exception:
        pass
    return 200, av


if __name__ == '__main__':
    code, res = get_av_by_id(id='GTJ-111', is_nice=True, magnet_max_count=3)
    # code, res = get_av_by_id(id='ipx-811', is_nice=False)
    # code, res = get_samples_by_id('ssni-497')
    # code, res = get_id_by_star_id('okq', 2)
    # code, res = get_id_by_star_name('白夜みくる')
    # code, res = get_max_page('https://www.javbus.com/star/okq')
    # code, res = get_id_by_star_id('okq')
    # code, res = get_id_by_star_name('三上悠亜')
    # code, res = get_id_from_home()
    if code == 200: print(res)