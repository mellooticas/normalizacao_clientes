#!/usr/bin/env python3
"""
Análise dos padrões de IDs para entender os 5000xxx
"""

import pandas as pd
from pathlib import Path
import re

def analisar_padroes_ids():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ANÁLISE DE PADRÕES DE IDs ===")
    
    # Carrega vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # Carrega UUID consolidado
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    
    vendas_unicos = vendas_df['cliente_id_str'].unique()
    uuid_unicos = set(uuid_consolidado['id_legado_str'])
    
    # Vendas SEM UUID
    vendas_sem_uuid = [id_cliente for id_cliente in vendas_unicos if id_cliente not in uuid_unicos]
    
    print(f"Total vendas únicos: {len(vendas_unicos)}")
    print(f"Vendas SEM UUID: {len(vendas_sem_uuid)}")
    
    # Análise de padrões
    padroes = {}
    for id_cliente in vendas_sem_uuid:
        if id_cliente.startswith('5000'):
            padroes['5000xxx'] = padroes.get('5000xxx', 0) + 1
        elif id_cliente.startswith('2'):
            padroes['2xxxxxx'] = padroes.get('2xxxxxx', 0) + 1
        elif id_cliente.startswith('3'):
            padroes['3xxxxxx'] = padroes.get('3xxxxxx', 0) + 1
        elif id_cliente.startswith('4'):
            padroes['4xxxxxx'] = padroes.get('4xxxxxx', 0) + 1
        else:
            padroes['outros'] = padroes.get('outros', 0) + 1
    
    print(f"\nPadrões IDs sem UUID:")
    for padrao, count in padroes.items():
        print(f"  {padrao}: {count}")
    
    # Análise específica dos 5000xxx
    ids_5000 = [id_cliente for id_cliente in vendas_sem_uuid if id_cliente.startswith('5000')]
    
    print(f"\nIDs 5000xxx sem UUID: {len(ids_5000)}")
    
    # Verifica se esses IDs 5000xxx estão nas vendas e suas lojas
    vendas_5000 = vendas_df[vendas_df['cliente_id_str'].isin(ids_5000)]
    lojas_5000 = vendas_5000['loja_id'].value_counts()
    
    print(f"\nDistribuição por loja dos IDs 5000xxx:")
    for loja_id, count in lojas_5000.items():
        print(f"  {loja_id}: {count} vendas")
    
    # Amostra de vendas 5000xxx
    print(f"\nAmostra vendas 5000xxx:")
    amostra_5000 = vendas_5000.head(15)[['cliente_id', 'nome_cliente_temp', 'loja_id', 'data_venda']].values
    for linha in amostra_5000:
        print(f"  ID: {linha[0]}, Nome: {linha[1]}, Loja: {linha[2]}, Data: {linha[3]}")
    
    # Análise temporal - IDs 5000xxx são mais recentes?
    vendas_5000_sorted = vendas_5000.sort_values('data_venda')
    print(f"\nRange temporal IDs 5000xxx:")
    print(f"  Primeira venda: {vendas_5000_sorted['data_venda'].min()}")
    print(f"  Última venda: {vendas_5000_sorted['data_venda'].max()}")
    
    # Comparação com outros IDs
    vendas_outros = vendas_df[~vendas_df['cliente_id_str'].isin(ids_5000)]
    vendas_outros_sorted = vendas_outros.sort_values('data_venda')
    print(f"\nRange temporal outros IDs:")
    print(f"  Primeira venda: {vendas_outros_sorted['data_venda'].min()}")
    print(f"  Última venda: {vendas_outros_sorted['data_venda'].max()}")
    
    print(f"\n=== CONCLUSÃO ===")
    print(f"Os IDs 5000xxx parecem ser NOVOS CLIENTES não presentes no sistema anterior!")
    print(f"Precisamos criar UUIDs para estes {len(ids_5000)} novos clientes.")
    
    return ids_5000

if __name__ == "__main__":
    resultado = analisar_padroes_ids()