#!/usr/bin/env python3
"""
Script para cruzar itens OSS com vendas existentes e criar sistema integrado
"""

import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime
import numpy as np

def carregar_vendas_existentes():
    """Carrega vendas existentes do sistema"""
    vendas_files = [
        "data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv",
        "data/vendas_para_importar/vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv",
        "data/vendas_para_importar/vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    ]
    
    for file_path in vendas_files:
        if Path(file_path).exists():
            print(f"Carregando vendas de: {file_path}")
            df = pd.read_csv(file_path, dtype=str, low_memory=False)
            print(f"  - {len(df)} vendas carregadas")
            return df
    
    print("Nenhum arquivo de vendas encontrado!")
    return pd.DataFrame()

def normalizar_chave_os(valor):
    """Normaliza chave OS para comparação"""
    if pd.isna(valor):
        return None
    
    valor = str(valor).strip().upper()
    # Remove caracteres especiais comuns
    valor = valor.replace(',', '').replace('.0', '').replace('_', '')
    return valor

def encontrar_vendas_por_cliente_id(vendas_df, cliente_id):
    """Encontra vendas existentes para um cliente_id"""
    matches = []
    
    # Procurar por ID do cliente em diferentes colunas
    for col in ['cliente_id', 'ID.2', 'id_cliente', 'CLIENT_ID']:
        if col in vendas_df.columns:
            matches_col = vendas_df[vendas_df[col].astype(str) == str(cliente_id)]
            if not matches_col.empty:
                matches.append(matches_col)
    
    if matches:
        return pd.concat(matches).drop_duplicates()
    return pd.DataFrame()

def encontrar_vendas_por_os(vendas_df, os_chave, numero_os, loja_nome):
    """Encontra vendas por número de OS"""
    matches = []
    
    # Normalizar valores de busca
    os_norm = normalizar_chave_os(os_chave) if os_chave else None
    num_norm = normalizar_chave_os(numero_os) if numero_os else None
    
    # Procurar em colunas de OS
    os_columns = ['os_chave', 'numero_os', 'OS_N', 'OS', 'os_numero', 'numero_ordem_servico']
    
    for col in os_columns:
        if col in vendas_df.columns:
            # Buscar por OS normalizada
            vendas_df_norm = vendas_df.copy()
            vendas_df_norm[f'{col}_norm'] = vendas_df_norm[col].apply(normalizar_chave_os)
            
            if os_norm:
                matches_os = vendas_df_norm[vendas_df_norm[f'{col}_norm'] == os_norm]
                if not matches_os.empty:
                    matches.append(matches_os.drop(columns=[f'{col}_norm']))
            
            if num_norm and num_norm != os_norm:
                matches_num = vendas_df_norm[vendas_df_norm[f'{col}_norm'] == num_norm]
                if not matches_num.empty:
                    matches.append(matches_num.drop(columns=[f'{col}_norm']))
    
    if matches:
        return pd.concat(matches).drop_duplicates()
    return pd.DataFrame()

def encontrar_vendas_por_dados_cliente(vendas_df, cliente_nome, data_compra, loja_nome):
    """Encontra vendas por dados do cliente"""
    if pd.isna(cliente_nome) or not cliente_nome:
        return pd.DataFrame()
    
    cliente_norm = str(cliente_nome).strip().upper()
    matches = []
    
    # Procurar por nome em diferentes colunas
    nome_columns = ['cliente_nome', 'NOME', 'nome_cliente', 'nome_normalizado']
    
    for col in nome_columns:
        if col in vendas_df.columns:
            vendas_norm = vendas_df[vendas_df[col].astype(str).str.upper().str.contains(cliente_norm[:20], na=False)]
            if not vendas_norm.empty:
                # Filtrar por loja se possível
                if 'loja_nome' in vendas_norm.columns:
                    vendas_loja = vendas_norm[vendas_norm['loja_nome'].str.upper() == loja_nome.upper()]
                    if not vendas_loja.empty:
                        matches.append(vendas_loja)
                else:
                    matches.append(vendas_norm)
    
    if matches:
        return pd.concat(matches).drop_duplicates()
    return pd.DataFrame()

def main():
    print("=== CRUZAMENTO OSS ITENS COM VENDAS EXISTENTES ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar dados
    print("\n1. Carregando dados...")
    vendas_df = carregar_vendas_existentes()
    
    if vendas_df.empty:
        print("Não foi possível carregar vendas existentes!")
        return
    
    # Carregar itens OSS
    itens_files = list(Path("data/processados").glob("OSS_ITENS_VENDAS_COMPLETO_*.csv"))
    if not itens_files:
        print("Nenhum arquivo de itens OSS encontrado!")
        return
    
    itens_file = sorted(itens_files)[-1]  # Mais recente
    print(f"Carregando itens OSS de: {itens_file}")
    itens_df = pd.read_csv(itens_file, dtype=str, low_memory=False)
    print(f"  - {len(itens_df)} itens carregados")
    
    print(f"\nColunas vendas: {list(vendas_df.columns)}")
    print(f"Colunas itens: {list(itens_df.columns)}")
    
    # Estatísticas de cruzamento
    stats = {
        'total_itens': len(itens_df),
        'matches_por_cliente_id': 0,
        'matches_por_os': 0,
        'matches_por_nome': 0,
        'sem_match': 0,
        'itens_com_venda_id': 0,
        'clientes_unicos_processados': 0
    }
    
    print(f"\n2. Iniciando cruzamento...")
    itens_processados = []
    clientes_processados = set()
    
    for idx, item in itens_df.iterrows():
        if idx % 1000 == 0:
            print(f"  Processando item {idx}/{len(itens_df)}...")
        
        item_processado = item.copy()
        venda_encontrada = pd.DataFrame()
        tipo_match = "SEM_MATCH"
        
        cliente_id = item['cliente_id']
        os_chave = item['os_chave']
        numero_os = item['numero_os']
        cliente_nome = item['cliente_nome']
        data_compra = item['data_compra']
        loja_nome = item['loja_nome']
        
        clientes_processados.add(cliente_id)
        
        # Estratégia 1: Buscar por cliente_id
        if cliente_id and not pd.isna(cliente_id):
            venda_encontrada = encontrar_vendas_por_cliente_id(vendas_df, cliente_id)
            if not venda_encontrada.empty:
                tipo_match = "CLIENTE_ID"
                stats['matches_por_cliente_id'] += 1
        
        # Estratégia 2: Buscar por OS se não encontrou por cliente_id
        if venda_encontrada.empty and (os_chave or numero_os):
            venda_encontrada = encontrar_vendas_por_os(vendas_df, os_chave, numero_os, loja_nome)
            if not venda_encontrada.empty:
                tipo_match = "OS_NUMERO"
                stats['matches_por_os'] += 1
        
        # Estratégia 3: Buscar por dados do cliente se não encontrou
        if venda_encontrada.empty and cliente_nome:
            venda_encontrada = encontrar_vendas_por_dados_cliente(vendas_df, cliente_nome, data_compra, loja_nome)
            if not venda_encontrada.empty:
                tipo_match = "NOME_CLIENTE"
                stats['matches_por_nome'] += 1
        
        # Se encontrou venda, pegar a primeira (ou mais relevante)
        if not venda_encontrada.empty:
            venda = venda_encontrada.iloc[0]
            # Usar venda_uuid se existir, senão gerar novo
            venda_id = venda.get('venda_uuid') or venda.get('uuid') or venda.get('id') or str(uuid.uuid4())
            item_processado['venda_id'] = venda_id
            item_processado['match_tipo'] = tipo_match
            item_processado['venda_valor_total'] = venda.get('valor_total')
            item_processado['venda_data'] = venda.get('data_venda') or venda.get('data_compra')
            stats['itens_com_venda_id'] += 1
        else:
            # Criar nova venda para itens sem match
            item_processado['venda_id'] = str(uuid.uuid4())
            item_processado['match_tipo'] = "NOVA_VENDA"
            stats['sem_match'] += 1
        
        itens_processados.append(item_processado)
    
    stats['clientes_unicos_processados'] = len(clientes_processados)
    
    # Criar DataFrame final
    df_final = pd.DataFrame(itens_processados)
    
    print(f"\n=== RESULTADOS DO CRUZAMENTO ===")
    print(f"Total de itens: {stats['total_itens']}")
    print(f"Matches por cliente_id: {stats['matches_por_cliente_id']}")
    print(f"Matches por OS: {stats['matches_por_os']}")
    print(f"Matches por nome: {stats['matches_por_nome']}")
    print(f"Sem match (novas vendas): {stats['sem_match']}")
    print(f"Itens com venda_id: {stats['itens_com_venda_id']}")
    print(f"Clientes únicos: {stats['clientes_unicos_processados']}")
    
    # Análise por tipo de match
    if not df_final.empty:
        print(f"\n=== DISTRIBUIÇÃO POR TIPO DE MATCH ===")
        match_counts = df_final['match_tipo'].value_counts()
        for match_type, count in match_counts.items():
            porcentagem = (count / len(df_final)) * 100
            print(f"{match_type}: {count} ({porcentagem:.1f}%)")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/processados")
    
    # Arquivo completo com cruzamento
    arquivo_completo = output_dir / f"OSS_ITENS_CRUZAMENTO_COMPLETO_{timestamp}.csv"
    df_final.to_csv(arquivo_completo, index=False, encoding='utf-8')
    print(f"\nArquivo completo: {arquivo_completo}")
    
    # Arquivo apenas com itens que têm venda_id (para Supabase)
    itens_com_venda = df_final[df_final['venda_id'].notna()].copy()
    
    # Colunas para Supabase itens_venda
    colunas_supabase = [
        'item_venda_uuid', 'venda_id', 'produto_codigo', 'produto_descricao',
        'quantidade', 'valor_unitario', 'valor_total', 'desconto', 'observacoes',
        'created_at', 'updated_at'
    ]
    
    # Garantir que todas as colunas existem
    for col in colunas_supabase:
        if col not in itens_com_venda.columns:
            itens_com_venda[col] = None
    
    df_supabase = itens_com_venda[colunas_supabase]
    arquivo_supabase = output_dir / f"OSS_ITENS_PARA_SUPABASE_FINAL_{timestamp}.csv"
    df_supabase.to_csv(arquivo_supabase, index=False, encoding='utf-8')
    print(f"Arquivo Supabase: {arquivo_supabase}")
    
    # Relatório de estatísticas
    relatorio = {
        'timestamp': timestamp,
        'estatisticas': stats,
        'distribuicao_matches': match_counts.to_dict() if not df_final.empty else {},
        'arquivo_vendas_usado': 'vendas_existentes',
        'arquivo_itens_usado': str(itens_file),
        'total_arquivos_gerados': 2
    }
    
    arquivo_relatorio = output_dir / f"OSS_RELATORIO_CRUZAMENTO_{timestamp}.json"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Relatório: {arquivo_relatorio}")
    
    print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
    print(f"Fim: {datetime.now()}")

if __name__ == "__main__":
    main()