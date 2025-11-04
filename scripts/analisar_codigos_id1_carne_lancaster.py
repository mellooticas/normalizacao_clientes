#!/usr/bin/env python3
"""
Análise da coluna ID.1 do arquivo ordem_servico_pdv_carne_lancaster.csv
Extração de códigos únicos das formas de pagamento CARNE LANCASTER
"""

import pandas as pd

def analisar_codigos_id1_carne_lancaster():
    arquivo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_carne_lancaster.csv'
    
    print("=== ANÁLISE COLUNA ID.1 - CARNE LANCASTER ===\n")
    
    # Carregar dados
    print("📁 Carregando arquivo...")
    df = pd.read_csv(arquivo, encoding='utf-8-sig')
    print(f"✅ {len(df):,} registros carregados")
    print()
    
    # Analisar coluna ID.1
    print("🔍 ANÁLISE DA COLUNA ID.1:")
    
    # Valores únicos na coluna ID.1
    codigos_id1 = df['ID.1'].dropna().unique()
    print(f"Total de códigos únicos: {len(codigos_id1)}")
    print()
    
    # Contagem por código
    contagem_codigos = df['ID.1'].value_counts()
    print("📊 DISTRIBUIÇÃO DOS CÓDIGOS:")
    for codigo, qtd in contagem_codigos.items():
        if pd.notna(codigo):
            percentual = (qtd / len(df)) * 100
            print(f"  '{codigo}' -> {qtd:,} registros ({percentual:.1f}%)")
    print()
    
    # Cruzamento ID.1 x Pagamento
    print("🔗 CRUZAMENTO ID.1 x TIPO DE PAGAMENTO:")
    cruzamento = df.groupby(['ID.1', 'Pagamento']).size().reset_index(name='quantidade')
    cruzamento = cruzamento.sort_values(['ID.1', 'quantidade'], ascending=[True, False])
    
    for codigo in codigos_id1:
        if pd.notna(codigo):
            print(f"\n  📋 Código '{codigo}':")
            subset = cruzamento[cruzamento['ID.1'] == codigo]
            for _, row in subset.iterrows():
                print(f"    {row['Pagamento']:40} -> {row['quantidade']:,}")
    
    return df

if __name__ == "__main__":
    df = analisar_codigos_id1_carne_lancaster()