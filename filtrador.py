import pandas as pd
import gender_guesser.detector as gender
import os

# Inicializar o detector de gênero
detector = gender.Detector(case_sensitive=False)

# Lista de nomes ambíguos para tratar como "desconhecido/não-feminino"
ambiguous_names = ['chris', 'ray', 'van', 'nic', 'naty', 'kellen', 'malu', 'elo', 'maya', 'cris', 'andreza']

# Carregar APENAS a lista estática de nomes femininos (Economia de RAM O(n))
static_names = pd.read_csv('brazilian-names-and-gender.csv', delimiter=',')
static_names['Name'] = static_names['Name'].str.lower()
female_names = set(static_names[static_names['Gender'] == 'F']['Name'].tolist())

# Solicitar ao usuário o nome do arquivo de entrada
filename = input("Por favor, insira o nome do arquivo de entrada (com extensão, ex: lista.csv): ")

# Extrair o nome base do arquivo (sem extensão)
base_name = os.path.splitext(filename)[0]

# Carregar o CSV com os leads
leads = pd.read_csv(filename, delimiter=';')

# Verificar se a coluna 'nome' existe no arquivo de leads
if 'nome' not in leads.columns:
    raise ValueError("A coluna 'nome' não foi encontrada no arquivo de leads.")

# Função Booleana de Barreira: Só devolve True se confirmar feminino
def is_female(name):
    if not isinstance(name, str) or name.strip() == '':
        return False
        
    first_name = name.split()[0].lower()
    
    # Verificar se é um nome ambíguo (Não exclui)
    if first_name in ambiguous_names:
        return False
    
    # 1. Verificar na blacklist primária (O(1) lookup usando set)
    if first_name in female_names:
        return True
    
    # 2. Aplicar a regra morfológica
    if first_name.endswith('a'):
        return True
    
    # Se terminar em O, já sabemos que não é feminino.
    if first_name.endswith('o'):
        return False
    
    # 3. Usar gender-guesser como última opção
    gender_guess = detector.get_gender(first_name)
    if gender_guess in ['female', 'mostly_female']:
        return True
        
    return False

# Contagem inicial
total_inicial = len(leads)

# Aplicar a barreira. Mantemos apenas onde is_female é Falso.
leads_filtrados = leads[~leads['nome'].apply(is_female)]

total_final = len(leads_filtrados)
removidos = total_inicial - total_final

# Salvar o arquivo de saída (Sem criar pastas adicionais para economizar IO e espaço)
output_filename = f"{base_name}_sem_mulheres.csv"
leads_filtrados.to_csv(output_filename, sep=';', index=False)

# Exibir relatório termodinâmico simples
print("Resultado final da operação de limpeza:")
print(f"Total inicial de leads: {total_inicial}")
print(f"Mulheres removidas: {removidos}")
print(f"Leads restantes (Masculinos, Ambíguos e Desconhecidos): {total_final}")
print(f"Arquivo salvo com sucesso em: {output_filename}")