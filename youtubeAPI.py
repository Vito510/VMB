import json
import logging
import time
from html import unescape
import requests
from urllib.parse import parse_qs, urlparse

import googleapiclient.discovery
import click

import cache
import functions


with open('./config/token.json', 'r') as f:
    token = json.load(f)

if token['youtube_data_API_v3_key'] != '':
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = token['youtube_data_API_v3_key'])
else:
    click.secho('No YouTube data API v3 key: search will use slower method, playlist importing will not work',fg='yellow')


def search(search):
    """Returns a youtube video title and a url from a search term"""
    global search_url,search_title

    start_time = time.time()

    c = cache.load(search,0)

    if c == None:

        try:
            request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=search
            )


            response = request.execute()
        except Exception as e:
            logging.error("Youtube API v3 Error - falling back to youtube_search() - "+str(e))

            return functions.youtube_search(search)

        if len(response["items"]) == 0:
            logging.info("No results found")
            return None

        search_url = "https://www.youtube.com/watch?v="+response['items'][0]['id']['videoId']
        search_title = unescape(response['items'][0]['snippet']['title'])
        cache.save(search,search_url,search_title,0)
    else:
        search_url = c['url']
        search_title = unescape(c['title'])

    t = str(round((time.time()-start_time)*1000))+'ms'
    logging.info("Found: \x1B[4m"+search_title+"\x1B[0m in "+t)

    return [search_url,search_title]

def playlist(url):
    """Returns a list of urls from a youtube playlist"""
    start_time = time.time()

    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    c = cache.load(playlist_id,1)
    c = None

    if c == None:
        list = []

        try:
            request = youtube.playlistItems().list(
                part = "snippet",
                playlistId = playlist_id,
                maxResults = 1
            )
        except:
            logging.error('To use playlist import add a YouTube API v3 key')
            return None

        try:
            response = request.execute()
        except Exception as e:
            logging.error("Error in request - "+str(e))

            return []

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)
        
        jsn = []
        for t in playlist_items:
            jsn.append(
                {
                    "source": 'https://www.youtube.com/watch?v='+t["snippet"]["resourceId"]["videoId"],
                    "title": t["snippet"]["title"],
                    "playlist": url
                }
            )


        #cache.save(playlist_id,jsn,1)
        print("cacheing disabled")
    else:
        urls = c['url']
        titles = c['title']


    t = str(round((time.time()-start_time)*1000))+'ms'
    logging.info("Got {} items from {} in {}".format(len(jsn),playlist_id,t))


    return jsn

def related(url,amount=10):
    '''Returns related music videos'''

    if 'youtube' in url:
        url = url.split('watch?v=')[-1]
    else:
        return None


    URL = 'https://youtube.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={}&maxResults={}&type=video&key={}&topicId=%2Fm%2F04rlf'.format(url,amount,token['youtube_data_API_v3_key'])
    data = requests.get(URL)

    if data.status_code != 200:
        logging.error('Error in request: '+str(data))
        raise 'Error in request'


    d = json.loads(data.text)
    urls = []
    titles = []


    for item in d['items']:
        url = 'https://www.youtube.com/watch?v='+item['id']['videoId']

        try:
            title = item['snippet']['title']
        except:
            #some results are deleted videos they keep id's but dont contain snippets
            continue

        urls.append(url)
        titles.append(title)

    return [urls,titles]