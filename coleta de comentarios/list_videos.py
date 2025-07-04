# listar_videos.py
import requests

API_KEY = 'AIzaSyBTbuclbGsapnvhgDRYUhW19rFHWGgmSxU'
CANAL = 'LTASul'

def obter_channel_id(nome_canal):
    r = requests.get('https://www.googleapis.com/youtube/v3/search', params={
        'part': 'snippet', 'type': 'channel', 'q': nome_canal, 'key': API_KEY
    }).json()
    return r['items'][0]['snippet']['channelId']

def obter_uploads_playlist_id(channel_id):
    r = requests.get('https://www.googleapis.com/youtube/v3/channels', params={
        'part': 'contentDetails', 'id': channel_id, 'key': API_KEY
    }).json()
    return r['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def obter_video_ids(playlist_id):
    video_ids = []
    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'contentDetails',
        'playlistId': playlist_id,
        'maxResults': 50,
        'key': API_KEY
    }
    while True:
        r = requests.get(url, params=params).json()
        video_ids.extend(item['contentDetails']['videoId'] for item in r.get('items', []))
        if 'nextPageToken' in r:
            params['pageToken'] = r['nextPageToken']
        else:
            break
    return video_ids

if __name__ == '__main__':
    print('[1/3] Obtendo channel ID...')
    channel_id = obter_channel_id(CANAL)
    print('[2/3] Obtendo playlist de uploads...')
    uploads_id = obter_uploads_playlist_id(channel_id)
    print('[3/3] Coletando IDs dos vídeos...')
    ids = obter_video_ids(uploads_id)
    with open('video_ids.txt', 'w') as f:
        for vid in ids:
            f.write(vid + '\n')
    print(f'Concluído. {len(ids)} vídeos salvos em video_ids.txt')
