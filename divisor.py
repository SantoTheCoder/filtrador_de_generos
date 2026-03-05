import os
import glob
import pandas as pd
from math import ceil

def dividir_csv_em_partes(caminho_raiz='.', encoding='utf-8'):
    # Buscar arquivo CSV na raiz
    arquivos = glob.glob(os.path.join(caminho_raiz, '*.csv'))
    if not arquivos:
        print("Nenhum arquivo CSV encontrado na raiz.")
        return

    caminho_csv = arquivos[0]
    print(f"Arquivo encontrado: {os.path.basename(caminho_csv)}")

    # Carregar CSV com delimitador ';'
    df = pd.read_csv(caminho_csv, delimiter=';', encoding=encoding)

    # Perguntar número de partes
    while True:
        try:
            partes = int(input("Em quantas partes deseja dividir? "))
            if partes <= 0:
                raise ValueError
            break
        except ValueError:
            print("Digite um número inteiro positivo válido.")

    # Dividir de forma balanceada
    total_linhas = len(df)
    tamanho_parte = ceil(total_linhas / partes)

    base_nome = os.path.splitext(os.path.basename(caminho_csv))[0]

    for i in range(partes):
        inicio = i * tamanho_parte
        fim = inicio + tamanho_parte
        df_parte = df.iloc[inicio:fim]

        nome_arquivo = f"{base_nome}_parte_{i+1}.csv"
        df_parte.to_csv(nome_arquivo, index=False, sep=';', encoding=encoding)
        print(f"{nome_arquivo} salvo com {len(df_parte)} registros.")

    print("Divisão concluída.")

if __name__ == '__main__':
    dividir_csv_em_partes()
