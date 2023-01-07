# -*- coding: UTF-8 -*-
import requests
import re
import cfg
import random
from bs4 import BeautifulSoup

BASE_URL = 'https://www.javbus.com'
# BASE_URL = 'https://www.seejav.me'
HOST = BASE_URL.split('://')[1]
HOME_MAX_PAGE = 100
proxies = {}
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}


def get_headers(url: str) -> dict:
    '''获取请求头

    :param str url: 'Referer'字段值，访问源至哪里来
    :return dict: 请求头
    '''
    return {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
        'Host': HOST,
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': url.encode('utf-8'),
    }


def get_max_page(url: str) -> int:
    '''获取最大页数（只适用于不超过10页的页面）

    :param str url: 页面地址
    :return int: 最大页数
    '''
    resp = requests.get(url=url, proxies=proxies, headers=get_headers(url))
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'lxml')
    tag_pagination = soup.find(class_='pagination pagination-lg')
    # 如果没有分页块则只有第一页
    if not tag_pagination: return 1
    tags_li = tag_pagination.find_all('li')
    return int(tags_li[len(tags_li) - 2].a.text)


def get_id_from_page(base_page_url: str, page=-1) -> str:
    '''从av列表页面获取一个番号

    :param str base_page: 基础页地址，也是第一页地址
    :param int page: 用于指定爬取哪一页的数据，默认值为-1，表示随机获取某一页
    :return str: 番号
    '''
    # 准备url地址
    url = ''
    if page != -1:
        url = f'{base_page_url}/{page}'
    else:
        max_page = get_max_page(base_page_url)
        if max_page:
            url = f'{base_page_url}/{random.randint(1, max_page)}'
    if url == '': return None
    # 开始获取番号
    resp = requests.get(url=url, proxies=proxies, headers=get_headers(url))
    if resp.status_code != 200:
        return None
    ids = []
    soup = BeautifulSoup(resp.text, 'lxml')
    tags = soup.find_all(class_='movie-box')
    for tag in tags:
        id_link = tag['href']
        id = id_link[id_link.rfind('/') + 1:]
        ids.append(id)
    if ids != []:
        return random.choice(ids)


def get_id_from_home(page=-1) -> str:
    '''从javbus主页获取一个番号

    :param int page: 用于指定爬取哪一页的数据，默认值为-1，表示随机获取某一页
    :return str: 番号
    '''
    if page == -1:
        page = random.randint(1, HOME_MAX_PAGE)
    return get_id_from_page(base_page_url=BASE_URL + '/page', page=page)


def get_id_by_star_name(star_name: str, page=-1) -> str:
    '''根据演员名称获取一个番号

    :param str star_name: 演员名称
    :param int page: 用于指定爬取哪一页的数据，默认值为-1，表示随机获取某一页
    :return str: 番号
    '''
    return get_id_from_page(base_page_url=f'{BASE_URL}/search/{star_name}',
                            page=page)


def get_id_by_star_id(star_id: str, page=-1) -> str:
    '''根据演员编号获取一个番号

    :param str star_id: 演员编号
    :param int page: 用于指定爬取哪一页的数据，默认值为-1，表示随机获取某一页
    :return str: 番号
    '''
    return get_id_from_page(base_page_url=f'{BASE_URL}/star/{star_id}',
                            page=page)


def get_samples_by_id(id: str) -> list:
    '''根据番号获取截图

    :param str id: 番号
    :return list: 截图列表
    '''
    samples = []
    url = f'{BASE_URL}/{id}'
    resp = requests.get(url, proxies=proxies, headers=get_headers(url))
    if resp.status_code != 200:
        return None
    # 获取soup
    soup = BeautifulSoup(resp.text, 'lxml')
    # 获取截图
    sample_tags = soup.find_all(class_='sample-box')
    for tag in sample_tags:
        sample_link = tag['href']
        if sample_link.find('https') == -1:
            sample_link = BASE_URL + sample_link
        samples.append(sample_link)
    if samples == []: return None
    return samples


def get_nice_magnets(magnets: list, prop: str, expect_val) -> list:
    '''过滤磁链列表

    :param list magnets: 要过滤的磁链列表
    :param str prop: 过滤属性
    :param _type_ expect_val: 过滤属性的期望值
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
    # 统一单位为MB
    for magnet in magnets:
        size = magnet['size']
        gb_idx = size.lower().find('gb')
        mb_idx = size.lower().find('mb')
        if gb_idx != -1:  # 单位为GB
            magnet['size_no_unit'] = float(size[:gb_idx]) * 1024
        elif mb_idx != -1:  # 单位为MB
            magnet['size_no_unit'] = float(size[:mb_idx])
    # 根据size_no_unit大小排序
    magnets = sorted(magnets, key=lambda m: m['size_no_unit'], reverse=True)
    return magnets


def get_av_by_id(id: str, is_nice: bool, magnet_max_count=100) -> dict:
    '''通过javbus获取番号对应av

    :param str id: 番号
    :param bool is_nice: 是否过滤磁链
    :param int magnet_max_count: 过滤后磁链的最大数目
    :return dict: av
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
    resp = requests.get(url, proxies=proxies, headers=get_headers(url))
    if resp.status_code != 200:
        return None
    # 获取soup和html
    soup = BeautifulSoup(resp.text, 'lxml')
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
        return av
    # 得到磁链的ajax请求地址
    url = f'{BASE_URL}/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&uc={uc}'
    # 发送请求获取含磁链页
    resp = requests.get(url, proxies=proxies, headers=get_headers(url))
    if resp.status_code != 200:
        return av
    soup = BeautifulSoup(resp.text, 'lxml')
    # 解析页面获取磁链
    for tr in soup.find_all('tr'):
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
    return av


if __name__ == '__main__':
    res = None
    # javbus id test
    res = get_av_by_id(id='GTJ-111', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='YMDD-301', is_nice=False)
    # res = get_av_by_id(id='ipx-811', is_nice=False)
    # res = get_av_by_id(id='091318_01', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='080916-226', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='n1282', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='ibw-631z', is_nice=True, magnet_max_count=3)
    
    # fc2 id test
    # res = get_av_by_id(id='fc2-ppv-880652', is_nice=True, magnet_max_count=3)
    # res = get_av_by_id(id='880652', is_nice=True, magnet_max_count=3)
    
    # other test
    # res = get_samples_by_id('ssni-497')
    # res = get_id_by_star_id('okq', 2)
    # res = get_id_by_star_name('白夜みくる')
    # res = get_max_page('https://www.javbus.com/star/okq')
    # res = get_id_by_star_id('okq')
    # res = get_id_by_star_name('三上悠亜')
    # res = get_id_from_home()
    if res: print(res)