import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import AutoTokenizer, AutoModel
from langdetect import detect
import torch
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import defaultdict
import datetime

# === Configurações ===
bert_model = "neuralmind/bert-base-portuguese-cased"
anotados_csv = "300_test_equal.csv"
entrada_json = "comentarios_relevantes.json"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === 1. Funções auxiliares ===

def detecta_pt(texto):
    try:
        return detect(texto) == "pt"
    except:
        return False

def bert_embed(texto):
    tokens = tokenizer(texto, return_tensors='pt', truncation=True, padding=True, max_length=128).to(device)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state[:, 0, :].squeeze().cpu().numpy()  # [CLS]

def data_para_ano(data):
    try:
        return datetime.datetime.fromisoformat(data.replace("Z", "")).year
    except:
        return None

# === 2. Carregar modelo BERTimbau ===
print("Carregando BERTimbau...")
tokenizer = AutoTokenizer.from_pretrained(bert_model)
model = AutoModel.from_pretrained(bert_model).to(device)
model.eval()

# === 3. Carregar dados anotados ===
print("Lendo comentários anotados...")
df = pd.read_csv(anotados_csv).dropna(subset=["texto", "sentimento"])
df = df[df["texto"].apply(detecta_pt)].reset_index(drop=True)

# === 4. Gerar embeddings ===
print("Gerando embeddings dos comentários anotados...")
embeddings = []
for texto in tqdm(df["texto"].tolist()):
    embeddings.append(bert_embed(texto))
X = np.array(embeddings)
y = df["sentimento"].values

# === 5. Treinar classificador ===
print("Treinando classificador...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

# Avaliar
print("\nRelatório de classificação no conjunto de teste:")
print(classification_report(y_test, clf.predict(X_test)))

# === 6. Classificar base completa com ponderação por likes ===
print("\nClassificando comentários relevantes...")
with open(entrada_json, "r", encoding="utf-8") as f:
    comentarios = json.load(f)

resultados = defaultdict(list)

for comentario in tqdm(comentarios):
    texto = comentario.get("texto", "").strip()
    data = comentario.get("data")
    likes = comentario.get("likes", 0)

    if not texto or not data:
        continue
    if not detecta_pt(texto):
        continue

    ano = data_para_ano(data)
    if not ano:
        continue

    embedding = bert_embed(texto)
    classe = clf.predict([embedding])[0]

    peso = likes + 1  # Mínimo de 1 voto por comentário
    resultados[ano].extend([classe] * peso)

# === 7. Agregar e plotar ===
print("Gerando gráfico por ano...")
anos = sorted(resultados.keys())
contagens = {classe: [] for classe in ["positivo", "neutro", "negativo"]}

for ano in anos:
    total = len(resultados[ano])
    for classe in contagens:
        qtd = resultados[ano].count(classe)
        contagens[classe].append(qtd / total if total > 0 else 0)

# Plot
plt.figure(figsize=(10, 6))
for classe, valores in contagens.items():
    plt.plot(anos, valores, label=classe)
plt.title("Proporção de sentimentos por ano")
plt.xlabel("Ano")
plt.ylabel("Proporção")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Garante que todos os anos aparecem no eixo x
plt.xticks(anos, rotation=45)

plt.savefig("grafico_sentimentos_por_ano_ponderado.png")
plt.show()
