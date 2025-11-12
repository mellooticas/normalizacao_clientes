#!/usr/bin/env python3
"""
Script para analisar compatibilidade entre client_id OSS e vendas existentes
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    print("=== ANÁLISE DE COMPATIBILIDADE CLIENT_ID ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar vendas existentes
    vendas_file = "data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    print(f"\n1. Carregando vendas de: {vendas_file}")
    vendas_df = pd.read_csv(vendas_file, dtype=str, low_memory=False)
    print(f"  - {len(vendas_df)} vendas carregadas")
    
    # Carregar itens OSS
    itens_files = list(Path("data/processados").glob("OSS_ITENS_VENDAS_COMPLETO_*.csv"))
    itens_file = sorted(itens_files)[-1]
    print(f"\n2. Carregando itens OSS de: {itens_file}")
    itens_df = pd.read_csv(itens_file, dtype=str, low_memory=False)
    print(f"  - {len(itens_df)} itens carregados")
    
    # Analisar client_id nas vendas
    print(f"\n=== ANÁLISE VENDAS EXISTENTES ===")
    vendas_client_ids = set(vendas_df['cliente_id'].dropna().unique())
    print(f"Total de client_ids únicos nas vendas: {len(vendas_client_ids)}")
    print(f"Exemplos de client_ids vendas:")
    for i, client_id in enumerate(list(vendas_client_ids)[:5]):
        print(f"  {i+1}. {client_id}")
    
    # Analisar client_id nos itens OSS
    print(f"\n=== ANÁLISE ITENS OSS ===")
    oss_client_ids = set(itens_df['cliente_id'].dropna().unique())
    print(f"Total de client_ids únicos nos itens OSS: {len(oss_client_ids)}")
    print(f"Exemplos de client_ids OSS:")
    for i, client_id in enumerate(list(oss_client_ids)[:5]):
        print(f"  {i+1}. {client_id}")
    
    # Verificar source dos client_ids OSS
    print(f"\n=== ANÁLISE SOURCE OSS ===")
    sources_count = itens_df['cliente_source'].value_counts()
    print("Distribuição por source:")
    for source, count in sources_count.items():
        print(f"  {source}: {count} itens")
    
    # Buscar interseção
    print(f"\n=== ANÁLISE DE COMPATIBILIDADE ===")
    intersecao = vendas_client_ids.intersection(oss_client_ids)
    print(f"Client_IDs em comum: {len(intersecao)}")
    
    if intersecao:
        print("Client_IDs compatíveis encontrados:")
        for client_id in list(intersecao)[:10]:
            print(f"  - {client_id}")
    
    # Analisar por loja
    print(f"\n=== ANÁLISE POR LOJA ===")
    print("Distribuição OSS por loja:")
    oss_por_loja = itens_df.groupby(['loja_nome', 'cliente_source'])['cliente_id'].nunique()
    for (loja, source), count in oss_por_loja.items():
        print(f"  {loja} ({source}): {count} clientes únicos")
    
    # Verificar se podemos mapear por numero_venda/numero_os
    print(f"\n=== ANÁLISE MAPEAMENTO POR NÚMERO ===")
    
    # Verificar se há números de venda similares
    vendas_numeros = set()
    for num in vendas_df['numero_venda'].dropna():
        try:
            vendas_numeros.add(float(num))
        except:
            pass
    
    print(f"Range de números de venda: {min(vendas_numeros) if vendas_numeros else 'N/A'} - {max(vendas_numeros) if vendas_numeros else 'N/A'}")
    
    # Verificar números OSS
    oss_numeros = set()
    for num in itens_df['numero_os'].dropna():
        try:
            if str(num).replace('.0', '').isdigit():
                oss_numeros.add(float(str(num).replace('.0', '')))
        except:
            pass
    
    print(f"Range de números OSS: {min(oss_numeros) if oss_numeros else 'N/A'} - {max(oss_numeros) if oss_numeros else 'N/A'}")
    
    # Buscar números em comum
    numeros_comum = vendas_numeros.intersection(oss_numeros)
    print(f"Números em comum: {len(numeros_comum)}")
    
    if numeros_comum:
        print("Exemplos de números compatíveis:")
        for num in list(numeros_comum)[:10]:
            print(f"  - {num}")
    
    # Verificar se é questão de format do client_id
    print(f"\n=== ANÁLISE FORMATO CLIENT_ID ===")
    
    # Amostras para análise de formato
    print("Formato vendas (primeiros 3):")
    for client_id in list(vendas_client_ids)[:3]:
        print(f"  {client_id} (len: {len(client_id)})")
    
    print("Formato OSS (primeiros 3):")
    for client_id in list(oss_client_ids)[:3]:
        print(f"  {client_id} (len: {len(client_id)})")
    
    # Verificar se client_id OSS é numérico vs UUID vendas
    oss_numericos = [cid for cid in oss_client_ids if cid.isdigit()]
    vendas_uuid = [cid for cid in vendas_client_ids if len(cid) == 36 and '-' in cid]
    
    print(f"\nOSS client_ids numéricos: {len(oss_numericos)}")
    print(f"Vendas client_ids UUID: {len(vendas_uuid)}")
    
    print(f"\n=== CONCLUSÃO ===")
    if len(intersecao) > 0:
        print("✅ Há compatibilidade direta entre alguns client_ids")
    elif len(numeros_comum) > 0:
        print("⚠️  Não há compatibilidade direta, mas há números de OS em comum")
        print("   Recomendação: Mapear por numero_venda/numero_os")
    else:
        print("❌ Não há compatibilidade direta")
        print("   Os dados OSS usam IDs diferentes das vendas existentes")
        print("   Recomendação: Criar vendas separadas para itens OSS")
    
    print(f"\nFim: {datetime.now()}")

if __name__ == "__main__":
    main()