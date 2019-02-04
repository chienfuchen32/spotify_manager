import http.client, urllib.parse
import json
import os

from spotify_oauth_token import access_token

uri = 'api.spotify.com'
header = {
    'Authorization': 'Bearer {}'.format(access_token),
    'Content-Length': 0
}

folder = 'artist_list'
folder_not_found = 'not_found'

artist_list = os.listdir(folder)
print(artist_list)
follow_limit = 50
not_found_artist = []
def concate_artist_id(batch_artist_id_follow):
    batch_id = ''
    for i in range(len(batch_artist_id_follow)):
        batch_id += batch_artist_id_follow[i]
        if i is not len(batch_artist_id_follow) - 1:
            batch_id += ','
    return batch_id
def follow(batch_artist_id_follow):
    conn = http.client.HTTPSConnection(uri)
    batch_id = concate_artist_id(batch_artist_id_follow)
    params = urllib.parse.urlencode({
                    'type': 'artist',
                    'ids': batch_id
                })
    query_str = '/v1/me/following?' + params
    conn.request('PUT', query_str, None, header)
    r1 = conn.getresponse()
    print('batch follow response:', r1.status)

for filename_list in artist_list:
    with open(os.path.join(folder, filename_list), 'r') as f:
        artists = f.readlines()
    artists = [x.strip() for x in artists]
    batch_artist_id_follow = []
    for artist in artists:
        print(artist)
        # check artist
        conn = http.client.HTTPSConnection(uri)
        params = urllib.parse.urlencode({ 'q': artist, 'type': 'artist'})
        query_str = '/v1/search?' + params
        conn.request('GET', query_str, None, header)
        r1 = conn.getresponse()
        data = json.loads(r1.read())
        if len(data['artists']['items']) == 0:
            not_found_artist.append(artist)
            continue
        match_artist = data['artists']['items'][0]
        if match_artist['name'].lower() != artist.lower():
            print(match_artist['name'], artist, 'not quite match')
        batch_artist_id_follow.append(match_artist['id'])

        # follow the artist
        if len(batch_artist_id_follow) == follow_limit:
            follow(batch_artist_id_follow)
            batch_artist_id_follow = []
    follow(batch_artist_id_follow)
with open(os.path.join(folder_not_found, 'not_found_artist.txt'), 'w') as f:
    json.dump(not_found_artist, f, ensure_ascii=False)
