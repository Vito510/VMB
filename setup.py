# Required:
#     logs folder
#     cache folder
#           playlist.json
#           search.json
#           url.json     
#     packs folder
#           example/default packs
#     config folder:
#           config.json
#           packs.json
#           token.json
import os
import json


# check dependencies
x = input('Do you want to install required dependencies [y/N]? ')
if x == 'y' or x == 'Y':
    os.system('pip install -r requirements.txt')


# create folders
folders = ['logs', 'cache', 'packs', 'config']

for folder in folders:
    if not os.path.isdir('./'+folder):
        try:
            os.mkdir('./'+folder)
        except:
            pass
        finally:
            print('Created '+folder+' folder')


#cache files

files = ['playlist','search','url']

for file in files:
    if os.path.exists('./cache/'+file+'.json'):
        x = input('There is already a {}.json file, overwrite[y/n]? '.format(file))
        if x != 'y' or x != 'Y':
            continue

    with open('./cache/'+file+'.json', 'w') as f:
        json.dump({}, f, indent=4)


# example packs

default = [
    {
        "name": "example_I.txt",
        "content": "Hello World!\nHello Again!"
    },
    {
        "name": "example_O.txt",
        "content": "Bye!\nGoodbye!"
    },
    {
        "name": "example2_O.txt",
        "content": "Don't now what to say!\nFunny?"
    }
]

for item in default:
    with open('./packs/'+item['name'], 'w', encoding='utf-8') as f:
        f.write(item['content'])


# config folder
#   config.json


default = {
    "UseYoutubeSearchAPI": True,
    "JoinLeaveMessages": True,
    "AllowHostLocalFiles": False,
    "EnableTestCommands": False,
    "AllowEndSession": True,
    "AllowClearCache": False,
    "Admins": [

    ],
    "AloneTime": 120,
    "queueMode": "none",
    "MaxCacheAge": 0,
    "ffmpegWait": 0.75,
    "UseYT_APIforRecommendations": False,
    "ytdl_format_options": {
        'format': 'bestaudio',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    },
    "ffmpeg_options": {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -v quiet'
    },
    "packs": [
        {
            "name": "example",
            "type": "IO",
            "weight": 0.5,
            "dir": "packs/example"
        },
        {
            "name": "example2",
            "type": "O",
            "weight": 0.5,
            "dir": "packs/example2"
        }
    ]
}


if os.path.exists('./config/config.json'):
    x = input('There is already a config file, overwrite[y/n]? ')
    if x == 'y' or x == 'Y':
        with open('./config/config.json', 'w') as f:
            json.dump(default, f, indent=4)
else:
    with open('./config/config.json', 'w') as f:
        json.dump(default, f, indent=4)

#   token.json

default = {
    "token": "DISCORD_BOT_TOKEN",
    "youtube_data_API_v3_key": "",
    "spotify_client_id": "",
    "spotify_client_secret": ""
}

if os.path.exists('./config/token.json'):
    x = input('There is already a token file, overwrite[y/n]? ')
    if x == 'y' or x == 'Y':
        with open('./config/token.json', 'w') as f:
            json.dump(default, f, indent=4)
else:
    with open('./config/token.json', 'w') as f:
        json.dump(default, f, indent=4)

x = input('Done, press ENTER to close')
