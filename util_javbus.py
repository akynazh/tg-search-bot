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
        'date': '',    # 发行日期
        'tags': '',    # 标签
        'stars': [],   # 演员
        'magnets': [], # 磁链
        'samples': [], # 截图
    }
    磁链格式:
    {
        'link': '', # 链接
        'hd': '0',  # 是否高清 0 否 | 1 是
        'zm': '0'   # 是否有字幕 0 否 | 1 是
    }
    演员格式:
    {
        'name': '', # 演员名称
        'link': ''  # 演员链接
    }
    '''
    av = {
        'id': id,
        'title': '',
        'img': '',
        'date': '',
        'tags': '',
        'stars': [],
        'magnets': [],
        'samples': [],
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
    uc = match[0].replace('var uc = ', '').replace(';', '')

    # 获取gid
    gid_pattern = re.compile(r'var gid = .*?;')
    match = gid_pattern.findall(html)
    gid = match[0].replace('var gid = ', '').replace(';', '')

    # 获取截图
    sample_tags = soup.find_all(class_='sample-box')
    for tag in sample_tags:
        av['samples'].append(tag['href'])

    # 得到磁链的ajax请求地址
    url = f'{BASE_URL}/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&img={img}&uc={uc}'

    # 发送请求获取含磁链页
    headers['Referer'] = url
    resp = requests.get(url, proxies=proxies, headers=headers)
    if resp.status_code != 200:
        return None
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
    return av


if __name__ == '__main__':
    av = get_av('JFB-303')
    print(av)