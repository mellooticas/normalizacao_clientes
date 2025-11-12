import pandas as pd
import numpy as np
import re

arquivo = 'dados_processados/originais/vendas/OSS_COM_IDS_CLIENTES_FINAL.csv'

df = pd.read_csv(arquivo, sep=';', encoding='utf-8')

# Remover colunas Unnamed (vazias)
colunas_uteis = [col for col in df.columns if not col.startswith('Unnamed')]
df = df[colunas_uteis]

print('='*80)
print('VALIDACAO COMPLETA - OSS_COM_IDS_CLIENTES_FINAL.csv')
print('Para importação na tabela vendas.vendas')
print('='*80)

print(f'\nTotal de registros: {len(df):,}')

# ============================================================================
# 1. VALIDACAO: Campos NOT NULL
# ============================================================================
print(f'\n' + '='*80)
print('1. CAMPOS OBRIGATORIOS (NOT NULL)')
print('='*80)

erros = []

# numero_venda (NOT NULL, VARCHAR(50))
null_numero = df['numero_venda'].isna().sum()
if null_numero > 0:
    erros.append({
        'tipo': 'NULL',
        'campo': 'numero_venda',
        'quantidade': null_numero,
        'linhas': df[df['numero_venda'].isna()].index.tolist()
    })
    print(f'\n❌ numero_venda: {null_numero} valores NULL')
    print(f'   Linhas: {df[df["numero_venda"].isna()].index.tolist()}')
else:
    print(f'\n✓ numero_venda: OK')

# loja_id (NOT NULL, UUID)
null_loja = df['loja_id'].isna().sum()
if null_loja > 0:
    erros.append({
        'tipo': 'NULL',
        'campo': 'loja_id',
        'quantidade': null_loja,
        'linhas': df[df['loja_id'].isna()].index.tolist()
    })
    print(f'❌ loja_id: {null_loja} valores NULL')
else:
    print(f'✓ loja_id: OK')

# data_venda (NOT NULL, DATE)
null_data = df['data_venda'].isna().sum()
if null_data > 0:
    erros.append({
        'tipo': 'NULL',
        'campo': 'data_venda',
        'quantidade': null_data,
        'linhas': df[df['data_venda'].isna()].index.tolist()
    })
    print(f'❌ data_venda: {null_data} valores NULL')
else:
    print(f'✓ data_venda: OK')

# valor_total (NOT NULL, NUMERIC)
null_valor = df['valor_total'].isna().sum()
if null_valor > 0:
    erros.append({
        'tipo': 'NULL',
        'campo': 'valor_total',
        'quantidade': null_valor,
        'linhas': df[df['valor_total'].isna()].index.tolist()
    })
    print(f'❌ valor_total: {null_valor} valores NULL')
else:
    print(f'✓ valor_total: OK')

# ============================================================================
# 2. VALIDACAO: Formato UUID
# ============================================================================
print(f'\n' + '='*80)
print('2. FORMATO UUID')
print('='*80)

uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

for col in ['cliente_id', 'loja_id', 'vendedor_id']:
    invalidos = []
    for idx, val in df[col].items():
        if pd.notna(val) and not uuid_pattern.match(str(val)):
            invalidos.append((idx, val))
    
    if len(invalidos) > 0:
        erros.append({
            'tipo': 'UUID_INVALIDO',
            'campo': col,
            'quantidade': len(invalidos),
            'exemplos': invalidos[:5]
        })
        print(f'\n❌ {col}: {len(invalidos)} UUIDs inválidos')
        for idx, val in invalidos[:5]:
            print(f'   Linha {idx}: {val}')
    else:
        nulos = df[col].isna().sum()
        print(f'\n✓ {col}: OK ({nulos} NULL)')

# ============================================================================
# 3. VALIDACAO: Valores Numéricos
# ============================================================================
print(f'\n' + '='*80)
print('3. VALORES NUMERICOS')
print('='*80)

# Converter para numérico
df['valor_total_num'] = pd.to_numeric(df['valor_total'], errors='coerce')
df['valor_entrada_num'] = pd.to_numeric(df['valor_entrada'], errors='coerce').fillna(0)

# Verificar conversão
nao_convertidos_total = df['valor_total_num'].isna().sum()
if nao_convertidos_total > 0:
    print(f'\n⚠️  valor_total: {nao_convertidos_total} valores não numéricos')
    print(f'   Exemplos: {df[df["valor_total_num"].isna()]["valor_total"].head().tolist()}')

# valor_total >= 0
negativos_total = (df['valor_total_num'] < 0).sum()
if negativos_total > 0:
    erros.append({
        'tipo': 'VALOR_NEGATIVO',
        'campo': 'valor_total',
        'quantidade': negativos_total,
        'linhas': df[df['valor_total_num'] < 0].index.tolist()
    })
    print(f'\n❌ valor_total: {negativos_total} valores NEGATIVOS')
    print(f'   Valores: {df[df["valor_total_num"] < 0]["valor_total"].tolist()}')
else:
    print(f'\n✓ valor_total: OK (todos >= 0)')

# valor_entrada >= 0
negativos_entrada = (df['valor_entrada_num'] < 0).sum()
if negativos_entrada > 0:
    erros.append({
        'tipo': 'VALOR_NEGATIVO',
        'campo': 'valor_entrada',
        'quantidade': negativos_entrada,
        'linhas': df[df['valor_entrada_num'] < 0].index.tolist()
    })
    print(f'❌ valor_entrada: {negativos_entrada} valores NEGATIVOS')
else:
    print(f'✓ valor_entrada: OK (todos >= 0)')

# valor_entrada <= valor_total (CONSTRAINT)
entrada_maior = (df['valor_entrada_num'] > df['valor_total_num']).sum()
if entrada_maior > 0:
    erros.append({
        'tipo': 'CONSTRAINT_VIOLADA',
        'campo': 'valor_entrada > valor_total',
        'quantidade': entrada_maior,
        'linhas': df[df['valor_entrada_num'] > df['valor_total_num']].index.tolist()
    })
    print(f'❌ CONSTRAINT: {entrada_maior} casos onde entrada > total')
    casos = df[df['valor_entrada_num'] > df['valor_total_num']][['numero_venda', 'valor_total', 'valor_entrada']].head(5)
    print(f'\n   Exemplos:')
    print(casos.to_string(index=False))
else:
    print(f'✓ entrada <= total: OK')

# ============================================================================
# 4. VALIDACAO: tipo_operacao
# ============================================================================
print(f'\n' + '='*80)
print('4. TIPO DE OPERACAO')
print('='*80)

valores_permitidos = ['VENDA', 'GARANTIA', 'TROCA', 'DEVOLUCAO', 'CORTESIA']
if 'tipo_operacao' in df.columns:
    valores_invalidos = df[~df['tipo_operacao'].str.upper().isin(valores_permitidos + [''])]
    if len(valores_invalidos) > 0:
        erros.append({
            'tipo': 'VALOR_INVALIDO',
            'campo': 'tipo_operacao',
            'quantidade': len(valores_invalidos),
            'valores': valores_invalidos['tipo_operacao'].unique().tolist()
        })
        print(f'\n❌ tipo_operacao: {len(valores_invalidos)} valores inválidos')
        print(f'   Valores únicos: {valores_invalidos["tipo_operacao"].unique().tolist()}')
    else:
        print(f'\n✓ tipo_operacao: OK')
        print(f'   Distribuição: {df["tipo_operacao"].value_counts().to_dict()}')

# ============================================================================
# RESUMO FINAL
# ============================================================================
print(f'\n' + '='*80)
print('RESUMO FINAL')
print('='*80)

if len(erros) == 0:
    print(f'\n✅ ARQUIVO VÁLIDO!')
    print(f'   {len(df):,} registros prontos para importação')
else:
    print(f'\n❌ ARQUIVO COM {len(erros)} PROBLEMAS:')
    print(f'\n   Registros total: {len(df):,}')
    print(f'   Erros encontrados: {len(erros)}')
    
    print(f'\n   Detalhamento:')
    for i, erro in enumerate(erros, 1):
        print(f'   {i}. {erro["tipo"]}: {erro["campo"]} - {erro["quantidade"]} casos')

# Salvar relatório
import json
with open('dados_processados/originais/vendas/VALIDACAO_OSS_RELATORIO.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_registros': len(df),
        'total_erros': len(erros),
        'erros': erros
    }, f, indent=2, ensure_ascii=False, default=str)

print(f'\n✓ Relatório salvo em: VALIDACAO_OSS_RELATORIO.json')
