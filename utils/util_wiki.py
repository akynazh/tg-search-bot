# -*- coding: UTF-8 -*-
import wikipediaapi
import sys
import logging

logging.getLogger('wikipediaapi').setLevel(logging.ERROR)

sys.path.append('..')
import common


def get_chinese_wiki_page(topic: str, lang: str) -> dict:
    '''根据搜索词和原来语言码返回中文维基页，如果搜索不到结果则返回空，如果搜索到结果但找不到中文维基页则返回原页

    :param str topic: 搜索词
    :param str lang: 原来语言码
    :return dict: 结果集
    {
        'title': '', # 标题
        'url': '', # 地址
        'lang': '' # 语言码
    }
    '''
    wiki = wikipediaapi.Wikipedia(language=lang, proxies=common.PROXY)
    page = wiki.page(title=topic)
    # links = page.links
    # for k in links.keys():
    #     if links[k].title.find(topic) != -1:
    #         print(links[k].fullurl)
    if page.text:
        langlinks = page.langlinks
        for k in langlinks.keys():
            if k == 'zh':
                return {
                    'title': langlinks[k].title,
                    'url': langlinks[k].fullurl,
                    'lang': langlinks[k].language
                }
        return {'title': page.title, 'url': page.fullurl, 'lang': lang}


if __name__ == '__main__':
    res = get_chinese_wiki_page(topic='相沢みなみ', lang='ja')
    if res:
        print(res)
    else:
        print('找不到结果')