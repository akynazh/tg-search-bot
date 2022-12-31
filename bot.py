# -*- coding: UTF-8 -*-
import telebot
from telebot import types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import cfg
import json
import os
import sys
import re
import string
import util_pikpak
import util_javbus
import util_avgle

TG_BOT_TOKEN = cfg.TG_BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN)
TG_CHAT_ID = cfg.TG_CHAT_ID
PATH_ROOT = sys.path[0]
PATH_RECORD_FILE = PATH_ROOT + '/record.json'
proxies = {}
BASE_URL_JAVBUS = 'https://javbus.com'
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}
    apihelper.proxy = proxies


def get_nice_magnets(magnets: list, prop: str, expect_val) -> list:
    '''过滤磁链列表

    :param list magnets: 要过滤的磁链列表
    :param str prop: 过滤属性
    :param _type_ expect_val: 过滤属性的期望值
    :return list: 过滤后的磁链列表
    '''
    if len(magnets) == 0:
        return []
    if len(magnets) == 1:
        return magnets

    magnets_nice = []
    for magnet in magnets:
        if magnet[prop] == expect_val:
            magnets_nice.append(magnet)

    # 如果过滤后已经没了，返回原来磁链列表
    if len(magnets_nice) == 0:
        return magnets
    return magnets_nice


def get_record(classify_by: str = ''):
    '''发送查询记录

    :param str classify_by: 分类字段, 演员: 'stars', 番号：'id', defaults to None
    '''
    avs = []
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        if classify_by != '':
            avs.sort(key=lambda i: i[classify_by])
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text='尚无记录 =_=')
        return
    msg = ''
    i = 1
    for av in avs:
        if classify_by == 'stars':
            msg += f'''{av["stars"]}  <a href="{BASE_URL_JAVBUS}/{av["id"]}">{av["id"]}</a>
'''
        else:
            msg += f'''<a href="{BASE_URL_JAVBUS}/{av["id"]}">{av["id"]}</a>  {av["stars"]}
'''
        i += 1
        if i == 30:
            bot.send_message(
                chat_id=TG_CHAT_ID,
                text=msg,
                disable_web_page_preview=True,
                parse_mode='HTML',
            )
            msg = ''
    if msg != '':
        bot.send_message(
            chat_id=TG_CHAT_ID,
            text=msg,
            disable_web_page_preview=True,
            parse_mode='HTML',
        )


def get_record_json():
    '''发送查询记录文件'''
    if os.path.exists(PATH_RECORD_FILE):
        bot.send_document(chat_id=TG_CHAT_ID,
                          document=types.InputFile(PATH_RECORD_FILE))
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text='尚无记录 =_=')


def record(id: str, stars: str):
    '''记录查询信息

    :param str id: 番号
    :param str stars: 演员
    '''
    avs = []
    new_av = {'id': id, 'stars': stars}
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
    exists = False
    for av in avs:
        if av['id'].lower() == id.lower():
            exists = True
            break
    if not exists:
        avs.append(new_av)
        record = {'avs': avs}
        with open(PATH_RECORD_FILE, 'w') as f:
            json.dump(record,
                      f,
                      separators=(',', ': '),
                      indent=4,
                      ensure_ascii=False)


def get_av_by_id(id: str):
    '''根据番号获取 av

    :param str id: 番号
    '''
    av = util_javbus.get_av(id)
    if not av:
        bot.send_message(chat_id=TG_CHAT_ID, text=f'妹查找到该番号：{id} Q_Q')
        return
    title = av['title']
    img = av['img']
    stars = av['stars']
    magnets = av['magnets']

    # 过滤磁链
    magnets = get_nice_magnets(magnets, 'hd', expect_val='1')
    magnets = get_nice_magnets(magnets, 'zm', expect_val='1')
    if len(magnets) > 4:
        magnets = magnets[0:4]

    # 拼接演员名称
    stars_msg = ''
    for star in stars:
        stars_msg += f'{star}  '
    stars_msg = stars_msg.strip()
    if stars_msg.strip() == '':
        stars_msg = 'unknown'

    # 一些重要链接
    url = f'{BASE_URL_JAVBUS}/{id}'
    wiki_url = f'https://ja.wikipedia.org/wiki/{stars_msg}'
    more_av_url = f'{BASE_URL_JAVBUS}/search/{stars_msg}'

    # 拼接消息
    msg = f'''【标题】<a href="{url}">{title}</a>
【番号】<code>{id}</code>
【演员】<code>{stars_msg}</code> | <a href="{wiki_url}">Wiki</a> | <a href="{more_av_url}">其它AV</a>'''

    # 加上磁链消息
    for i, magnet in enumerate(magnets):
        if i == 0: send_to_pikpak_magnet = magnet
        msg += f'''
【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>'''

    # 生成回调按钮
    pv_btn = InlineKeyboardButton(text='观看预览视频', callback_data=f'{id}:0')
    fv_btn = InlineKeyboardButton(text='观看完整视频', callback_data=f'{id}:1')
    markup = InlineKeyboardMarkup().row(pv_btn, fv_btn)

    # 发送消息
    bot.send_photo(chat_id=TG_CHAT_ID,
                   photo=img,
                   caption=msg,
                   parse_mode='HTML',
                   reply_markup=markup)

    # 发给pikpak
    if cfg.USE_PIKPAK == 1 and send_to_pikpak_magnet:
        send_to_pikpak(send_to_pikpak_magnet)

    # 记录查询
    record(id=id, stars=stars_msg)


def send_to_pikpak(magnet):
    '''将磁链发送到pikpak

    :param _type_ magnet: 磁链
    '''
    name = cfg.PIKPAK_BOT_NAME
    if util_pikpak.send_msg(magnet['link']):  # 成功发送
        bot.send_message(
            chat_id=TG_CHAT_ID,
            text=
            f'已经将筛选出的最佳磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a> ^-^',
            parse_mode='HTML',
        )
    else:  # 发送失败
        bot.send_message(
            chat_id=TG_CHAT_ID,
            text=
            f'未能将筛选出的最佳磁链<b>A</b>发送到 <a href="https://t.me/{name}">@{name}</a> 请自行发送或重试 =_=',
            parse_mode='HTML',
        )


def get_av(text: str):
    '''解析消息获得番号列表，遍历番号列表, 依次查询 av

    :param str text: 消息
    '''
    ids = re.compile(r'[a-zA-Z]+-\d+').findall(text)
    if not ids:
        bot.send_message(chat_id=TG_CHAT_ID, text='你滴消息不存在番号捏 =_=')
        return
    for i in range(0, len(ids)):
        ids[i] = ids[i].lower().strip()
    ids = list(set(ids))
    for id in ids:
        get_av_by_id(id)


def watch_av(id: str, type: str):
    '''获取番号对应在线视频

    :param str id: 番号
    :param str type: 0 预览视频 | 1 完整视频
    '''
    video = util_avgle.get_video(id)
    if video:
        if type == 0:
            bot.send_video(chat_id=TG_CHAT_ID, video=video['pv'])
        elif type == 1:
            bot.send_message(chat_id=TG_CHAT_ID, text=f'番号{id}对应视频地址：{video["fv"]}')
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text=f'未找到{id}对应视频 =_=')


def intercept_msg(message) -> bool:
    '''拦截请求，检查消息来源

    :param _type_ message: 消息
    :return bool: 是否为自己发送的消息
    '''
    if str(message.from_user.id) != TG_CHAT_ID:
        bot.send_message(
            chat_id=message.from_user.id,
            text='该机器人仅供私人使用哦, 如需使用请自行部署, \
项目地址：https://github.com/akynazh/tg-javbus-bot',
        )
        return False
    return True


@bot.message_handler(content_types=['text'])
def handle_text(message):
    '''处理文本消息

    :param _type_ message: 消息
    '''
    if not intercept_msg(message):
        return
    my_msg = message.text.strip()
    if my_msg == '/record':
        get_record()
    elif my_msg == '/record_id':
        get_record('id')
    elif my_msg == '/record_stars':
        get_record('stars')
    elif my_msg == '/record_json':
        get_record_json()
    else:
        get_av(my_msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    '''消息回调处理器

    :param _type_ call: 触发回调的消息内容
    '''
    lst = call.data.split(':')
    content = lst[0]
    type = lst[1]
    if type == '0':  # 类型0：发送番号对应预览视频
        watch_av(content, 0)
    elif type == '1':  # 类型1：发送番号对应完整视频
        watch_av(content, 1)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    '''处理图像消息

    :param _type_ message: 消息
    '''
    if not intercept_msg(message):
        return
    if message.caption:
        get_av(message.caption)


@bot.message_handler(content_types=['video'])
def handle_video(message):
    '''处理视频消息

    :param _type_ message: 消息
    '''
    if not intercept_msg(message):
        return
    if message.caption:
        get_av(message.caption)


def set_command():
    '''设置机器人命令'''
    tg_cmd_dict = {
        'record': '获取查询记录（默认根据查询时间排序）',
        'record_id': '获取查询记录，根据番号名称排序',
        'record_stars': '获取查询记录，根据演员名称排序',
        'record_json': '发送查询记录文件',
    }
    cmds = []
    for cmd in tg_cmd_dict:
        cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
    bot.set_my_commands(cmds)


if __name__ == '__main__':
    os.chdir(PATH_ROOT)
    set_command()
    bot.infinity_polling()
