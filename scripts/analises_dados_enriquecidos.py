#!/usr/bin/env python3
"""
Análises Completas dos Dados Enriquecidos do Caixa
Foco em Performance por Loja, Análise Financeira e Operacional
"""

import pandas as pd
import glob
import os
from pathlib import Path
import json
from datetime import datetime

def carregar_dados_enriquecidos():
    """Carrega todos os dados enriquecidos"""
    print("🔄 CARREGANDO DADOS ENRIQUECIDOS...")
    print("="*50)
    
    dados = {}
    
    # Tabelas para analisar
    tabelas = [
        'vendas',
        'restante_entrada', 
        'recebimento_carne',
        'os_entregues_dia',
        'entrega_carne'
    ]
    
    for tabela in tabelas:
        print(f"\n📋 Carregando: {tabela.upper()}")
        
        # Buscar arquivos enriquecidos (excluindo consolidados)
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        
        # Filtrar apenas lojas individuais (não consolidado)
        arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
        
        dfs_tabela = []
        for arquivo in arquivos_lojas:
            df = pd.read_csv(arquivo)
            print(f"   📁 {Path(arquivo).stem}: {len(df)} registros")
            dfs_tabela.append(df)
        
        if dfs_tabela:
            dados[tabela] = pd.concat(dfs_tabela, ignore_index=True)
            print(f"   ✅ Total {tabela}: {len(dados[tabela])} registros")
        else:
            print(f"   ⚠️  Nenhum arquivo encontrado para {tabela}")
    
    return dados

def analise_performance_por_loja(dados):
    """Análise de performance por loja"""
    print("\n" + "="*60)
    print("📊 ANÁLISE DE PERFORMANCE POR LOJA")
    print("="*60)
    
    resultados = {}
    
    if 'vendas' in dados:
        df_vendas = dados['vendas']
        
        print("\n💰 VENDAS POR LOJA:")
        print("-" * 30)
        
        vendas_loja = df_vendas.groupby('loja_nome').agg({
            'valor_venda': ['count', 'sum', 'mean'],
            'entrada': 'sum',
            'nn_venda': 'nunique'
        }).round(2)
        
        vendas_loja.columns = ['Qtd_Vendas', 'Valor_Total', 'Valor_Medio', 'Entrada_Total', 'OS_Unicas']
        vendas_loja = vendas_loja.sort_values('Valor_Total', ascending=False)
        
        for loja, row in vendas_loja.iterrows():
            print(f"🏪 {loja}:")
            print(f"   💰 Valor Total: R$ {float(row['Valor_Total']):,.2f}")
            print(f"   📊 Vendas: {int(row['Qtd_Vendas']):,.0f} ({int(row['OS_Unicas']):,.0f} OS únicas)")
            print(f"   💵 Ticket Médio: R$ {float(row['Valor_Medio']):,.2f}")
            print(f"   💳 Entrada Total: R$ {float(row['Entrada_Total']):,.2f}")
            entrada_perc = (float(row['Entrada_Total'])/float(row['Valor_Total'])*100) if float(row['Valor_Total']) > 0 else 0
            print(f"   📈 % Entrada: {entrada_perc:,.1f}%")
            print()
        
        resultados['vendas_por_loja'] = vendas_loja.to_dict('index')
    
    return resultados

def analise_formas_pagamento(dados):
    """Análise detalhada das formas de pagamento"""
    print("\n" + "="*60)
    print("💳 ANÁLISE DE FORMAS DE PAGAMENTO")
    print("="*60)
    
    resultados = {}
    
    if 'vendas' in dados:
        df_vendas = dados['vendas']
        
        print("\n📊 DISTRIBUIÇÃO POR FORMA DE PAGAMENTO:")
        print("-" * 40)
        
        # Análise geral
        formas_pagto = df_vendas.groupby('forma_pagamento_normalizada').agg({
            'valor_venda': ['count', 'sum', 'mean'],
            'entrada': 'sum',
            'loja_nome': lambda x: x.nunique()
        }).round(2)
        
        formas_pagto.columns = ['Qtd', 'Valor_Total', 'Valor_Medio', 'Entrada_Total', 'Lojas']
        formas_pagto = formas_pagto.sort_values('Valor_Total', ascending=False)
        
        for forma, row in formas_pagto.iterrows():
            if pd.notna(forma):
                print(f"💳 {forma}:")
                print(f"   📊 Quantidade: {int(row['Qtd']):,.0f}")
                print(f"   💰 Valor Total: R$ {float(row['Valor_Total']):,.2f}")
                print(f"   💵 Ticket Médio: R$ {float(row['Valor_Medio']):,.2f}")
                print(f"   🏪 Lojas: {int(row['Lojas']):,.0f}")
                print()
        
        # Análise por loja
        print("\n🏪 FORMAS DE PAGAMENTO POR LOJA:")
        print("-" * 35)
        
        forma_loja = df_vendas.groupby(['loja_nome', 'forma_pagamento_normalizada']).agg({
            'valor_venda': ['count', 'sum']
        }).round(2)
        
        forma_loja.columns = ['Qtd', 'Valor']
        
        for loja in df_vendas['loja_nome'].unique():
            if pd.notna(loja):
                print(f"\n🏪 {loja}:")
                dados_loja = forma_loja.loc[loja].sort_values('Valor', ascending=False)
                for forma, row in dados_loja.head(5).iterrows():
                    if pd.notna(forma):
                        print(f"   💳 {forma}: {int(row['Qtd']):,.0f} vendas - R$ {float(row['Valor']):,.2f}")
        
        resultados['formas_pagamento'] = formas_pagto.to_dict('index')
        resultados['forma_por_loja'] = forma_loja.to_dict('index')
    
    return resultados

def analise_operacional_entregas(dados):
    """Análise operacional de entregas e carnês"""
    print("\n" + "="*60)
    print("🚚 ANÁLISE OPERACIONAL - ENTREGAS E CARNÊS")
    print("="*60)
    
    resultados = {}
    
    # Análise de OS Entregues
    if 'os_entregues_dia' in dados:
        df_entregas = dados['os_entregues_dia']
        
        print("\n📦 OS ENTREGUES POR LOJA:")
        print("-" * 25)
        
        entregas_loja = df_entregas.groupby('loja_nome').agg({
            'os': ['count', 'nunique'],
            'carne': lambda x: (x == 'Sim').sum(),
            'vendedor_nome_normalizado': 'nunique'
        })
        
        entregas_loja.columns = ['Total_Entregas', 'OS_Unicas', 'Entregas_Carne', 'Vendedores']
        entregas_loja['Perc_Carne'] = (entregas_loja['Entregas_Carne'] / entregas_loja['Total_Entregas'] * 100).round(1)
        
        for loja, row in entregas_loja.iterrows():
            if pd.notna(loja):
                print(f"🏪 {loja}:")
                print(f"   📦 Total Entregas: {int(row['Total_Entregas']):,.0f}")
                print(f"   📋 OS Únicas: {int(row['OS_Unicas']):,.0f}")
                print(f"   🥩 Entregas Carnê: {int(row['Entregas_Carne']):,.0f} ({float(row['Perc_Carne']):.1f}%)")
                print(f"   👥 Vendedores: {int(row['Vendedores']):,.0f}")
                print()
        
        resultados['entregas_por_loja'] = entregas_loja.to_dict('index')
    
    # Análise de Recebimento de Carnê
    if 'recebimento_carne' in dados:
        df_carne = dados['recebimento_carne']
        
        print("\n🥩 RECEBIMENTO DE CARNÊ:")
        print("-" * 25)
        
        carne_loja = df_carne.groupby('loja_nome').agg({
            'nn_venda': ['count', 'nunique'],
            'valor_recebido': ['sum', 'mean'],
            'vendedor_nome_normalizado': 'nunique'
        }).round(2)
        
        carne_loja.columns = ['Total_Receb', 'OS_Unicas', 'Valor_Total', 'Valor_Medio', 'Vendedores']
        
        for loja, row in carne_loja.iterrows():
            if pd.notna(loja):
                print(f"🏪 {loja}:")
                print(f"   💰 Valor Total: R$ {float(row['Valor_Total']):,.2f}")
                print(f"   📊 Recebimentos: {int(row['Total_Receb']):,.0f}")
                print(f"   💵 Valor Médio: R$ {float(row['Valor_Medio']):,.2f}")
                print(f"   👥 Vendedores: {int(row['Vendedores']):,.0f}")
                print()
        
        resultados['carne_por_loja'] = carne_loja.to_dict('index')
    
    return resultados

def analise_temporal_dados(dados):
    """Análise temporal dos dados"""
    print("\n" + "="*60)
    print("📅 ANÁLISE TEMPORAL")
    print("="*60)
    
    resultados = {}
    
    if 'vendas' in dados:
        df_vendas = dados['vendas']
        
        # Converter data_movimento para datetime
        df_vendas['data_movimento'] = pd.to_datetime(df_vendas['data_movimento'])
        df_vendas['mes_ano'] = df_vendas['data_movimento'].dt.to_period('M')
        
        print("\n📊 VENDAS POR MÊS:")
        print("-" * 20)
        
        vendas_mes = df_vendas.groupby('mes_ano').agg({
            'valor_venda': ['count', 'sum'],
            'nn_venda': 'nunique',
            'loja_nome': lambda x: x.nunique()
        }).round(2)
        
        vendas_mes.columns = ['Qtd_Vendas', 'Valor_Total', 'OS_Unicas', 'Lojas_Ativas']
        
        for mes, row in vendas_mes.iterrows():
            print(f"📅 {mes}:")
            print(f"   💰 R$ {float(row['Valor_Total']):,.2f} ({int(row['Qtd_Vendas']):,.0f} vendas)")
            print(f"   📋 {int(row['OS_Unicas']):,.0f} OS únicas")
            print(f"   🏪 {int(row['Lojas_Ativas']):,.0f} lojas ativas")
            print()
        
        # Análise por loja e mês
        print("\n🏪 EVOLUÇÃO POR LOJA:")
        print("-" * 25)
        
        vendas_loja_mes = df_vendas.groupby(['loja_nome', 'mes_ano']).agg({
            'valor_venda': 'sum'
        }).round(2)
        
        for loja in df_vendas['loja_nome'].unique():
            if pd.notna(loja):
                print(f"\n🏪 {loja}:")
                dados_loja = vendas_loja_mes.loc[loja]
                for mes, valor in dados_loja['valor_venda'].items():
                    print(f"   📅 {mes}: R$ {float(valor):,.2f}")
        
        resultados['vendas_por_mes'] = vendas_mes.to_dict('index')
        resultados['vendas_loja_mes'] = vendas_loja_mes.to_dict('index')
    
    return resultados

def gerar_relatorio_consolidado(resultados_analises):
    """Gera relatório consolidado das análises"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO CONSOLIDADO DAS ANÁLISES")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_relatorio = f"relatorio_analises_enriquecidas_{timestamp}.json"
    
    # Salvar resultados em JSON
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(resultados_analises, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    print(f"\n🎯 RESUMO EXECUTIVO:")
    print("-" * 20)
    
    if 'performance' in resultados_analises and 'vendas_por_loja' in resultados_analises['performance']:
        vendas_loja = resultados_analises['performance']['vendas_por_loja']
        
        # Top 3 lojas por faturamento
        top_lojas = sorted(vendas_loja.items(), key=lambda x: x[1]['Valor_Total'], reverse=True)[:3]
        
        print(f"🏆 TOP 3 LOJAS POR FATURAMENTO:")
        for i, (loja, dados) in enumerate(top_lojas, 1):
            print(f"   {i}º {loja}: R$ {float(dados['Valor_Total']):,.2f}")
        
        # Total geral
        total_vendas = sum(float(dados['Valor_Total']) for dados in vendas_loja.values())
        total_os = sum(int(dados['OS_Unicas']) for dados in vendas_loja.values())
        
        print(f"\n📊 TOTAIS GERAIS:")
        print(f"   💰 Faturamento Total: R$ {total_vendas:,.2f}")
        print(f"   📋 OS Únicas: {total_os:,.0f}")
        print(f"   🏪 Lojas Analisadas: {len(vendas_loja)}")

def executar_analises_completas():
    """Executa todas as análises dos dados enriquecidos"""
    print("🚀 INICIANDO ANÁLISES DOS DADOS ENRIQUECIDOS")
    print("="*60)
    
    # Carregar dados
    dados = carregar_dados_enriquecidos()
    
    if not dados:
        print("❌ Nenhum dado enriquecido encontrado!")
        return
    
    # Executar análises
    resultados_analises = {}
    
    # 1. Performance por loja
    resultados_analises['performance'] = analise_performance_por_loja(dados)
    
    # 2. Formas de pagamento
    resultados_analises['formas_pagamento'] = analise_formas_pagamento(dados)
    
    # 3. Análise operacional
    resultados_analises['operacional'] = analise_operacional_entregas(dados)
    
    # 4. Análise temporal
    resultados_analises['temporal'] = analise_temporal_dados(dados)
    
    # 5. Relatório final
    gerar_relatorio_consolidado(resultados_analises)
    
    print("\n✅ ANÁLISES CONCLUÍDAS!")
    return resultados_analises

if __name__ == "__main__":
    resultados = executar_analises_completas()