import json
import csv

# Caminhos
entrada_json = "comentarios_amostra.json"  # ou o seu json com 300 comentários
saida_csv = "comentarios_para_treinar.csv"

# Carregar comentários
with open(entrada_json, "r", encoding="utf-8") as f:
    comentarios = json.load(f)

# Gerar CSV com campo de anotação vazio
with open(saida_csv, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "texto", "sentimento"])  # cabeçalho

    for i, comentario in enumerate(comentarios):
        texto = comentario.get("texto", "").replace("\n", " ").strip()
        if texto:
            writer.writerow([i, texto, ""])  # você vai preencher a coluna "sentimento"

print(f"Arquivo gerado: {saida_csv}")
