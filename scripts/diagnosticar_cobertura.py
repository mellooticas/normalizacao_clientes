#!/usr/bin/env python3
"""
Diagnóstico: Por que a abordagem híbrida não chegou a 100%?
"""

import pandas as pd
from pathlib import Path

def diagnosticar_cobertura():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== DIAGNÓSTICO DE COBERTURA ===")
    
    # 1. Análise OSS original
    arquivos_oss = [
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_maua_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_perus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_rio_pequeno_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_sao_mateus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano2_clientes_ids.csv"
    ]
    
    todos_oss = []
    for arquivo in arquivos_oss:
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            todos_oss.append(df)
    
    oss_df = pd.concat(todos_oss, ignore_index=True)
    oss_df['cliente_id_str'] = oss_df['cliente_id'].astype(str).str.replace('.0', '')
    
    print(f"OSS únicos: {len(oss_df['cliente_id_str'].unique())}")
    
    # 2. Análise vendas 
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    print(f"Vendas únicos: {len(vendas_df['cliente_id_str'].unique())}")
    
    # 3. Overlap entre OSS e vendas
    oss_unicos = set(oss_df['cliente_id_str'].unique())
    vendas_unicos = set(vendas_df['cliente_id_str'].unique())
    
    overlap = oss_unicos & vendas_unicos
    so_oss = oss_unicos - vendas_unicos  
    so_vendas = vendas_unicos - oss_unicos
    
    print(f"\nOverlap OSS x Vendas:")
    print(f"  Comuns: {len(overlap)}")
    print(f"  Só OSS: {len(so_oss)}")
    print(f"  Só Vendas: {len(so_vendas)}")
    
    # 4. Análise lookup
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    lookup_unicos = set(lookup_df['id_cliente'].astype(str))
    
    print(f"\nLookup únicos: {len(lookup_unicos)}")
    
    # Overlap vendas x lookup
    overlap_lookup = vendas_unicos & lookup_unicos
    vendas_sem_lookup = vendas_unicos - lookup_unicos
    
    print(f"Vendas em lookup: {len(overlap_lookup)} ({len(overlap_lookup)/len(vendas_unicos)*100:.1f}%)")
    print(f"Vendas SEM lookup: {len(vendas_sem_lookup)}")
    
    # 5. Análise UUID consolidado  
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    uuid_unicos = set(uuid_consolidado['id_legado_str'])
    
    print(f"\nUUID consolidado únicos: {len(uuid_unicos)}")
    
    # Overlap vendas x uuid consolidado
    overlap_uuid = vendas_unicos & uuid_unicos
    vendas_sem_uuid = vendas_unicos - uuid_unicos
    
    print(f"Vendas com UUID: {len(overlap_uuid)} ({len(overlap_uuid)/len(vendas_unicos)*100:.1f}%)")
    print(f"Vendas SEM UUID: {len(vendas_sem_uuid)}")
    
    # 6. Detalhes das vendas sem UUID
    if len(vendas_sem_uuid) > 0:
        print(f"\n=== AMOSTRA VENDAS SEM UUID ===")
        vendas_sem = vendas_df[vendas_df['cliente_id_str'].isin(vendas_sem_uuid)]
        amostra = vendas_sem.head(10)[['cliente_id', 'nome_cliente_temp', 'loja_id']].values
        for linha in amostra:
            print(f"  ID: {linha[0]}, Nome: {linha[1]}, Loja: {linha[2]}")
    
    print(f"\n=== CONCLUSÃO DIAGNÓSTICO ===")
    print(f"O problema está na diferença entre:")
    print(f"  - IDs presentes nas VENDAS: {len(vendas_unicos)}")
    print(f"  - IDs com UUID no consolidado: {len(uuid_unicos)}")
    print(f"  - Diferença: {len(vendas_sem_uuid)} vendas sem UUID")
    
    return vendas_sem_uuid

if __name__ == "__main__":
    resultado = diagnosticar_cobertura()