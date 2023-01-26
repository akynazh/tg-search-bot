import os
import json
import typing
import common

LOG = common.LOG


def check_has_record() -> typing.Tuple[dict, bool, bool]:
    '''检查是否有收藏记录，如果有则返回记录

    :return tuple[dict, bool, bool]: 收藏记录, 演员记录是否存在, 番号记录是否存在
    '''
    # 初始化数据
    record = {}
    # 加载记录
    if os.path.exists(common.PATH_RECORD_FILE):
        try:
            with open(common.PATH_RECORD_FILE, 'r') as f:
                record = json.load(f)
        except Exception as e:
            LOG.error(e)
            return None, False, False
    # 尚无记录
    if not record or record == {}:
        return None, False, False
    # 检查并返回记录
    is_stars_exists = False
    is_avs_exists = False
    if 'stars' in record.keys() and record['stars'] != [] and len(
            record['stars']) > 0:
        is_stars_exists = True
    if 'avs' in record.keys() and record['avs'] != [] and len(
            record['avs']) > 0:
        is_avs_exists = True
    return record, is_stars_exists, is_avs_exists


def renew_record(record: dict) -> bool:
    '''更新记录

    :param dict record: 新的记录
    :return bool: 是否更新成功
    '''
    try:
        with open(common.PATH_RECORD_FILE, 'w') as f:
            json.dump(record,
                      f,
                      separators=(',', ': '),
                      indent=4,
                      ensure_ascii=False)
        return True
    except Exception as e:
        LOG.error(e)
        return False


def record_star(star_name: str, star_id: str) -> bool:
    '''记录演员

    :param str star_name: 演员名称
    :param str star_id: 演员编号
    :return bool: 是否收藏成功
    '''
    # 加载记录
    record, is_stars_exists, _ = check_has_record()
    if not record:
        record, stars = {}, []
    else:
        if not is_stars_exists:
            stars = []
        else:
            stars = record['stars']
    # 检查记录是否存在
    exists = False
    for star in stars:
        if star['id'].lower() == star_id.lower():
            exists = True
            break
    # 如果记录需要更新则写回记录
    if not exists:
        stars.append({'name': star_name, 'id': star_id.lower()})
        record['stars'] = stars
        return renew_record(record)
    return True


def record_id(id: str, stars: list) -> bool:
    '''记录番号

    :param str id: 番号
    :param list stars: 演员编号列表
    :return bool: 是否收藏成功
    '''
    # 加载记录
    record, _, is_avs_exists = check_has_record()
    if not record:
        record, avs = {}, []
    else:
        if not is_avs_exists: avs = []
        else: avs = record['avs']
    # 检查记录是否存在
    exists = False
    for av in avs:
        if av['id'].lower() == id.lower():
            exists = True
            break
    # 如果记录需要更新则写回记录
    if not exists:
        avs.append({'id': id.lower(), 'stars': stars})
        record['avs'] = avs
        return renew_record(record)
    return True


def undo_record_star(star_id: str) -> bool:
    '''取消收藏演员

    :param str star_id: 演员id
    :return bool: 是否取消收藏成功
    '''
    # 加载记录
    record, _, _ = check_has_record()
    stars = record['stars']
    exists = False
    # 删除记录
    for i, star in enumerate(stars):
        if star['id'] == star_id:
            del stars[i]
            exists = True
            break
    # 更新记录
    if exists:
        record['stars'] = stars
        return renew_record(record)
    return True


def undo_record_id(id: str) -> bool:
    '''取消收藏番号

    :param str id: 番号
    :return bool: 是否取消收藏成功
    '''
    # 加载记录
    record, _, _ = check_has_record()
    avs = record['avs']
    exists = False
    # 删除记录
    for i, av in enumerate(avs):
        if av['id'] == id:
            del avs[i]
            exists = True
            break
    # 更新记录
    if exists:
        record['avs'] = avs
        return renew_record(record)
    return True