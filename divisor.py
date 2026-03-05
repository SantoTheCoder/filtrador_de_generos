import os
import glob
import pandas as pd
from math import ceil
import gender_guesser.detector as gender

# Inicializar recursos O(1) do oráculo anti-mulher
detector = gender.Detector(case_sensitive=False)
ambiguous_names = set(['chris', 'ray', 'van', 'nic', 'naty', 'kellen', 'malu', 'elo', 'maya', 'cris', 'andreza'])

print("[*] Carregando barreira ontológica (brazilian-names-and-gender.csv)...")
try:
    static_names = pd.read_csv('brazilian-names-and-gender.csv', delimiter=',')
    static_names['Name'] = static_names['Name'].str.lower()
    female_names = set(static_names[static_names['Gender'] == 'F']['Name'].tolist())
except FileNotFoundError:
    print("[!] ERRO FATAL: Arquivo brazilian-names-and-gender.csv não encontrado na mesma pasta. Abortando.")
    exit(1)

def is_female(name):
    if not isinstance(name, str) or name.strip() == '':
        return False
    first_name = name.split()[0].lower()
    if first_name in ambiguous_names:
        return False
    if first_name in female_names:
        return True
    if first_name.endswith('a'):
        return True
    if first_name.endswith('o'):
        return False
    
    gender_guess = detector.get_gender(first_name)
    if gender_guess in ['female', 'mostly_female']:
        return True
    return False

def processar_e_dividir(encoding='utf-8'):
    print("\n=== ARCHON-OMEGA: DIVISOR & PURIFICADOR ===")
    
    # 1. Obter o arquivo
    filename = input("Por favor, insira o nome do arquivo de entrada (com extensão, ex: lista.csv): ")
    if not os.path.exists(filename):
        print(f"[!] ERRO: Arquivo '{filename}' não encontrado.")
        return
        
    base_nome = os.path.splitext(os.path.basename(filename))[0]

    # 2. Obter a quantidade de partes
    while True:
        try:
            partes = int(input("Em quantas partes deseja dividir? "))
            if partes <= 0: raise ValueError
            break
        except ValueError:
            print("Digite um número inteiro positivo válido.")

    print(f"\n[*] Carregando arquivo {filename} na memória (Aguarde)...")
    try:
        df = pd.read_csv(filename, delimiter=';', encoding=encoding)
        # Normalização estrutural para evitar anomalias de formatação humana
        df.columns = df.columns.str.lower().str.strip()
    except Exception as e:
        print(f"[!] Erro ao ler o CSV. Tente outro encoding ou verifique o arquivo. Detalhe: {e}")
        return

    if 'nome' not in df.columns:
        print("[!] ERRO FATAL: A coluna 'nome' não foi encontrada no arquivo. Colunas atuais:", list(df.columns))
        return

    # Normalizar espaços na coluna de nomes para precisão absoluta do oráculo
    df['nome'] = df['nome'].astype(str).str.strip()

    total_bruto = len(df)
    print(f"[*] Aplicando barreira de obliteração feminina sobre {total_bruto} registros...")

    # 3. Aniquilar as mulheres do conjunto principal antes da divisão
    df_filtrado = df[~df['nome'].apply(is_female)]
    
    total_valido = len(df_filtrado)
    mulheres_removidas = total_bruto - total_valido
    
    print(f"[+] Limpeza concluída. {mulheres_removidas} mulheres purgadas.")
    print(f"[*] Restam {total_valido} registros masculinos/desconhecidos para divisão.")
    
    if total_valido == 0:
        print("[!] O arquivo ficou vazio após a filtragem. Divisão abortada.")
        return

    # 4. Dividir de forma balanceada o que sobrou
    tamanho_parte = ceil(total_valido / partes)

    print("\n[*] Iniciando fracionamento de disco...")
    for i in range(partes):
        inicio = i * tamanho_parte
        fim = inicio + tamanho_parte
        df_parte = df_filtrado.iloc[inicio:fim]

        if len(df_parte) > 0:
            nome_arquivo = f"{base_nome}_parte_{i+1}.csv"
            df_parte.to_csv(nome_arquivo, index=False, sep=';', encoding=encoding)
            print(f"  -> {nome_arquivo} salvo com {len(df_parte)} registros.")

    print("\n[+] Operação Transcendental Concluída.")

if __name__ == '__main__':
    processar_e_dividir()
