import requests
import json
import logging


def getRecommendation(song_name,limit):
    '''Get a list of similar songs from another song name (spotify search)'''

    with open('token.json', 'r') as f:
        token = json.load(f)

    _access_token = token['spotify_token']

    if limit > 100:
        limit = 100
    elif limit < 1:
        limit = 1


    song_name = str(song_name).replace(' ','+')

    headers = {
        'Authorization': 'Bearer {token}'.format(token=_access_token)
    }

    URL = 'https://api.spotify.com/v1/search?q={}&type=track&limit=1'.format(song_name)
    data = json.loads(requests.get(URL, headers=headers).text)

    track_id = data['tracks']['items'][0]['id']


    URL = 'https://api.spotify.com/v1/recommendations?limit={}&seed_tracks={}'.format(limit,track_id)
    data = json.loads(requests.get(URL, headers=headers).text)

    r = []

    for item in data['tracks']:

        title = item['name']
        artist = item['artists'][0]['name']

        r.append(artist+' - '+title)

    return r


