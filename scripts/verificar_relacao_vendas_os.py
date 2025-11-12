#!/usr/bin/env python3
"""
Verificar relação entre vendas e OSs
"""

import pandas as pd
import numpy as np

def verificar_relacao_vendas_os():
    print("📊 ANÁLISE DE CRUZAMENTO VENDAS <-> OSs")
    print("=" * 50)
    
    # Carregar vendas e OSs de Suzano para análise
    vendas = pd.read_csv('data/originais/cxs/finais_postgresql_prontos/vendas_suzano_final.csv')
    oss = pd.read_csv('data/originais/oss/finais_postgresql_prontos/SUZANO_postgresql_pronto.csv')
    
    # Converter nn_venda para número
    vendas['nn_venda_num'] = pd.to_numeric(vendas['nn_venda'], errors='coerce')
    
    # Converter OS Lancaster para número
    oss['os_lancaster_num'] = pd.to_numeric(oss['OS Lancaster'], errors='coerce')
    
    print(f"Vendas total: {len(vendas)}")
    print(f"Vendas range: {vendas['nn_venda_num'].min():.0f} - {vendas['nn_venda_num'].max():.0f}")
    print(f"OSs total: {len(oss)}")
    print(f"OS Lancaster range: {oss['os_lancaster_num'].min():.0f} - {oss['os_lancaster_num'].max():.0f}")
    
    # Verificar se há overlap
    vendas_set = set(vendas['nn_venda_num'].dropna().astype(int))
    os_set = set(oss['os_lancaster_num'].dropna().astype(int))
    
    overlap = vendas_set.intersection(os_set)
    print(f"\n🔗 Números em comum: {len(overlap)}")
    
    if len(overlap) > 0:
        print(f"📝 Exemplos de números em comum: {sorted(list(overlap))[:10]}")
        
        # Fazer um cruzamento de exemplo
        exemplo_num = sorted(list(overlap))[0]
        venda_exemplo = vendas[vendas['nn_venda_num'] == exemplo_num].iloc[0]
        os_exemplo = oss[oss['os_lancaster_num'] == exemplo_num].iloc[0]
        
        print(f"\n🔍 Exemplo de cruzamento (Número {exemplo_num}):")
        print(f"   VENDA:")
        print(f"      Cliente: {venda_exemplo['cliente']}")
        print(f"      Valor: R$ {venda_exemplo.get('valor_venda', 'N/A')}")
        print(f"      Data: {venda_exemplo['data_movimento']}")
        print(f"   OS:")
        print(f"      Cliente: {os_exemplo['NOME:']}")
        print(f"      Vendedor: {os_exemplo['vendedor_nome_normalizado']}")
        print(f"      Valor Total: R$ {os_exemplo.get('TOTAL', 'N/A')}")
        print(f"      Data: {os_exemplo['data_compra']}")
        
        print(f"\n✅ CONCLUSÃO: Podemos usar OS Lancaster para cruzar com vendas!")
        print(f"   - Usar 'nn_venda' (vendas) = 'OS Lancaster' (OSs)")
        print(f"   - Isso nos dará acesso ao vendedor_uuid das OSs")
        
    else:
        print("❌ Não há números em comum entre vendas e OSs")
        print("   Será necessário fazer cruzamento por cliente")

if __name__ == "__main__":
    verificar_relacao_vendas_os()