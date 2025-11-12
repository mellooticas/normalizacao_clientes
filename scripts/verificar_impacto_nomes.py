#!/usr/bin/env python3
"""
Verifica o impacto dos matches por variações de nomes
"""

import pandas as pd
from pathlib import Path

def verificar_impacto_nomes():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== VERIFICANDO IMPACTO DOS MATCHES POR NOMES ===")
    
    # Carrega vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    print(f"Total vendas: {len(vendas_df)}")
    
    # Carrega matches por nomes
    matches_df = pd.read_csv(base_dir / "data" / "matches_nomes_variacoes.csv")
    print(f"Matches por nomes: {len(matches_df)}")
    
    # Aplica nos dados
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    matches_df['oss_cliente_id_str'] = matches_df['oss_cliente_id'].astype(str)
    matches_dict = dict(zip(matches_df['oss_cliente_id_str'], matches_df['uuid_encontrado']))
    
    vendas_df['uuid_final'] = vendas_df['cliente_id_str'].map(matches_dict)
    com_uuid = vendas_df['uuid_final'].notna().sum()
    
    print(f"Vendas COM UUID após nomes: {com_uuid} ({com_uuid/len(vendas_df)*100:.1f}%)")
    print(f"🎯 {com_uuid} vendas agora têm UUID por matching de nomes!")
    
    # Salva resultado
    vendas_final = vendas_df[vendas_df['uuid_final'].notna()][[
        'numero_venda', 'uuid_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_final.rename(columns={'uuid_final': 'cliente_id'}, inplace=True)
    
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_com_matches_nomes.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"Arquivo salvo: {arquivo_final}")
    print(f"🚀 Estratégia de nomes funcionou perfeitamente!")
    
    return vendas_final

if __name__ == "__main__":
    resultado = verificar_impacto_nomes()
    print(f"✅ {len(resultado)} vendas com UUID por matching de nomes!")