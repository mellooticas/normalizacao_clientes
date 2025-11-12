#!/usr/bin/env python3
"""
Script para análise detalhada da coluna origem no lookup
Identifica padrões dos IDs sem UUID por origem
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

def analisar_origem_lookup():
    """Analisa origem dos clientes para entender falta de UUIDs"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ANÁLISE DETALHADA POR ORIGEM ===")
    
    # 1. Carrega dados
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    clientes_uuid_df = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    
    print(f"Lookup: {len(lookup_df)} registros")
    print(f"Vendas: {len(vendas_df)} registros")
    print(f"Clientes UUID: {len(clientes_uuid_df)} registros")
    
    # 2. Prepara dados
    lookup_df['id_cliente_str'] = lookup_df['id_cliente'].astype(str)
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    clientes_uuid_df['id_legado_str'] = clientes_uuid_df['id_legado'].astype(str).str.replace('.0', '')
    
    # Remove vendas sem cliente_id
    vendas_com_id = vendas_df[vendas_df['cliente_id'].notna()].copy()
    
    print(f"Vendas com cliente_id: {len(vendas_com_id)}")
    
    # 3. Análise por origem no lookup
    print(f"\n=== DISTRIBUIÇÃO POR ORIGEM NO LOOKUP ===")
    origem_counts = lookup_df['origem'].value_counts()
    for origem, count in origem_counts.items():
        print(f"{origem}: {count} clientes ({count/len(lookup_df)*100:.1f}%)")
    
    # 4. Categoriza IDs das vendas por presença no lookup e origem
    print(f"\n=== CATEGORIZAÇÃO DOS IDs DAS VENDAS ===")
    
    # Sets para análise
    ids_vendas = set(vendas_com_id['cliente_id_str'])
    ids_lookup = set(lookup_df['id_cliente_str'])
    ids_uuid = set(clientes_uuid_df['id_legado_str'])
    
    # IDs que estão no lookup
    ids_vendas_no_lookup = ids_vendas.intersection(ids_lookup)
    ids_vendas_fora_lookup = ids_vendas - ids_lookup
    
    print(f"IDs vendas NO lookup: {len(ids_vendas_no_lookup)}")
    print(f"IDs vendas FORA do lookup: {len(ids_vendas_fora_lookup)}")
    
    # 5. Analisa origem dos IDs que estão no lookup
    print(f"\n=== ORIGEM DOS IDs QUE ESTÃO NO LOOKUP ===")
    
    vendas_no_lookup = vendas_com_id[vendas_com_id['cliente_id_str'].isin(ids_vendas_no_lookup)]
    
    for origem in lookup_df['origem'].unique():
        ids_origem = set(lookup_df[lookup_df['origem'] == origem]['id_cliente_str'])
        vendas_origem = vendas_com_id[vendas_com_id['cliente_id_str'].isin(ids_origem)]
        
        # Verifica quantos têm UUID
        ids_origem_com_uuid = ids_origem.intersection(ids_uuid)
        vendas_origem_com_uuid = vendas_origem[vendas_origem['cliente_id_str'].isin(ids_origem_com_uuid)]
        
        print(f"\n{origem}:")
        print(f"  Clientes no lookup: {len(ids_origem)}")
        print(f"  Vendas desta origem: {len(vendas_origem)} (R$ {vendas_origem['valor_total'].sum():,.2f})")
        print(f"  IDs com UUID disponível: {len(ids_origem_com_uuid)}")
        print(f"  Vendas com UUID: {len(vendas_origem_com_uuid)} ({len(vendas_origem_com_uuid)/len(vendas_origem)*100 if len(vendas_origem) > 0 else 0:.1f}%)")
        print(f"  Vendas SEM UUID: {len(vendas_origem) - len(vendas_origem_com_uuid)}")
    
    # 6. Analisa IDs fora do lookup
    print(f"\n=== ANÁLISE DOS IDs FORA DO LOOKUP ===")
    
    vendas_fora_lookup = vendas_com_id[vendas_com_id['cliente_id_str'].isin(ids_vendas_fora_lookup)]
    
    print(f"Total vendas fora do lookup: {len(vendas_fora_lookup)}")
    print(f"Valor fora do lookup: R$ {vendas_fora_lookup['valor_total'].sum():,.2f}")
    
    # Analisa padrões dos IDs fora do lookup
    print(f"\nPadrões dos IDs fora do lookup:")
    
    padroes = defaultdict(list)
    for id_str in ids_vendas_fora_lookup:
        if id_str.startswith('5000'):
            padroes['5000XXX'].append(id_str)
        elif id_str.startswith('6000'):
            padroes['6000XXX'].append(id_str)
        elif id_str.startswith('7000'):
            padroes['7000XXX'].append(id_str)
        elif id_str.startswith('8000'):
            padroes['8000XXX'].append(id_str)
        elif id_str.startswith('9000'):
            padroes['9000XXX'].append(id_str)
        elif id_str.startswith('10000'):
            padroes['10000XXX'].append(id_str)
        else:
            padroes['OUTROS'].append(id_str)
    
    for padrao, ids in padroes.items():
        vendas_padrao = vendas_fora_lookup[vendas_fora_lookup['cliente_id_str'].isin(ids)]
        ids_padrao_com_uuid = set(ids).intersection(ids_uuid)
        
        print(f"  {padrao}: {len(ids)} IDs, {len(vendas_padrao)} vendas, R$ {vendas_padrao['valor_total'].sum():,.2f}")
        print(f"    Com UUID disponível: {len(ids_padrao_com_uuid)}")
        print(f"    Sem UUID: {len(ids) - len(ids_padrao_com_uuid)}")
        
        # Mostra exemplos
        if len(ids) > 0:
            print(f"    Exemplos: {', '.join(list(ids)[:5])}")
    
    # 7. Conclusões e recomendações
    print(f"\n=== CONCLUSÕES ===")
    
    total_vendas_com_id = len(vendas_com_id)
    vendas_com_uuid_possivel = len(vendas_com_id[vendas_com_id['cliente_id_str'].isin(ids_uuid)])
    
    print(f"Total vendas com cliente_id: {total_vendas_com_id}")
    print(f"Vendas com UUID possível: {vendas_com_uuid_possivel} ({vendas_com_uuid_possivel/total_vendas_com_id*100:.1f}%)")
    print(f"Gap restante: {total_vendas_com_id - vendas_com_uuid_possivel} vendas ({(total_vendas_com_id - vendas_com_uuid_possivel)/total_vendas_com_id*100:.1f}%)")
    
    # 8. Recomendações por origem
    print(f"\n=== RECOMENDAÇÕES ===")
    
    print("1. VIXEN vs OS:")
    print("   - Verificar se há diferença na migração entre clientes VIXEN e OS")
    print("   - Clientes OS podem ter sido criados mais recentemente")
    
    print("2. IDs fora do lookup:")
    print("   - Séries 5000, 6000, 7000, 8000+ podem ser clientes OSS_NOVO")
    print("   - Podem precisar de processo de migração específico")
    
    print("3. Próximos passos:")
    print("   - Investigar se séries numéricas correspondem a períodos específicos")
    print("   - Verificar se há outros arquivos com estes clientes")
    print("   - Considerar criação manual dos clientes mais valiosos")
    
    return {
        'vendas_com_id': vendas_com_id,
        'lookup_df': lookup_df,
        'padroes': padroes,
        'cobertura_atual': vendas_com_uuid_possivel/total_vendas_com_id*100
    }

if __name__ == "__main__":
    resultado = analisar_origem_lookup()
    print(f"\n🎯 ANÁLISE CONCLUÍDA!")
    print(f"📊 Cobertura atual confirmada: {resultado['cobertura_atual']:.1f}%")