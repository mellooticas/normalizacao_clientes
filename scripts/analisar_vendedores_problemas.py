#!/usr/bin/env python3
"""
Script para analisar e mapear vendedores corretos
Compara vendedores no arquivo de vendas com os existentes nos dados normalizados
"""

import pandas as pd
import json
from pathlib import Path

def analisar_vendedores():
    """Analisa vendedores nas vendas vs vendedores normalizados"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ANÁLISE DE VENDEDORES PARA CORREÇÃO ===")
    
    # 1. Vendedores no arquivo de vendas
    print("\n1. VENDEDORES NO ARQUIVO DE VENDAS:")
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_final_importacao.csv")
    vendedores_vendas = vendas_df['vendedor_id'].value_counts()
    
    print(f"Total vendedores únicos: {len(vendedores_vendas)}")
    for vendedor_id, count in vendedores_vendas.head(10).items():
        print(f"  {vendedor_id}: {count} vendas")
    
    # 2. Vendedores normalizados disponíveis
    print("\n2. VENDEDORES NORMALIZADOS DISPONÍVEIS:")
    vendedores_uuid_df = pd.read_csv(base_dir / "VENDEDORES_UNICOS_UUID.csv")
    print(f"Total vendedores normalizados: {len(vendedores_uuid_df)}")
    print("Amostra:")
    for _, row in vendedores_uuid_df.head(10).iterrows():
        print(f"  {row['uuid']}: {row['nome_padronizado']}")
    
    # 3. Verificar intersecção
    print("\n3. VERIFICANDO INTERSECÇÃO:")
    vendedores_vendas_set = set(vendedores_vendas.index)
    vendedores_uuid_set = set(vendedores_uuid_df['uuid'])
    
    intersecao = vendedores_vendas_set.intersection(vendedores_uuid_set)
    diferenca = vendedores_vendas_set - vendedores_uuid_set
    
    print(f"Vendedores em comum: {len(intersecao)}")
    print(f"Vendedores nas vendas mas não nos normalizados: {len(diferenca)}")
    
    if len(diferenca) > 0:
        print("\nVendedores problemáticos:")
        for v in list(diferenca)[:10]:
            count = vendedores_vendas[v]
            print(f"  {v}: {count} vendas")
    
    # 4. Analisar origem dos vendedores problemáticos
    print("\n4. ANALISANDO ORIGEM DOS VENDEDORES PROBLEMÁTICOS:")
    
    # Carrega dados originais para ver de onde vieram
    vendas_originais = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_oss_lojas_unidas.csv")
    
    print("Colunas de vendedor disponíveis:")
    colunas_vendedor = [col for col in vendas_originais.columns if 'vendedor' in col.lower()]
    for col in colunas_vendedor:
        print(f"  {col}")
    
    # 5. Verificar mapeamento atual
    if 'vendedor_uuid_loja' in vendas_originais.columns:
        print("\n5. VERIFICANDO MAPEAMENTO VENDEDOR_UUID_LOJA:")
        vendedores_orig = vendas_originais['vendedor_uuid_loja'].value_counts()
        print(f"Vendedores únicos no original: {len(vendedores_orig)}")
        
        # Comparar com normalizados
        vendedores_orig_set = set(vendedores_orig.index.dropna())
        intersecao_orig = vendedores_orig_set.intersection(vendedores_uuid_set)
        diferenca_orig = vendedores_orig_set - vendedores_uuid_set
        
        print(f"Vendedores originais em comum com normalizados: {len(intersecao_orig)}")
        print(f"Vendedores originais não encontrados: {len(diferenca_orig)}")
        
        if len(diferenca_orig) > 0:
            print("\nVendedores originais problemáticos:")
            for v in list(diferenca_orig)[:10]:
                if pd.notna(v):
                    count = vendedores_orig[v]
                    print(f"  {v}: {count} ocorrências")
    
    # 6. Sugerir estratégia de correção
    print("\n=== ESTRATÉGIA DE CORREÇÃO ===")
    
    if len(diferenca) == 0:
        print("✅ Todos os vendedores estão mapeados corretamente!")
    else:
        print("❌ Problemas encontrados:")
        print(f"  {len(diferenca)} vendedores não mapeados")
        print(f"  {sum(vendedores_vendas[v] for v in diferenca)} vendas afetadas")
        
        print("\nOpções de correção:")
        print("1. Mapear vendedores problemáticos para vendedores genéricos")
        print("2. Criar novos vendedores no banco")
        print("3. Usar vendedor padrão 'NÃO INFORMADO'")
    
    return {
        'vendedores_vendas': vendedores_vendas,
        'vendedores_uuid': vendedores_uuid_df,
        'problemáticos': diferenca,
        'normalizados_disponiveis': vendedores_uuid_set
    }

if __name__ == "__main__":
    resultado = analisar_vendedores()
    print("\n📊 Análise concluída!")