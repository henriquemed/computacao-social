import json

# Dados de times brasileiros
times_brasileiros = [
    "vti ignis", "pain gaming", "keyd stars", "vivo keyd stars", "intz", "kabum",
    "red canids kalunga", "flamengo esports", "team one", "loud", "furia",
    "netshoes miners", "cruzeiro esports"
]

# Variações dos campeonatos internacionais
variacoes_torneios = ["msi", "mid-season invitational", "worlds", "world championship"]

# Palavras-chave para desempenho internacional
palavras_chave_comentario = [
    'lá fora', 'fora do brasil', 'internacional', 'internacionais'
]

# Normalize para minúsculo
times_brasileiros = [t.lower() for t in times_brasileiros]
variacoes_torneios = [v.lower() for v in variacoes_torneios]
palavras_chave_comentario = [p.lower() for p in palavras_chave_comentario]

# Armazenamento dos resultados
comentarios_dos_videos_relevantes = []
comentarios_relevantes_fora_dos_videos = []

# Identificadores dos vídeos relevantes
videos_relevantes_ids = set()

with open("comentarios_lta.jsonl", "r", encoding="utf-8") as f:
    for linha in f:
        if not linha.strip():
            continue

        video = json.loads(linha)
        video_id = video.get("video_id")
        titulo = video.get("titulo", "").lower()

        # Identifica vídeos relevantes (1 time BR + 1 torneio internacional)
        times_no_titulo = [time for time in times_brasileiros if time in titulo]
        tem_torneio = any(torneio in titulo for torneio in variacoes_torneios)
        eh_relevante = len(times_no_titulo) == 1 and tem_torneio

        if eh_relevante:
            videos_relevantes_ids.add(video_id)

        for comentario in video.get("comentarios", []):
            comentario["video_id"] = video_id

            if eh_relevante:
                comentarios_dos_videos_relevantes.append(comentario)
            else:
                texto = comentario.get("texto", "").lower()
                if any(p in texto for p in palavras_chave_comentario):
                    comentarios_relevantes_fora_dos_videos.append(comentario)

            for resposta in comentario.get("respostas", []):
                resposta["video_id"] = video_id

                if eh_relevante:
                    comentarios_dos_videos_relevantes.append(resposta)
                else:
                    texto_resp = resposta.get("texto", "").lower()
                    if any(p in texto_resp for p in palavras_chave_comentario):
                        comentarios_relevantes_fora_dos_videos.append(resposta)

# Exportar os resultados
with open("comentarios_dos_videos_relevantes.json", "w", encoding="utf-8") as f:
    json.dump(comentarios_dos_videos_relevantes, f, ensure_ascii=False, indent=2)

with open("comentarios_relevantes_fora_dos_videos.json", "w", encoding="utf-8") as f:
    json.dump(comentarios_relevantes_fora_dos_videos, f, ensure_ascii=False, indent=2)

# Relatório
print(f"Vídeos relevantes encontrados: {len(videos_relevantes_ids)}")
print(f"Comentários dos vídeos relevantes: {len(comentarios_dos_videos_relevantes)}")
print(f"Comentários relevantes fora dos vídeos: {len(comentarios_relevantes_fora_dos_videos)}")
