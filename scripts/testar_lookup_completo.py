#!/usr/bin/env python3
"""
Script para testar match usando clientes_lookup.csv
Este arquivo pode ter todos os IDs necessários
"""

import pandas as pd
import numpy as np
from pathlib import Path

def testar_lookup_completo():
    """Testa match usando clientes_lookup.csv"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== TESTE COM CLIENTES_LOOKUP.CSV ===")
    
    # 1. Carrega lookup
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    print(f"Lookup carregado: {len(lookup_df)} registros")
    print(f"Origens: {lookup_df['origem'].value_counts()}")
    
    # 2. Carrega vendas com números originais
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    print(f"Vendas carregadas: {len(vendas_df)}")
    
    # 3. Prepara dados para match
    lookup_df['id_cliente_str'] = lookup_df['id_cliente'].astype(str)
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    print(f"\nRange IDs lookup: {lookup_df['id_cliente'].min()} - {lookup_df['id_cliente'].max()}")
    print(f"Range IDs vendas: {vendas_df['cliente_id'].min()} - {vendas_df['cliente_id'].max()}")
    
    # 4. Testa match direto por ID
    print(f"\n=== TESTE MATCH DIRETO ===")
    
    # Cria set para verificação rápida
    ids_lookup = set(lookup_df['id_cliente_str'])
    ids_vendas = set(vendas_df['cliente_id_str'])
    
    # Remove NaN
    ids_vendas.discard('nan')
    
    print(f"IDs únicos no lookup: {len(ids_lookup)}")
    print(f"IDs únicos nas vendas: {len(ids_vendas)}")
    
    # Interseção
    ids_em_comum = ids_lookup.intersection(ids_vendas)
    ids_so_vendas = ids_vendas - ids_lookup
    ids_so_lookup = ids_lookup - ids_vendas
    
    print(f"IDs em comum: {len(ids_em_comum)}")
    print(f"IDs só nas vendas: {len(ids_so_vendas)}")
    print(f"IDs só no lookup: {len(ids_so_lookup)}")
    
    if len(ids_so_vendas) > 0:
        print(f"\nExemplos IDs só nas vendas:")
        for i, id_venda in enumerate(list(ids_so_vendas)[:10]):
            print(f"  {id_venda}")
    
    # 5. Verifica se há UUIDs nos clientes consolidados para estes IDs
    print(f"\n=== VERIFICANDO UUIDS DISPONÍVEIS ===")
    
    # Carrega clientes UUID consolidado
    clientes_uuid_df = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    clientes_uuid_df['id_legado_str'] = clientes_uuid_df['id_legado'].astype(str).str.replace('.0', '')
    
    uuids_disponiveis = set(clientes_uuid_df['id_legado_str'])
    
    print(f"UUIDs disponíveis: {len(uuids_disponiveis)}")
    
    # Verifica cobertura dos IDs que não estão no lookup
    ids_vendas_com_uuid = ids_so_vendas.intersection(uuids_disponiveis)
    ids_vendas_sem_solucao = ids_so_vendas - uuids_disponiveis
    
    print(f"IDs só nas vendas que TÊM UUID: {len(ids_vendas_com_uuid)}")
    print(f"IDs só nas vendas SEM solução: {len(ids_vendas_sem_solucao)}")
    
    # 6. Análise de cobertura total possível
    print(f"\n=== ANÁLISE DE COBERTURA TOTAL ===")
    
    # Total de vendas com ID
    vendas_com_id = vendas_df[vendas_df['cliente_id'].notna()]
    total_vendas_com_id = len(vendas_com_id)
    
    # IDs que têm solução (lookup + UUID direto)
    ids_com_solucao = ids_em_comum.union(ids_vendas_com_uuid)
    
    # Conta vendas que podem ser resolvidas
    vendas_com_id['pode_resolver'] = vendas_com_id['cliente_id_str'].isin(ids_com_solucao)
    vendas_resolviveis = vendas_com_id['pode_resolver'].sum()
    
    print(f"Total vendas com ID: {total_vendas_com_id}")
    print(f"Vendas que podem ser resolvidas: {vendas_resolviveis}")
    print(f"% de cobertura máxima possível: {vendas_resolviveis/total_vendas_com_id*100:.1f}%")
    
    # 7. Mostra problemas específicos
    if len(ids_vendas_sem_solucao) > 0:
        print(f"\n=== IDs PROBLEMÁTICOS (sem solução) ===")
        vendas_problema = vendas_df[vendas_df['cliente_id_str'].isin(ids_vendas_sem_solucao)]
        
        print(f"Vendas sem solução: {len(vendas_problema)}")
        print(f"Valor perdido: R$ {vendas_problema['valor_total'].sum():,.2f}")
        
        # Mostra exemplos
        for i, (_, row) in enumerate(vendas_problema.head(5).iterrows()):
            print(f"  OS {row['numero_venda']}: ID {row['cliente_id']} - R$ {row['valor_total']}")
    
    return {
        'lookup_df': lookup_df,
        'vendas_df': vendas_df,
        'ids_em_comum': ids_em_comum,
        'cobertura_maxima': vendas_resolviveis/total_vendas_com_id*100 if total_vendas_com_id > 0 else 0
    }

if __name__ == "__main__":
    resultado = testar_lookup_completo()
    print(f"\n🎯 ANÁLISE COMPLETA!")
    print(f"📊 Cobertura máxima possível: {resultado['cobertura_maxima']:.1f}%")