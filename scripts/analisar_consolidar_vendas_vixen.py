#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise e Preparação de vendas_vixen.csv para Importação
Identifica duplicidades e prepara arquivo consolidado
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Caminhos
base_dir = Path('1_normalizacao/dados_processados/vendas_para_importar')
arquivo_entrada = base_dir / 'vendas_vixen.csv'
arquivo_saida = base_dir / 'vendas_vixen_consolidado.csv'
arquivo_duplicados = base_dir / 'vendas_vixen_duplicados_detalhado.csv'

print("="*80)
print("📊 ANÁLISE DETALHADA: vendas_vixen.csv")
print("="*80)

# Ler CSV
print("\n📖 Lendo arquivo...")
df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8', low_memory=False, dtype=str)
print(f"✅ {len(df):,} linhas carregadas")

# CONVERTER VALORES: vírgula → ponto (formato brasileiro → internacional)
print("\n💰 Convertendo valores (vírgula → ponto)...")

def converter_valor(valor):
    """Converte valores do formato brasileiro (vírgula) para float"""
    if pd.isna(valor) or valor == '':
        return 0.0
    valor_str = str(valor).strip()
    # Remover pontos de milhar e substituir vírgula por ponto
    valor_str = valor_str.replace('.', '').replace(',', '.')
    try:
        return float(valor_str)
    except:
        return 0.0

df['valor_total_num'] = df['valor_total'].apply(converter_valor)
df['valor_entrada_num'] = df['valor_entrada'].apply(converter_valor)

valores_antes = (df['valor_total'].isna() | (df['valor_total'] == '')).sum()
valores_depois = (df['valor_total_num'] == 0).sum()
print(f"   Valores vazios/nulos ANTES: {valores_antes:,}")
print(f"   Valores = 0 DEPOIS: {valores_depois:,}")
print(f"   ✅ Conversão concluída!")

# CONVERTER DATAS DO FORMATO EXCEL (número serial)
print("\n📅 Convertendo datas do formato Excel...")

def converter_data_excel(valor):
    """Converte data do formato numérico do Excel ou dd/mm/yyyy para yyyy-mm-dd (PostgreSQL)"""
    if pd.isna(valor) or valor == '' or valor == 'nan':
        return None
    
    valor_str = str(valor).strip()
    
    # Se é número (serial do Excel)
    try:
        valor_num = float(valor_str)
        # Excel conta dias desde 30/12/1899
        data_base = datetime(1899, 12, 30)
        data_convertida = data_base + timedelta(days=valor_num)
        return data_convertida.strftime('%Y-%m-%d')
    except (ValueError, OverflowError):
        pass
    
    # Se é string com formato dd/mm/yyyy
    if '/' in valor_str:
        try:
            partes = valor_str.split('/')
            if len(partes) == 3:
                dia, mes, ano = partes
                # Garantir ano com 4 dígitos
                if len(ano) == 2:
                    ano = '20' + ano if int(ano) < 50 else '19' + ano
                return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
        except:
            pass
    
    # Se já está em formato yyyy-mm-dd
    if '-' in valor_str and len(valor_str) == 10:
        return valor_str
    
    return None

# Aplicar conversão
datas_antes = df['data_venda'].isna().sum()
df['data_venda'] = df['data_venda'].apply(converter_data_excel)
datas_depois = df['data_venda'].isna().sum()

print(f"   Datas nulas ANTES: {datas_antes:,}")
print(f"   Datas nulas DEPOIS: {datas_depois:,}")
if datas_antes > datas_depois:
    print(f"   ✅ {datas_antes - datas_depois:,} datas convertidas com sucesso!")
print(f"   ✅ Formato: YYYY-MM-DD (PostgreSQL)")

# Exibir primeiras linhas
print(f"\n📋 Estrutura dos dados:")
print(df.head(3).to_string())

print(f"\n🔍 ANÁLISE DE DUPLICIDADES:")
print("-"*80)

# Identificar duplicados
duplicados_mask = df.duplicated(subset=['numero_venda'], keep=False)
df_duplicados = df[duplicados_mask].copy()
df_duplicados = df_duplicados.sort_values('numero_venda')

print(f"   Total de linhas duplicadas: {len(df_duplicados):,}")
print(f"   Vendas únicas com duplicatas: {df_duplicados['numero_venda'].nunique():,}")

# Análise detalhada das duplicatas
print(f"\n📊 RAZÕES DAS DUPLICATAS:")

# Agrupar duplicados por numero_venda
grupos_duplicados = df_duplicados.groupby('numero_venda')

# Analisar padrões
print(f"\n   Analisando padrões de duplicação...")

exemplos = []
for num_venda, grupo in list(grupos_duplicados)[:10]:
    print(f"\n   📌 Venda {num_venda} ({len(grupo)} linhas):")
    
    # Verificar diferenças
    colunas_check = ['valor_total', 'valor_entrada', 'cliente_id', 'data_venda']
    for col in colunas_check:
        valores_unicos = grupo[col].nunique()
        if valores_unicos > 1:
            print(f"      • {col}: {valores_unicos} valores diferentes")
            print(f"        Valores: {grupo[col].unique()}")
    
    # Guardar exemplo
    exemplos.append({
        'numero_venda': num_venda,
        'quantidade_linhas': len(grupo),
        'valores_total_unicos': grupo['valor_total'].nunique(),
        'valores_entrada_unicos': grupo['valor_entrada'].nunique(),
        'clientes_diferentes': grupo['cliente_id'].nunique()
    })

# Criar DataFrame de exemplos
df_exemplos = pd.DataFrame(exemplos)

print(f"\n📈 ESTATÍSTICAS DAS DUPLICATAS:")
print(f"   Distribuição de linhas por venda duplicada:")
contagem = df_duplicados.groupby('numero_venda').size().value_counts().sort_index()
for n_linhas, qtd_vendas in contagem.items():
    print(f"      • {n_linhas} linhas: {qtd_vendas} vendas")

print(f"\n⚠️  PROBLEMAS IDENTIFICADOS:")

# 1. Datas nulas
datas_nulas = df['data_venda'].isna().sum()
print(f"   1. Datas de venda nulas: {datas_nulas:,}")
if datas_nulas > 0:
    print(f"      ⚠️  ATENÇÃO: {datas_nulas} vendas sem data")

# 2. Cliente #N/D - REMOVER essas linhas
clientes_nd = (df['cliente_id'] == '#N/D').sum()
print(f"   2. Cliente ID = '#N/D': {clientes_nd:,}")
if clientes_nd > 0:
    print(f"      🗑️  Essas linhas serão REMOVIDAS antes da consolidação")

# 3. Valores
valores_negativos_total = (df['valor_total_num'] < 0).sum()
valores_negativos_entrada = (df['valor_entrada_num'] < 0).sum()
valores_zero_total = (df['valor_total_num'] == 0).sum()
entrada_maior_total = (df['valor_entrada_num'] > df['valor_total_num']).sum()

print(f"   3. Valores zero em valor_total: {valores_zero_total}")
print(f"   4. Valores negativos em valor_total: {valores_negativos_total}")
print(f"   5. Valores negativos em valor_entrada: {valores_negativos_entrada}")
print(f"   6. Entrada > Total: {entrada_maior_total}")

print(f"\n💡 ESTRATÉGIA DE CONSOLIDAÇÃO:")
print("-"*80)

print("""
IMPORTANTE: As linhas duplicadas representam FORMAS DE PAGAMENTO diferentes!

Estratégia de consolidação:
1. REMOVER linhas com cliente_id = '#N/D'
2. Agrupar por (numero_venda + loja_id) = VENDA ÚNICA
3. SOMAR valor_entrada de todas as formas de pagamento
4. MANTER valor_total (é o mesmo para todas as linhas da mesma venda)
5. Consolidar outras informações (primeira linha como referência)

Exemplo:
  Venda 4026 com 4 linhas = 4 formas de pagamento diferentes
  Resultado: 1 linha com valor_entrada = soma das 4 entradas

Transformação esperada:
  11.171 linhas → 8.233 vendas únicas
  Redução: 2.938 linhas (representavam formas de pagamento adicionais)
""")

print(f"\n🔧 CONSOLIDANDO VENDAS...")

# PASSO 1: Remover linhas com cliente_id = #N/D
linhas_antes_remocao = len(df)
df = df[df['cliente_id'] != '#N/D'].copy()
linhas_removidas_nd = linhas_antes_remocao - len(df)
print(f"   🗑️  Removidas {linhas_removidas_nd} linhas com cliente_id = '#N/D'")
print(f"   📊 Linhas restantes: {len(df):,}")

# PASSO 2: Identificar duplicatas por (numero_venda + loja_id)
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
    venda['valor_entrada'] = grupo['valor_entrada_num'].sum()
    
    # Valor total é o mesmo para todas as linhas (manter o primeiro)
    venda['valor_total'] = grupo['valor_total_num'].iloc[0]
    
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

# Limpar dados para importação
print(f"\n🧹 LIMPEZA DE DADOS:")

# Remover coluna auxiliar
df_final = df_final.drop(columns=['chave_unica'], errors='ignore')

# Limpar valores
df_final['valor_entrada'] = df_final['valor_entrada_num']
df_final['valor_total'] = df_final['valor_total_num']

# Garantir que valor_entrada <= valor_total
problemas_entrada = df_final[df_final['valor_entrada'] > df_final['valor_total']]
if len(problemas_entrada) > 0:
    print(f"   ⚠️  Corrigindo {len(problemas_entrada)} vendas com entrada > total")
    df_final.loc[df_final['valor_entrada'] > df_final['valor_total'], 'valor_entrada'] = \
        df_final.loc[df_final['valor_entrada'] > df_final['valor_total'], 'valor_total']
else:
    print(f"   ✅ Todos os valores de entrada <= total")

print(f"   ✅ Limpeza concluída")

# Selecionar colunas para importação
colunas_importacao = [
    'numero_venda', 'cliente_id', 'loja_id', 'vendedor_id', 
    'data_venda', 'valor_total', 'valor_entrada', 
    'nome_cliente_temp', 'observacoes', 'cancelado',
    'tipo_operacao'
]

df_importacao = df_final[colunas_importacao].copy()

# Salvar arquivo consolidado
print(f"\n💾 SALVANDO ARQUIVOS:")
df_importacao.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8')
print(f"   ✅ Arquivo consolidado: {arquivo_saida}")
print(f"   📊 {len(df_importacao):,} vendas prontas para importar")

# Salvar detalhamento de duplicados (para auditoria)
df_duplicados.to_csv(arquivo_duplicados, index=False, sep=';', encoding='utf-8')
print(f"   ✅ Detalhamento de duplicados: {arquivo_duplicados}")

print(f"\n" + "="*80)
print("✅ ANÁLISE E CONSOLIDAÇÃO CONCLUÍDA!")
print("="*80)

print(f"\n📋 RESUMO FINAL:")
print(f"   Arquivo original: {linhas_antes_remocao:,} linhas")
print(f"   Linhas removidas (cliente #N/D): {linhas_removidas_nd}")
print(f"   Linhas com formas de pagamento: {len(df):,}")
print(f"   Vendas consolidadas: {len(df_importacao):,} vendas únicas")
print(f"   Redução: {len(df) - len(df_importacao):,} linhas (formas de pagamento extras)")
print(f"   Arquivo pronto: {arquivo_saida}")

print(f"\n🎯 PRÓXIMO PASSO:")
print(f"   Importar: vendas_vixen_consolidado.csv → vendas.vendas")
print(f"   Constraint OK: (numero_venda + loja_id) único ✅")
print(f"   Sem clientes #N/D ✅")
print(f"   Formas de pagamento somadas ✅")

print(f"\n" + "="*80)
