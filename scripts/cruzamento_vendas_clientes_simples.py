#!/usr/bin/env python3
"""
Script SIMPLES para cruzar vendas com clientes UUID
Estratégia: vendas.cliente_id = clientes.cliente_id_principal -> clientes.cliente_uuid
"""

import pandas as pd
import os
from pathlib import Path

def cruzamento_vendas_clientes_simples():
    """Faz cruzamento simples entre vendas e clientes UUID"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== CRUZAMENTO SIMPLES VENDAS x CLIENTES ===")
    
    # 1. Carrega vendas
    vendas_file = base_dir / "data" / "vendas_para_importar" / "vendas_oss_lojas_unidas.csv"
    print(f"Carregando vendas: {vendas_file}")
    
    vendas_df = pd.read_csv(vendas_file, low_memory=False)
    print(f"Vendas carregadas: {len(vendas_df)} registros")
    print(f"Cliente_id únicos: {vendas_df['cliente_id'].nunique()}")
    
    # 2. Une rapidamente os 6 arquivos de clientes UUID
    print(f"\nUnindo arquivos de clientes UUID...")
    clientes_dir = base_dir / "data" / "clientes_uuid"
    
    todos_clientes = []
    
    arquivos_clientes = [
        'clientes_maua.csv',
        'clientes_perus.csv', 
        'clientes_rio_pequeno.csv',
        'clientes_sao_mateus.csv',
        'clientes_suzano.csv',
        'clientes_suzano2.csv'
    ]
    
    for arquivo in arquivos_clientes:
        arquivo_path = clientes_dir / arquivo
        print(f"  Processando: {arquivo}")
        
        df = pd.read_csv(arquivo_path, low_memory=False)
        
        # Identifica coluna do ID principal
        if 'ID' in df.columns and df['ID'].notna().sum() > 0:
            df['cliente_id_principal'] = df['ID'].astype(str).str.replace('.0', '', regex=False)
        elif 'cliente_id_x' in df.columns and df['cliente_id_x'].notna().sum() > 0:
            df['cliente_id_principal'] = df['cliente_id_x'].astype(str).str.replace('.0', '', regex=False)
        
        # Pega apenas as colunas necessárias
        colunas_necessarias = ['cliente_id_principal', 'cliente_id_y']
        if all(col in df.columns for col in colunas_necessarias):
            df_limpo = df[colunas_necessarias].copy()
            df_limpo['arquivo_origem'] = arquivo.replace('.csv', '')
            todos_clientes.append(df_limpo)
            print(f"    {len(df_limpo)} clientes adicionados")
    
    # 3. Consolida clientes
    clientes_df = pd.concat(todos_clientes, ignore_index=True)
    clientes_df = clientes_df.dropna(subset=['cliente_id_principal', 'cliente_id_y'])
    clientes_df = clientes_df.drop_duplicates(subset=['cliente_id_principal'])
    
    print(f"\nClientes consolidados: {len(clientes_df)} registros únicos")
    
    # 4. Faz o cruzamento
    print(f"\nRealizando cruzamento...")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str)
    
    vendas_com_uuid = vendas_df.merge(
        clientes_df[['cliente_id_principal', 'cliente_id_y']], 
        left_on='cliente_id_str', 
        right_on='cliente_id_principal', 
        how='left'
    )
    
    # 5. Estatísticas do cruzamento
    total_vendas = len(vendas_com_uuid)
    com_uuid = vendas_com_uuid['cliente_id_y'].notna().sum()
    sem_uuid = vendas_com_uuid['cliente_id_y'].isna().sum()
    
    print(f"\n=== RESULTADO DO CRUZAMENTO ===")
    print(f"Total de vendas: {total_vendas}")
    print(f"Com cliente UUID: {com_uuid} ({com_uuid/total_vendas*100:.1f}%)")
    print(f"Sem cliente UUID: {sem_uuid} ({sem_uuid/total_vendas*100:.1f}%)")
    
    # 6. Prepara para tabela vendas.vendas
    print(f"\nPreparando dados para tabela vendas.vendas...")
    
    # Renomeia a coluna UUID
    vendas_com_uuid['cliente_uuid'] = vendas_com_uuid['cliente_id_y']
    
    # Remove colunas auxiliares
    vendas_com_uuid = vendas_com_uuid.drop(['cliente_id_str', 'cliente_id_principal', 'cliente_id_y'], axis=1)
    
    # Salva resultado
    arquivo_saida = base_dir / "data" / "vendas_para_importar" / "vendas_com_cliente_uuid.csv"
    vendas_com_uuid.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== ARQUIVO FINAL ===")
    print(f"Arquivo salvo: {arquivo_saida}")
    print(f"Total de registros: {len(vendas_com_uuid)}")
    
    # Amostra do resultado
    print(f"\n=== AMOSTRA DO RESULTADO ===")
    colunas_importantes = ['cliente_id', 'cliente_uuid', 'loja_id_oss', 'total_venda']
    if all(col in vendas_com_uuid.columns for col in colunas_importantes):
        amostra = vendas_com_uuid[colunas_importantes].head(5)
        print(amostra.to_string())
    
    return vendas_com_uuid

if __name__ == "__main__":
    resultado = cruzamento_vendas_clientes_simples()
    print("\n✅ Cruzamento simples concluído!")
    print("🎯 Agora temos cliente_uuid para as vendas!")