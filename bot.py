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


def get_nice_magnets(magnets: list, prop: str, expect_val) -> list:
    '''过滤磁链列表

    :param list magnets: 要过滤的磁链列表
    :param str prop: 过滤属性
    :param _type_ expect_val: 过滤属性的期望值
    :return list: 过滤后的磁链列表
    '''
    # 已经无法再过滤
    if len(magnets) == 0:
        return []
    if len(magnets) == 1:
        return magnets
    # 开始过滤
    magnets_nice = []
    for magnet in magnets:
        if magnet[prop] == expect_val:
            magnets_nice.append(magnet)
    # 如果过滤后已经没了，返回原来磁链列表
    if len(magnets_nice) == 0:
        return magnets
    return magnets_nice


def check_has_record() -> list:
    '''检查是否有记录，如果有，返回记录

    :return list: 记录
    '''
    avs = []
    # 加载记录
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
    # 尚无记录
    if avs == [] or len(avs) == 0:
        send_msg('尚无记录 =_=')
        return None
    return avs


def get_record(num: int = -1):
    '''发送所有查询记录
    
    @param int num: 查询条数
    '''
    # 检查并获取记录
    avs = check_has_record()
    if not avs: return
    # 提取记录
    msg = ''
    if num == -1: num = len(avs)
    i, c = len(avs) - 1, 1
    while i != -1:
        av = avs[i]
        stars = av['stars']
        stars_msg = ''
        if stars == []:
            stars_msg = '未知'
        else:
            stars_msg = f'<a href="{stars[0]["link"]}">{stars[0]["name"]}</a>'
            if len(stars) > 1:
                stars_msg += '...'
        msg += f'''<a href="{BASE_URL_JAVBUS}/{av["id"]}">{av["id"]}</a>  {stars_msg}
'''
        c += 1
        if c % 30 == 0:  # 满30条就发送记录
            send_msg(msg)
            msg = ''
        i -= 1
        num -= 1
        if num == 0: break
    # 发送记录
    if msg != '':
        send_msg(msg)


def get_record_stars():
    '''获取所有查询过的演员'''
    # 检查并获取记录
    avs = check_has_record()
    if not avs: return
    # 提取记录
    msg = ''
    links = {}
    c = 1
    for av in avs:
        stars = av['stars']
        for star in stars:
            link = star['link']
            name = star['name']
            if link in links.keys(): continue
            links[link] = 1
            msg += f'''
<a href="{link}">{c}</a>  <code>{name}</code>'''
            c += 1
            if c % 30 == 0:  # 满30条就发送记录
                send_msg(msg)
                msg = ''
    # 发送记录
    if msg != '':
        send_msg(msg)


def get_record_json():
    '''发送查询记录文件'''
    if os.path.exists(PATH_RECORD_FILE):
        bot.send_document(chat_id=TG_CHAT_ID,
                          document=types.InputFile(PATH_RECORD_FILE))
    else:
        send_msg('尚无记录 =_=')


def get_record_by_id(id: str) -> dict:
    '''根据番号在本地记录中搜索av

    :param str id: 番号
    :return dict: av
    '''
    avs = check_has_record()
    if avs:
        for av in avs:
            if av['id'] == id:
                return av


def get_record_by_star_name(star_name: str) -> list:
    '''根据演员名称在本地记录中搜索av

    :param str star_name 演员名称
    :return list: 搜过的该演员的av列表
    '''
    avs = check_has_record()
    if not avs: return
    # 生成消息
    res = []
    link = ''
    for av in avs:
        stars = av['stars']
        for star in stars:
            if star['name'] == star_name:
                res.append(av)
                if link == '': link = star['link']
    msg = f'<a href="{link}">{star_name}</a>'
    # 生成回调按钮
    markup = InlineKeyboardMarkup()
    for av in res:
        id = av["id"]
        btn = InlineKeyboardButton(text=f'{id}', callback_data=f'{id}:3')
        markup.add(btn)
    send_msg(msg=msg, markup=markup)


def record(new_av: dict):
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
    # 首先在本地中查询记录
    av = get_record_by_id(id)
    record_exists = True
    # 本地查询记录不存在该番号
    if not av:
        record_exists = False
        av = util_javbus.get_av(id)
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
    samples = av['samples']
    # 过滤磁链
    if not record_exists:  # 如果是最新查询的，需要进行过滤
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
    # 加上其它消息
    if record_exists:
        msg += f'''【其它】从本地记录中获取到该内容
'''
    else:
        msg += f'''【其它】从网络中查询到该内容
'''
    # 加上磁链消息
    send_to_pikpak_magnet = ''
    for i, magnet in enumerate(magnets):
        if i == 0: send_to_pikpak_magnet = magnet
        msg += f'''【{string.ascii_letters[i].upper()}. {magnet["size"]}】<code>{magnet["link"]}</code>
'''
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
    if cfg.USE_PIKPAK == 1 and send_to_pikpak_magnet != '' and not record_exists:
        send_to_pikpak(send_to_pikpak_magnet)
    # 记录本次查询
    if not record_exists:
        av['magnets'] = magnets
        record(av)


def send_to_pikpak(magnet):
    '''将磁链发送到pikpak

    :param _type_ magnet: 磁链
    '''
    name = cfg.PIKPAK_BOT_NAME
    if util_pikpak.send_msg(magnet['link']):  # 成功发送
        send_msg(f'已经将筛选出的最佳磁链 <b>A</b> 发送到 <a href="https://t.me/{name}">@{name}</a> ^-^', pv=True)
    else:  # 发送失败
        send_msg('未能将筛选出的最佳磁链<b>A</b>发送到 <a href="https://t.me/{name}">@{name}</a> 请自行发送或重试 =_=', pv=True)


def get_av(text: str):
    '''解析消息获得番号列表，遍历番号列表, 依次查询 av

    :param str text: 消息
    '''
    # 正则解析消息获取番号列表
    ids = re.compile(r'[a-zA-Z]+-\d+').findall(text)
    if not ids:
        send_msg('你滴消息不存在番号捏 =_=')
        return
    for i in range(0, len(ids)):
        ids[i] = ids[i].lower().strip()
    # 番号去重
    ids = list(set(ids))
    # 开始查询
    for id in ids:
        get_av_by_id(id)


def get_sample_by_id(id: str):
    '''根据番号获取av截图

    :param str id: 番号
    '''
    av = get_record_by_id(id)
    if not av:
        send_msg('本地找不到该番号记录，请重新获取番号消息=_=')
        return
    # 发送图片列表
    samples = av['samples']
    samples_imp = []
    has_samples = False
    for i, sample in enumerate(samples):
        samples_imp.append(InputMediaPhoto(sample))
        if i == 9:  # 图片数目达到9张则发送一次
            has_samples = True
            bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
            samples_imp = []
    if samples_imp != []:
        has_samples = True
        bot.send_media_group(chat_id=TG_CHAT_ID, media=samples_imp)
    if not has_samples:
        send_msg(f'未找到{id}对应截图 =_=')


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
    elif type == '3':  # 类型3：发送番号对应av
        get_av_by_id(content)


@bot.message_handler(content_types=['text', 'photo', 'animation', 'video'])
def handle_message(message):
    '''消息处理器

    :param _type_ message: 消息
    '''
    # 拦截请求，检查消息来源
    if str(message.from_user.id) != TG_CHAT_ID:
        bot.send_message(
            chat_id=message.from_user.id,
            text='该机器人仅供私人使用, 如需使用请自行部署, 项目地址：https://github.com/akynazh/tg-javbus-bot',
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
    elif msg == '/record_json':
        get_record_json()
    elif msg == '/record10':
        get_record(10)
    elif msg == '/record':
        get_record()
    elif msg.find('/record') != -1:
        param = get_msg_param(msg)
        if param and param.isdigit(): get_record(int(param))
        else: get_record()
    elif msg.find('/star') != -1:
        param = get_msg_param(msg)
        if param: get_record_by_star_name(param)
        else: get_record_stars()
    else:
        get_av(msg)


def test():
    '''用于测试'''
    return


def help():
    '''发送指令帮助消息'''
    msg = '''/help  查看指令帮助

/star  获取所有搜过的演员（后接名称获取该演员对应的记录）
    
/record  获取所有查询记录（根据查询时间排序，后接数字可指定条数）
    
/record10  获取最近10条查询记录

/record_json  获取记录文件
'''
    send_msg(msg)


def set_command():
    '''设置机器人命令'''
    tg_cmd_dict = {
        'help': '查看指令帮助',
        'star': '获取所有搜过的演员',
        'record': '获取所有查询记录',
        'record10': '获取最近10条查询记录',
        'record_json': '获取记录文件',
    }
    cmds = []
    for cmd in tg_cmd_dict:
        cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
    bot.set_my_commands(cmds)


if __name__ == '__main__':
    os.chdir(PATH_ROOT)
    set_command()
    bot.infinity_polling()