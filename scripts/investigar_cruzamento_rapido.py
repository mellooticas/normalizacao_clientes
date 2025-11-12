#!/usr/bin/env python3
"""
Investigação específica dos campos para cruzamento
"""

import pandas as pd

def investigar_cruzamento():
    print("=== INVESTIGAÇÃO ESPECÍFICA DE CRUZAMENTO ===\n")
    
    # Carregar arquivos
    arquivo_rec = 'data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/REC. CORRENTISTA.csv'
    arquivo_outros = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid.csv'
    
    print("📁 Carregando arquivos...")
    df_rec = pd.read_csv(arquivo_rec, encoding='utf-8-sig', nrows=100)  # Carregar apenas 100 linhas para análise rápida
    df_outros = pd.read_csv(arquivo_outros, encoding='utf-8-sig', nrows=100)
    
    print(f"REC. CORRENTISTA (amostra): {len(df_rec)} registros")
    print(f"OUTROS PAGAMENTOS (amostra): {len(df_outros)} registros")
    print()
    
    # Mostrar estrutura dos primeiros registros
    print("🔍 ESTRUTURA REC. CORRENTISTA (primeiros 3 registros):")
    print("Campos mais relevantes:")
    campos_relevantes = ['ID fin.', 'Nro.operação', 'ID operação', 'ID.2', 'Referência', 'Nro.doc.', 'Nr.identificação']
    
    for campo in campos_relevantes:
        if campo in df_rec.columns:
            valores = df_rec[campo].head(3).tolist()
            print(f"  {campo:15}: {valores}")
    print()
    
    print("🔍 ESTRUTURA OUTROS PAGAMENTOS (primeiros 3 registros):")
    for campo in campos_relevantes:
        if campo in df_outros.columns:
            valores = df_outros[campo].head(3).tolist()
            print(f"  {campo:15}: {valores}")
    print()
    
    # Análise da coluna Referência no REC. CORRENTISTA
    print("💡 ANÁLISE DETALHADA - COLUNA 'Referência' (REC. CORRENTISTA):")
    if 'Referência' in df_rec.columns:
        referencias = df_rec['Referência'].dropna()
        print(f"Total de referências: {len(referencias)}")
        
        for i, ref in enumerate(referencias.head(10)):
            print(f"  {i+1:2d}. {ref}")
    
    print("\nℹ️  HIPÓTESE:")
    print("REC. CORRENTISTA contém os PAGAMENTOS dos carnês")
    print("ORDEM DE SERVIÇO PDV contém as EMISSÕES dos carnês")
    print("O cruzamento deve ser feito por cliente (ID.2) ou número do documento")

if __name__ == "__main__":
    investigar_cruzamento()