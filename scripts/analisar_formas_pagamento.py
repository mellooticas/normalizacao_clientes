#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise das formas de pagamento nos dados de vendas do caixa
"""

import pandas as pd
import os
from collections import Counter
import json

def analisar_formas_pagamento():
    """Analisa todas as formas de pagamento nos dados de vendas"""
    
    pasta_vendas = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_por_tipo\vendas"
    
    print("🔍 ANÁLISE DE FORMAS DE PAGAMENTO")
    print("=" * 50)
    
    # Ler arquivo consolidado
    arquivo_consolidado = os.path.join(pasta_vendas, "vendas_todas_lojas.csv")
    
    if not os.path.exists(arquivo_consolidado):
        print("❌ Arquivo consolidado não encontrado!")
        return
    
    df = pd.read_csv(arquivo_consolidado)
    
    # Limpar valores nulos e espaços
    df['forma_de_pgto'] = df['forma_de_pgto'].fillna('SEM_INFORMACAO').astype(str).str.strip()
    
    print(f"📊 Total de registros de vendas: {len(df):,}")
    print(f"🏪 Lojas: {', '.join(sorted(df['loja_arquivo'].unique()))}")
    print()
    
    # Análise geral das formas de pagamento
    formas_unicas = df['forma_de_pgto'].unique()
    print(f"💳 Formas de pagamento únicas encontradas: {len(formas_unicas)}")
    
    # Contar frequência
    contagem_formas = df['forma_de_pgto'].value_counts()
    print("\n📈 TOP 20 FORMAS DE PAGAMENTO:")
    print("-" * 40)
    for forma, count in contagem_formas.head(20).items():
        percentual = (count / len(df)) * 100
        print(f"{forma:<20} | {count:>6,} ({percentual:>5.1f}%)")
    
    # Análise por loja
    print(f"\n🏪 ANÁLISE POR LOJA:")
    print("-" * 50)
    for loja in sorted(df['loja_arquivo'].unique()):
        df_loja = df[df['loja_arquivo'] == loja]
        formas_loja = df_loja['forma_de_pgto'].nunique()
        print(f"{loja:<15} | {len(df_loja):>6,} vendas | {formas_loja:>3} formas únicas")
    
    # Identificar formas "suspeitas" (possíveis variações)
    print(f"\n🔍 FORMAS POTENCIALMENTE SIMILARES:")
    print("-" * 40)
    
    formas_lista = sorted(formas_unicas)
    similares = {}
    
    for i, forma1 in enumerate(formas_lista):
        for forma2 in formas_lista[i+1:]:
            # Verificar similaridades básicas
            if forma1.lower() == forma2.lower() and forma1 != forma2:
                if forma1 not in similares:
                    similares[forma1] = []
                similares[forma1].append(forma2)
            
            # Verificar variações de DN (Dinheiro)
            if 'DN' in [forma1, forma2] and any(x in forma1.upper() + forma2.upper() for x in ['DINH', 'CASH']):
                if 'DN' not in similares:
                    similares['DN'] = []
                if forma1 != 'DN':
                    similares['DN'].append(forma1)
                if forma2 != 'DN' and forma2 not in similares['DN']:
                    similares['DN'].append(forma2)
    
    if similares:
        for principal, variações in similares.items():
            print(f"{principal} → {', '.join(variações)}")
    else:
        print("Nenhuma variação óbvia detectada")
    
    # Salvar lista completa para análise
    relatório = {
        'total_registros': len(df),
        'total_formas_unicas': len(formas_unicas),
        'formas_por_frequencia': contagem_formas.to_dict(),
        'formas_completas': sorted(formas_unicas.tolist()),
        'analise_por_loja': {}
    }
    
    for loja in sorted(df['loja_arquivo'].unique()):
        df_loja = df[df['loja_arquivo'] == loja]
        relatório['analise_por_loja'][loja] = {
            'total_vendas': len(df_loja),
            'formas_unicas': df_loja['forma_de_pgto'].nunique(),
            'formas_lista': sorted(df_loja['forma_de_pgto'].unique().tolist()),
            'top_5_formas': df_loja['forma_de_pgto'].value_counts().head(5).to_dict()
        }
    
    # Salvar relatório
    pasta_analises = r"d:\projetos\carne_facil\carne_facil\_analises"
    os.makedirs(pasta_analises, exist_ok=True)
    
    caminho_relatorio = os.path.join(pasta_analises, "analise_formas_pagamento.json")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatório, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {caminho_relatorio}")
    
    # Exibir todas as formas únicas
    print(f"\n📋 LISTA COMPLETA DAS {len(formas_unicas)} FORMAS DE PAGAMENTO:")
    print("-" * 60)
    for i, forma in enumerate(sorted(formas_unicas), 1):
        freq = contagem_formas[forma]
        print(f"{i:2d}. {forma:<25} ({freq:,} registros)")

if __name__ == "__main__":
    analisar_formas_pagamento()