import pandas as pd
import gender_guesser.detector as gender

# Inicializar o detector de gênero
detector = gender.Detector(case_sensitive=False)

# Carregar a lista estática de nomes brasileiros do arquivo CORRETO
static_names = pd.read_csv('brazilian-names-and-gender.csv', delimiter=',')
print("Colunas na lista estática:", static_names.columns.tolist())

# Converter os nomes para minúsculas
static_names['Name'] = static_names['Name'].str.lower()

# Separar os nomes masculinos e femininos
male_names = static_names[static_names['Gender'] == 'M']['Name'].tolist()
female_names = static_names[static_names['Gender'] == 'F']['Name'].tolist()

# Carregar o CSV com os leads (ajuste o nome do arquivo se necessário)
leads = pd.read_csv('24-05-2025_lista_play_2.csv', delimiter=';')
print("Colunas nos leads:", leads.columns.tolist())

# Verificar se a coluna 'nome' existe no arquivo de leads
if 'nome' not in leads.columns:
    raise ValueError("A coluna 'nome' não foi encontrada no arquivo de leads.")

# Função para determinar o gênero
def get_gender(name):
    if not isinstance(name, str):
        return 'desconhecido'
    first_name = name.split()[0].lower()
    if first_name in male_names:
        return 'masculino'
    elif first_name in female_names:
        return 'feminino'
    else:
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

# Salvar em arquivos Excel
masculino.to_excel('leads_masculino.xlsx', index=False)
feminino.to_excel('leads_feminino.xlsx', index=False)
desconhecido.to_excel('leads_desconhecido.xlsx', index=False)

# Contar os resultados
contagem_generos = leads['genero'].value_counts()
print("Resultado final:")
print(f"Masculino: {contagem_generos.get('masculino', 0)}")
print(f"Feminino: {contagem_generos.get('feminino', 0)}")
print(f"Desconhecido: {contagem_generos.get('desconhecido', 0)}")