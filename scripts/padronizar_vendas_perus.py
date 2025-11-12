"""
Padronização de números de venda de PERUS
Todas as vendas devem começar com 6 (6xxx)
"""

import pandas as pd
from pathlib import Path

# Arquivo de vendas de Perus
arquivo = Path('dados_processados/originais/cxs/planilhas_originais/perus/vendas_perus_consolidado.csv')

print('=' * 80)
print('PADRONIZAÇÃO DE NÚMEROS DE VENDA - PERUS')
print('=' * 80)

# Ler arquivo
df = pd.read_csv(arquivo, sep=';', dtype=str)

print(f'\n📊 Total de registros: {len(df)}')

# Analisar números de venda atuais
print(f'\n🔍 ANÁLISE DOS NÚMEROS DE VENDA:')

# Separar os que já começam com 6 e os que não começam
ja_com_6 = df[df['nn_venda'].str.startswith('6', na=False)]
sem_6 = df[~df['nn_venda'].str.startswith('6', na=False)]

print(f'\n   ✅ Já começam com "6": {len(ja_com_6)} vendas')
print(f'   ❌ Não começam com "6": {len(sem_6)} vendas')

if len(sem_6) > 0:
    print(f'\n📋 Exemplos de vendas SEM "6" (primeiras 10):')
    for idx, venda in enumerate(sem_6['nn_venda'].head(10), 1):
        print(f'      {idx}. {venda}')

# Função para padronizar
def padronizar_numero_venda(num_venda):
    """Adiciona 6 no início se não tiver"""
    if pd.isna(num_venda):
        return num_venda
    
    num_str = str(num_venda).strip()
    
    # Se já começa com 6, manter
    if num_str.startswith('6'):
        return num_str
    
    # Adicionar 6 no início
    return f'6{num_str}'

# Aplicar padronização
print(f'\n🔄 Aplicando padronização...')

df_original = df.copy()
df['nn_venda'] = df['nn_venda'].apply(padronizar_numero_venda)

# Verificar resultados
alterados = (df_original['nn_venda'] != df['nn_venda']).sum()
print(f'\n✅ Números de venda alterados: {alterados}')

# Verificar se todos agora começam com 6
todos_com_6 = df['nn_venda'].str.startswith('6', na=False).sum()
print(f'✅ Total de vendas começando com "6": {todos_com_6}/{len(df)}')

# Mostrar exemplos de alterações
if alterados > 0:
    print(f'\n📋 Exemplos de alterações (primeiros 10):')
    
    mask_alterado = df_original['nn_venda'] != df['nn_venda']
    alteracoes = df[mask_alterado][['data_movimento', 'nn_venda', 'cliente']].head(10)
    
    for idx, row in alteracoes.iterrows():
        num_original = df_original.loc[idx, 'nn_venda']
        num_novo = row['nn_venda']
        print(f'      {num_original} → {num_novo} ({row["data_movimento"]} - {row["cliente"][:30]})')

# Salvar arquivo atualizado
print(f'\n💾 Salvando arquivo atualizado...')
df.to_csv(arquivo, sep=';', index=False, encoding='utf-8-sig')

print(f'✅ Arquivo salvo: {arquivo.name}')

# Estatísticas finais
print(f'\n{"=" * 80}')
print('ESTATÍSTICAS FINAIS')
print('=' * 80)
print(f'   - Total de registros: {len(df)}')
print(f'   - Vendas alteradas: {alterados}')
print(f'   - Todas começam com "6": {todos_com_6 == len(df)}')
print(f'   - Vendas únicas: {df["nn_venda"].nunique()}')

print(f'\n✅ Padronização concluída!')
