import json
import logging
import time
from html import unescape
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
    logging.info("Got {} items from {} in {}".format(len(titles),playlist_id,t))


    return [urls,titles]
