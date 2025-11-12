#!/usr/bin/env python3
"""
Análises Simplificadas dos Dados Enriquecidos - Versão Robusta
Foco em análises básicas que funcionem com dados imperfeitos
"""

import pandas as pd
import glob
import numpy as np
from pathlib import Path

def carregar_e_limpar_vendas():
    """Carrega e limpa dados de vendas de forma robusta"""
    print("🔄 CARREGANDO E LIMPANDO DADOS DE VENDAS...")
    print("="*50)
    
    # Buscar arquivos de vendas enriquecidos
    caminho = "data/originais/cxs/extraidos_corrigidos/vendas/*_enriquecido_completo.csv"
    arquivos = glob.glob(caminho)
    
    # Filtrar apenas lojas individuais
    arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
    
    dfs_vendas = []
    
    for arquivo in arquivos_lojas:
        print(f"📁 Processando: {Path(arquivo).name}")
        
        try:
            df = pd.read_csv(arquivo)
            
            # Limpeza robusta dos dados
            df['valor_venda'] = pd.to_numeric(df['valor_venda'], errors='coerce')
            df['entrada'] = pd.to_numeric(df['entrada'], errors='coerce')
            df['nn_venda'] = pd.to_numeric(df['nn_venda'], errors='coerce')
            
            # Filtrar apenas registros válidos
            df_limpo = df[
                (df['valor_venda'].notna()) & 
                (df['valor_venda'] >= 0) &
                (df['nn_venda'].notna()) &
                (df['loja_nome'].notna())
            ].copy()
            
            # Tratar entrada nula como 0
            df_limpo['entrada'] = df_limpo['entrada'].fillna(0)
            
            print(f"   ✅ {len(df)} → {len(df_limpo)} registros válidos")
            
            if len(df_limpo) > 0:
                dfs_vendas.append(df_limpo)
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {arquivo}: {e}")
    
    if dfs_vendas:
        df_total = pd.concat(dfs_vendas, ignore_index=True)
        print(f"\n✅ Total de vendas limpas: {len(df_total)} registros")
        return df_total
    else:
        print("\n❌ Nenhum dado válido encontrado")
        return None

def analise_vendas_por_loja(df_vendas):
    """Análise simplificada de vendas por loja"""
    print("\n" + "="*60)
    print("📊 ANÁLISE DE VENDAS POR LOJA")
    print("="*60)
    
    # Agrupar por loja
    vendas_loja = df_vendas.groupby('loja_nome').agg({
        'valor_venda': ['count', 'sum', 'mean'],
        'entrada': 'sum',
        'nn_venda': 'nunique'
    }).round(2)
    
    vendas_loja.columns = ['Qtd_Vendas', 'Valor_Total', 'Ticket_Medio', 'Entrada_Total', 'OS_Unicas']
    vendas_loja = vendas_loja.sort_values('Valor_Total', ascending=False)
    
    print("\n💰 RANKING DE FATURAMENTO:")
    print("-" * 30)
    
    for i, (loja, row) in enumerate(vendas_loja.iterrows(), 1):
        valor_total = row['Valor_Total']
        qtd_vendas = int(row['Qtd_Vendas'])
        os_unicas = int(row['OS_Unicas'])
        ticket_medio = row['Ticket_Medio']
        entrada_total = row['Entrada_Total']
        
        # Calcular % entrada de forma segura
        perc_entrada = (entrada_total / valor_total * 100) if valor_total > 0 else 0
        
        print(f"{i}º 🏪 {loja}:")
        print(f"   💰 Faturamento: R$ {valor_total:,.2f}")
        print(f"   📊 Vendas: {qtd_vendas:,} ({os_unicas:,} OS únicas)")
        print(f"   💵 Ticket Médio: R$ {ticket_medio:,.2f}")
        print(f"   💳 Entrada: R$ {entrada_total:,.2f} ({perc_entrada:.1f}%)")
        print()
    
    # Totais gerais
    total_faturamento = vendas_loja['Valor_Total'].sum()
    total_vendas = vendas_loja['Qtd_Vendas'].sum()
    total_os = vendas_loja['OS_Unicas'].sum()
    
    print(f"🎯 TOTAIS CONSOLIDADOS:")
    print(f"   💰 Faturamento Total: R$ {total_faturamento:,.2f}")
    print(f"   📊 Total Vendas: {int(total_vendas):,}")
    print(f"   📋 Total OS Únicas: {int(total_os):,}")
    print(f"   🏪 Lojas Ativas: {len(vendas_loja)}")
    
    return vendas_loja

def analise_formas_pagamento_simples(df_vendas):
    """Análise simplificada de formas de pagamento"""
    print("\n" + "="*60)
    print("💳 ANÁLISE DE FORMAS DE PAGAMENTO")
    print("="*60)
    
    # Filtrar apenas registros com forma de pagamento válida
    df_com_forma = df_vendas[df_vendas['forma_pagamento_normalizada'].notna()].copy()
    
    if len(df_com_forma) == 0:
        print("❌ Nenhum registro com forma de pagamento encontrado")
        return None
    
    formas_pagto = df_com_forma.groupby('forma_pagamento_normalizada').agg({
        'valor_venda': ['count', 'sum', 'mean']
    }).round(2)
    
    formas_pagto.columns = ['Quantidade', 'Valor_Total', 'Valor_Medio']
    formas_pagto = formas_pagto.sort_values('Valor_Total', ascending=False)
    
    print(f"\n📊 RANKING POR FORMA DE PAGAMENTO:")
    print("-" * 35)
    
    for forma, row in formas_pagto.iterrows():
        quantidade = int(row['Quantidade'])
        valor_total = row['Valor_Total']
        valor_medio = row['Valor_Medio']
        
        print(f"💳 {forma}:")
        print(f"   📊 Quantidade: {quantidade:,} vendas")
        print(f"   💰 Valor Total: R$ {valor_total:,.2f}")
        print(f"   💵 Valor Médio: R$ {valor_medio:,.2f}")
        print()
    
    return formas_pagto

def carregar_os_entregues():
    """Carrega dados de OS entregues de forma robusta"""
    print("\n🔄 CARREGANDO DADOS DE ENTREGAS...")
    print("-" * 30)
    
    caminho = "data/originais/cxs/extraidos_corrigidos/os_entregues_dia/*_enriquecido_completo.csv"
    arquivos = glob.glob(caminho)
    arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
    
    dfs_entregas = []
    
    for arquivo in arquivos_lojas:
        try:
            df = pd.read_csv(arquivo)
            
            # Limpeza básica
            df['os'] = pd.to_numeric(df['os'], errors='coerce')
            df_limpo = df[
                (df['os'].notna()) &
                (df['loja_nome'].notna())
            ].copy()
            
            print(f"📁 {Path(arquivo).name}: {len(df_limpo)} registros")
            
            if len(df_limpo) > 0:
                dfs_entregas.append(df_limpo)
                
        except Exception as e:
            print(f"❌ Erro: {arquivo} - {e}")
    
    if dfs_entregas:
        df_total = pd.concat(dfs_entregas, ignore_index=True)
        print(f"✅ Total entregas: {len(df_total)} registros")
        return df_total
    
    return None

def analise_entregas_por_loja(df_entregas):
    """Análise de entregas por loja"""
    print("\n" + "="*60)
    print("🚚 ANÁLISE DE ENTREGAS POR LOJA")
    print("="*60)
    
    if df_entregas is None:
        print("❌ Nenhum dado de entrega disponível")
        return None
    
    entregas_loja = df_entregas.groupby('loja_nome').agg({
        'os': ['count', 'nunique'],
        'carne': lambda x: (x.str.upper() == 'SIM').sum() if x.notna().any() else 0
    })
    
    entregas_loja.columns = ['Total_Entregas', 'OS_Unicas', 'Entregas_Carne']
    entregas_loja['Perc_Carne'] = (entregas_loja['Entregas_Carne'] / entregas_loja['Total_Entregas'] * 100).round(1)
    entregas_loja = entregas_loja.sort_values('Total_Entregas', ascending=False)
    
    print(f"\n📦 RANKING DE ENTREGAS:")
    print("-" * 25)
    
    for loja, row in entregas_loja.iterrows():
        total_entregas = int(row['Total_Entregas'])
        os_unicas = int(row['OS_Unicas'])
        entregas_carne = int(row['Entregas_Carne'])
        perc_carne = row['Perc_Carne']
        
        print(f"🏪 {loja}:")
        print(f"   📦 Total Entregas: {total_entregas:,}")
        print(f"   📋 OS Únicas: {os_unicas:,}")
        print(f"   🥩 Entregas Carnê: {entregas_carne:,} ({perc_carne:.1f}%)")
        print()
    
    return entregas_loja

def executar_analises_robustas():
    """Executa análises robustas dos dados enriquecidos"""
    print("🚀 ANÁLISES ROBUSTAS DOS DADOS ENRIQUECIDOS")
    print("="*60)
    
    # 1. Análise de Vendas
    df_vendas = carregar_e_limpar_vendas()
    if df_vendas is not None:
        vendas_loja = analise_vendas_por_loja(df_vendas)
        formas_pagto = analise_formas_pagamento_simples(df_vendas)
    
    # 2. Análise de Entregas
    df_entregas = carregar_os_entregues()
    if df_entregas is not None:
        entregas_loja = analise_entregas_por_loja(df_entregas)
    
    print("\n✅ ANÁLISES CONCLUÍDAS!")
    print("🎯 Dados analisados com filtros robustos para tratar inconsistências")

if __name__ == "__main__":
    executar_analises_robustas()