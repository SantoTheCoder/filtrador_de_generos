import pandas as pd
import gender_guesser.detector as gender
import os

# Inicializar o detector de gênero
detector = gender.Detector(case_sensitive=False)

# Lista de nomes ambíguos para tratar como "desconhecido"
ambiguous_names = ['chris', 'ray', 'van', 'nic', 'naty', 'kellen', 'malu', 'elo', 'maya', 'cris', 'andreza']

# Carregar a lista estática de nomes brasileiros
static_names = pd.read_csv('brazilian-names-and-gender.csv', delimiter=',')
static_names['Name'] = static_names['Name'].str.lower()
male_names = static_names[static_names['Gender'] == 'M']['Name'].tolist()
female_names = static_names[static_names['Gender'] == 'F']['Name'].tolist()

# Solicitar ao usuário o nome do arquivo de entrada
filename = input("Por favor, insira o nome do arquivo de entrada (com extensão, ex: lista.csv): ")

# Extrair o nome base do arquivo (sem extensão)
base_name = os.path.splitext(filename)[0]

# Criar a pasta com o nome base, se não existir
output_dir = base_name
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Carregar o CSV com os leads
leads = pd.read_csv(filename, delimiter=';')

# Verificar se a coluna 'nome' existe no arquivo de leads
if 'nome' not in leads.columns:
    raise ValueError("A coluna 'nome' não foi encontrada no arquivo de leads.")

# Função para determinar o gênero
def get_gender(name):
    if not isinstance(name, str) or name.strip() == '':
        return 'desconhecido'
    first_name = name.split()[0].lower()
    
    # Verificar se é um nome ambíguo
    if first_name in ambiguous_names:
        return 'desconhecido'
    
    # 1. Verificar na lista estática
    if first_name in male_names:
        return 'masculino'
    elif first_name in female_names:
        return 'feminino'
    
    # 2. Aplicar a regra de terminação
    if first_name.endswith('a'):
        return 'feminino'
    elif first_name.endswith('o'):
        return 'masculino'
    
    # 3. Usar gender-guesser como última opção
    gender_guess = detector.get_gender(first_name)
    if gender_guess in ['male', 'mostly_male']:
        return 'masculino'
    elif gender_guess in ['female', 'mostly_female']:
        return 'feminino'
    else:
        return 'desconhecido'

# Adicionar a coluna 'genero' ao DataFrame de leads
leads['genero'] = leads['nome'].apply(get_gender)

# Criar DataFrames separados
masculino = leads[leads['genero'] == 'masculino']
feminino = leads[leads['genero'] == 'feminino']
desconhecido = leads[leads['genero'] == 'desconhecido']

# Salvar os arquivos CSV dentro da pasta criada, sem a coluna 'genero'
masculino.drop(columns=['genero']).to_csv(os.path.join(output_dir, f"{base_name}_masculino.csv"), sep=';', index=False)
feminino.drop(columns=['genero']).to_csv(os.path.join(output_dir, f"{base_name}_feminino.csv"), sep=';', index=False)
desconhecido.drop(columns=['genero']).to_csv(os.path.join(output_dir, f"{base_name}_desconhecido.csv"), sep=';', index=False)

# Contar os resultados
contagem_generos = leads['genero'].value_counts()
print("Resultado final:")
print(f"Masculino: {contagem_generos.get('masculino', 0)}")
print(f"Feminino: {contagem_generos.get('feminino', 0)}")
print(f"Desconhecido: {contagem_generos.get('desconhecido', 0)}")