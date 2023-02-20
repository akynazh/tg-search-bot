# -*- coding: UTF-8 -*-
import sys
import typing
import random

sys.path.append('..')
import common

BASE_URL = 'https://www.javlibrary.com'
# nice
BASE_URL_BEST_RATED_LAST_MONTH = BASE_URL + '/cn/vl_bestrated.php?mode=1&page='
BASE_URL_BEST_RATED_ALL = BASE_URL + '/cn/vl_bestrated.php?mode=2&page='
BASE_URL_MOST_WANTED_LAST_MONTH = BASE_URL + '/cn/vl_mostwanted.php?&mode=1&page='
BASE_URL_MOST_WANTED_ALL = BASE_URL + '/cn/vl_mostwanted.php?&mode=2&page='
# new
BASE_URL_NEW_RELEASE_HAVE_COMMENT = BASE_URL + '/cn/vl_newrelease.php?&mode=1&page='
BASE_URL_NEW_RELEASE_ALL = BASE_URL + '/cn/vl_newrelease.php?&mode=2&page='
BASE_URL_NEW_ENTRIES = BASE_URL + '/cn/vl_newentries.php?page='
URLS_NICE = [
    BASE_URL_BEST_RATED_LAST_MONTH, BASE_URL_BEST_RATED_ALL,
    BASE_URL_MOST_WANTED_LAST_MONTH, BASE_URL_MOST_WANTED_ALL
]
URLS_NEW = [
    BASE_URL_NEW_RELEASE_HAVE_COMMENT, BASE_URL_NEW_RELEASE_ALL,
    BASE_URL_NEW_ENTRIES
]
MAX_PAGE = 25


def get_random_id(list_type: int) -> typing.Tuple[int, str]:
    '''从排行榜中随机获取番号

    :param int list_type: 排行榜类型 0 nice | 1 new
    :return typing.Tuple[int, str]: 状态码和番号
    '''
    if list_type == 0:
        url = random.choice(URLS_NICE)
    elif list_type == 1:
        url = random.choice(URLS_NEW)
    page = random.randint(1, MAX_PAGE)
    code, resp = common.send_req(url + str(page))
    if code != 200:
        return code, None
    soup = common.get_soup(resp)
    tag_ids = soup.find_all(class_='id')
    if not tag_ids:
        return 404, None
    ids = [tag.text for tag in tag_ids]
    if len(ids) > 0:
        return 200, random.choice(ids)
    else:
        return 404, None


if __name__ == '__main__':
    # code, res = get_random_id(0)
    code, res = get_random_id(1)
    if code == 200: print(res)