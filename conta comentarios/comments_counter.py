import json

total_comentarios = 0
num_videos = 0

with open("comentarios_lta.jsonl", "r", encoding="utf-8") as f:
    for linha in f:
        if not linha.strip():
            continue  # pula linhas em branco
        video = json.loads(linha)
        num_videos += 1

        comentarios = video.get("comentarios", [])
        total_comentarios += len(comentarios)

        for comentario in comentarios:
            total_comentarios += len(comentario.get("respostas", []))

print(f"Total de vídeos processados: {num_videos}")
print(f"Total de comentários coletados (incluindo respostas): {total_comentarios}")
