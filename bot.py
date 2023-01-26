# -*- coding: UTF-8 -*-
import telebot
from telebot import types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import math
import os
import re
import typing
import string
import common
import recorder
import concurrent.futures
import utils.util_javbus as util_javbus
import utils.util_avgle as util_avgle
import utils.util_sukebei as util_sukebei
import utils.util_dmm as util_dmm
import utils.util_javlibrary as util_javlibrary
if common.USE_PIKPAK:
    import utils.util_pikpak as util_pikpak

# 定义回调按键值
KEY_GET_SAMPLE_BY_ID = 'k0_0'
KEY_GET_MORE_MAGNETS_BY_ID = 'k0_1'
KEY_SEARCH_STAR_BY_NAME = 'k0_2'
KEY_GET_TOP_STARS = 'k0_3'

KEY_WATCH_PV_BY_ID = 'k1_0'
KEY_WATCH_FV_BY_ID = 'k1_1'

KEY_GET_AV_BY_ID = 'k2_0'
kEY_RANDOM_GET_AV_BY_STAR_ID = 'k2_1'
KEY_RANDOM_GET_AV_NICE = 'k2_2'
KEY_RANDOM_GET_AV_NEW = 'k2_3'
KEY_GET_NEW_AVS_BY_STAR_NAME_ID = 'k2_4'

KEY_RECORD_STAR = 'k3_0'
KEY_RECORD_AV = 'k3_1'
KEY_GET_STARS_RECORD = 'k3_2'
KEY_GET_AVS_RECORD = 'k3_3'
KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID = 'k3_4'
KEY_GET_AV_DETAIL_RECORD_BY_ID = 'k3_5'
KEY_UNDO_RECORD_STAR = 'k3_6'
KEY_UNDO_RECORD_AV = 'k3_7'

# 设置代理
apihelper.proxy = common.PROXY
# 初始化机器人
bot = telebot.TeleBot(common.TG_BOT_TOKEN)
# 日志记录器
LOG = common.LOG


def send_action_typing():
    '''显示机器人正在处理消息
    '''
    bot.send_chat_action(chat_id=common.TG_CHAT_ID, action='typing')


def send_msg(msg, pv=False, markup=None):
    '''发送消息

    :param _type_ msg: 消息文本内容
    :param bool pv: 是否展现预览, 默认不展示
    :param _type_ markup: 标记, 默认没有
    '''
    bot.send_message(chat_id=common.TG_CHAT_ID,
                     text=msg,
                     disable_web_page_preview=not pv,
                     parse_mode='HTML',
                     reply_markup=markup)


def send_msg_code(code: int, msg=''):
    '''根据状态码发送消息
    '''
    if code == 200:
        send_msg('操作成功 ^_^')
    elif code == 404:
        send_msg('未查找到结果 Q_Q')
    elif code == 500:
        send_msg('操作失败，请重试 =_=')
    elif code == 502:
        send_msg('网络请求失败，请重试 Q_Q')


def check_success(code: int, m_500='', m_404='', m_502='') -> bool:
    '''检查状态码，确认请求是否成功

    :param int code: 状态码
    :param str m_404: 自己指定 404 时要发送的消息
    :param str m_500: 自己指定 500 时要发送的消息
    :param str m_502: 自己指定 502 时要发送的消息
    :return bool: 请求成功与否
    '''
    if code == 200:
        return True
    elif code == 404:
        send_msg_code(code=404, msg=m_404)
        return False
    elif code == 500:
        send_msg_code(code=500, msg=m_500)
    elif code == 502:
        send_msg_code(code=502, msg=m_502)
        return False


def create_btn(key_type: str, obj: dict) -> InlineKeyboardButton:
    '''根据按钮种类创建按钮

    :param str key_type: 按钮种类
    :param dict obj: 数据对象
    :return InlineKeyboardButton: 按钮对象
    '''
    if key_type == KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
        return InlineKeyboardButton(
            text=obj['name'],
            callback_data=
            f'{obj["name"]}|{obj["id"]}:{KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID}'
        )
    elif key_type == KEY_GET_AV_DETAIL_RECORD_BY_ID:
        return InlineKeyboardButton(
            text=obj, callback_data=f'{obj}:{KEY_GET_AV_DETAIL_RECORD_BY_ID}')
    elif key_type == KEY_SEARCH_STAR_BY_NAME:
        return InlineKeyboardButton(
            text=obj, callback_data=f'{obj}:{KEY_SEARCH_STAR_BY_NAME}')


def send_msg_btns(max_btn_per_row: int,
                  max_row_per_msg: int,
                  key_type: str,
                  title: str,
                  objs: list,
                  extra_btns=[],
                  extra_btns_br=True,
                  page_btns=[]):
    '''发送按钮消息

    :param int max_btn_per_row: 每行最大按钮数量
    :param int max_row_per_msg: 每条消息最多行数
    :param str key_type: 按钮种类
    :param str title: 消息标题
    :param dict objs: 数据对象数组
    :param list extra_btns: 附加按钮列表，每行一个按钮，附加在每条消息尾部，默认为空
    :param bool extra_btns_br: 附加按钮列表是否换行，默认换行
    :param list page_btns: 分页块
    '''
    # 初始化数据
    markup = InlineKeyboardMarkup()
    row_count = 0
    btns = []
    # 开始生成按钮和发送消息
    for obj in objs:
        btns.append(create_btn(key_type, obj))
        # 若一行按钮的数量达到 max_btn_per_row，则加入行
        if len(btns) == max_btn_per_row:
            markup.row(*btns)
            row_count += 1
            btns = []
        # 若消息中行数达到 max_row_per_msg，则发送消息
        if row_count == max_row_per_msg:
            if extra_btns_br:
                for extra_btn in extra_btns:
                    markup.row(extra_btn)
            else:
                markup.row(*extra_btns)
            if page_btns != []:
                markup.row(*page_btns)
            send_msg(msg=title, markup=markup)
            row_count = 0
            markup = InlineKeyboardMarkup()
    # 若当前行按钮数量不为 0，则加入行
    if btns != []:
        markup.row(*btns)
        row_count += 1
    # 若当前行数不为 0，则发送消息
    if row_count != 0:
        if extra_btns_br:
            for extra_btn in extra_btns:
                markup.row(extra_btn)
        else:
            markup.row(*extra_btns)
        if page_btns != []:
            markup.row(*page_btns)
        send_msg(msg=title, markup=markup)


def get_page_elements(objs: dict, page: int, col: int, row: int,
                      key_type: str) -> typing.Tuple[dict, list, str]:
    '''获取当前页对象字典，分页按钮列表，数量标题

    :param dict objs: 对象字典
    :param int page: 当前页
    :param int col: 当前页列数
    :param int row: 当前页行数
    :param str key_type: 按键类型
    :return tuple[dict, list, str]: 当前页对象字典，分页按钮列表，数量标题
    '''
    # 记录总数
    record_count_total = len(objs)
    # 每页记录数
    record_count_per_page = col * row
    # 页数
    if record_count_per_page > record_count_total:
        page_count = 1
    else:
        page_count = math.ceil(record_count_total / record_count_per_page)
    # 如果要获取的页大于总页数，那么获取的页设为最后一页
    if page > page_count:
        page = page_count
    # 获取当前页对象字典
    start_idx = (page - 1) * record_count_per_page
    objs = objs[start_idx:start_idx + record_count_per_page]
    # 获取按键列表
    if page == 1:
        to_previous = 1
    else:
        to_previous = page - 1
    if page == page_count:
        to_next = page_count
    else:
        to_next = page + 1
    btn_to_first = InlineKeyboardButton(text='<<',
                                        callback_data=f'1:{key_type}')
    btn_to_previous = InlineKeyboardButton(
        text='<', callback_data=f'{to_previous}:{key_type}')
    btn_to_current = InlineKeyboardButton(text=f'-{page}-',
                                          callback_data=f'{page}:{key_type}')
    btn_to_next = InlineKeyboardButton(text='>',
                                       callback_data=f'{to_next}:{key_type}')
    btn_to_last = InlineKeyboardButton(
        text='>>', callback_data=f'{page_count}:{key_type}')
    # 获取数量标题
    title = f'总数：<b>{record_count_total}</b>，总页数：<b>{page_count}</b>'
    return objs, [
        btn_to_first, btn_to_previous, btn_to_current, btn_to_next, btn_to_last
    ], title


def get_stars_record(page=1):
    '''获取演员收藏记录
    
    :param int page: 第几页，默认第一页
    '''
    # 初始化数据
    record, is_star_exists, _ = recorder.check_has_record()
    if not record or not is_star_exists:
        send_msg('尚无演员收藏记录 =_=')
        return
    stars = record['stars']
    col, row = 4, 5
    objs, page_btns, title = get_page_elements(objs=stars,
                                               page=page,
                                               col=col,
                                               row=row,
                                               key_type=KEY_GET_STARS_RECORD)
    # 发送按钮消息
    send_msg_btns(max_btn_per_row=col,
                  max_row_per_msg=row,
                  key_type=KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID,
                  title='收藏的演员：' + title,
                  objs=objs,
                  page_btns=page_btns)


def get_star_detail_record(star_name: str, star_id: str):
    '''根据演员名称和编号获取该演员更多信息

    :param str star_name: 演员名称
    :param str star_id: 演员编号
    '''
    # 初始化数据
    record, _, is_avs_exists = recorder.check_has_record()
    if not record:
        send_msg('尚无收藏记录 =_=')
        return
    avs = []
    star_avs = []
    if is_avs_exists:
        avs = record['avs']
        for av in avs:
            # 如果演员编号在该 AV 的演员编号列表中
            if star_id in av['stars']:
                star_avs.append(av['id'])
    # 发送按钮消息
    extra_btn1 = InlineKeyboardButton(
        text=f'演员随机 AV',
        callback_data=f'{star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}')
    extra_btn2 = InlineKeyboardButton(
        text=f'演员最新 AV',
        callback_data=f'{star_name}|{star_id}:{KEY_GET_NEW_AVS_BY_STAR_NAME_ID}'
    )
    extra_btn3 = InlineKeyboardButton(
        text=f'取消收藏', callback_data=f'{star_id}:{KEY_UNDO_RECORD_STAR}')
    title = f'<code>{star_name}</code> | <a href="{common.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{util_javbus.BASE_URL_SEARCH_BY_STAR_ID}/{star_id}">Javbus</a>'
    if len(star_avs) == 0:  # 没有该演员对应 AV 收藏记录
        markup = InlineKeyboardMarkup()
        markup.row(extra_btn1, extra_btn2, extra_btn3)
        send_msg(msg=title, markup=markup)
        return
    send_msg_btns(max_btn_per_row=4,
                  max_row_per_msg=10,
                  key_type=KEY_GET_AV_DETAIL_RECORD_BY_ID,
                  title=title,
                  objs=star_avs,
                  extra_btns_br=False,
                  extra_btns=[extra_btn1, extra_btn2, extra_btn3])


def get_avs_record(page=1):
    '''获取番号收藏记录
    
    :param int page: 第几页，默认第一页
    '''
    # 初始化数据
    record, _, is_avs_exists = recorder.check_has_record()
    if not record or not is_avs_exists:
        send_msg('尚无 AV 收藏记录 =_=')
        return
    avs = [av['id'] for av in record['avs']]
    # 发送按钮消息
    extra_btn1 = InlineKeyboardButton(
        text='随机高分 AV', callback_data=f'0:{KEY_RANDOM_GET_AV_NICE}')
    extra_btn2 = InlineKeyboardButton(
        text='随机最新 AV', callback_data=f'0:{KEY_RANDOM_GET_AV_NEW}')
    col, row = 4, 10
    objs, page_btns, title = get_page_elements(objs=avs,
                                               page=page,
                                               col=col,
                                               row=row,
                                               key_type=KEY_GET_AVS_RECORD)
    send_msg_btns(max_btn_per_row=col,
                  max_row_per_msg=row,
                  key_type=KEY_GET_AV_DETAIL_RECORD_BY_ID,
                  title='收藏的番号：' + title,
                  objs=objs,
                  extra_btns=[extra_btn1, extra_btn2],
                  extra_btns_br=False,
                  page_btns=page_btns)


def get_av_detail_record(id: str):
    '''根据番号获取该番号更多信息

    :param str id: 番号
    '''
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f'获取对应 AV',
                                callback_data=f'{id}:{KEY_GET_AV_BY_ID}')
    btn2 = InlineKeyboardButton(text=f'取消收藏',
                                callback_data=f'{id}:{KEY_UNDO_RECORD_AV}')
    markup.row(btn1, btn2)
    send_msg(msg=f'<code>{id}</code>', markup=markup)


def get_av_by_id(id: str,
                 send_to_pikpak=False,
                 is_nice=True,
                 magnet_max_count=3,
                 not_send=False) -> dict:
    '''根据番号获取 av

    :param str id: 番号
    :param bool send_to_pikpak: 是否发给 pikpak，默认是
    :param bool is_nice: 是否过滤磁链，默认是
    :param int magnet_max_count: 过滤后磁链的最大数目，默认为 3
    :param not_send: 是否不发送 AV 结果，默认发送
    :return dict: 当不发送 AV 结果时，返回得到的 AV（如果有）
    '''
    # 获取 AV
    av_score = None
    futures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        if not not_send:
            futures[executor.submit(util_dmm.get_score_by_id,
                                    id)] = 0  # 获取 AV 评分
        futures[executor.submit(util_javbus.get_av_by_id, id, is_nice,
                                magnet_max_count)] = 1  # 通过 javbus 获取 AV
        futures[executor.submit(util_sukebei.get_av_by_id, id, is_nice,
                                magnet_max_count)] = 2  # 通过 sukebei 获取 AV
        for future in concurrent.futures.as_completed(futures):
            future_type = futures[future]
            if future_type == 0:
                _, av_score = future.result()
            elif future_type == 1:
                code_javbus, av_javbus = future.result()
            elif future_type == 2:
                code_sukebei, av_sukebei = future.result()
    if code_javbus != 200 and code_sukebei != 200:
        if code_javbus == 502 or code_sukebei == 502:
            send_msg_code(502)
        else:
            send_msg_code(404)
        return
    if code_javbus == 200:  # 优先选择 javbus
        av = av_javbus
        av_url = f'{util_javbus.BASE_URL}/{id}'
    elif code_sukebei == 200:
        av = av_sukebei
        av_url = f'{util_sukebei.BASE_URL}?q={id}'
    if not_send:
        return av
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
    if av_title != '':
        msg += f'''【标题】<a href="{av_url}">{av_title}</a>
'''
    msg += f'''【番号】<code>{av_id}</code>
'''
    if av_date != '':
        msg += f'''【日期】{av_date}
'''
    if av_score:
        msg += f'''【评分】{av_score}
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
        wiki = f'{common.BASE_URL_JAPAN_WIKI}/{name}'
        msg += f'''【演员】<code>{name}</code> | <a href="{wiki}">Wiki</a> | <a href="{link}">Javbus</a>
'''
    if av_tags != '':
        msg += f'''【标签】{av_tags}
'''
    # 加上其它消息
    msg += f'''【其它】<a href="https://t.me/{common.PIKPAK_BOT_NAME}">@{common.PIKPAK_BOT_NAME}</a> | <a href="{common.PROJECT_ADDRESS}">项目地址</a>
'''
    # 加上磁链消息
    magnet_send_to_pikpak = ''
    for i, magnet in enumerate(av_magnets):
        if i == 0:
            magnet_send_to_pikpak = magnet['link']
        msg_tmp = f'''【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>
'''
        if len(msg + msg_tmp) >= 2000:
            break
        msg += msg_tmp
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
    star_record_btn = None
    if len(av_stars) == 1:
        show_star_name = av_stars[0]['name']
        show_star_link = av_stars[0]['link']
        show_star_id = show_star_link[show_star_link.rfind('/') + 1:]
        if recorder.check_star_exists(star_id=show_star_id):
            star_record_btn = InlineKeyboardButton(
                text=f'取消收藏{show_star_name}',
                callback_data=f'{show_star_id}:{KEY_UNDO_RECORD_STAR}')
        else:
            star_record_btn = InlineKeyboardButton(
                text=f'收藏{show_star_name}',
                callback_data=
                f'{show_star_name}|{show_star_id}:{KEY_RECORD_STAR}')
    star_ids = ''
    for i, star in enumerate(av_stars):
        star_link = star['link']
        star_id = star_link[star_link.rfind('/') + 1:]
        star_ids += star_id + '|'
        if i >= 5:
            star_ids += '...|'
            break
    if star_ids != '': star_ids = star_ids[:len(star_ids) - 1]
    if recorder.check_id_exists(id=av_id):
        av_record_btn = InlineKeyboardButton(
            text=f'取消收藏番号', callback_data=f'{av_id}:{KEY_UNDO_RECORD_AV}')
    else:
        av_record_btn = InlineKeyboardButton(
            text=f'收藏番号', callback_data=f'{av_id}|{star_ids}:{KEY_RECORD_AV}')
    if star_record_btn:
        markup.row(av_record_btn, star_record_btn)
    else:
        markup.row(av_record_btn)
    # 发送消息
    if av_img == '':
        send_msg(msg=msg, markup=markup)
    else:
        try:
            bot.send_photo(chat_id=common.TG_CHAT_ID,
                           photo=av_img,
                           caption=msg,
                           parse_mode='HTML',
                           reply_markup=markup)
        except Exception:  # 少数图片可能没法发送
            send_msg(msg=msg, markup=markup)
    # 发给pikpak
    if common.USE_PIKPAK == 1 and magnet_send_to_pikpak != '' and send_to_pikpak:
        send_magnet_to_pikpak(magnet_send_to_pikpak)


def send_magnet_to_pikpak(magnet: str):
    '''发送磁链到pikpak
    
    :param str magnet: 磁链
    '''
    name = common.PIKPAK_BOT_NAME
    if util_pikpak.send_msg(magnet):
        send_msg(
            f'已经将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>')
    else:
        send_msg(
            f'未能将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>')


def get_sample(id: str):
    '''根据番号获取av截图

    :param str id: 番号
    '''
    # 获取截图
    code, samples = util_javbus.get_samples_by_id(id)
    if not check_success(code):
        return
    # 发送图片列表
    samples_imp = []
    sample_error = False
    for sample in samples:
        samples_imp.append(InputMediaPhoto(sample))
        if len(samples_imp) == 10:  # 图片数目达到 10 张则发送一次
            try:
                bot.send_media_group(chat_id=common.TG_CHAT_ID,
                                     media=samples_imp)
                samples_imp = []
            except Exception:
                sample_error = True
                send_msg('图片解析失败 Q_Q')
                break
    if samples_imp != [] and not sample_error:
        try:
            bot.send_media_group(chat_id=common.TG_CHAT_ID, media=samples_imp)
        except Exception:
            send_msg('图片解析失败 Q_Q')


def watch_av(id: str, type: str):
    '''获取番号对应视频

    :param str id: 番号
    :param str type: 0 预览视频 | 1 完整视频
    '''
    if type == 0:
        futures = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures[executor.submit(util_dmm.get_pv_by_id, id)] = 1
            futures[executor.submit(util_avgle.get_pv_by_id, id)] = 2
            for future in concurrent.futures.as_completed(futures):
                if futures[future] == 1:
                    code_dmm, pv_dmm = future.result()
                elif futures[future] == 2:
                    code_avgle, pv_avgle = future.result()
        if code_dmm != 200 and code_avgle != 200:
            if code_dmm == 502 or code_avgle == 502:
                send_msg_code(502)
            else:
                send_msg_code(404)
        if code_dmm == 200:  # 优先 dmm
            try:
                # 获取更清晰的视频
                pv_dmm_nice = util_dmm.get_nice_pv_by_src(pv_dmm)
                # 发送普通视频，附带更清晰的视频链接
                bot.send_video(
                    chat_id=common.TG_CHAT_ID,
                    video=pv_dmm,
                    caption=
                    f'通过 DMM 搜索得到结果，<a href="{pv_dmm_nice}">在这里观看更清晰的版本</a>',
                    parse_mode='HTML')
            except Exception:
                send_msg(
                    f'通过 DMM 搜索得到结果，但视频解析失败：<a href="{pv_dmm_nice}">视频地址</a> Q_Q'
                )
        elif code_avgle == 200:
            try:
                bot.send_video(
                    chat_id=common.TG_CHAT_ID,
                    video=pv_avgle,
                    caption=f'通过 Avgle 搜索得到结果：<a href="{pv_avgle}">视频地址</a>',
                    parse_mode='HTML')
            except Exception:
                send_msg(
                    f'通过 Avgle 搜索得到结果，但视频解析失败：<a href="{pv_avgle}">视频地址</a> Q_Q'
                )
    elif type == 1:
        code, video = util_avgle.get_fv_by_id(id)
        if check_success(code):
            send_msg(f'Avgle 视频地址：{video}')


def search_star(star_name: str):
    '''根据演员名称搜索演员

    :param str star_name: 演员名称
    '''
    code, star_id = util_javbus.check_star_exists(star_name)
    if not check_success(code):
        return
    if recorder.check_star_exists(star_id):
        get_star_detail_record(star_name=star_name, star_id=star_id)
        return
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text='演员最新 AV',
            callback_data=
            f'{star_name}|{star_id}:{KEY_GET_NEW_AVS_BY_STAR_NAME_ID}'),
        InlineKeyboardButton(
            text='演员随机 AV',
            callback_data=f'{star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}'))
    send_msg(
        msg=
        f'<code>{star_name}</code> | <a href="{common.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{util_javbus.BASE_URL_SEARCH_BY_STAR_NAME}/{star_name}">Javbus</a>',
        markup=markup)


def get_top_stars(page=1):
    '''获取 DMM 排行榜前 100 名女优，每页 20 位女优
    
    :param int page: 第几页，默认第一页
    '''
    code, stars = util_dmm.get_all_top_stars()
    if not check_success(code):
        return
    col, row = 4, 5
    objs, page_btns, title = get_page_elements(objs=stars,
                                               page=page,
                                               col=4,
                                               row=5,
                                               key_type=KEY_GET_TOP_STARS)
    send_msg_btns(max_btn_per_row=col,
                  max_row_per_msg=row,
                  key_type=KEY_SEARCH_STAR_BY_NAME,
                  title='DMM 女优排行榜前 100 位：' + title,
                  objs=objs,
                  page_btns=page_btns)


def get_msg_param(msg: str) -> str:
    '''获取消息参数

    :param str msg: 消息文本，已经通过 strip() 函数将两旁空白清除
    :return str: 消息参数（保证只有一个）
    '''
    msgs = msg.split(' ', 1)  # 划分为两部分
    if len(msgs) > 1:  # 有参数
        param = ''.join(msgs[1].split())  # 去除参数所有空白
        if param != '':
            return param


def get_more_magnets(id: str):
    '''根据番号获取更多磁链
    
    :param id: 番号
    '''
    av = get_av_by_id(id=id, is_nice=False, not_send=True)
    if not av:
        return
    msg = ''
    for magnet in av['magnets']:
        msg_tmp = f'''【{magnet["size"]}】<code>{magnet["link"]}</code>
'''
        if len(msg + msg_tmp) >= 4000:
            send_msg(msg)
            msg = msg_tmp
        else:
            msg += msg_tmp
    if msg != '':
        send_msg(msg)


def get_star_new_avs(star_name: str, star_id: str):
    '''获取演员最新 AV

    :param str star_name: 演员名称
    :param str star_id: 演员 id
    '''
    code, ids = util_javbus.get_new_ids_by_star_id(star_id=star_id)
    title = f'<code>{star_name}</code> 最新 AV'
    if check_success(code):
        btns = [
            InlineKeyboardButton(text=id,
                                 callback_data=f'{id}:{KEY_GET_AV_BY_ID}')
            for id in ids
        ]
        if len(btns) <= 4:
            send_msg(msg=title, markup=InlineKeyboardMarkup().row(*btns))
        else:
            markup = InlineKeyboardMarkup()
            markup.row(*btns[:4])
            markup.row(*btns[4:])
            send_msg(msg=title, markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def listen_callback(call):
    '''消息回调处理器

    :param _type_ call: 触发回调的消息内容
    '''
    send_action_typing()
    # 提取回调内容
    s = call.data.rfind(':')
    content = call.data[:s]
    key_type = call.data[s + 1:]
    # 检查按键类型并处理
    if key_type == KEY_WATCH_PV_BY_ID:
        watch_av(id=content, type=0)
    elif key_type == KEY_WATCH_FV_BY_ID:
        watch_av(id=content, type=1)
    elif key_type == KEY_GET_SAMPLE_BY_ID:
        get_sample(id=content)
    elif key_type == KEY_GET_MORE_MAGNETS_BY_ID:
        get_more_magnets(id=content)
    elif key_type == kEY_RANDOM_GET_AV_BY_STAR_ID:
        code, id = util_javbus.get_id_by_star_id(star_id=content)
        if check_success(code):
            get_av_by_id(id=id)
    elif key_type == KEY_GET_NEW_AVS_BY_STAR_NAME_ID:
        tmp = content.split('|')
        star_name = tmp[0]
        star_id = tmp[1]
        get_star_new_avs(star_name=star_name, star_id=star_id)
    elif key_type == KEY_RECORD_STAR:
        s = content.find('|')
        star_name = content[:s]
        star_id = content[s + 1:]
        if recorder.record_star(star_name=star_name, star_id=star_id):
            send_msg(f'成功收藏<code>{star_name}</code> ^_^')
        else:
            send_msg_code(500)
    elif key_type == KEY_RECORD_AV:
        res = content.split('|')
        id = res[0]
        stars = [s for s in res[1:]]
        if recorder.record_id(id=id, stars=stars):
            send_msg_code(f'成功收藏 <code>{id}</code> ^_^')
        else:
            send_msg_code(500)
    elif key_type == KEY_GET_STARS_RECORD:
        get_stars_record(page=int(content))
    elif key_type == KEY_GET_AVS_RECORD:
        get_avs_record(page=int(content))
    elif key_type == KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
        s = content.find('|')
        get_star_detail_record(star_name=content[:s], star_id=content[s + 1:])
    elif key_type == KEY_GET_AV_DETAIL_RECORD_BY_ID:
        get_av_detail_record(id=content)
    elif key_type == KEY_GET_AV_BY_ID:
        get_av_by_id(id=content)
    elif key_type == KEY_RANDOM_GET_AV_NICE:
        code, id = util_javlibrary.get_random_id(0)
        if check_success(code):
            get_av_by_id(id=id)
    elif key_type == KEY_RANDOM_GET_AV_NEW:
        code, id = util_javlibrary.get_random_id(1)
        if check_success(code):
            get_av_by_id(id=id)
    elif key_type == KEY_UNDO_RECORD_AV:
        if recorder.undo_record_id(id=content):
            send_msg_code(200)
        else:
            send_msg_code(500)
    elif key_type == KEY_UNDO_RECORD_STAR:
        if recorder.undo_record_star(star_id=content):
            send_msg_code(200)
        else:
            send_msg_code(500)
    elif key_type == KEY_SEARCH_STAR_BY_NAME:
        search_star(content)
    elif key_type == KEY_GET_TOP_STARS:
        get_top_stars(page=int(content))


@bot.message_handler(content_types=['text', 'photo', 'animation', 'video'])
def handle_message(message):
    '''消息处理器

    :param _type_ message: 消息
    '''
    send_action_typing()
    # 拦截请求，检查消息来源
    if str(message.from_user.id) != common.TG_CHAT_ID:
        LOG.info(f'拦截到非目标用户请求，id: {message.from_user.id}')
        bot.send_message(
            chat_id=message.from_user.id,
            text=
            f'该机器人仅供私人使用, 如需使用请自行部署：<a href="{common.PROJECT_ADDRESS}">项目地址</a>',
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
    elif msg == '/help' or msg.find('/start') != -1:
        help()
    elif msg == '/nice':
        code, id = util_javlibrary.get_random_id(0)
        if check_success(code):
            get_av_by_id(id=id)
    elif msg == '/new':
        code, id = util_javlibrary.get_random_id(1)
        if check_success(code):
            get_av_by_id(id=id)
    elif msg == '/stars':
        get_stars_record()
    elif msg == '/avs':
        get_avs_record()
    elif msg == '/record':
        if os.path.exists(common.PATH_RECORD_FILE):
            bot.send_document(chat_id=common.TG_CHAT_ID,
                              document=types.InputFile(
                                  common.PATH_RECORD_FILE))
        else:
            send_msg('尚无收藏记录 =_=')
    elif msg == '/top100':
        get_top_stars(1)
    elif msg.find('/star') != -1:
        param = get_msg_param(msg)
        if param:
            send_msg(f'搜索演员：{param} ......')
            search_star(param)
    elif msg.find('/av') != -1:
        param = get_msg_param(msg)
        if param:
            send_msg(f'搜索番号：{param} ......')
            get_av_by_id(id=param, send_to_pikpak=True)
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
            send_msg(f'检测到番号：{ids_msg}，开始搜索......')
            for id in ids:
                get_av_by_id(id=id, send_to_pikpak=True)


def test():
    '''用于测试'''
    return


def help():
    '''发送指令帮助消息'''
    msg = '''发送给机器人一条含有番号的消息，机器人会匹配并搜索消息中所有符合<b>“字母-数字”</b>格式的番号，其它格式的番号可通过<code>/av</code>命令查找。

/help  查看指令帮助

/stars  获取收藏的演员

/avs  获取收藏的番号

/nice  随机获取一部高分 AV

/new  随机获取一部最新 AV

/top100  获取 DMM 女优排行榜前 100 位名单

/record  获取收藏记录文件

<code>/star</code>  后接演员名称（日语）可搜索该演员

<code>/av</code>  后接番号可搜索该番号
'''
    send_msg(msg)


def set_command():
    '''设置机器人命令'''
    tg_cmd_dict = {
        'help': '查看指令帮助',
        'stars': '获取收藏的演员',
        'avs': '获取收藏的 AV',
        'nice': '随机获取一部高分 AV',
        'new': '随机获取一部最新 AV',
        'top100': '获取 DMM 女优排行榜前 100 位名单',
        'record': '获取收藏记录文件',
    }
    cmds = []
    for cmd in tg_cmd_dict:
        cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
    bot.set_my_commands(cmds)


if __name__ == '__main__':
    set_command()
    bot.infinity_polling()