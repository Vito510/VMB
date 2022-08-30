import datetime
import json
import logging
import os
import re
import time
import click

import youtube_dl
from youtube_search import YoutubeSearch

import cache

with open('config.json') as f:
    configuration = json.load(f)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

def timestamp():
    now = datetime.datetime.now()
    return ('['+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+'] ')

def is_supported(url):
    extractors = youtube_dl.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False

def queue_type(x):
    #0 = Local directory, 1 = Online link
    r = 0
    check = ["http",".com","youtube.com/playlist?list"]

    for item in check:
        if item in x: r = check.index(item)
    
    return r

def play_type(x):
    '''Is the input a youtube playlist, search term or another online audio source
    0 = yt link, 1 = yt Playlist, 2 = Online link'''

    if 'youtube.com/playlist' in x:
        return 1
    elif 'youtube.com/watch' in x:
        return 0
    elif 'http' in x[:4]:
        return 2
    else:
        return -1
    
def get_title(url):
    '''Gets the title of a yt link using yt-dlp'''
    start_time = time.time()
    title = ytdl.extract_info(url, download=False)['title']
    t = str(round((time.time()-start_time)*1000))+'ms'
    logging.info("Found: "+title+" in "+t)
    return title

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def is_available(url):
    try:
        ytdl.extract_info(url, download=False)
        return True
    except Exception as e:
        logging.error("Error: URL is not available: "+str(e))
        return False

def youtube_search(search):
    '''Youtube search function from library youtube_search'''
    start_time = time.time()

    c = cache.load(search,0)

    if c == None:
        x = json.loads(YoutubeSearch(search, max_results=1).to_json())

        search_url = "https://www.youtube.com/watch?v="+x["videos"][0:][0]['id']    #title, id, channel, duration
        search_title = x["videos"][0:][0]["title"]

        cache.save(search,search_url,search_title,0)
    else:
        search_url = c['url']
        search_title = c['title']
    
    t = str(round((time.time()-start_time)*1000))+'ms'
    logging.info("Found: \x1B[4m"+search_title+"\x1B[0m in "+t)
    
    return [search_url,search_title]

def generate_dir_list(dir):
    list_str = ""
    list_list = os.listdir(dir)

    for i in range(0,len(list_list)): list_str = list_str + (str(i) + ": " + list_list[i] + "\n") 

    with open("cache/local_files_queue.txt", "w", encoding="utf-8") as f:
        f.write(list_str)
    
    return 'cache/local_files_queue.txt'

def create():
    """Creates all the files/folders the bot needs"""
    if not os.path.isdir('cache'):
        logging.info("Creating cache folder")

        os.mkdir('cache')

        stuff = ['playlist.json','search.json','url.json']

        for i in stuff:
            with open('cache/'+i, "w") as f:
                f.write("{}")   

    if not os.path.isdir('logs'):
        logging.info("Creating logs folder")

        os.mkdir('logs')
    
    if not os.path.isdir('packs'):
        logging.info("Creating packs folder")

        os.mkdir('packs')

        with open('packs/example_I.txt', 'w') as f:
            f.write("Hello World!\nHello Again!")

        with open('packs/example_O.txt', 'w') as f:
            f.write("Bye!\nGoodbye!")

        with open('packs/example2_O.txt', 'w') as f:
            f.write("Don't now what to say!\nFunny?")

        

    if not os.path.isfile('packs.json'):
        logging.info("Creating packs.json")

        with open('packs.json', 'w') as f:
            x = [{'name':'example','type':'IO','weight':0.5,'dir':'packs/example'},
                 {'name':'example2','type':'O','weight':0.5,'dir':'packs/example2'}]
            json.dump(x, f, indent=4)

    if not os.path.isfile('token.json'):
        logging.info("Creating token.json")

        with open('token.json', 'w') as f:
            json.dump({'token':'YOUR_TOKEN','token_debug':'SECONDARY_TOKEN_FOR_DEBUG'}, f, indent=4)

        click.echo("Put your token in token.json")
        exit()