import datetime
import json
import logging
import os
import re
import time
from urllib.parse import parse_qs, urlparse

import click
import googleapiclient.discovery
import youtube_dl
from youtube_search import YoutubeSearch

import cache

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = "AIzaSyBUnRYlLX6xXinu9plpwpvZOg9_rv-i040")

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
    click.secho(timestamp()+'Found: '+title+' in '+t, fg='green')
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
        click.secho(timestamp()+"Error: URL is not available", fg="red")
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
    click.secho(timestamp()+'Found: '+search_title+' in '+t, fg='green')
    logging.info("Found: "+search_title+" in "+t)
    
    return [search_url,search_title]

def youtube_searchGOOD(search):
    global search_url,search_title
    '''Youtube search function from Youtube API v3'''

    start_time = time.time()

    c = cache.load(search,0)

    if c == None:

        request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=search
            )

        try:
            response = request.execute()
        except Exception as e:
            click.secho(timestamp()+"youtube_searchGOOD() - Youtube API v3 Error - falling back to youtube_search()", fg="red")
            logging.error("youtube_searchGOOD() - Youtube API v3 Error - falling back to youtube_search() - "+str(e))

            return youtube_search(search)

        if len(response["items"]) == 0:
            click.secho(timestamp()+"youtube_searchGOOD() - No results found", fg="red")
            return None

        search_url = "https://www.youtube.com/watch?v="+response['items'][0]['id']['videoId']
        search_title = response['items'][0]['snippet']['title']
        cache.save(search,search_url,search_title,0)
    else:
        search_url = c['url']
        search_title = c['title']

    t = str(round((time.time()-start_time)*1000))+'ms'
    click.secho(timestamp()+'Found[YT-API-v3]: '+search_title+' in '+t, fg='green')
    logging.info("Found[YT-API-v3]: "+search_title+" in "+t)

    return [search_url,search_title]

def generate_dir_list(dir):
    list_str = ""
    list_list = os.listdir(dir)
    click.secho(timestamp()+"generate_dir_list_and_send() - generating directory list and sending", fg="green")

    for i in range(0,len(list_list)): list_str = list_str + (str(i) + ": " + list_list[i] + "\n") 

    with open("cache/local_files_queue.txt", "w", encoding="utf-8") as f:
        f.write(list_str)
    
    return 'cache/local_files_queue.txt'

def list_from_playlist(url):
    start_time = time.time()

    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    c = cache.load(playlist_id,1)

    if c == None:
        list = []

        request = youtube.playlistItems().list(
            part = "snippet",
            playlistId = playlist_id,
            maxResults = 1
        )

        try:
            response = request.execute()
        except Exception as e:
            click.secho(timestamp()+"list_from_playlist() - Error in request", fg="red")
            logging.error("list_from_playlist() - Error in request - "+str(e))

            return []

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)
        
        for t in playlist_items:
            list.append('https://www.youtube.com/watch?v='+t["snippet"]["resourceId"]["videoId"])
        urls = list
        list = []
        for t in playlist_items:
            list.append(t["snippet"]["title"])

        titles = list

        cache.save(playlist_id,urls,titles,1)
    else:
        urls = c['url']
        titles = c['title']


    t = str(round((time.time()-start_time)*1000))+'ms'
    click.secho(timestamp()+'Got[YT-API-v3]: {} items from {} in {}'.format(len(titles),playlist_id,t), fg='green')
    logging.info("Got[YT-API-v3]: {} items from {} in {}".format(len(titles),playlist_id,t))


    return [urls,titles]
