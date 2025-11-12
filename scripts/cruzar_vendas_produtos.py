#!/usr/bin/env python3
"""
Script para cruzar vendas com produtos usando números DAV normalizados
"""

import pandas as pd
from datetime import datetime

def cruzar_vendas_produtos():
    """
    Cruza vendas com produtos usando DAV normalizado
    """
    print("🎯 === CRUZAMENTO VENDAS x PRODUTOS === 🎯")
    
    # Carregar dados
    vendas_file = 'data/vendas_totais_com_uuid.csv'  # Arquivo de vendas
    produtos_file = 'data/itens_venda_preparados_TIMESTAMP.csv'  # Substituir TIMESTAMP
    
    try:
        df_vendas = pd.read_csv(vendas_file)
        df_produtos = pd.read_csv(produtos_file)
        
        print(f"📊 Vendas: {len(df_vendas):,}")
        print(f"📊 Produtos: {len(df_produtos):,}")
        
        # Cruzamento por DAV normalizado
        cruzamentos = []
        
        for _, produto in df_produtos.iterrows():
            dav_produto = produto['dav_numero']
            empresa_produto = produto['empresa']
            
            # Buscar venda correspondente
            venda_match = df_vendas[
                (df_vendas['numero_os'] == dav_produto) &
                (df_vendas['loja_id'].str.contains(str(int(empresa_produto)), na=False))
            ]
            
            if not venda_match.empty:
                produto['venda_id'] = venda_match.iloc[0]['id']
                cruzamentos.append(produto)
        
        df_cruzados = pd.DataFrame(cruzamentos)
        
        print(f"✅ Cruzamentos encontrados: {len(df_cruzados):,}")
        
        # Salvar resultado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_final = f'data/itens_venda_com_vendas_{timestamp}.csv'
        df_cruzados.to_csv(arquivo_final, index=False)
        
        print(f"💾 Arquivo final: {arquivo_final}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    cruzar_vendas_produtos()
