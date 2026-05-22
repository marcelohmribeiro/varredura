import pandas as pd
import os

# ------------------------------------------
# CAMINHO DA PASTA ONDE ESTÃO OS CSVs
# ------------------------------------------
BASE_DIR = r"C:\Users\anton\Documents\tata\Alerta Segurança\AlertaSeguranca\data\out"

# NOMES EXATOS DOS ARQUIVOS
FILES = [
    "comentarios toxicos 1.csv",
    "comentarios toxicos 2.csv"
]

def clean_csv(file_path):
    linhas_corrigidas = []
    buffer = ""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")

            if buffer == "":
                buffer = line
            else:
                buffer += " " + line

            # Se o número de aspas é PAR → linha completa
            if buffer.count('"') % 2 == 0:
                linhas_corrigidas.append(buffer)
                buffer = ""

    clean_path = file_path.replace(".csv", "_clean.csv")

    with open(clean_path, "w", encoding="utf-8", newline="") as f:
        for line in linhas_corrigidas:
            f.write(line + "\n")

    print(f"[OK] Arquivo limpo salvo: {clean_path}")


# PROCESSAR OS DOIS ARQUIVOS
for fname in FILES:
    file_path = os.path.join(BASE_DIR, fname)
    print(f"Limpando: {file_path}")

    if not os.path.exists(file_path):
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        continue

    clean_csv(file_path)

print("\nFinalizado!")
