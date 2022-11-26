import telebot
import requests
import credential

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

@bot.message_handler(func=lambda m: True)
def get_av_by_id(message):
    id = message.text.strip()
    resp = requests.get(SERVER_URL + id)
    
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
    msg = f'''<a href="https://www.javbus.com/{id}"><b>{title}</b></a>
Stars: {stars_msg}'''
    bot.send_photo(chat_id=TG_CHAT_ID, photo=img, caption=msg, parse_mode='HTML')
    # bot.send_message(chat_id=TG_CHAT_ID, text=msg, parse_mode='HTML')
    for magnet in magnets:
        bot.send_message(chat_id=TG_CHAT_ID, text=f'<code>{magnet["link"]}</code>     {magnet["size"]}', parse_mode='HTML')
        
if __name__ == '__main__':
    bot.infinity_polling()