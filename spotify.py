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

def getRecommendation(song_name,limit):
    '''Get a list of similar songs from another song name (spotify search)'''

    access_token = _getToken()

    if limit > 100:
        limit = 100
    elif limit < 1:
        limit = 1

    song_name = str(song_name).replace(' ','+')

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    URL = 'https://api.spotify.com/v1/search?q={}&type=track&limit=1'.format(song_name)
    data = requests.get(URL, headers=headers)

    logging.info('Search: {}'.format(data))
    data = json.loads(data.text)

    track_id = data['tracks']['items'][0]['id']


    URL = 'https://api.spotify.com/v1/recommendations?limit={}&seed_tracks={}'.format(limit,track_id)
    data = requests.get(URL, headers=headers)
    logging.info('Recommendation: {}'.format(data))
    data = json.loads(data.text)

    r = []

    for item in data['tracks']:

        title = item['name']
        artist = item['artists'][0]['name']

        r.append(artist+' - '+title)

    return r


