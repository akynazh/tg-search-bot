# -*- coding: UTF-8 -*-
import telebot
from telebot import types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import cfg
import json
import os
import sys
import re
import logging
import typing
import string
import util_pikpak
import util_javbus
import util_avgle
import util_sukebei
import util_dmm

TG_BOT_TOKEN = cfg.TG_BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN)
TG_CHAT_ID = cfg.TG_CHAT_ID
PATH_ROOT = sys.path[0]
PATH_RECORD_FILE = PATH_ROOT + '/record.json'  # 收藏记录文件
PATH_LOG_FILE = PATH_ROOT + '/log.txt'  # 日志记录文件
proxies = {}
BASE_URL_JAVBUS = util_javbus.BASE_URL
BASE_URL_SUKEBEI = util_sukebei.BASE_URL
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}
    apihelper.proxy = proxies
# 按钮键值定义
KEY_WATCH_PV_BY_ID = 0
KEY_WATCH_FV_BY_ID = 1
KEY_GET_SAMPLE_BY_ID = 2
KEY_GET_MORE_MAGNETS_BY_ID = 3
kEY_RANDOM_GET_AV_BY_STAR_ID = 4
KEY_RECORD_STAR = 5
KEY_RECORD_AV = 6
KEY_GET_STARS_RECORD = 7
KEY_GET_AVS_RECORD = 8
KEY_GET_STAR_DETAIL_RECORD = 9
KEY_GET_AV_BY_ID = 10
KEY_RANDOM_GET_AV = 11
KEY_UNDO_RECORD_STAR = 12
KEY_UNDO_RECORD_AV = 13
KEY_GET_AV_DETAIL_RECORD = 14
PROJECT_ADDRESS = 'https://github.com/akynazh/tg-jav-bot'
PROJECT_NAME = 'tg-jav-bot'
AUTHOR = 'https://github.com/akynazh'


class Logger:
    '''日志记录器
    '''

    def __init__(self, log_level):
        '''初始化日志记录器

        :param _type_ log_level: 记录级别
        '''
        self.logger = logging.getLogger()
        self.logger.addHandler(self.get_file_handler(PATH_LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        return file_handler


def send_msg(msg, pv=False, markup=None):
    '''发送消息

    :param _type_ msg: 消息文本内容
    :param bool pv: 是否展现预览, 默认不展示
    :param _type_ markup: 标记, 默认没有
    '''
    bot.send_message(chat_id=TG_CHAT_ID,
                     text=msg,
                     disable_web_page_preview=not pv,
                     parse_mode='HTML',
                     reply_markup=markup)


def check_has_record() -> typing.Tuple[dict, bool, bool]:
    '''检查是否有收藏记录，如果有则返回记录

    :return tuple[dict, bool, bool]: 收藏记录, 演员记录是否存在, 番号记录是否存在
    '''
    # 初始化数据
    record = {}
    # 加载记录
    if os.path.exists(PATH_RECORD_FILE):
        try:
            with open(PATH_RECORD_FILE, 'r') as f:
                record = json.load(f)
        except Exception:
            LOG.info('文件格式有误')
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


def get_record_json():
    '''发送收藏记录文件'''
    if os.path.exists(PATH_RECORD_FILE):
        bot.send_document(chat_id=TG_CHAT_ID,
                          document=types.InputFile(PATH_RECORD_FILE))
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text='尚无记录 =_=')


def renew_record(record: dict):
    '''更新记录

    :param dict record: 新的记录
    '''
    with open(PATH_RECORD_FILE, 'w') as f:
        json.dump(record,
                  f,
                  separators=(',', ': '),
                  indent=4,
                  ensure_ascii=False)


def record_star(star_name: str, star_id: str):
    '''记录演员

    :param str star_name: 演员名称
    :param str star_id: 演员编号
    '''
    # 加载记录
    record, is_stars_exists, _ = check_has_record()
    if not record:
        record, stars = {}, []
    else:
        if not is_stars_exists: stars = []
        else: stars = record['stars']
    # 检查记录是否存在
    exists = False
    for star in stars:
        if star['id'].lower() == star_id.lower():
            exists = True
            break
    # 如果记录需要更新则写回记录
    if not exists:
        LOG.info(f'收藏新的演员：{star_name}')
        stars.append({'name': star_name, 'id': star_id.lower()})
        record['stars'] = stars
        renew_record(record)
        send_msg(f'成功收藏<code>{star_name}</code> ^-^')
    else:
        send_msg(f'已经收藏过<code>{star_name}</code>了 =_=')


def record_id(id: str, stars: list):
    '''记录番号

    :param str id: 番号
    :param list stars: 演员编号列表
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
        LOG.info(f'收藏AV【番号：{id}, 演员：{str(stars)}】')
        avs.append({'id': id.lower(), 'stars': stars})
        record['avs'] = avs
        renew_record(record)
        send_msg(f'成功收藏<code>{id}</code> ^-^')
    else:
        send_msg(f'已经收藏过<code>{id}</code>了 =_=')


def undo_record_star(star_id: str):
    '''取消收藏演员

    :param str star_id: 演员id
    '''
    # 加载记录
    record, _, _ = check_has_record()
    stars = record['stars']
    # 删除记录
    for i, star in enumerate(stars):
        if star['id'] == star_id:
            del stars[i]
            break
    # 更新记录
    record['stars'] = stars
    renew_record(record)
    send_msg(msg='操作成功')


def undo_record_id(id: str):
    '''取消收藏番号

    :param str id: 番号
    '''
    # 加载记录
    record, _, _ = check_has_record()
    avs = record['avs']
    # 删除记录
    for i, av in enumerate(avs):
        if av['id'] == id:
            del avs[i]
            break
    # 更新记录
    record['avs'] = avs
    renew_record(record)
    send_msg(msg='操作成功')


def create_btn(btn_type: int, obj: dict):
    '''根据按钮种类创建按钮

    :param int type: 按钮种类 0 演员 | 1 番号
    :param dict obj: 数据对象
    :return _type_: 按钮
    '''
    if btn_type == 0:  # star
        return InlineKeyboardButton(
            text=obj['name'],
            callback_data=
            f'{obj["name"]}|{obj["id"]}:{KEY_GET_STAR_DETAIL_RECORD}')
    elif btn_type == 1:  # av
        return InlineKeyboardButton(
            text=obj, callback_data=f'{obj}:{KEY_GET_AV_DETAIL_RECORD}')


def send_msg_btns(max_btn_per_row: int,
                  max_row_per_msg: int,
                  btn_type: int,
                  title: str,
                  objs: list,
                  extra_btns=[]):
    '''发送按钮消息

    :param int max_btn_per_row: 每行最大按钮数量
    :param int max_row_per_msg: 每条消息最多行数
    :param int btn_type: 按钮种类 0 演员 | 1 番号
    :param str title: 消息标题
    :param dict objs: 数据对象数组
    :param list extra_btns: 附加按钮列表，每行一个按钮，附加在每条消息尾部，默认为空
    '''
    # 初始化数据
    markup = InlineKeyboardMarkup()
    row_count = 0
    btns = []
    # 开始生成按钮和发送消息
    for obj in objs:
        btns.append(create_btn(btn_type, obj))
        # 若一行按钮的数量达到max_btn_per_row，则加入行
        if len(btns) == max_btn_per_row:
            markup.row(*btns)
            row_count += 1
            btns = []
        # 若消息中行数达到max_row_per_msg，则发送消息
        if row_count == max_row_per_msg:
            for extra_btn in extra_btns:
                markup.row(extra_btn)
            send_msg(msg=title, markup=markup)
            row_count = 0
            markup = InlineKeyboardMarkup()
    # 若当前行按钮数量不为0，则加入行
    if btns != []:
        markup.row(*btns)
        row_count += 1
    # 若当前行数不为0，则发送消息
    if row_count != 0:
        for extra_btn in extra_btns:
            markup.row(extra_btn)
        send_msg(msg=title, markup=markup)


def get_stars_record():
    '''获取演员收藏记录
    '''
    # 初始化数据
    record, is_star_exists, _ = check_has_record()
    if not record or not is_star_exists:
        send_msg('尚无收藏记录 =_=')
        return
    stars = record['stars']
    # 发送按钮消息
    send_msg_btns(max_btn_per_row=4,
                  max_row_per_msg=15,
                  btn_type=0,
                  title='<b>收藏的演员</b>',
                  objs=stars)


def get_star_detail_record(star_name: str, star_id: str):
    '''根据演员编号获取该演员更多信息

    :param str star_name: 演员名称
    :param str star_id: 演员编号
    '''
    # 初始化数据
    record, _, is_avs_exists = check_has_record()
    if not record or not is_avs_exists:
        send_msg('尚无收藏记录 =_=')
        return
    avs = record['avs']
    star_avs = []
    for av in avs:
        # 如果演员编号在该AV的演员编号列表中
        if star_id in av['stars']:
            star_avs.append(av['id'])
    # 发送按钮消息
    extra_btn1 = InlineKeyboardButton(
        text=f'随机获取一部{star_name}的AV',
        callback_data=f'{star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}')
    extra_btn2 = InlineKeyboardButton(
        text=f'取消收藏{star_name}',
        callback_data=f'{star_id}:{KEY_UNDO_RECORD_STAR}')
    title = f'<code>{star_name}</code> | <a href="https://ja.wikipedia.org/wiki/{star_name}">Wiki</a> | <a href="{util_javbus.BASE_URL}/star/{star_id}">Javbus</a>'
    if len(star_avs) == 0:  # 没有收藏记录
        markup = InlineKeyboardMarkup()
        markup.row(extra_btn1)
        markup.row(extra_btn2)
        send_msg(msg=title, markup=markup)
        return
    send_msg_btns(max_btn_per_row=5,
                  max_row_per_msg=20,
                  btn_type=1,
                  title=title,
                  objs=star_avs,
                  extra_btns=[extra_btn1, extra_btn2])


def get_avs_record():
    '''获取番号收藏记录
    '''
    # 初始化数据
    record, _, is_avs_exists = check_has_record()
    if not record or not is_avs_exists:
        send_msg('尚无收藏记录 =_=')
        return
    avs = [av['id'] for av in record['avs']]
    # 发送按钮消息
    extra_btn = InlineKeyboardButton(text='随机获取一部AV',
                                     callback_data=f'0:{KEY_RANDOM_GET_AV}')
    send_msg_btns(max_btn_per_row=5,
                  max_row_per_msg=20,
                  btn_type=1,
                  title='<b>收藏的番号</b>',
                  objs=avs,
                  extra_btns=[extra_btn])


def get_av_detail_record(id: str):
    '''根据番号获取该番号更多信息

    :param str id: 番号
    '''
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text=f'获取{id}对应AV',
                             callback_data=f'{id}:{KEY_GET_AV_BY_ID}'))
    markup.row(
        InlineKeyboardButton(text=f'取消收藏{id}',
                             callback_data=f'{id}:{KEY_UNDO_RECORD_AV}'))
    send_msg(msg=f'<a href="{util_javbus.BASE_URL}/{id}">{id}</a>',
             markup=markup)


def get_av_by_id(id: str,
                 send_to_pikpak=True,
                 is_nice=True,
                 magnet_max_count=3):
    '''根据番号获取 av

    :param str id: 番号
    :param bool send_to_pikpak: 是否发给pikpak，默认是
    :param bool is_nice: 是否过滤磁链，默认是
    :param int magnet_max_count: 过滤后磁链的最大数目，默认为3
    '''
    # 获取AV
    try:
        # 首先通过javbus查找
        av_url = f'{BASE_URL_JAVBUS}/{id}'
        av = util_javbus.get_av_by_id(id, is_nice, magnet_max_count)
        if not av:  # 如果找不到，再通过sukebei查找
            av_url = f'{BASE_URL_SUKEBEI}?q={id}'
            av = util_sukebei.get_av_by_id(id, is_nice, magnet_max_count)
    except Exception as e:
        LOG.info(e)
        send_msg(f'网络请求失败，请重试 Q_Q')
        return
    # 未查找到该番号对应的AV
    if not av:
        send_msg(f'妹找到番号<code>{id}</code>对应的AV Q_Q')
        return
    # 提取数据
    av_id = id
    av_title = av['title']
    av_img = av['img']
    av_date = av['date']
    av_tags = av['tags']
    av_stars = av['stars']
    av_magnets = av['magnets']
    # 拼接消息
    msg = ''
    print(av_title)
    if av_title != '':
        msg += f'''【标题】<a href="{av_url}">{av_title}</a>
'''
    msg += f'''【番号】<code>{av_id}</code>
'''
    if av_date != '':
        msg += f'''【日期】{av_date}
'''

    # 加上演员消息
    if av_stars == []:
        msg += f'''【演员】未知
'''
    for i, star in enumerate(av_stars):
        if i > 5:
            msg += f'''【演员】<a href="{av_url}">查看更多...</a>
'''
            break
        name = star['name']
        link = star['link']
        wiki = f'https://ja.wikipedia.org/wiki/{name}'
        msg += f'''【演员】<code>{name}</code> | <a href="{wiki}">Wiki</a> | <a href="{link}">Javbus</a>
'''
    if av_tags != '':
        msg += f'''【标签】{av_tags}
'''
    # 加上其它消息
    msg += f'''【其它】<a href="https://t.me/{cfg.PIKPAK_BOT_NAME}">@{cfg.PIKPAK_BOT_NAME}</a> | <a href="{PROJECT_ADDRESS}">项目地址</a>
'''
    # 加上磁链消息
    magnet_send_to_pikpak = ''
    for i, magnet in enumerate(av_magnets):
        if i == 0:
            magnet_send_to_pikpak = magnet['link']
        msg += f'''【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>
'''
        if len(msg) > 2000: break
    # 生成回调按钮
    pv_btn = InlineKeyboardButton(
        text='预览', callback_data=f'{av_id}:{KEY_WATCH_PV_BY_ID}')
    fv_btn = InlineKeyboardButton(
        text='观看', callback_data=f'{av_id}:{KEY_WATCH_FV_BY_ID}')
    sample_btn = InlineKeyboardButton(
        text='截图', callback_data=f'{av_id}:{KEY_GET_SAMPLE_BY_ID}')
    more_btn = InlineKeyboardButton(
        text='更多磁链', callback_data=f'{av_id}:{KEY_GET_MORE_MAGNETS_BY_ID}')
    markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn, more_btn)
    star_random_btn = None
    star_record_btn = None
    if len(av_stars) == 1:
        show_star_name = av_stars[0]['name']
        show_star_link = av_stars[0]['link']
        show_star_id = show_star_link[show_star_link.rfind('/') + 1:]
        star_random_btn = InlineKeyboardButton(
            text=f'演员随机AV',
            callback_data=f'{show_star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}')
        star_record_btn = InlineKeyboardButton(
            text=f'收藏{show_star_name}',
            callback_data=f'{show_star_name}|{show_star_id}:{KEY_RECORD_STAR}')
    star_ids = ''
    for i, star in enumerate(av_stars):
        star_link = star['link']
        star_id = star_link[star_link.rfind('/') + 1:]
        star_ids += star_id + '|'
        if i >= 5:
            star_ids += '...|'
            break
    if star_ids != '': star_ids = star_ids[:len(star_ids) - 1]
    av_record_btn = InlineKeyboardButton(
        text=f'收藏番号', callback_data=f'{av_id}|{star_ids}:{KEY_RECORD_AV}')
    if star_random_btn and star_record_btn:
        markup.row(av_record_btn, star_record_btn, star_random_btn)
    else:
        markup.row(av_record_btn)
    # 发送消息
    if av_img == '':
        send_msg(msg=msg, markup=markup)
    else:
        try:
            bot.send_photo(chat_id=TG_CHAT_ID,
                           photo=av_img,
                           caption=msg,
                           parse_mode='HTML',
                           reply_markup=markup)
        except Exception:  # 少数图片可能没法发送
            send_msg(msg=msg, markup=markup)
    # 发给pikpak
    if cfg.USE_PIKPAK == 1 and magnet_send_to_pikpak != '' and send_to_pikpak:
        send_magnet_to_pikpak(magnet_send_to_pikpak)


def send_magnet_to_pikpak(magnet: str):
    '''发送磁链到pikpak
    
    :param str magnet: 磁链
    '''
    name = cfg.PIKPAK_BOT_NAME
    try:
        if util_pikpak.send_msg(magnet):  # 成功发送
            send_msg(
                f'已经将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>'
            )
        else:  # 发送失败
            send_msg(
                f'未能将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>'
            )
    except Exception as e:
        LOG.info(e)
        send_msg(f'网络请求失败，请重试 Q_Q')
        return


def get_sample_by_id(id: str):
    '''根据番号获取av截图

    :param str id: 番号
    '''
    # 获取截图
    try:
        samples = util_javbus.get_samples_by_id(id)
    except Exception as e:
        LOG.info(e)
        send_msg(f'网络请求失败，请重试 Q_Q')
        return
    if not samples:
        send_msg(f'未找到截图 Q_Q')
        return
    # 发送图片列表
    samples_imp = []
    sample_error = False
    for sample in samples:
        samples_imp.append(InputMediaPhoto(sample))
        if len(samples_imp) == 10:  # 图片数目达到10张则发送一次
            try:
                bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
                samples_imp = []
            except Exception as e:
                sample_error = True
                LOG.error(e)
                send_msg('图片解析失败 Q_Q')
                break
    if samples_imp != [] and not sample_error:
        try:
            bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
        except Exception as e:
            LOG.error(e)
            send_msg('图片解析失败 Q_Q')


def watch_av(id: str, type: str):
    '''获取番号对应视频

    :param str id: 番号
    :param str type: 0 预览视频 | 1 完整视频
    '''
    try:
        if type == 0:
            video = util_dmm.get_pv_by_id(id)
        elif type == 1:
            video = util_avgle.get_fv_by_id(id)
    except Exception as e:
        LOG.info(e)
        send_msg(f'网络请求失败，请重试 Q_Q')
        return
    if video:
        if type == 0:
            try:
                bot.send_video(chat_id=TG_CHAT_ID, video=video)
            except Exception as e:
                LOG.info(e)
                send_msg('视频解析失败 Q_Q')
        elif type == 1:
            send_msg(f'番号{id}对应视频地址：{video}')
    else:
        send_msg(f'未找到{id}对应视频 =_=')


def get_msg_param(msg):
    '''获取消息参数

    :param _type_ msg: 消息文本，已经通过strip()函数将两旁空白清除
    :return _type_: 消息参数（保证只有一个）
    '''
    msgs = msg.split(' ', 1)  # 划分为两部分
    if len(msgs) > 1:  # 有参数
        param = ''.join(msgs[1].split())  # 去除参数所有空白
        if param != '': return param


@bot.callback_query_handler(func=lambda call: True)
def listen_callback(call):
    '''消息回调处理器

    :param _type_ call: 触发回调的消息内容
    '''
    idx = call.data.rfind(':')
    content = call.data[:idx]
    key_type = int(call.data[idx + 1:])
    if key_type == KEY_WATCH_PV_BY_ID:
        watch_av(id=content, type=0)
    elif key_type == KEY_WATCH_FV_BY_ID:
        watch_av(id=content, type=1)
    elif key_type == KEY_GET_SAMPLE_BY_ID:
        get_sample_by_id(id=content)
    elif key_type == KEY_GET_MORE_MAGNETS_BY_ID:
        try:
            av = util_javbus.get_av_by_id(id=content, is_nice=False)
            if not av:
                av = util_sukebei.get_av_by_id(id=content, is_nice=False)
        except Exception as e:
            LOG.info(e)
            send_msg(f'网络请求失败，请重试 Q_Q')
            return
        if not av:
            send_msg('获取失败，请重试 =_=')
            return
        msg = ''
        for magnet in av['magnets']:
            msg += f'''【{magnet["size"]}】<code>{magnet["link"]}</code>
'''
            if len(msg) > 2000:
                send_msg(msg)
                msg = ''
        if msg != '': send_msg(msg)
    elif key_type == kEY_RANDOM_GET_AV_BY_STAR_ID:
        try:
            id = util_javbus.get_id_by_star_id(star_id=content)
        except Exception as e:
            LOG.info(e)
            send_msg(f'网络请求失败，请重试 Q_Q')
            return
        if id: get_av_by_id(id=id, send_to_pikpak=False)
        else: send_msg('获取失败，请重试=_=')
    elif key_type == KEY_RECORD_STAR:
        s = content.find('|')
        record_star(star_name=content[:s], star_id=content[s + 1:])
    elif key_type == KEY_RECORD_AV:
        res = content.split('|')
        id = res[0]
        stars = [s for s in res[1:]]
        record_id(id=id, stars=stars)
    elif key_type == KEY_GET_STARS_RECORD:
        get_stars_record()
    elif key_type == KEY_GET_AVS_RECORD:
        get_avs_record()
    elif key_type == KEY_GET_STAR_DETAIL_RECORD:
        s = content.find('|')
        get_star_detail_record(star_name=content[:s], star_id=content[s + 1:])
    elif key_type == KEY_GET_AV_DETAIL_RECORD:
        get_av_detail_record(id=content)
    elif key_type == KEY_GET_AV_BY_ID:
        get_av_by_id(id=content, send_to_pikpak=False)
    elif key_type == KEY_RANDOM_GET_AV:
        try:
            id = util_javbus.get_id_from_home()
        except Exception as e:
            LOG.info(e)
            send_msg(f'网络请求失败，请重试 Q_Q')
            return
        if not id: send_msg('获取失败，请重试 =_=')
        else: get_av_by_id(id=id, send_to_pikpak=False)
    elif key_type == KEY_UNDO_RECORD_AV:
        undo_record_id(id=content)
    elif key_type == KEY_UNDO_RECORD_STAR:
        undo_record_star(star_id=content)


@bot.message_handler(content_types=['text', 'photo', 'animation', 'video'])
def handle_message(message):
    '''消息处理器

    :param _type_ message: 消息
    '''
    # 拦截请求，检查消息来源
    if str(message.from_user.id) != TG_CHAT_ID:
        LOG.info(f'拦截到非目标用户请求，id: {message.from_user.id}')
        bot.send_message(
            chat_id=message.from_user.id,
            text=
            f'该机器人仅供私人使用, 如需使用请自行部署，项目地址：<a href="{PROJECT_ADDRESS}">{PROJECT_NAME}</a>',
            parse_mode='HTML',
        )
        return
    # 获取消息文本内容
    if message.content_type != 'text':
        msg = message.caption
    else:
        msg = message.text
    if not msg or msg.strip() == '':
        return
    msg = msg.strip()
    LOG.info(f'收到消息：{msg}')
    # 处理消息
    if msg == '/test':
        test()
    elif msg == '/help':
        help()
    elif msg == '/random':
        try:
            id = util_javbus.get_id_from_home()
        except Exception as e:
            LOG.info(e)
            send_msg(f'网络请求失败，请重试 Q_Q')
            return
        if not id: send_msg('获取失败，请重试 =_=')
        else: get_av_by_id(id=id, send_to_pikpak=False)
    elif msg == '/stars':
        get_stars_record()
    elif msg == '/avs':
        get_avs_record()
    elif msg == '/record':
        get_record_json()
    elif msg.find('/star') != -1:
        param = get_msg_param(msg)
        if param:
            try:
                send_msg(f'搜索演员：{param}')
                id = util_javbus.get_id_by_star_name(star_name=param)
            except Exception as e:
                LOG.info(e)
                send_msg(f'网络请求失败，请重试 Q_Q')
                return
            if not id: send_msg(f'妹找到{param}，请重试或用其它方式搜索 =_=')
            else: get_av_by_id(id=id, send_to_pikpak=False)
    elif msg.find('/av') != -1:
        param = get_msg_param(msg)
        if param:
            try:
                send_msg(f'搜索番号：{param}')
                get_av_by_id(id=param)
            except Exception as e:
                LOG.info(e)
                send_msg(f'网络请求失败，请重试 Q_Q')
                return
    else:
        # ids = re.compile(r'^[A-Za-z]+[-][0-9]+$').findall(msg)
        ids = re.compile(r'[A-Za-z]+[-][0-9]+').findall(msg)
        if not ids:
            send_msg(
                '消息似乎不存在符合<b>“字母-数字”</b>格式的番号，请重试或使用“<code>/av</code> 番号”进行查找 =_='
            )
        else:
            ids = [id.lower() for id in ids]
            ids = set(ids)
            ids_msg = ', '.join(ids)
            send_msg(f'检测到番号：{ids_msg}，开始搜索...')
            for id in ids:
                get_av_by_id(
                    id=id,
                    send_to_pikpak=True,
                    is_nice=True,
                )


def test():
    '''用于测试'''
    return


def help():
    '''发送指令帮助消息'''
    msg = '''发送给机器人一条含有番号的消息，机器人会匹配并搜索消息中所有符合<b>“字母-数字”</b>格式的番号，其它格式的番号可通过<code>/av</code>命令查找。
    
/help  查看指令帮助

/stars  获取收藏的演员

/avs  获取收藏的番号

/random  随机获取一部AV

/record  获取收藏记录文件

<code>/star</code>  后接演员名称（日语）可随机获取一部该演员的AV

<code>/av</code>  后接番号可搜索该番号
'''
    send_msg(msg)


def set_command():
    '''设置机器人命令'''
    tg_cmd_dict = {
        'help': '查看指令帮助',
        'stars': '获取收藏的演员',
        'avs': '获取收藏的AV',
        'random': '随机获取一部AV',
        'record': '获取收藏记录文件'
    }
    cmds = []
    for cmd in tg_cmd_dict:
        cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
    bot.set_my_commands(cmds)


if __name__ == '__main__':
    os.chdir(PATH_ROOT)
    LOG = Logger(log_level=logging.INFO).logger
    LOG.info(f'当前工作目录：{PATH_ROOT}')
    set_command()
    bot.infinity_polling()