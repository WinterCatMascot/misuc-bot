from vkaudiotoken import  get_vk_official_token
import requests
import json
import telebot
import urllib
import sys

#check start args
try:
    if len(sys.argv) != 4:
        raise Exception

    botApiKey = sys.argv[1]
    login = sys.argv[2]
    password = sys.argv[3]
except: 
    print('Not enough arguments')
    print('Example: py filename.py botApiKey login password')
    print('')
    sys.exit()

#check apikey
try:
    bot = telebot.TeleBot(botApiKey)
except:
    print('Bot Error: Check botApiKey')
    print('')
    sys.exit()

#check vk auth
try: 
    tokenObj = get_vk_official_token(login, password)
except:
    print('Login Error: Check login and password')
    print('')
    sys.exit()

#create vk session
token = tokenObj['token']
user_agent = tokenObj['user_agent']

sess = requests.session()
sess.headers.update({'User-Agent': user_agent})

#trackList transform
def getTracks(result):
    data = json.loads(result.content.decode('utf-8'))
    tracks = data['response']['items']
    tracks.reverse()
    return tracks

#m3u8 url convet to mp3 url
def getMp3FromM3u8(url):
    if url.find("index.m3u8?") == -1:
        return url
    parts = url.split('/')
    newUrl = parts[0] + '//' + parts[2] + '/' + parts[3] + '/' + parts[5] + '.mp3'
    return newUrl

#telegram bot
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Moscow Music Bot. Введите число треков")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Введите число треков")
    else:
        try:
            count = int(message.text)   

            tracks = getTracks(sess.get(
                "https://api.vk.com/method/audio.get",
                params=[('access_token', token),
                    ('count', count),
                    ('v', '5.95')]     
            ))

            for track in tracks:
                title = track['title']
                artist = track['artist']
                duration = track['duration']
                url = getMp3FromM3u8(track['url'])
                file = urllib.request.urlopen(url)
                bot.send_audio(message.from_user.id, file, duration=duration, title=title, performer=artist)
        except:
             bot.send_message(message.from_user.id, "Ошибка исполнения")

bot.infinity_polling()
