# coletar_dados.py
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os

API_KEY = 'AIzaSyBTbuclbGsapnvhgDRYUhW19rFHWGgmSxU'
THREADS = 10
ARQUIVO_SAIDA = 'comentarios_lta.jsonl'

def ja_processado(video_id):
    if not os.path.exists(ARQUIVO_SAIDA):
        return False
    with open(ARQUIVO_SAIDA, 'r', encoding='utf-8') as f:
        for linha in f:
            try:
                if json.loads(linha)['video_id'] == video_id:
                    return True
            except:
                continue
    return False

def obter_dados_video(video_id):
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet',
        'id': video_id,
        'key': API_KEY
    }
    r = requests.get(url, params=params).json()
    if not r.get('items'):
        return None
    s = r['items'][0]['snippet']
    return {
        'video_id': video_id,
        'titulo': s.get('title'),
        'descricao': s.get('description'),
        'data_publicacao': s.get('publishedAt'),
    }

def obter_comentarios(video_id):
    comentarios = []
    url = 'https://www.googleapis.com/youtube/v3/commentThreads'
    params = {
        'part': 'snippet,replies',
        'videoId': video_id,
        'maxResults': 100,
        'textFormat': 'plainText',
        'key': API_KEY
    }
    while True:
        r = requests.get(url, params=params).json()
        for item in r.get('items', []):
            top = item['snippet']['topLevelComment']['snippet']
            c = {
                'tipo': 'comentario',
                'autor': top.get('authorDisplayName'),
                'texto': top.get('textDisplay'),
                'likes': top.get('likeCount'),
                'data': top.get('publishedAt'),
                'respostas': []
            }
            for rep in item.get('replies', {}).get('comments', []):
                rs = rep['snippet']
                c['respostas'].append({
                    'tipo': 'resposta',
                    'autor': rs.get('authorDisplayName'),
                    'texto': rs.get('textDisplay'),
                    'likes': rs.get('likeCount'),
                    'data': rs.get('publishedAt')
                })
            comentarios.append(c)
        if 'nextPageToken' in r:
            params['pageToken'] = r['nextPageToken']
        else:
            break
        time.sleep(0.1)
    return comentarios

def processar_video(video_id):
    if ja_processado(video_id):
        return None
    try:
        dados = obter_dados_video(video_id)
        if not dados:
            return None
        dados['comentarios'] = obter_comentarios(video_id)
        return dados
    except Exception as e:
        return {'video_id': video_id, 'erro': str(e)}

if __name__ == '__main__':
    with open('video_ids.txt') as f:
        video_ids = [l.strip() for l in f.readlines() if l.strip()]

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(processar_video, vid): vid for vid in video_ids}

        with open(ARQUIVO_SAIDA, 'a', encoding='utf-8') as f_out:
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processando vídeos"):
                resultado = future.result()
                if resultado:
                    f_out.write(json.dumps(resultado, ensure_ascii=False) + '\n')
