"""
Cria ID único para cada CLIENTE no arquivo consolidadas.csv
- Um cliente pode ter múltiplas OSS
- ID baseado em CPF (ou nome+data_nascimento se CPF vazio)
- Evita conflito com IDs do VIXEN (começa após maior ID do VIXEN)
- Coluna ID inserida ANTES da coluna NOME:
"""

import pandas as pd
from pathlib import Path
import hashlib

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CONSOLIDADAS_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'
VIXEN_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'VIXEN.csv'

print("=" * 80)
print("CRIANDO ID ÚNICO PARA CLIENTES EM CONSOLIDADAS.CSV")
print("=" * 80)

# 1. Ler VIXEN para pegar maior ID
print(f"\n1. Lendo arquivo VIXEN: {VIXEN_PATH.name}")
vixen = pd.read_csv(VIXEN_PATH, sep=';', dtype=str)
vixen['ID'] = vixen['ID'].astype(int)
maior_id_vixen = vixen['ID'].max()
print(f"   ✓ {len(vixen):,} registros no VIXEN")
print(f"   ✓ Maior ID no VIXEN: {maior_id_vixen:,}")
print(f"   ✓ IDs para OSS começarão em: {maior_id_vixen + 1:,}")

# 2. Ler consolidadas
print(f"\n2. Lendo arquivo: {CONSOLIDADAS_PATH.name}")
df = pd.read_csv(CONSOLIDADAS_PATH, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip()
print(f"   ✓ {len(df):,} registros (OSS)")
print(f"   ✓ {len(df.columns)} colunas")

# 3. Criar chave única por cliente
print(f"\n3. Identificando clientes únicos...")

def criar_chave_cliente(row):
    """Cria chave única baseada em CPF ou NOME+DT_NASC"""
    cpf = str(row.get('CPF', '')).strip()
    nome = str(row.get('NOME:', '')).strip().upper()
    dt_nasc = str(row.get('DT NASC', '')).strip()
    
    # Se tem CPF válido, usa CPF
    if cpf and cpf != 'nan' and len(cpf) >= 11:
        return f"CPF_{cpf}"
    
    # Senão, usa NOME + DATA_NASCIMENTO
    if nome and nome != 'nan':
        if dt_nasc and dt_nasc != 'nan':
            return f"NOME_{nome}_{dt_nasc}"
        else:
            return f"NOME_{nome}"
    
    # Fallback: hash da linha inteira
    row_str = ''.join(str(v) for v in row.values)
    hash_id = hashlib.md5(row_str.encode()).hexdigest()[:12]
    return f"HASH_{hash_id}"

# Criar chave única
df['_chave_cliente'] = df.apply(criar_chave_cliente, axis=1)

# 4. Mapear clientes únicos para IDs
print(f"\n4. Criando mapeamento de IDs...")
clientes_unicos = df['_chave_cliente'].unique()
print(f"   ✓ {len(clientes_unicos):,} clientes únicos identificados")

# Criar dicionário: chave_cliente → ID
proximo_id = maior_id_vixen + 1
mapeamento_ids = {}
for chave in sorted(clientes_unicos):
    mapeamento_ids[chave] = proximo_id
    proximo_id += 1

print(f"   ✓ IDs gerados: {maior_id_vixen + 1:,} até {proximo_id - 1:,}")

# 5. Aplicar IDs ao dataframe
print(f"\n5. Aplicando IDs ao dataframe...")
df['ID_CLIENTE'] = df['_chave_cliente'].map(mapeamento_ids)

# Remover coluna temporária
df = df.drop(columns=['_chave_cliente'])

# 6. Reordenar colunas: ID_CLIENTE antes de NOME:
print(f"\n6. Reordenando colunas...")
colunas = df.columns.tolist()
idx_nome = colunas.index('NOME:')

# Remover ID_CLIENTE de onde está
colunas.remove('ID_CLIENTE')

# Inserir ID_CLIENTE antes de NOME:
colunas.insert(idx_nome, 'ID_CLIENTE')

# Aplicar nova ordem
df = df[colunas]

print(f"   ✓ Coluna ID_CLIENTE inserida antes de NOME:")
print(f"   ✓ Nova ordem: ...{', '.join(colunas[idx_nome-1:idx_nome+3])}...")

# 7. Verificações
print(f"\n7. Verificações...")
print(f"   ✓ Total de OSS: {len(df):,}")
print(f"   ✓ Clientes únicos: {df['ID_CLIENTE'].nunique():,}")
print(f"   ✓ IDs sem duplicatas: {df['ID_CLIENTE'].duplicated().sum() == 0}")

# Estatísticas de clientes com múltiplas OSS
clientes_com_multiplas_oss = df['ID_CLIENTE'].value_counts()
com_1_oss = (clientes_com_multiplas_oss == 1).sum()
com_2_oss = (clientes_com_multiplas_oss == 2).sum()
com_3_mais_oss = (clientes_com_multiplas_oss >= 3).sum()

print(f"\n   Distribuição de OSS por cliente:")
print(f"   - {com_1_oss:,} clientes com 1 OS")
print(f"   - {com_2_oss:,} clientes com 2 OSS")
print(f"   - {com_3_mais_oss:,} clientes com 3+ OSS")

# Mostrar exemplos de clientes com múltiplas OSS
print(f"\n   Top 10 clientes com mais OSS:")
for idx, (id_cliente, qtd) in enumerate(clientes_com_multiplas_oss.head(10).items(), 1):
    cliente_exemplo = df[df['ID_CLIENTE'] == id_cliente].iloc[0]
    nome = cliente_exemplo.get('NOME:', 'N/A')[:30]
    cpf = cliente_exemplo.get('CPF', 'N/A')[:14]
    print(f"   {idx:>2}. ID {id_cliente}: {qtd} OSS - {nome} (CPF: {cpf})")

# 8. Salvar
print(f"\n8. Salvando arquivo...")
df.to_csv(CONSOLIDADAS_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {CONSOLIDADAS_PATH.name}")
print(f"   ✓ {len(df):,} registros mantidos")
print(f"   ✓ {len(df.columns)} colunas (+ ID_CLIENTE)")

print("\n" + "=" * 80)
print("✅ ID DE CLIENTES CRIADO COM SUCESSO!")
print("=" * 80)
print(f"\nResumo:")
print(f"  - IDs VIXEN: 24,560 até {maior_id_vixen:,}")
print(f"  - IDs OSS: {maior_id_vixen + 1:,} até {proximo_id - 1:,}")
print(f"  - Total de clientes únicos: {df['ID_CLIENTE'].nunique():,}")
print(f"  - Total de OSS: {len(df):,}")
print("=" * 80)
