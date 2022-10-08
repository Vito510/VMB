import datetime
import json
import logging
import os
import re
import time
import threading
import functools
import asyncio
import typing

import youtube_dl
from youtube_search import YoutubeSearch

import cache

with open('./config/config.json') as f:
    configuration = json.load(f)


ytdl = youtube_dl.YoutubeDL(configuration['ytdl_format_options'])

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

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
    elif 'spotify.com/playlist' in x:
        return 3
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
    
    return [{"source": search_url,"title": search_title}]

@to_thread
def youtube_search_thread(searches):
    """Threaded YouTube search ([url,title])"""

    result = [None] * len(searches)
    threads = [None] * len(searches)

    def search(search, result, index):
        r = json.loads(YoutubeSearch(search, max_results=1).to_json())

        search_url = "https://www.youtube.com/watch?v="+r["videos"][0:][0]['id']
        search_title = r["videos"][0:][0]["title"]

        result[index] = (search_url,search_title)

    logging.info('Running on {} threads'.format(len(searches)))
    for i in range(len(threads)):
        threads[i] = threading.Thread(target=search, args=(searches[i], result, i))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    jsn = []

    for item in result:
        jsn.append({
            "source": item[0],
            "title": item[1]
        })

    return jsn


def generate_dir_list(dir):
    list_str = ""
    list_list = os.listdir(dir)

    for i in range(0,len(list_list)): list_str = list_str + (str(i) + ": " + list_list[i] + "\n") 

    with open("cache/local_files_queue.txt", "w", encoding="utf-8") as f:
        f.write(list_str)
    
    return 'cache/local_files_queue.txt'
