"""
Cria CSV de CLIENTES ÚNICOS do arquivo OSS_OUTRAS_LOJAS.csv
para importação na tabela core.clientes

Campos mapeados:
- id_legado: ID_CLIENTE (nosso ID único)
- nome: NOME:
- cpf: CPF
- rg: RG
- data_nascimento: DT NASC
- cliente_desde: DATA DE COMPRA (primeira compra)
- email: EMAIL:
- status: 'ATIVO'
- origem: 'IMPORTACAO_OSS_OUTRAS_LOJAS'
- observacoes: Informações da primeira OS
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent
OSS_OUTRAS_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'OSS_OUTRAS_LOJAS.csv'
OUTPUT_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("CRIANDO CSV DE CLIENTES ÚNICOS PARA IMPORTAÇÃO")
print("Fonte: OSS_OUTRAS_LOJAS.csv")
print("Destino: core.clientes")
print("=" * 80)

# 1. Ler arquivo OSS_OUTRAS_LOJAS.csv
print(f"\n1. Lendo arquivo: {OSS_OUTRAS_PATH.name}")
df_oss = pd.read_csv(OSS_OUTRAS_PATH, sep=';', dtype=str, encoding='utf-8')
df_oss.columns = df_oss.columns.str.strip()
print(f"   ✓ {len(df_oss):,} OSS")
print(f"   ✓ {df_oss['ID_CLIENTE'].nunique():,} clientes únicos")

# 2. Agrupar por cliente (pegar primeira OS de cada cliente)
print(f"\n2. Agrupando por cliente (usando primeira OS ordenada por data)...")

# Ordenar por ID_CLIENTE e DATA DE COMPRA para pegar a primeira compra
df_oss['DATA_ORDENACAO'] = pd.to_datetime(df_oss['DATA DE COMPRA'], format='%d/%m/%Y', errors='coerce')
df_oss_sorted = df_oss.sort_values(['ID_CLIENTE', 'DATA_ORDENACAO'])

# Pegar primeira OSS de cada cliente (a mais antiga)
df_clientes = df_oss_sorted.groupby('ID_CLIENTE').first().reset_index()
print(f"   ✓ {len(df_clientes):,} clientes únicos extraídos")
print(f"   ✓ Ordenados pela data de primeira compra")

# 3. Função para converter data
def converter_data(data_str):
    """Converte data de DD/MM/YYYY para YYYY-MM-DD"""
    if pd.isna(data_str) or str(data_str).strip() == '':
        return None
    
    try:
        # Tenta formato DD/MM/YYYY
        if '/' in str(data_str):
            partes = str(data_str).split('/')
            if len(partes) == 3:
                dia, mes, ano = partes
                # Se ano tem 2 dígitos, assume 19XX ou 20XX
                if len(ano) == 2:
                    ano = '19' + ano if int(ano) > 25 else '20' + ano
                return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
    except:
        pass
    
    return None

# 4. Criar dataframe para importação
print(f"\n3. Mapeando colunas para tabela core.clientes...")

clientes_import = pd.DataFrame()

# Campos obrigatórios
clientes_import['id_legado'] = df_clientes['ID_CLIENTE']
clientes_import['nome'] = df_clientes['NOME:']

# Campos opcionais
clientes_import['cpf'] = df_clientes['CPF'].apply(lambda x: x if pd.notna(x) and str(x).strip() != '' else None)
clientes_import['rg'] = df_clientes['RG'].apply(lambda x: x if pd.notna(x) and str(x).strip() != '' else None)

# Data de nascimento (converter formato)
clientes_import['data_nascimento'] = df_clientes['DT NASC'].apply(converter_data)

# Cliente desde (data da primeira compra)
clientes_import['cliente_desde'] = df_clientes['DATA DE COMPRA'].apply(converter_data)

# Sexo (não temos, deixar NULL)
clientes_import['sexo'] = None

# Email
clientes_import['email'] = df_clientes['EMAIL:'].apply(
    lambda x: x if pd.notna(x) and str(x).strip() != '' and str(x).upper() != 'SEM EMAIL' else None
)

# Status (sempre ATIVO)
clientes_import['status'] = 'ATIVO'

# Origem
clientes_import['origem'] = 'IMPORTACAO_OSS_OUTRAS_LOJAS'

# Tags (criar array como string)
def criar_tags(row):
    tags = ['CLIENTE_OSS']
    loja = str(row.get('LOJA', '')).strip()
    if loja:
        tags.append(f'LOJA_{loja.upper().replace(" ", "_")}')
    return '{' + ','.join(tags) + '}'

clientes_import['tags'] = df_clientes.apply(criar_tags, axis=1)

# Observações
def criar_observacoes(row):
    obs_parts = []
    obs_parts.append(f"Cliente importado de OSS - Loja: {row.get('LOJA', 'N/A')}")
    obs_parts.append(f"Primeira OS: {row.get('OS N°', 'N/A')} em {row.get('DATA DE COMPRA', 'N/A')}")
    
    # Contar total de OSS deste cliente
    id_cliente = row.get('ID_CLIENTE')
    total_oss = len(df_oss[df_oss['ID_CLIENTE'] == id_cliente])
    obs_parts.append(f"Total de OSS: {total_oss}")
    
    return ' | '.join(obs_parts)

clientes_import['observacoes'] = df_clientes.apply(criar_observacoes, axis=1)

# 5. Estatísticas
print(f"\n4. Estatísticas do arquivo de importação:")
print(f"   ✓ Total de clientes: {len(clientes_import):,}")
print(f"   ✓ Com CPF: {clientes_import['cpf'].notna().sum():,} ({clientes_import['cpf'].notna().sum()/len(clientes_import)*100:.1f}%)")
print(f"   ✓ Com RG: {clientes_import['rg'].notna().sum():,} ({clientes_import['rg'].notna().sum()/len(clientes_import)*100:.1f}%)")
print(f"   ✓ Com email: {clientes_import['email'].notna().sum():,} ({clientes_import['email'].notna().sum()/len(clientes_import)*100:.1f}%)")
print(f"   ✓ Com data nascimento: {clientes_import['data_nascimento'].notna().sum():,} ({clientes_import['data_nascimento'].notna().sum()/len(clientes_import)*100:.1f}%)")
print(f"   ✓ Com cliente_desde: {clientes_import['cliente_desde'].notna().sum():,} ({clientes_import['cliente_desde'].notna().sum()/len(clientes_import)*100:.1f}%)")

# Distribuição por loja
print(f"\n   Distribuição por loja:")
for loja, count in df_clientes['LOJA'].value_counts().items():
    print(f"     - {loja}: {count:,} clientes")

# 6. Validações
print(f"\n5. Validações...")

# Validar nomes não vazios
nomes_vazios = clientes_import['nome'].isna().sum() + (clientes_import['nome'] == '').sum()
print(f"   ✓ Nomes vazios: {nomes_vazios}")

# Validar CPFs duplicados (dentro do arquivo)
cpfs_duplicados = clientes_import[clientes_import['cpf'].notna()]['cpf'].duplicated().sum()
print(f"   ✓ CPFs duplicados: {cpfs_duplicados}")

# Validar id_legado duplicados
id_legado_duplicados = clientes_import['id_legado'].duplicated().sum()
print(f"   ✓ id_legado duplicados: {id_legado_duplicados}")

if nomes_vazios > 0 or cpfs_duplicados > 0 or id_legado_duplicados > 0:
    print(f"\n   ⚠️ ATENÇÃO: Existem problemas de validação!")
else:
    print(f"\n   ✅ Todas as validações passaram!")

# 7. Salvar arquivo
print(f"\n6. Salvando arquivo CSV para importação...")
clientes_import.to_csv(OUTPUT_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {OUTPUT_PATH.name}")
print(f"   ✓ {len(clientes_import):,} clientes")
print(f"   ✓ {len(clientes_import.columns)} colunas")

# Mostrar primeiros registros
print(f"\n7. Primeiros 5 registros (preview):")
print(clientes_import.head(5)[['id_legado', 'nome', 'cpf', 'email', 'status', 'origem']].to_string(index=False))

print("\n" + "=" * 80)
print("✅ CSV DE CLIENTES CRIADO COM SUCESSO!")
print("=" * 80)
print(f"\nArquivo para importação: {OUTPUT_PATH.name}")
print(f"Total de registros: {len(clientes_import):,}")
print(f"\nColunas incluídas:")
for col in clientes_import.columns:
    print(f"  - {col}")
print("\n" + "=" * 80)
