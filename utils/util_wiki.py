# -*- coding: UTF-8 -*-
import wikipediaapi
import sys
import logging

logging.getLogger('wikipediaapi').setLevel(logging.ERROR)

sys.path.append('..')
import common


def get_wiki_page_by_lang(topic: str, from_lang: str, to_lang: str) -> dict:
    '''根据搜索词和原来语言码返回指定语言维基页，如果搜索不到结果则返回空，如果搜索到结果但找不到指定语言维基页则返回原页

    :param str topic: 搜索词
    :param str from_lang: 原来语言码
    :param str to_lang: 目标语言码
    :return dict: 结果集
    {
        'title': '', # 标题
        'url': '', # 地址
        'lang': '' # 语言码
    }
    '''
    try:
        wiki = wikipediaapi.Wikipedia(language=from_lang, proxies=common.PROXY)
        page = wiki.page(title=topic)
        # links = page.links
        # for k in links.keys():
        #     if links[k].title.find(topic) != -1:
        #         print(links[k].fullurl)
        if page.text:
            langlinks = page.langlinks
            for k in langlinks.keys():
                if k == to_lang:
                    return {
                        'title': langlinks[k].title,
                        'url': langlinks[k].fullurl,
                        'lang': langlinks[k].language
                    }
            return {
                'title': page.title,
                'url': page.fullurl,
                'lang': from_lang
            }
    except Exception as e:
        common.LOG.error(e)
        return


if __name__ == '__main__':
    res = get_wiki_page_by_lang(topic='田中柠檬', from_lang='zh', to_lang='ja')
    if res:
        print(res)
    else:
        print('找不到结果')