#!/usr/bin/env python3
"""
Análise específica do arquivo ORDEM DE SERVIÇO PDV.csv
Foco: tipos de pagamento, estrutura e normalização
"""

import pandas as pd
import numpy as np
from collections import Counter
import json

def analisar_ordem_servico_pdv():
    arquivo_pdv = 'data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/ORDEM DE SERVIÇO PDV.csv'
    
    print("=== ANÁLISE ESPECÍFICA: ORDEM DE SERVIÇO PDV ===\n")
    
    # Carregar dados
    df = pd.read_csv(arquivo_pdv, encoding='utf-8-sig')
    
    print(f"📊 Total de registros: {len(df):,}")
    print(f"📊 Total de colunas: {len(df.columns)}")
    print()
    
    # Estrutura das colunas
    print("📋 ESTRUTURA DAS COLUNAS:")
    for i, col in enumerate(df.columns):
        print(f"{i+1:2d}. {col}")
    print()
    
    # Análise dos tipos de pagamento
    print("💳 ANÁLISE DOS TIPOS DE PAGAMENTO:")
    pagamentos = df['Pagamento'].value_counts()
    print(f"Total de tipos diferentes: {len(pagamentos)}")
    
    for tipo, qtd in pagamentos.items():
        percentual = (qtd / len(df)) * 100
        print(f"  {tipo:25} | {qtd:6,} ({percentual:5.1f}%)")
    print()
    
    # Verificar se existe CARNE LANCASTER
    carne_lancaster = df[df['Pagamento'].str.contains('CARNE LANCASTER', na=False, case=False)]
    print(f"🍖 CARNE LANCASTER encontrados: {len(carne_lancaster):,}")
    
    if len(carne_lancaster) > 0:
        print("Variações encontradas:")
        variacoes_carne = carne_lancaster['Pagamento'].value_counts()
        for var, qtd in variacoes_carne.items():
            print(f"  '{var}' -> {qtd:,}")
    print()
    
    # Análise de clientes únicos
    print("👥 ANÁLISE DE CLIENTES:")
    clientes_col_id2 = df['ID.2'].dropna().nunique()
    clientes_col_cliente = df['Cliente'].dropna().nunique()
    print(f"Clientes únicos (ID.2): {clientes_col_id2:,}")
    print(f"Clientes únicos (Cliente): {clientes_col_cliente:,}")
    print()
    
    # Análise temporal
    print("📅 ANÁLISE TEMPORAL:")
    if 'Dh.emissão' in df.columns:
        df['Dh.emissão'] = pd.to_datetime(df['Dh.emissão'], errors='coerce')
        periodo_inicio = df['Dh.emissão'].min()
        periodo_fim = df['Dh.emissão'].max()
        print(f"Período: {periodo_inicio} até {periodo_fim}")
        
        # Distribuição por ano
        df['ano'] = df['Dh.emissão'].dt.year
        anos = df['ano'].value_counts().sort_index()
        print("Distribuição por ano:")
        for ano, qtd in anos.items():
            if not pd.isna(ano):
                print(f"  {int(ano)}: {qtd:,}")
    print()
    
    # Análise de valores
    print("💰 ANÁLISE DE VALORES:")
    if 'Vl.movimento' in df.columns:
        valores = df['Vl.movimento'].dropna()
        print(f"Valor total: R$ {valores.sum():,.2f}")
        print(f"Valor médio: R$ {valores.mean():.2f}")
        print(f"Valor mediano: R$ {valores.median():.2f}")
        print(f"Valor mínimo: R$ {valores.min():.2f}")
        print(f"Valor máximo: R$ {valores.max():,.2f}")
    print()
    
    # Verificar campo de origem dos arquivos
    if 'arquivo_origem' in df.columns:
        origens = df['arquivo_origem'].value_counts()
        print("📁 ARQUIVOS DE ORIGEM:")
        print(f"Total de arquivos diferentes: {len(origens)}")
        for arquivo, qtd in origens.head(10).items():
            print(f"  {arquivo}: {qtd:,}")
        if len(origens) > 10:
            print(f"  ... e mais {len(origens)-10} arquivos")
    
    # Salvar análise detalhada
    analise = {
        'total_registros': len(df),
        'total_colunas': len(df.columns),
        'colunas': list(df.columns),
        'tipos_pagamento': dict(pagamentos),
        'carne_lancaster_encontrados': len(carne_lancaster),
        'clientes_unicos_id2': clientes_col_id2,
        'clientes_unicos_nome': clientes_col_cliente,
        'valor_total': float(df['Vl.movimento'].sum()) if 'Vl.movimento' in df.columns else 0,
        'periodo_inicio': str(periodo_inicio) if 'Dh.emissão' in df.columns else None,
        'periodo_fim': str(periodo_fim) if 'Dh.emissão' in df.columns else None
    }
    
    with open('analise_ordem_servico_pdv.json', 'w', encoding='utf-8') as f:
        json.dump(analise, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Análise salva em: analise_ordem_servico_pdv.json")
    
    return df

if __name__ == "__main__":
    df = analisar_ordem_servico_pdv()