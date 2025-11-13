#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar arquivo final de vendas para importação
Remove apenas linhas com campos obrigatórios faltando
Mantém vendas com valor_entrada = 0 (pagamento posterior)
"""

import pandas as pd

df = pd.read_csv('1_normalizacao/dados_processados/vendas_para_importar/vendas_vixen_consolidado.csv', 
                 sep=';', encoding='utf-8')

print('LIMPEZA FINAL - Removendo apenas dados OBRIGATORIOS faltando')
print('='*70)

total_antes = len(df)
print(f'Total inicial: {total_antes:,} vendas\n')

print('CAMPOS OBRIGATORIOS (NOT NULL no banco):')
print(f'   • numero_venda nulo: {df["numero_venda"].isna().sum()}')
print(f'   • loja_id nulo: {df["loja_id"].isna().sum()}')
print(f'   • data_venda nula: {df["data_venda"].isna().sum()}')
print(f'   • valor_total nulo: {df["valor_total"].isna().sum()}')

print(f'\nCAMPOS OPCIONAIS (podem ser NULL):')
print(f'   • cliente_id nulo: {df["cliente_id"].isna().sum():,}')
print(f'   • vendedor_id nulo: {df["vendedor_id"].isna().sum():,}')
entrada_zero = (df["valor_entrada"] == 0).sum()
print(f'   • valor_entrada = 0: {entrada_zero:,} (valido - pagamento posterior)')

# Remover APENAS linhas com campos obrigatorios nulos
df_limpo = df[
    df['numero_venda'].notna() &
    df['loja_id'].notna() &
    df['data_venda'].notna() &
    df['valor_total'].notna()
].copy()

total_depois = len(df_limpo)
removidas = total_antes - total_depois

print(f'\n' + '='*70)
print(f'RESULTADO:')
print(f'   Removidas: {removidas:,} vendas (faltando dados obrigatorios)')
print(f'   Mantidas: {total_depois:,} vendas')

# Validações finais
duplicatas = df_limpo.duplicated(subset=["numero_venda", "loja_id"]).sum()
entrada_zero_final = (df_limpo["valor_entrada"] == 0).sum()

print(f'\nVALIDACOES FINAIS:')
print(f'   Duplicatas: {duplicatas}')
print(f'   Todos os campos obrigatorios preenchidos')
print(f'   Vendas com entrada R$ 0,00: {entrada_zero_final:,} (mantidas)')

# Salvar
arquivo_final = '1_normalizacao/dados_processados/vendas_para_importar/vendas_vixen_final.csv'
df_limpo.to_csv(arquivo_final, index=False, sep=';', encoding='utf-8')

print(f'\nArquivo salvo: vendas_vixen_final.csv')
print(f'{total_depois:,} vendas prontas para importar no Supabase!')
print('='*70)
