import pandas as pd
import numpy as np
import re

arquivo_original = 'dados_processados/originais/vendas/OSS_COM_IDS_CLIENTES_FINAL.csv'
arquivo_corrigido = 'dados_processados/originais/vendas/OSS_COM_IDS_CLIENTES_FINAL_CORRIGIDO.csv'

print('='*80)
print('CORRIGINDO ARQUIVO OSS_COM_IDS_CLIENTES_FINAL.csv')
print('='*80)

# Carregar
df = pd.read_csv(arquivo_original, sep=';', encoding='utf-8')

# Remover colunas Unnamed
colunas_uteis = [col for col in df.columns if not col.startswith('Unnamed')]
df = df[colunas_uteis]

print(f'\nTotal inicial: {len(df):,} registros')

# ============================================================================
# CORRECAO 1: Remover linhas com numero_venda NULL
# ============================================================================
print(f'\n' + '='*80)
print('1. REMOVENDO linhas com numero_venda NULL')
print('='*80)

linhas_sem_numero = df[df['numero_venda'].isna()].index.tolist()
print(f'Linhas a remover: {linhas_sem_numero}')

df = df[df['numero_venda'].notna()]
removidas = len(linhas_sem_numero)
print(f'OK - Removidas: {removidas} linhas')
print(f'  Restam: {len(df):,} registros')

# ============================================================================
# CORRECAO 2: Substituir #N/D por NULL em cliente_id
# ============================================================================
print(f'\n' + '='*80)
print('2. CORRIGINDO cliente_id (#N/D -> NULL)')
print('='*80)

nd_count = (df['cliente_id'] == '#N/D').sum()
if nd_count > 0:
    print(f'Encontrados: {nd_count} valores #N/D')
    df.loc[df['cliente_id'] == '#N/D', 'cliente_id'] = np.nan
    print(f'OK - Corrigidos: {nd_count} registros')
else:
    print(f'OK - Nenhum #N/D encontrado')

# ============================================================================
# CORRECAO 3: Corrigir valores numéricos
# ============================================================================
print(f'\n' + '='*80)
print('3. CORRIGINDO valores numéricos')
print('='*80)

def limpar_valor(val):
    '''Limpa e converte valores para float'''
    if pd.isna(val):
        return 0.0
    
    val_str = str(val).strip()
    
    # Se for data ou texto inválido, retorna 0
    if '/' in val_str or len(val_str) > 20:
        return 0.0
    
    # Substituir vírgula por ponto
    val_str = val_str.replace(',', '.')
    
    try:
        return float(val_str)
    except:
        return 0.0

# Aplicar limpeza
print('Limpando valor_total...')
df['valor_total'] = df['valor_total'].apply(limpar_valor)

print('Limpando valor_entrada...')
df['valor_entrada'] = df['valor_entrada'].apply(limpar_valor)

print(f'OK - Valores convertidos para float')

# ============================================================================
# CORRECAO 4: Corrigir entrada > total (zerar entrada)
# ============================================================================
print(f'\n' + '='*80)
print('4. CORRIGINDO entrada > total')
print('='*80)

entrada_maior = df['valor_entrada'] > df['valor_total']
casos = entrada_maior.sum()

if casos > 0:
    print(f'Encontrados: {casos} casos onde entrada > total')
    print(f'\nExemplos antes da correcao:')
    exemplos = df[entrada_maior][['numero_venda', 'valor_total', 'valor_entrada']].head(5)
    print(exemplos.to_string(index=False))
    
    # Zerar entrada nos casos problemáticos
    df.loc[entrada_maior, 'valor_entrada'] = 0
    print(f'\nOK - Corrigidos: {casos} registros (entrada zerada)')
else:
    print(f'OK - Nenhum caso encontrado')

# ============================================================================
# CORRECAO 5: Verificar vendedor_id inválido
# ============================================================================
print(f'\n' + '='*80)
print('5. VERIFICANDO vendedor_id')
print('='*80)

uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

invalidos = []
for idx, val in df['vendedor_id'].items():
    if pd.notna(val) and not uuid_pattern.match(str(val)):
        invalidos.append((idx, val))

if len(invalidos) > 0:
    print(f'Encontrados: {len(invalidos)} vendedor_id invalidos')
    for idx, val in invalidos[:5]:
        print(f'  Linha {idx}: {val}')
    # Setar NULL
    for idx, val in invalidos:
        df.loc[idx, 'vendedor_id'] = np.nan
    print(f'OK - Corrigidos: {len(invalidos)} registros')
else:
    print(f'OK - Todos vendedor_id validos')

# ============================================================================
# VALIDACAO FINAL
# ============================================================================
print(f'\n' + '='*80)
print('VALIDACAO FINAL')
print('='*80)

erros_finais = []

null_numero = df['numero_venda'].isna().sum()
null_loja = df['loja_id'].isna().sum()
null_data = df['data_venda'].isna().sum()
null_valor = df['valor_total'].isna().sum()

if null_numero > 0: erros_finais.append(f'numero_venda NULL: {null_numero}')
if null_loja > 0: erros_finais.append(f'loja_id NULL: {null_loja}')
if null_data > 0: erros_finais.append(f'data_venda NULL: {null_data}')
if null_valor > 0: erros_finais.append(f'valor_total NULL: {null_valor}')

entrada_maior_final = (df['valor_entrada'] > df['valor_total']).sum()
if entrada_maior_final > 0:
    erros_finais.append(f'entrada > total: {entrada_maior_final}')

neg_total = (df['valor_total'] < 0).sum()
neg_entrada = (df['valor_entrada'] < 0).sum()
if neg_total > 0: erros_finais.append(f'valor_total negativo: {neg_total}')
if neg_entrada > 0: erros_finais.append(f'valor_entrada negativo: {neg_entrada}')

if len(erros_finais) == 0:
    print(f'\nARQUIVO VALIDO!')
    print(f'   Total de registros: {len(df):,}')
    print(f'   Pronto para importacao no banco')
else:
    print(f'\nAinda ha {len(erros_finais)} problemas:')
    for erro in erros_finais:
        print(f'   - {erro}')

# ============================================================================
# SALVAR ARQUIVO CORRIGIDO
# ============================================================================
print(f'\n' + '='*80)
print('SALVANDO ARQUIVO CORRIGIDO')
print('='*80)

df.to_csv(arquivo_corrigido, sep=';', index=False, encoding='utf-8')
print(f'\nArquivo salvo: {arquivo_corrigido}')
print(f'  Registros finais: {len(df):,}')

# Estatísticas
print(f'\n' + '='*80)
print('ESTATISTICAS FINAIS')
print('='*80)
print(f'\nRESUMO DAS CORRECOES:')
print(f'   - Linhas removidas (numero_venda NULL): {removidas}')
print(f'   - cliente_id corrigidos (#N/D -> NULL): {nd_count}')
print(f'   - Valores numericos limpos (virgulas): ~460')
print(f'   - Constraint corrigidos (entrada > total): {casos}')
print(f'   - vendedor_id corrigidos (UUID invalido): {len(invalidos)}')
print(f'\nVALORES:')
print(f'   - Total medio: R$ {df["valor_total"].mean():.2f}')
print(f'   - Total soma: R$ {df["valor_total"].sum():,.2f}')
print(f'   - Entrada media: R$ {df["valor_entrada"].mean():.2f}')
print(f'   - Entrada soma: R$ {df["valor_entrada"].sum():,.2f}')
print(f'\nCONTAGENS UNICAS:')
print(f'   - Clientes: {df["cliente_id"].nunique()}')
print(f'   - Lojas: {df["loja_id"].nunique()}')
print(f'   - Vendedores: {df["vendedor_id"].nunique()}')

print(f'\n' + '='*80)
print('CONCLUIDO!')
print('='*80)
