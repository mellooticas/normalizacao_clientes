#!/usr/bin/env python3
"""
Script para consolidar TODOS os clientes UUID e fazer match completo
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def consolidar_todos_clientes_uuids():
    """Consolida TODOS os clientes UUID de todas as lojas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    pasta_clientes = base_dir / "data" / "clientes_uuid"
    
    print("=== CONSOLIDANDO TODOS OS CLIENTES UUID ===")
    
    todos_clientes = []
    
    # Lista TODOS os arquivos de clientes
    arquivos_clientes = list(pasta_clientes.glob("clientes_*.csv"))
    
    for arquivo in arquivos_clientes:
        print(f"\nProcessando: {arquivo.name}")
        df = pd.read_csv(arquivo)
        
        print(f"  Registros: {len(df)}")
        print(f"  Colunas: {df.columns.tolist()}")
        
        # Padroniza colunas cliente_id
        if 'cliente_id_y' in df.columns:
            df['cliente_id'] = df['cliente_id_y']
        elif 'cliente_id_x' in df.columns:
            df['cliente_id'] = df['cliente_id_x']
        
        # Padroniza id_legado
        if 'id_legado' in df.columns:
            df['id_legado'] = df['id_legado']
        elif 'ID' in df.columns:
            df['id_legado'] = df['ID']
        else:
            print(f"  ❌ Sem coluna id_legado/ID")
            continue
        
        # Seleciona colunas necessárias
        colunas_necessarias = ['cliente_id', 'id_legado']
        if 'Nome Completo' in df.columns:
            colunas_necessarias.append('Nome Completo')
        if 'loja_nome' in df.columns:
            colunas_necessarias.append('loja_nome')
        
        df_selecionado = df[colunas_necessarias].copy()
        
        # Remove registros sem cliente_id ou id_legado
        antes = len(df_selecionado)
        df_selecionado = df_selecionado[
            (df_selecionado['cliente_id'].notna()) & 
            (df_selecionado['id_legado'].notna())
        ]
        depois = len(df_selecionado)
        
        print(f"  Válidos: {depois}/{antes}")
        
        if len(df_selecionado) > 0:
            todos_clientes.append(df_selecionado)
    
    # Combina todos
    if len(todos_clientes) > 0:
        clientes_consolidados = pd.concat(todos_clientes, ignore_index=True)
        
        # Remove duplicatas por id_legado (mantém primeiro)
        antes = len(clientes_consolidados)
        clientes_consolidados = clientes_consolidados.drop_duplicates(subset=['id_legado'], keep='first')
        depois = len(clientes_consolidados)
        
        print(f"\n=== CONSOLIDAÇÃO FINAL ===")
        print(f"Total registros: {antes}")
        print(f"Únicos por id_legado: {depois}")
        print(f"Duplicatas removidas: {antes - depois}")
        
        # Salva consolidado
        arquivo_consolidado = base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv"
        clientes_consolidados.to_csv(arquivo_consolidado, index=False)
        
        print(f"Arquivo salvo: {arquivo_consolidado}")
        
        return clientes_consolidados
    else:
        print("❌ Nenhum arquivo válido encontrado!")
        return None

def corrigir_com_base_completa():
    """Corrige vendas usando base completa de clientes"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("\n=== CORREÇÃO COM BASE COMPLETA ===")
    
    # 1. Consolida todos os clientes
    clientes_df = consolidar_todos_clientes_uuids()
    
    if clientes_df is None:
        return None
    
    # 2. Carrega vendas
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    
    print(f"\nVendas carregadas: {len(vendas_df)}")
    
    # 3. Prepara dados para match
    clientes_df['id_legado_str'] = clientes_df['id_legado'].astype(str).str.replace('.0', '')
    vendas_df['id_legado_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # 4. Faz match
    legado_para_uuid = dict(zip(clientes_df['id_legado_str'], clientes_df['cliente_id']))
    
    vendas_df['cliente_uuid'] = vendas_df['id_legado_str'].map(legado_para_uuid)
    
    matches = vendas_df['cliente_uuid'].notna().sum()
    print(f"Matches encontrados: {matches} ({matches/len(vendas_df)*100:.1f}%)")
    
    # 5. Aplica correção
    vendas_df['cliente_id'] = vendas_df['cliente_uuid']
    
    # 6. Prepara arquivo final
    vendas_final = vendas_df[[
        'numero_venda', 'cliente_id', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    # 7. Salva
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_uuids_completos.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    # 8. Estatísticas
    com_uuid = vendas_final['cliente_id'].notna().sum()
    sem_uuid = vendas_final['cliente_id'].isna().sum()
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Total vendas: {len(vendas_final)}")
    print(f"COM UUID: {com_uuid} ({com_uuid/len(vendas_final)*100:.1f}%)")
    print(f"SEM UUID: {sem_uuid} ({sem_uuid/len(vendas_final)*100:.1f}%)")
    
    if com_uuid > 0:
        uuid_exemplo = vendas_final[vendas_final['cliente_id'].notna()]['cliente_id'].iloc[0]
        print(f"Exemplo UUID: {uuid_exemplo}")
    
    print(f"Arquivo final: {arquivo_final}")
    
    # 9. Comandos SQL
    print(f"\n=== COMANDOS SQL ===")
    print(f"TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;")
    print(f"\\copy vendas.vendas FROM '{arquivo_final}' CSV HEADER;")
    print(f"SELECT COUNT(*), COUNT(cliente_id) FROM vendas.vendas;")
    
    return vendas_final

if __name__ == "__main__":
    resultado = corrigir_com_base_completa()
    if resultado is not None:
        print("\n🎉 CORREÇÃO COMPLETA FINALIZADA!")
        print("✅ Base completa de clientes consolidada!")
        print("🚀 Arquivo final com máximos UUIDs possíveis!")