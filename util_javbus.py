# -*- coding: UTF-8 -*-
import requests
import re
import cfg
from bs4 import BeautifulSoup

BASE_URL = 'http://www.javbus.com'
proxies = {}
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}


def get_av(id: str) -> dict:
    '''通过javbus获取番号对应av

    :param str id: 番号
    :return dict: av
    av格式: 
    {
        'id': id,      # 番号
        'title': '',   # 标题
        'img': '',     # 封面地址
        'stars': [],   # 演员
        'magnets': [], # 磁链
    }
    磁链格式:
    {
        'link': '', # 链接
        'hd': '0',  # 是否高清 0 否 | 1 是
        'zm': '0'   # 是否有字幕 0 否 | 1 是
    }
    '''
    av = {
        'id': id,
        'title': '',
        'img': '',
        'stars': [],
        'magnets': [],
    }
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
        'Host': 'www.javbus.com',
        'Connection': 'close',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': '',
    }

    # 查找av
    url = f'{BASE_URL}/{id}'
    headers['Referer'] = url
    resp = requests.get(url, proxies=proxies, headers=headers)
    if resp.status_code != 200:
        return None

    # 获取soup和html
    soup = BeautifulSoup(resp.text, 'lxml')
    html = soup.prettify()

    # 获取封面和标题
    big_image = soup.find(class_='bigImage')
    img = big_image['href']
    av['img'] = f'{BASE_URL}/{img}'
    av['title'] = big_image.img['title']

    # 获取演员
    for name in soup.find_all(class_='star-name'):
        av['stars'].append(name.text)

    # 获取uc
    uc_pattern = re.compile(r'var uc = .*?;')
    match = uc_pattern.findall(html)
    uc = match[0].replace('var uc = ', '').replace(';', '')

    # 获取gid
    gid_pattern = re.compile(r'var gid = .*?;')
    match = gid_pattern.findall(html)
    gid = match[0].replace('var gid = ', '').replace(';', '')

    # 得到磁链的ajax请求地址
    url = f'{BASE_URL}/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&img={img}&uc={uc}'
    headers['Referer'] = url
    resp = requests.get(url, proxies=proxies, headers=headers)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'lxml')

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
    return av


if __name__ == '__main__':
    av = get_av('RHTS-034')
    print(av)