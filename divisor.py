import os
import glob
import pandas as pd
from math import ceil
import gender_guesser.detector as gender

# Inicializar recursos O(1) do oráculo anti-mulher
detector = gender.Detector(case_sensitive=False)
ambiguous_names = set(['chris', 'ray', 'van', 'nic', 'naty', 'kellen', 'malu', 'elo', 'maya', 'cris', 'andreza'])

print("[*] Carregando barreira ontológica (Dataset Base Unificado)...")
female_names = set()

# 1. Carregar Base Original (Matriz Pura)
try:
    df_base = pd.read_csv('brazilian-names-and-gender.csv', delimiter=',')
    df_base['Name'] = df_base['Name'].str.lower().str.strip()
    female_names.update(df_base[df_base['Gender'] == 'F']['Name'].tolist())
except Exception as e:
    print(f"[!] ERRO FATAL: brazilian-names-and-gender.csv falhou ({e}). Abortando.")
    exit(1)

if not female_names:
    print("[!] ERRO FATAL: Nenhuma lista de nomes femininos pôde ser carregada na RAM. Abortando.")
    exit(1)

print(f"[+] O(1) Hash Map estabelecido: {len(female_names)} assinaturas femininas prontas para bloqueio.")

def is_female(name):
    if not isinstance(name, str) or name.strip() == '':
        return False
    first_name = name.split()[0].lower()
    
    # 1. Barreira de Ambiguidade (Não Obliterar)
    if first_name in ambiguous_names:
        return False

    # 2. ORÁCULO DE ESTADO (Dataset Puro)
    if first_name in female_names:
        return True
        
    # 3. A GUILHOTINA LATINA (Morfologia Feminina Padrão)
    if first_name.endswith('a'):
        return True
        
    # 4. SALVAGUARDA MASCULINA (Se terminar em 'o', é homem, ignora ML)
    if first_name.endswith('o'):
        return False
    
    # 5. O VETOR DE FALLBACK ESTRANGEIRO (Machine Learning Simples)
    gender_guess = detector.get_gender(first_name)
    if gender_guess in ['female', 'mostly_female']:
        return True
        
    # Se sobreviveu a tudo, passa.
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

    # 3. Aniquilar as mulheres do conjunto principal (Operação com Máscara Vetorial O(n))
    mask_feminina = df['nome'].apply(is_female)
    
    df_filtrado = df[~mask_feminina] # O que sobrevive (Homens/Desconhecidos)
    df_mulheres = df[mask_feminina]  # O que foi obliterado

    total_valido = len(df_filtrado)
    mulheres_removidas = len(df_mulheres)
    
    # 3.1. Gerar LOG materializado (Evidência da aniquilação)
    if mulheres_removidas > 0:
        log_nome = f"{base_nome}_LOG_mulheres_purgadas.csv"
        df_mulheres.to_csv(log_nome, sep=';', index=False, encoding=encoding)
        print(f"[+] LOG GERADO: {mulheres_removidas} perfis femininos exportados para '{log_nome}' para auditoria.")
    else:
        print("[+] Limpeza concluída. Nenhuma mulher encontrada.")

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
