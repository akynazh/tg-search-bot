import telebot
import requests
import credential
import json
import os
import sys

TG_CHAT_ID = credential.TG_CHAT_ID
TG_BOT_TOKEN = credential.TG_BOT_TOKEN
SERVER_URL = credential.SERVER_URL

bot = telebot.TeleBot(TG_BOT_TOKEN)

def get_nice_magnets(magnets, prop):
    if len(magnets) == 0: return None
    if len(magnets) == 1: return magnets
    
    magnets_nice = []
    for magnet in magnets:
        if magnet[prop]:
            magnets_nice.append(magnet)
    if len(magnets_nice) == 0:
        return magnets
    return magnets_nice

def get_record():
    PATH_RECORD_FILE = PATH_ROOT + '/record.json'
    if os.path.exists(PATH_RECORD_FILE):
        with open(PATH_RECORD_FILE, 'r') as f:
            record = json.load(f)
        avs = record['avs']
        msg = ''
        i = 1
        for av in avs:
            msg += f'{av["id"]}  {av["stars"].strip()}  <a href="{av["url"]}">src</a>'
            i += 1
            if i == 30:
                bot.send_message(chat_id=TG_CHAT_ID, text=msg, disable_web_page_preview=True, parse_mode='HTML')
                msg = ''
        if msg != '':
            bot.send_message(chat_id=TG_CHAT_ID, text=msg, disable_web_page_preview=True, parse_mode='HTML')
    else:
        bot.send_message(chat_id=TG_CHAT_ID, text='尚无记录=_=')
        
def record(id, stars, url):
    PATH_RECORD_FILE = PATH_ROOT + '/record.json'
    avs = []
    new_av = {'id': id, 'stars': stars, 'url': url}
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
            json.dump(record, f, separators=(',', ': '), indent=4, ensure_ascii=False)
    
@bot.message_handler(func=lambda m: True)
def get_av_by_id(message):
    if message.text.strip() == '/record':
        get_record()
        return
    id = message.text.strip()
    resp = requests.get(SERVER_URL + id)
    if resp.status_code != 200:
        bot.send_message(chat_id=TG_CHAT_ID, text='未查找到该记录>_<')
        return
    id = resp.json()['id']
    title = resp.json()['title']
    img = resp.json()['img']
    stars = resp.json()['stars']
    magnets = resp.json()['magnets']
    magnets = get_nice_magnets(magnets, 'isHD')
    magnets = get_nice_magnets(magnets, 'hasSubtitle')
    if len(magnets) > 3: magnets = magnets[0:3]
    stars_msg = ''
    for star in stars:
        stars_msg += f'{star["starName"]}  '
    url = f'https://www.javbus.com/{id}'
    msg = f'''<a href="{url}"><b>{title}</b></a>
Stars: {stars_msg}'''
    bot.send_photo(chat_id=TG_CHAT_ID, photo=img, caption=msg, parse_mode='HTML')
    for magnet in magnets:
        bot.send_message(chat_id=TG_CHAT_ID, text=f'<code>{magnet["link"]}</code>     {magnet["size"]}', parse_mode='HTML')
    record(id=id, stars=stars_msg, url=url)
    
if __name__ == '__main__':
    PATH_ROOT = sys.path[0]
    bot.infinity_polling()