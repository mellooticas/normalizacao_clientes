#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparar arquivo final com APENAS as colunas necessárias para vendas.vendas
"""

import pandas as pd

print('PREPARANDO ARQUIVO FINAL PARA IMPORTAÇÃO')
print('='*70)

# Ler arquivo consolidado
df = pd.read_csv('1_normalizacao/dados_processados/vendas_para_importar/vendas_vixen_consolidado.csv',
                 sep=';', encoding='utf-8')

print(f'Total de vendas no arquivo consolidado: {len(df):,}')
print(f'\nColunas disponíveis ({len(df.columns)}):')
for col in df.columns:
    print(f'   • {col}')

# Remover linhas com dados obrigatórios faltando
df_limpo = df[
    df['numero_venda'].notna() &
    df['loja_id'].notna() &
    df['data_venda'].notna() &
    df['valor_total'].notna()
].copy()

print(f'\nVendas após limpeza: {len(df_limpo):,}')

# Selecionar APENAS as colunas que existem na tabela vendas.vendas
colunas_vendas = [
    'numero_venda',
    'cliente_id',
    'loja_id', 
    'vendedor_id',
    'data_venda',
    'valor_total',
    'valor_entrada',
    'nome_cliente_temp',
    'observacoes',
    'cancelado',
    'tipo_operacao'
]

# Verificar quais colunas existem
colunas_existentes = [col for col in colunas_vendas if col in df_limpo.columns]

print(f'\nColunas para exportar ({len(colunas_existentes)}):')
for col in colunas_existentes:
    print(f'   • {col}')

df_final = df_limpo[colunas_existentes].copy()

# Salvar arquivo final
arquivo_saida = '1_normalizacao/dados_processados/vendas_para_importar/vendas_vixen_final.csv'
df_final.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8')

print(f'\n✅ Arquivo salvo: vendas_vixen_final.csv')
print(f'✅ {len(df_final):,} vendas')
print(f'✅ {len(df_final.columns)} colunas')

print(f'\nPrimeiras 3 linhas (data_venda):')
print(df_final[['numero_venda', 'data_venda', 'valor_total']].head(3))

print('\n' + '='*70)
print('PRONTO PARA IMPORTAR NO SUPABASE!')
print('='*70)
