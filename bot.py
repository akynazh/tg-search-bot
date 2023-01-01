# -*- coding: UTF-8 -*-
import telebot
from telebot import types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
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
MAGNET_MAX_COUNT = 3
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


def get_all_record():
    '''发送所有查询记录'''
    avs = []
    
    # 加载记录
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        
    # 尚无记录
    if avs == [] or len(avs) == 0:
        bot.send_message(chat_id=TG_CHAT_ID, text='尚无记录 =_=')
        return
    
    # 提取记录
    msg = ''
    i = 1
    for av in avs:
        stars = av['stars']
        stars_msg = ''
        if stars == []:
            stars_msg = '未知'
        for star in stars:
            name = star['name']
            link = star['link']
            stars_msg += f'<a href="{link}">{name}</a> '
        msg += f'''<a href="{BASE_URL_JAVBUS}/{av["id"]}">{av["id"]}</a>  {stars_msg.strip()}
'''
        i += 1
        # 满30条记录，发送记录
        if i == 30:
            bot.send_message(
                chat_id=TG_CHAT_ID,
                text=msg,
                disable_web_page_preview=True,
                parse_mode='HTML',
            )
            msg = ''
    
    # 发送记录
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


def get_record_by_id(id:str) -> dict:
    '''根据番号在本地记录中搜索av

    :param str id: 番号
    :return dict: av
    '''
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        for av in avs:
            if av['id'] == id:
                return av


def get_record_by_star_name(star_name:str) -> list:
    '''根据演员名称在本地记录中搜索av

    :param str star_name 演员名称
    :return list: 搜过的该演员的av列表
    '''
    res = []
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        for av in avs:
            stars = av['stars']
            for star in stars:
                if star['name'] == star_name:
                    res.append(av)
    return res


def record(new_av:dict):
    '''记录查询信息

    :param dict av
    '''
    new_av_id = new_av['id']
    avs = []
    
    # 加载记录
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        
    # 更新记录
    exists = False
    for av in avs:
        if av['id'].lower() == new_av_id.lower():
            exists = True
            break
    
    # 如果记录得到更新则写回记录
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
    date = av['date']
    tags = av['tags']
    stars = av['stars']
    magnets = av['magnets']
    samples = av['samples']

    # 过滤磁链
    magnets = get_nice_magnets(magnets, 'hd', expect_val='1')
    magnets = get_nice_magnets(magnets, 'zm', expect_val='1')
    if len(magnets) > MAGNET_MAX_COUNT:
        magnets = magnets[0:MAGNET_MAX_COUNT]

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
        if i >= 10:
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
        msg += f'''
【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>'''

    # 生成回调按钮
    pv_btn = InlineKeyboardButton(text='观看预览视频', callback_data=f'{id}:0')
    fv_btn = InlineKeyboardButton(text='观看完整视频', callback_data=f'{id}:1')
    sample_btn = InlineKeyboardButton(text='获取截图', callback_data=f'{id}:2')
    markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn)

    # 发送消息
    bot.send_photo(chat_id=TG_CHAT_ID,
                   photo=img,
                   caption=msg,
                   parse_mode='HTML',
                   reply_markup=markup)

    # 发给pikpak
    if cfg.USE_PIKPAK == 1 and send_to_pikpak_magnet != '':
        send_to_pikpak(send_to_pikpak_magnet)

    # 记录本次查询
    av['magnets'] = magnets
    record(av)


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
        
        
def get_sample_by_id(id: str):
    '''根据番号获取av截图

    :param str id: 番号
    '''
    av = get_record_by_id(id)
    samples = av['samples']
    samples_imp = []
    for i, sample in enumerate(samples):
        samples_imp.append(InputMediaPhoto(sample))
        if i == 9: # 图片数目达到9张则发送一次
            bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
            samples_imp = []
    if samples_imp != []:
        bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text=f'未找到{id}对应截图 =_=')


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
            bot.send_message(chat_id=TG_CHAT_ID,
                             text=f'番号{id}对应视频地址：{video["fv"]}')
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
        get_all_record()
    elif my_msg == '/record_json':
        get_record_json()
    else:
        get_av(my_msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    '''消息回调处理器

    :param _type_ call: 触发回调的消息内容
    '''
    idx = call.data.rfind(':')
    content = call.data[:idx]
    type = call.data[idx+1:]
    if type == '0':  # 类型0：发送番号对应预览视频
        watch_av(content, 0)
    elif type == '1':  # 类型1：发送番号对应完整视频
        watch_av(content, 1)
    elif type == '2': # 类型2：发送番号对应视频截图
        get_sample_by_id(content)


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