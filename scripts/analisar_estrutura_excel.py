"""
Análise da estrutura dos arquivos Excel originais
Para entender como unificar todos os arquivos
"""

import pandas as pd
from pathlib import Path

# Analisar arquivo de exemplo (Mauá - Janeiro 2024)
arquivo = Path('dados_processados/originais/cxs/planilhas_originais/maua/jan_24.xlsx')

print('=' * 80)
print('ANÁLISE DE ARQUIVO EXCEL - MAUA - JANEIRO 2024')
print('=' * 80)

# Ler arquivo Excel
excel_file = pd.ExcelFile(arquivo)

print(f'\n📋 ABAS DISPONÍVEIS ({len(excel_file.sheet_names)}):')
for i, aba in enumerate(excel_file.sheet_names, 1):
    print(f'   {i}. {aba}')

# Analisar ABA RESUMO_CX
print(f'\n{"=" * 80}')
print('ABA: resumo_cx')
print('=' * 80)

df_resumo = pd.read_excel(arquivo, sheet_name='resumo_cx', nrows=10)
print(f'\n📊 Primeiras 10 linhas')
print(f'📋 Colunas ({len(df_resumo.columns)}):')
for col in df_resumo.columns:
    print(f'   - {col}')

print(f'\n📄 Amostra de dados:')
print(df_resumo.head(3))

# Analisar ABA DIA (exemplo: 01)
print(f'\n{"=" * 80}')
print('ABA: 01 (DIA 1)')
print('=' * 80)

df_dia = pd.read_excel(arquivo, sheet_name='01', nrows=10)
print(f'\n📊 Primeiras 10 linhas')
print(f'📋 Colunas ({len(df_dia.columns)}):')
for col in df_dia.columns:
    print(f'   - {col}')

print(f'\n📄 Amostra de dados:')
print(df_dia.head(3))

# Analisar ABA BASE
print(f'\n{"=" * 80}')
print('ABA: base')
print('=' * 80)

df_base = pd.read_excel(arquivo, sheet_name='base')
print(f'\n📊 Total de registros: {len(df_base)}')
print(f'📋 Colunas ({len(df_base.columns)}):')
for col in df_base.columns:
    print(f'   - {col}')

print(f'\n📄 Primeiras 5 linhas:')
print(df_base.head(5))

print(f'\n📊 ESTATÍSTICAS DA ABA BASE:')
print(f'   - Total registros: {len(df_base)}')
print(f'   - Total colunas: {len(df_base.columns)}')

# Verificar valores únicos em algumas colunas chave
if 'Nº Venda' in df_base.columns or 'OS' in df_base.columns:
    col_venda = 'Nº Venda' if 'Nº Venda' in df_base.columns else 'OS'
    vendas_unicas = df_base[col_venda].nunique()
    print(f'   - Vendas únicas: {vendas_unicas}')
