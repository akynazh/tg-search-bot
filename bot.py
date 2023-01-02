# -*- coding: UTF-8 -*-
import telebot
from telebot import types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import cfg
import json
import os
import sys
import re
import random
import logging
import string
import util_pikpak
import util_javbus
import util_avgle

TG_BOT_TOKEN = cfg.TG_BOT_TOKEN
bot = telebot.TeleBot(TG_BOT_TOKEN)
TG_CHAT_ID = cfg.TG_CHAT_ID
PATH_ROOT = sys.path[0]
PATH_RECORD_FILE = PATH_ROOT + '/record.json'
PATH_LOG_FILE = PATH_ROOT + '/log.txt'
proxies = {}
BASE_URL_JAVBUS = util_javbus.BASE_URL
if cfg.USE_PROXY == 1:
    proxies = {'http': cfg.PROXY_ADDR, 'https': cfg.PROXY_ADDR}
    apihelper.proxy = proxies


class Logger:

    def __init__(self, log_level):
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


def check_has_record() -> list:
    '''检查是否有记录，如果有则返回记录
    :return list: 记录
    '''
    # 初始化数据
    record = {}
    stars = []
    # 加载记录
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
    if record and 'stars' in record.keys():
        stars = record['stars']
    # 尚无记录
    if stars == [] or len(stars) == 0:
        send_msg('尚无记录 =_=')
        return None
    return stars


def record(name: str, id: str):
    '''记录演员

    :param str name: 演员名称
    :param str id: 演员编号
    '''
    # 加载记录
    stars = check_has_record()
    if not stars: stars = []
    # 更新记录
    exists = False
    for star in stars:
        if star['id'].lower() == id.lower():
            exists = True
            break
    # 如果记录得到更新则写回记录
    if not exists:
        LOG.info(f'收藏新的演员：{name}')
        stars.append({'name': name, 'id': id})
        with open(PATH_RECORD_FILE, 'w') as f:
            json.dump({'stars': stars},
                      f,
                      separators=(',', ': '),
                      indent=4,
                      ensure_ascii=False)


def get_record():
    stars = check_has_record()
    if not stars: return
    markup = InlineKeyboardMarkup()
    i = 0
    while i < len(stars):
        btn1 = InlineKeyboardButton(text=stars[i]['name'], callback_data=f'{stars[i]["id"]}:3')
        btn2, btn3 = None, None
        if i + 1 < len(stars): btn2 = InlineKeyboardButton(text=stars[i+1]['name'], callback_data=f'{stars[i+1]["id"]}:3')
        if i + 2 < len(stars): btn3 = InlineKeyboardButton(text=stars[i+2]['name'], callback_data=f'{stars[i+2]["id"]}:3')
        if btn2 and btn3: markup.row(btn1, btn2, btn3)
        elif btn2: markup.row(btn1, btn2)
        else: markup.row(btn1)
        i += 3
    send_msg(msg='收藏的演员如下，点击演员对应按钮可随机获取一部该演员的影片 ^-^', markup=markup)


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
    av = util_javbus.get_av_by_id(id, is_nice, magnet_max_count)
    # 未查找到该番号
    if not av:
        send_msg(f'妹查找到该番号：{id} Q_Q')
        return
    # 提取数据
    title = av['title']
    img = av['img']
    date = av['date']
    tags = av['tags']
    stars = av['stars']
    magnets = av['magnets']
    # 拼接消息
    av_url = f'{BASE_URL_JAVBUS}/{id}'
    msg = f'''【标题】<a href="{av_url}">{title}</a>
【日期】{date}
【标签】{tags}
【番号】<code>{id}</code>
'''
    # 加上演员消息
    if stars == []:
        msg += f'''【演员】未知
'''
    for i, star in enumerate(stars):
        if i >= 5:
            msg += f'''【演员】<a href="{av_url}">查看更多......</a>
'''
            break
        name = star['name']
        link = star['link']
        wiki = f'https://ja.wikipedia.org/wiki/{name}'
        msg += f'''【演员】<code>{name}</code> | <a href="{wiki}">Wiki</a> | <a href="{link}">其它AV</a>
'''
    # 加上磁链消息
    send_to_pikpak_magnet = ''
    for i, magnet in enumerate(magnets):
        if i == 0: send_to_pikpak_magnet = magnet
        msg += f'''【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>
'''
    # 生成回调按钮
    pv_btn = InlineKeyboardButton(text='预览', callback_data=f'{id}:0')
    fv_btn = InlineKeyboardButton(text='观看', callback_data=f'{id}:1')
    sample_btn = InlineKeyboardButton(text='截图', callback_data=f'{id}:2')
    more_btn = InlineKeyboardButton(text='更多磁链', callback_data=f'{id}:5')
    markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn, more_btn)
    if len(stars) == 1:
        name = stars[0]['name']
        link = stars[0]['link']
        star_id = link[link.rfind('/') + 1:]
        random_btn = InlineKeyboardButton(text=f'随机获取一部{name}的作品',
                                          callback_data=f'{star_id}:3')
        record_btn = InlineKeyboardButton(text=f'收藏{name}',
                                          callback_data=f'{name}|{star_id}:4')
        markup.row(record_btn, random_btn)
    # 发送消息
    bot.send_photo(chat_id=TG_CHAT_ID,
                   photo=img,
                   caption=msg,
                   parse_mode='HTML',
                   reply_markup=markup)
    # 发给pikpak
    if cfg.USE_PIKPAK == 1 and send_to_pikpak_magnet != '' and send_to_pikpak:
        name = cfg.PIKPAK_BOT_NAME
        if util_pikpak.send_msg(send_to_pikpak_magnet):  # 成功发送
            send_msg(
                f'已经将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>',
                pv=True)
        else:  # 发送失败
            send_msg(
                f'未能将磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a>',
                pv=True)


def get_sample_by_id(id: str):
    '''根据番号获取av截图

    :param str id: 番号
    '''
    # 获取截图
    samples = util_javbus.get_samples_by_id(id)
    if not samples:
        send_msg(f'未找到{id}对应截图 =_=')
        return
    # 发送图片列表
    samples_imp = []
    for i, sample in enumerate(samples):
        samples_imp.append(InputMediaPhoto(sample))
        if i == 9:  # 图片数目达到9张则发送一次
            bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
            samples_imp = []
    if samples_imp != []:
        bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)


def watch_av(id: str, type: str):
    '''获取番号对应在线视频

    :param str id: 番号
    :param str type: 0 预览视频 | 1 完整视频
    '''
    video = util_avgle.get_video_by_id(id)
    if video:
        if type == 0:
            bot.send_video(chat_id=TG_CHAT_ID, video=video['pv'])
        elif type == 1:
            send_msg(f'番号{id}对应视频地址：{video["fv"]}')
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
    type = call.data[idx + 1:]
    if type == '0':  # 类型0：发送番号对应预览视频
        watch_av(content, 0)
    elif type == '1':  # 类型1：发送番号对应完整视频
        watch_av(content, 1)
    elif type == '2':  # 类型2：发送番号对应视频截图
        get_sample_by_id(content)
    elif type == '3':  # 类型3：根据演员编号随机发送演员的一部av
        id = util_javbus.get_id_by_star_id(star_id=content)
        if id: get_av_by_id(id, send_to_pikpak=False)
        else: send_msg('获取失败，请重试=_=')
    elif type == '4':  # 类型4：收藏演员：star_name|star_id
        s = content.find('|')
        record(content[:s], content[s + 1:])
        send_msg('收藏成功 ^-^')
    elif type == '5':  # 类型5：获取更多磁链
        av = util_javbus.get_av_by_id(id=content, is_nice=False)
        if not av:
            send_msg('获取失败，请重试=_=')
            return
        msg = ''
        for magnet in av['magnets']:
            msg += f'''【{magnet["size"]}】<code>{magnet["link"]}</code>
'''
        send_msg(msg)


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
            '该机器人仅供私人使用, 如需使用请自行部署, 项目地址：https://github.com/akynazh/tg-jav-bot',
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
    # 处理消息
    if msg == '/test':
        test()
    elif msg == '/help':
        help()
    elif msg == '/random':
        id = util_javbus.get_id_from_home()
        get_av_by_id(id)
    elif msg.find('/star') != -1:
        param = get_msg_param(msg)
        if param:
            id = util_javbus.get_id_by_star_name(param)
            get_av_by_id(id, send_to_pikpak=False)
        else:
            get_record()
    else:
        ids = re.compile(r'[a-zA-Z]+-\d+').findall(msg)
        if not ids: send_msg('你滴消息不存在番号捏 =_=')
        else: get_av_by_id(
            id=ids[0],
            send_to_pikpak=True,
            is_nice=True,
        )


def test():
    '''用于测试'''
    return


def help():
    '''发送指令帮助消息'''
    msg = '''/help  查看指令帮助

/star  获取所有搜过的演员

/random  随机获取一部AV
'''
    send_msg(msg)


def set_command():
    '''设置机器人命令'''
    tg_cmd_dict = {
        'help': '查看指令帮助',
        'star': '获取收藏的演员',
        'random': '随机获取一部AV',
    }
    cmds = []
    for cmd in tg_cmd_dict:
        cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
    bot.set_my_commands(cmds)


if __name__ == '__main__':
    os.chdir(PATH_ROOT)
    LOG = Logger(log_level=logging.INFO).logger
    set_command()
    bot.infinity_polling()