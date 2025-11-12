#!/usr/bin/env python3
"""
Script para corrigir cliente_id usando UUIDs reais do banco
Faz match por id_legado em core.clientes
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def corrigir_uuids_clientes():
    """Corrige cliente_id usando UUIDs reais do banco via id_legado"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== CORREÇÃO DE CLIENTE_ID PARA UUIDS REAIS ===")
    print(f"Data/hora: {datetime.now()}")
    
    # 1. Carrega arquivo atual com números incorretos
    arquivo_atual = base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv"
    vendas_df = pd.read_csv(arquivo_atual)
    
    print(f"\n1. ARQUIVO ATUAL:")
    print(f"  Total vendas: {len(vendas_df)}")
    print(f"  COM cliente_id (números): {vendas_df['cliente_id'].notna().sum()}")
    print(f"  Exemplo cliente_id atual: {vendas_df['cliente_id'].iloc[0]} (tipo: {type(vendas_df['cliente_id'].iloc[0])})")
    
    # 2. Prepara dados para correção
    print(f"\n2. PREPARANDO CORREÇÃO:")
    
    # Move cliente_id atual para nome_cliente_temp se estiver vazio
    mask_sem_nome = vendas_df['nome_cliente_temp'].isna() | (vendas_df['nome_cliente_temp'] == '')
    mask_com_cliente_id = vendas_df['cliente_id'].notna()
    
    # Para os registros que não têm nome mas têm cliente_id (número), usa o id_legado
    vendas_df.loc[mask_sem_nome & mask_com_cliente_id, 'id_legado_temp'] = vendas_df.loc[mask_sem_nome & mask_com_cliente_id, 'cliente_id'].astype(str).str.replace('.0', '')
    
    # Para os que têm nome_cliente_temp, tenta extrair número se for numérico
    vendas_df['id_legado_temp'] = vendas_df['id_legado_temp'].fillna('')
    
    # Se cliente_id for número, usa como id_legado
    mask_cliente_id_numero = vendas_df['cliente_id'].notna()
    vendas_df.loc[mask_cliente_id_numero, 'id_legado_temp'] = vendas_df.loc[mask_cliente_id_numero, 'cliente_id'].astype(str).str.replace('.0', '')
    
    print(f"  IDs legados preparados: {(vendas_df['id_legado_temp'] != '').sum()}")
    
    # 3. Carrega dados de clientes consolidados com UUIDs
    print(f"\n3. CARREGANDO CLIENTES COM UUIDS:")
    
    # Tenta diferentes arquivos de clientes
    possiveis_arquivos = [
        base_dir / "data" / "clientes_uuid" / "clientes_uuid_consolidado.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_suzano.csv"
    ]
    
    clientes_df = None
    
    for arquivo in possiveis_arquivos:
        if arquivo.exists():
            print(f"  Tentando: {arquivo.name}")
            df = pd.read_csv(arquivo)
            print(f"    Colunas: {df.columns.tolist()}")
            
            # Verifica se tem as colunas necessárias
            if 'cliente_id' in df.columns or 'cliente_id_y' in df.columns:
                clientes_df = df.copy()
                
                # Padroniza nome da coluna cliente_id
                if 'cliente_id_y' in clientes_df.columns:
                    clientes_df['cliente_id'] = clientes_df['cliente_id_y']
                elif 'cliente_id_x' in clientes_df.columns:
                    clientes_df['cliente_id'] = clientes_df['cliente_id_x']
                
                # Verifica se tem id_legado
                if 'id_legado' in clientes_df.columns:
                    print(f"    ✅ Arquivo com id_legado encontrado!")
                    break
                elif 'ID' in clientes_df.columns:
                    clientes_df['id_legado'] = clientes_df['ID']
                    print(f"    ✅ Usando coluna 'ID' como id_legado!")
                    break
    
    if clientes_df is None:
        print("❌ Nenhum arquivo de clientes válido encontrado!")
        return None
    
    # Remove clientes sem UUID ou id_legado
    clientes_df = clientes_df[
        (clientes_df['cliente_id'].notna()) & 
        (clientes_df['id_legado'].notna())
    ].copy()
    
    # Converte id_legado para string para matching
    clientes_df['id_legado_str'] = clientes_df['id_legado'].astype(str).str.replace('.0', '')
    vendas_df['id_legado_str'] = vendas_df['id_legado_temp'].astype(str)
    
    print(f"  Clientes válidos: {len(clientes_df)}")
    print(f"  IDs legados únicos: {clientes_df['id_legado_str'].nunique()}")
    print(f"  Exemplo UUID: {clientes_df['cliente_id'].iloc[0]}")
    
    # 4. Faz match por id_legado
    print(f"\n4. FAZENDO MATCH POR ID_LEGADO:")
    
    # Cria dicionário id_legado -> UUID
    legado_para_uuid = dict(zip(clientes_df['id_legado_str'], clientes_df['cliente_id']))
    
    # Aplica matching
    vendas_df['cliente_uuid'] = vendas_df['id_legado_str'].map(legado_para_uuid)
    
    matches_encontrados = vendas_df['cliente_uuid'].notna().sum()
    print(f"  Matches encontrados: {matches_encontrados}")
    print(f"  % de match: {matches_encontrados/len(vendas_df)*100:.1f}%")
    
    # 5. Aplica correções
    print(f"\n5. APLICANDO CORREÇÕES:")
    
    # Substitui cliente_id pelos UUIDs corretos
    vendas_df['cliente_id'] = vendas_df['cliente_uuid']
    
    # Limpa colunas auxiliares
    vendas_corrigidas = vendas_df[[
        'numero_venda', 'cliente_id', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    # 6. Estatísticas finais
    print(f"\n6. RESULTADO FINAL:")
    
    com_uuid = vendas_corrigidas['cliente_id'].notna().sum()
    sem_uuid = vendas_corrigidas['cliente_id'].isna().sum()
    
    print(f"  Total vendas: {len(vendas_corrigidas)}")
    print(f"  COM UUID válido: {com_uuid} ({com_uuid/len(vendas_corrigidas)*100:.1f}%)")
    print(f"  SEM UUID: {sem_uuid} ({sem_uuid/len(vendas_corrigidas)*100:.1f}%)")
    
    # Verifica formato dos UUIDs
    if com_uuid > 0:
        uuid_exemplo = vendas_corrigidas[vendas_corrigidas['cliente_id'].notna()]['cliente_id'].iloc[0]
        print(f"  Exemplo UUID correto: {uuid_exemplo}")
        print(f"  Formato válido: {len(str(uuid_exemplo)) == 36 and '-' in str(uuid_exemplo)}")
    
    # 7. Salva arquivo corrigido
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_uuids_corretos.csv"
    vendas_corrigidas.to_csv(arquivo_final, index=False)
    
    print(f"\n7. ARQUIVO SALVO:")
    print(f"  📁 {arquivo_final}")
    print(f"  📊 {len(vendas_corrigidas)} vendas com UUIDs corretos")
    
    # 8. Comandos para importação
    print(f"\n8. COMANDOS PARA IMPORTAÇÃO:")
    print(f"-- Limpar tabela")
    print(f"TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;")
    print(f"")
    print(f"-- Importar com UUIDs corretos")
    print(f"\\copy vendas.vendas FROM '{arquivo_final}' CSV HEADER;")
    print(f"")
    print(f"-- Verificar importação")
    print(f"SELECT COUNT(*), COUNT(cliente_id) FROM vendas.vendas;")
    
    return vendas_corrigidas

if __name__ == "__main__":
    resultado = corrigir_uuids_clientes()
    if resultado is not None:
        print("\n🎉 CORREÇÃO DE UUIDS FINALIZADA!")
        print("✅ Arquivo pronto com UUIDs corretos!")
        print("🚀 Pode importar sem erros de UUID!")