import json

# Caminho do arquivo original
entrada = "../comentarios_relevantes.json"
saida = "comentarios_amostra.json"
N = 600  # quantidade de comentários que você quer extrair

# Ler os comentários
with open(entrada, "r", encoding="utf-8") as f:
    comentarios = json.load(f)

# Extrair os primeiros N
amostra = comentarios[:N]

# Salvar a amostra
with open(saida, "w", encoding="utf-8") as f:
    json.dump(amostra, f, indent=2, ensure_ascii=False)

print(f"Amostra de {N} comentários salva em {saida}")
