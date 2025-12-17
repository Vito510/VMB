import requests
import json
import logging

def _getToken():
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    with open('./config/token.json', 'r') as f:
        token = json.load(f)

    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': token['spotify_client_id'],
        'client_secret': token['spotify_client_secret'],
    })

    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def search(query, type):
    access_token = _getToken()


    query = str(query).replace(' ','+')

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    URL = 'https://api.spotify.com/v1/search?q={}&type={}&limit=1'.format(query, type)
    data = requests.get(URL, headers=headers)

    return data.text




def getRecommendation(song_name,limit):
    '''Get a list of similar songs from another song name (spotify search)'''

    access_token = _getToken()

    if limit > 100:
        limit = 100
    elif limit < 1:
        limit = 1
    else:
        limit = 10

    song_name = str(song_name).replace(' ','+')

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    url = "https://api.spotify.com/v1/search"

    params = {
        "q": song_name,
        "type": "track",
        "limit": 1
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data_json = response.json()

    logging.info('Search: {}'.format(song_name))
    track_id = data_json['tracks']['items'][0]['id']


    url = 'https://api.spotify.com/v1/recommendations'
    params = {
        "seed_tracks": track_id,
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data_json = response.json()
    logging.info('Recommendation: {}'.format(data_json))

    r = []

    for item in data_json['tracks']:

        title = item['name']
        artist = item['artists'][0]['name']

        r.append(artist+' - '+title)

    return r

def playlist(url):
    """Returns artist name and song title of every item in a playlist (artist - title)"""

    url = url.split('playlist/')[-1].split('?')[0]

    left = 1
    offset = 0

    re = []

    while left > 0:

        access_token = _getToken()

        headers = {
            'Authorization': 'Bearer {token}'.format(token=access_token)
        }

        URL = 'https://api.spotify.com/v1/playlists/{}/tracks?offset={}'.format(url,offset)
        r = requests.get(URL, headers=headers)


        data = json.loads(r.text)
        batch = len(data['items'])
        total = data['total']

        offset += batch
        left = total - offset


        for item in data['items']:
            item = item['track']
            title = item['name']
            artist = item['artists'][0]['name']

            re.append(artist+' - '+title)

    logging.info('Got: {} items'.format(len(re)))

    return re

