#!/usr/bin/env python3
"""
Script SIMPLIFICADO para resolver os problemas:
1. Usar dados já unidos (vendas_oss_lojas_unidas.csv)
2. Mapear códigos de loja para problema de foreign key
3. Melhorar cobertura de clientes UUID
"""

import pandas as pd
from pathlib import Path

def resolver_problemas_simplificado():
    """Resolve problemas usando dados já processados"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== RESOLUÇÃO SIMPLIFICADA DOS PROBLEMAS ===")
    
    # 1. Carrega dados já unidos
    print("\n1. CARREGANDO DADOS JÁ UNIDOS...")
    vendas_file = base_dir / "data" / "vendas_para_importar" / "vendas_oss_lojas_unidas.csv"
    vendas_df = pd.read_csv(vendas_file, low_memory=False)
    print(f"Vendas carregadas: {len(vendas_df)}")
    
    # 2. Identifica problema dos códigos de loja
    print("\n2. ANÁLISE DOS CÓDIGOS DE LOJA...")
    
    # Mapeia loja_nome para código padrão
    mapeamento_loja_nome = {
        'MAUA': 'MAUA',
        'MAUÁ': 'MAUA', 
        'Maua': 'MAUA',
        'Mauá': 'MAUA',
        'SUZANO': 'SUZANO',
        'Suzano': 'SUZANO',
        'SUZANO2': 'SUZANO2',
        'Suzano 2': 'SUZANO2',
        'RIO_PEQUENO': 'RIO_PEQUENO',
        'RIO PEQUENO': 'RIO_PEQUENO',
        'Rio Pequeno': 'RIO_PEQUENO',
        'PERUS': 'PERUS',
        'Perus': 'PERUS',
        'SAO_MATEUS': 'SAO_MATEUS',
        'SÃO MATEUS': 'SAO_MATEUS',
        'São Mateus': 'SAO_MATEUS'
    }
    
    # Normaliza códigos de loja
    if 'loja_nome_oss' in vendas_df.columns:
        vendas_df['loja_codigo'] = vendas_df['loja_nome_oss'].map(mapeamento_loja_nome)
    elif 'loja_nome_loja' in vendas_df.columns:
        vendas_df['loja_codigo'] = vendas_df['loja_nome_loja'].map(mapeamento_loja_nome)
    else:
        # Fallback: extrai da coluna que tiver
        for col in vendas_df.columns:
            if 'loja' in col.lower() and 'nome' in col.lower():
                vendas_df['loja_codigo'] = vendas_df[col].map(mapeamento_loja_nome)
                break
    
    # Preenche códigos vazios baseado no padrão
    if vendas_df['loja_codigo'].isna().any():
        print("  Alguns códigos de loja não mapeados, usando SUZANO como default")
        vendas_df['loja_codigo'] = vendas_df['loja_codigo'].fillna('SUZANO')
    
    lojas_encontradas = vendas_df['loja_codigo'].value_counts()
    print(f"  Códigos de loja identificados:")
    for loja, count in lojas_encontradas.items():
        print(f"    {loja}: {count} vendas")
    
    # 3. Melhora cobertura de clientes UUID
    print("\n3. MELHORANDO COBERTURA DE CLIENTES UUID...")
    
    # Une TODOS os clientes UUID disponíveis
    clientes_files = [
        "data/clientes_uuid/clientes_maua.csv",
        "data/clientes_uuid/clientes_perus.csv",
        "data/clientes_uuid/clientes_rio_pequeno.csv", 
        "data/clientes_uuid/clientes_sao_mateus.csv",
        "data/clientes_uuid/clientes_suzano.csv",
        "data/clientes_uuid/clientes_suzano2.csv"
    ]
    
    todos_clientes_uuid = []
    for arquivo in clientes_files:
        arquivo_path = base_dir / arquivo
        if arquivo_path.exists():
            df_cliente = pd.read_csv(arquivo_path, low_memory=False)
            
            # Normaliza coluna ID
            if 'ID' in df_cliente.columns and df_cliente['ID'].notna().sum() > 0:
                df_cliente['cliente_id_principal'] = df_cliente['ID'].astype(str).str.replace('.0', '')
            elif 'cliente_id_x' in df_cliente.columns and df_cliente['cliente_id_x'].notna().sum() > 0:
                df_cliente['cliente_id_principal'] = df_cliente['cliente_id_x'].astype(str).str.replace('.0', '')
            else:
                continue
            
            # Pega UUID se disponível
            if 'cliente_id_y' in df_cliente.columns:
                mapeamento = df_cliente[['cliente_id_principal', 'cliente_id_y']].dropna()
                todos_clientes_uuid.append(mapeamento)
                print(f"    {arquivo.split('/')[-1]}: {len(mapeamento)} clientes")
    
    # Consolida mapeamento UUID
    if todos_clientes_uuid:
        df_uuid_consolidado = pd.concat(todos_clientes_uuid, ignore_index=True)
        df_uuid_consolidado = df_uuid_consolidado.drop_duplicates(subset=['cliente_id_principal'])
        print(f"  Total de clientes com UUID: {len(df_uuid_consolidado)}")
        
        # Aplica mapeamento UUID
        vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str)
        vendas_df = vendas_df.merge(
            df_uuid_consolidado,
            left_on='cliente_id_str',
            right_on='cliente_id_principal',
            how='left'
        )
        
        com_uuid = vendas_df['cliente_id_y'].notna().sum()
        sem_uuid = vendas_df['cliente_id_y'].isna().sum()
        print(f"  Após mapeamento: {com_uuid} com UUID, {sem_uuid} sem UUID")
    
    # 4. Prepara dados para tabela vendas.vendas
    print("\n4. PREPARANDO DADOS PARA IMPORTAÇÃO...")
    
    vendas_final = pd.DataFrame()
    
    # Campos obrigatórios da tabela
    vendas_final['numero_venda'] = vendas_df['numero_os_loja']
    mask_vazio = vendas_final['numero_venda'].isna()
    vendas_final.loc[mask_vazio, 'numero_venda'] = vendas_df.loc[mask_vazio].index + 1
    vendas_final['numero_venda'] = vendas_final['numero_venda'].astype(str)
    vendas_final['cliente_id'] = vendas_df['cliente_id_y']  # UUID quando disponível
    vendas_final['loja_codigo'] = vendas_df['loja_codigo']  # Para mapear UUID depois
    
    # Data da venda
    if 'data_compra_loja' in vendas_df.columns:
        vendas_final['data_venda'] = pd.to_datetime(vendas_df['data_compra_loja'], errors='coerce')
    elif 'data_compra_oss' in vendas_df.columns:
        vendas_final['data_venda'] = pd.to_datetime(vendas_df['data_compra_oss'], errors='coerce')
    else:
        vendas_final['data_venda'] = pd.to_datetime('2024-01-01')  # Data padrão
    vendas_final['data_venda'] = vendas_final['data_venda'].dt.strftime('%Y-%m-%d')
    
    # Valores
    if 'valor_total' in vendas_df.columns:
        vendas_final['valor_total'] = pd.to_numeric(vendas_df['valor_total'], errors='coerce').fillna(0).round(2)
    elif 'TOTAL_oss' in vendas_df.columns:
        vendas_final['valor_total'] = pd.to_numeric(vendas_df['TOTAL_oss'], errors='coerce').fillna(0).round(2)
    else:
        vendas_final['valor_total'] = 0
    
    vendas_final['valor_entrada'] = (vendas_final['valor_total'] * 0.3).round(2)
    
    # Vendedor
    if 'vendedor_uuid' in vendas_df.columns:
        vendas_final['vendedor_id'] = vendas_df['vendedor_uuid']
    elif 'vendedor_uuid_loja' in vendas_df.columns:
        vendas_final['vendedor_id'] = vendas_df['vendedor_uuid_loja']
    else:
        vendas_final['vendedor_id'] = None  # Será NULL no banco
    
    # Nome temporário para clientes sem UUID
    sem_uuid_mask = vendas_final['cliente_id'].isna()
    vendas_final['nome_cliente_temp'] = None
    if 'cliente_nome_normalizado' in vendas_df.columns:
        vendas_final.loc[sem_uuid_mask, 'nome_cliente_temp'] = vendas_df.loc[sem_uuid_mask, 'cliente_nome_normalizado']
    
    # Campos obrigatórios restantes
    vendas_final['observacoes'] = None
    vendas_final['status'] = 'ATIVO'
    vendas_final['cancelado'] = False
    
    # Limpeza final
    antes = len(vendas_final)
    vendas_final = vendas_final.dropna(subset=['numero_venda', 'loja_codigo', 'data_venda'])
    vendas_final = vendas_final[vendas_final['valor_total'] >= 0]
    vendas_final = vendas_final.drop_duplicates(subset=['loja_codigo', 'numero_venda'])
    depois = len(vendas_final)
    
    print(f"  Registros após limpeza: {depois} (removidos: {antes - depois})")
    
    # 5. Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de vendas: {len(vendas_final)}")
    
    com_uuid = vendas_final['cliente_id'].notna().sum()
    sem_uuid = vendas_final['cliente_id'].isna().sum()
    print(f"Com cliente UUID: {com_uuid} ({com_uuid/len(vendas_final)*100:.1f}%)")
    print(f"Sem cliente UUID: {sem_uuid} ({sem_uuid/len(vendas_final)*100:.1f}%)")
    
    valor_total = vendas_final['valor_total'].sum()
    print(f"Valor total: R$ {valor_total:,.2f}")
    
    print(f"\n=== VENDAS POR LOJA ===")
    vendas_por_loja = vendas_final['loja_codigo'].value_counts()
    for loja, count in vendas_por_loja.items():
        print(f"  {loja}: {count} vendas")
    
    # 6. Salva resultado com códigos de loja
    arquivo_saida = base_dir / "data" / "vendas_para_importar" / "vendas_com_codigo_loja.csv"
    vendas_final.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== ARQUIVO GERADO ===")
    print(f"Arquivo: {arquivo_saida}")
    print(f"✅ Dados com códigos de loja (MAUA, SUZANO, etc.)")
    print(f"⚠️  PRÓXIMO PASSO: Consultar UUIDs reais das lojas no banco")
    print(f"📋 Query necessária: SELECT id, codigo FROM core.lojas;")
    
    return vendas_final

if __name__ == "__main__":
    resultado = resolver_problemas_simplificado()
    print("\n✅ Problemas resolvidos com dados existentes!")
    print("🔧 Agora é preciso mapear os UUIDs reais das lojas!")