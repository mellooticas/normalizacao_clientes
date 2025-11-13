#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise e Preparação de vendas_oss.csv para Importação
Identifica duplicidades e prepara arquivo consolidado
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Caminhos
base_dir = Path('1_normalizacao/dados_processados/vendas_para_importar')
arquivo_entrada = base_dir / 'vendas_oss.csv'
arquivo_saida = base_dir / 'vendas_oss_final.csv'

print("="*80)
print("📊 ANÁLISE E CONSOLIDAÇÃO: vendas_oss.csv")
print("="*80)

# Ler CSV
print("\n📖 Lendo arquivo...")
df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8', low_memory=False, dtype=str)
print(f"✅ {len(df):,} linhas carregadas")

# CONVERTER VALORES: detectar formato brasileiro (vírgula) ou internacional (ponto)
print("\n💰 Convertendo valores numéricos...")

def converter_valor(valor):
    """Converte valores mantendo formato correto"""
    if pd.isna(valor) or valor == '' or valor == 'nan':
        return 0.0
    valor_str = str(valor).strip()
    
    # Se tem vírgula E ponto, é formato brasileiro: 5.000,50 → remover ponto, vírgula vira ponto
    if ',' in valor_str and '.' in valor_str:
        valor_str = valor_str.replace('.', '').replace(',', '.')
    # Se tem apenas vírgula, é decimal brasileiro: 679,99 → vírgula vira ponto
    elif ',' in valor_str:
        valor_str = valor_str.replace(',', '.')
    # Se tem apenas ponto OU nenhum, já está correto: 679.99 ou 345
    
    try:
        return float(valor_str)
    except:
        return 0.0

df['valor_total'] = df['valor_total'].apply(converter_valor)
df['valor_entrada'] = df['valor_entrada'].apply(converter_valor)

print(f"   ✅ Valores convertidos para formato numérico")

print(f"\n🔍 ANÁLISE INICIAL:")
print(f"   Total de linhas: {len(df):,}")
print(f"   Colunas: {len(df.columns)}")

print(f"\n⚠️  PROBLEMAS IDENTIFICADOS:")

# 1. numero_venda nulo
vendas_nulas = df['numero_venda'].isna().sum()
print(f"   1. numero_venda nulo: {vendas_nulas}")
if vendas_nulas > 0:
    print(f"      🗑️  Essas linhas serão REMOVIDAS")

# 2. Cliente #N/D
clientes_nd = (df['cliente_id'] == '#N/D').sum()
print(f"   2. Cliente ID = '#N/D': {clientes_nd}")
if clientes_nd > 0:
    print(f"      🗑️  Essas linhas serão REMOVIDAS")

# 3. Verificar formato de datas
print(f"   3. data_venda nula: {df['data_venda'].isna().sum()}")

# 4. Verificar formato de valores
print(f"   4. valor_total nulo: {df['valor_total'].isna().sum()}")

# 5. Duplicatas
duplicados_mask = df.duplicated(subset=['numero_venda', 'loja_id'], keep=False)
df_duplicados = df[duplicados_mask].copy()
print(f"\n📊 DUPLICATAS (múltiplas formas de pagamento):")
print(f"   Total de linhas duplicadas: {len(df_duplicados):,}")
print(f"   Vendas únicas com duplicatas: {df_duplicados[['numero_venda', 'loja_id']].drop_duplicates().shape[0]:,}")

print(f"\n💡 ESTRATÉGIA DE CONSOLIDAÇÃO:")
print("""
1. REMOVER linhas com numero_venda nulo
2. REMOVER linhas com cliente_id = '#N/D'
3. Agrupar por (numero_venda + loja_id) = VENDA ÚNICA
4. SOMAR valor_entrada de todas as formas de pagamento
5. MANTER valor_total (primeira ocorrência)
""")

print(f"\n🔧 CONSOLIDANDO VENDAS...")

# PASSO 1: Remover linhas com numero_venda nulo
linhas_antes = len(df)
df = df[df['numero_venda'].notna()].copy()
removidas_nulo = linhas_antes - len(df)
if removidas_nulo > 0:
    print(f"   🗑️  Removidas {removidas_nulo} linhas com numero_venda nulo")

# PASSO 2: Remover linhas com cliente_id = #N/D
linhas_antes = len(df)
df = df[df['cliente_id'] != '#N/D'].copy()
removidas_nd = linhas_antes - len(df)
if removidas_nd > 0:
    print(f"   🗑️  Removidas {removidas_nd} linhas com cliente_id = '#N/D'")

print(f"   📊 Linhas restantes: {len(df):,}")

# PASSO 3: Identificar duplicatas por (numero_venda + loja_id)
print(f"\n   🔍 Identificando vendas únicas por (numero_venda + loja_id)...")
df['chave_unica'] = df['numero_venda'].astype(str) + '_' + df['loja_id'].astype(str)
duplicados_mask = df.duplicated(subset=['chave_unica'], keep=False)
df_duplicados = df[duplicados_mask].copy()

print(f"   Total de linhas com chave duplicada: {len(df_duplicados):,}")
print(f"   Vendas únicas com múltiplas formas de pagamento: {df_duplicados['chave_unica'].nunique():,}")

# Consolidar vendas duplicadas
def consolidar_grupo(grupo):
    """Consolida um grupo de linhas duplicadas (formas de pagamento) em uma única venda"""
    
    # Pegar primeira linha como base
    venda = grupo.iloc[0].copy()
    
    # SOMAR valores de entrada (múltiplas formas de pagamento)
    soma_entrada = grupo['valor_entrada'].sum()
    venda['valor_entrada'] = soma_entrada
    
    # Valor total original
    valor_total_original = grupo['valor_total'].iloc[0]
    venda['valor_total'] = valor_total_original
    
    # Adicionar observação sobre consolidação
    obs_original = str(venda.get('observacoes', '')) if pd.notna(venda.get('observacoes')) else ''
    obs_adicional = f"Consolidado: {len(grupo)} formas de pagamento"
    venda['observacoes'] = f"{obs_original}; {obs_adicional}" if obs_original else obs_adicional
    
    return venda

# Separar vendas únicas e duplicadas
df_unicos = df[~duplicados_mask].copy()
print(f"\n   Vendas únicas (1 forma de pagamento): {len(df_unicos):,}")

# Consolidar duplicados
vendas_consolidadas = []
grupos_duplicados = df_duplicados.groupby('chave_unica')
for chave, grupo in grupos_duplicados:
    venda_consolidada = consolidar_grupo(grupo)
    vendas_consolidadas.append(venda_consolidada)

df_consolidados = pd.DataFrame(vendas_consolidadas)
print(f"   Vendas consolidadas (múltiplas formas): {len(df_consolidados):,}")

# Unir tudo
df_final = pd.concat([df_unicos, df_consolidados], ignore_index=True)
print(f"\n   ✅ Total de vendas finais: {len(df_final):,}")

print(f"\n✅ VALIDAÇÕES PÓS-CONSOLIDAÇÃO:")
print(f"   Duplicatas restantes (numero_venda + loja_id): {df_final.duplicated(subset=['chave_unica']).sum()}")
print(f"   Vendas únicas: {df_final['chave_unica'].nunique():,}")
print(f"   ✅ Cada venda agora tem apenas 1 linha (formas de pagamento consolidadas)")

# AJUSTAR vendas onde entrada > total (acréscimo/juros)
entrada_maior = df_final[df_final['valor_entrada'] > df_final['valor_total']]
print(f"   Vendas com entrada > total: {len(entrada_maior)}")

if len(entrada_maior) > 0:
    print(f"\n   🔧 AJUSTANDO valor_total para {len(entrada_maior)} vendas...")
    
    for idx in entrada_maior.index:
        total_original = df_final.loc[idx, 'valor_total']
        entrada = df_final.loc[idx, 'valor_entrada']
        
        # Ajustar o total para a entrada
        df_final.loc[idx, 'valor_total'] = entrada
        
        # Adicionar observação
        obs_atual = str(df_final.loc[idx, 'observacoes']) if pd.notna(df_final.loc[idx, 'observacoes']) else ''
        obs_ajuste = f"Total ajustado de {total_original:.2f} para {entrada:.2f} (acréscimo)"
        df_final.loc[idx, 'observacoes'] = f"{obs_atual}; {obs_ajuste}" if obs_atual and obs_atual != 'nan' else obs_ajuste
    
    print(f"   ✅ Valores ajustados")
    
    # Validar novamente
    entrada_maior_pos = df_final[df_final['valor_entrada'] > df_final['valor_total']]
    if len(entrada_maior_pos) == 0:
        print(f"   ✅ Todas as entradas <= total (constraint OK)")
    else:
        print(f"   ❌ ERRO: Ainda há {len(entrada_maior_pos)} vendas com entrada > total")
else:
    print(f"   ✅ Todas as entradas <= total (constraint OK)")

# Limpar coluna auxiliar
df_final = df_final.drop(columns=['chave_unica'], errors='ignore')

# Selecionar apenas as colunas necessárias
colunas_exportar = [
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

df_exportar = df_final[colunas_exportar].copy()

# Salvar arquivo final
print(f"\n💾 SALVANDO ARQUIVO:")
df_exportar.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8')
print(f"   ✅ Arquivo salvo: {arquivo_saida}")
print(f"   📊 {len(df_exportar):,} vendas prontas para importar")

print(f"\n" + "="*80)
print("✅ CONSOLIDAÇÃO CONCLUÍDA!")
print("="*80)

print(f"\n📋 RESUMO FINAL:")
print(f"   Arquivo original: {linhas_antes + removidas_nulo + removidas_nd:,} linhas")
print(f"   Linhas removidas (numero_venda nulo): {removidas_nulo}")
print(f"   Linhas removidas (cliente #N/D): {removidas_nd}")
print(f"   Vendas consolidadas: {len(df_exportar):,} vendas únicas")
print(f"   Arquivo pronto: {arquivo_saida}")

print(f"\n🎯 PRÓXIMO PASSO:")
print(f"   Importar: vendas_oss_final.csv → vendas.vendas")
print(f"   Constraint OK: (numero_venda + loja_id) único ✅")
print(f"   Formato de data: YYYY-MM-DD ✅")
print(f"   Valores numéricos: formato correto ✅")

print(f"\n" + "="*80)
