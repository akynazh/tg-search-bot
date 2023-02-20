# -*- coding: UTF-8 -*-
from deep_translator import GoogleTranslator
import sys

sys.path.append('..')
import common


def trans(text: str, from_lang='auto', to_lang='zh-CN') -> str:
    '''翻译

    :param str text: 要翻译的文本
    :param str from_lang: 原文语言码, defaults to 'auto'
    :param str to_lang: 目标语言码, defaults to 'zh-CN'
    :return str: 翻译结果，如果失败则为 None
    '''
    try:
        return GoogleTranslator(source=from_lang,
                                target=to_lang,
                                proxies=common.PROXY).translate(text)
    except Exception:
        return None


if __name__ == '__main__':
    print(
        trans(text='催淫洗脳されたスレンダー美乳妻は嫌がりながらも淫乱ビッチになっていた 美谷朱里',
              from_lang='ja',
              to_lang='zh-CN'))
    print(trans(text='That is not a dog.', from_lang='en', to_lang='zh-CN'))