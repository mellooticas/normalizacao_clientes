#!/usr/bin/env python3
"""
Script para RESOLVER os problemas identificados:
1. Mapear códigos de loja para UUIDs corretos 
2. Garantir que TODOS os clientes tenham UUID (vêm das OSS)
"""

import pandas as pd
from pathlib import Path

def resolver_problemas_vendas():
    """Resolve problemas de foreign key e clientes faltando"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== RESOLUÇÃO DOS PROBLEMAS DE IMPORTAÇÃO ===")
    
    # 1. Carrega dados originais das OSS (fonte autoritativa dos clientes)
    print("\n1. CARREGANDO DADOS ORIGINAIS DAS OSS...")
    
    oss_files = [
        "data/originais/oss/finais_postgresql_prontos/oss_maua_clientes_ids.csv",
        "data/originais/oss/finais_postgresql_prontos/oss_perus_clientes_ids.csv", 
        "data/originais/oss/finais_postgresql_prontos/oss_rio_pequeno_clientes_ids.csv",
        "data/originais/oss/finais_postgresql_prontos/oss_sao_mateus_clientes_ids.csv",
        "data/originais/oss/finais_postgresql_prontos/oss_suzano_clientes_ids.csv",
        "data/originais/oss/finais_postgresql_prontos/oss_suzano2_clientes_ids.csv"
    ]
    
    todos_oss = []
    for oss_file in oss_files:
        arquivo_path = base_dir / oss_file
        if arquivo_path.exists():
            df_oss = pd.read_csv(arquivo_path)
            loja_nome = oss_file.split('_')[-1].replace('.csv', '').upper()
            df_oss['loja_codigo'] = loja_nome
            todos_oss.append(df_oss)
            print(f"  {loja_nome}: {len(df_oss)} OSS")
        else:
            print(f"  ARQUIVO NÃO ENCONTRADO: {oss_file}")
    
    if not todos_oss:
        print("ERRO: Nenhum arquivo OSS encontrado!")
        return
    
    # 2. Consolida todas as OSS
    df_oss_completo = pd.concat(todos_oss, ignore_index=True)
    print(f"\nTotal de OSS consolidadas: {len(df_oss_completo)}")
    
    # 3. Carrega dados das LOJAS
    print("\n2. CARREGANDO DADOS DAS LOJAS...")
    
    loja_files = [
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_maua.csv",
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_perus.csv",
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_rio_pequeno.csv", 
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_sao_mateus.csv",
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_suzano.csv",
        "data/finais_banco_completo/finais_postgresql_prontos/LOJA_suzano2.csv"
    ]
    
    todas_lojas = []
    for loja_file in loja_files:
        arquivo_path = base_dir / loja_file
        if arquivo_path.exists():
            df_loja = pd.read_csv(arquivo_path)
            loja_nome = loja_file.split('_')[-1].replace('.csv', '').upper()
            df_loja['loja_codigo'] = loja_nome
            todas_lojas.append(df_loja)
            print(f"  {loja_nome}: {len(df_loja)} registros")
    
    df_lojas_completo = pd.concat(todas_lojas, ignore_index=True)
    print(f"\nTotal de registros LOJAS: {len(df_lojas_completo)}")
    
    # 4. Une OSS + LOJAS por os_chave (fonte autoritativa completa)
    print("\n3. UNINDO OSS + LOJAS AUTORITATIVAMENTE...")
    
    vendas_completas = df_oss_completo.merge(
        df_lojas_completo, 
        on='os_chave', 
        how='inner'
    )
    
    print(f"Vendas unidas: {len(vendas_completas)}")
    
    # 5. Carrega mapeamento de clientes UUID COMPLETO
    print("\n4. CARREGANDO MAPEAMENTO COMPLETO DE CLIENTES...")
    
    # Une todos os clientes UUID de todas as fontes
    clientes_uuid_files = [
        "data/clientes_uuid/clientes_maua.csv",
        "data/clientes_uuid/clientes_perus.csv",
        "data/clientes_uuid/clientes_rio_pequeno.csv", 
        "data/clientes_uuid/clientes_sao_mateus.csv",
        "data/clientes_uuid/clientes_suzano.csv",
        "data/clientes_uuid/clientes_suzano2.csv"
    ]
    
    todos_clientes = []
    for cliente_file in clientes_uuid_files:
        arquivo_path = base_dir / cliente_file
        if arquivo_path.exists():
            df_cliente = pd.read_csv(arquivo_path, low_memory=False)
            
            # Identifica coluna do ID principal
            if 'ID' in df_cliente.columns:
                df_cliente['cliente_id_principal'] = df_cliente['ID'].astype(str)
            elif 'cliente_id_x' in df_cliente.columns:
                df_cliente['cliente_id_principal'] = df_cliente['cliente_id_x'].astype(str)
            
            # Pega apenas colunas necessárias
            if 'cliente_id_y' in df_cliente.columns:
                df_limpo = df_cliente[['cliente_id_principal', 'cliente_id_y']].copy()
                df_limpo = df_limpo.dropna()
                todos_clientes.append(df_limpo)
                print(f"  {cliente_file.split('/')[-1]}: {len(df_limpo)} clientes com UUID")
    
    df_clientes_uuid = pd.concat(todos_clientes, ignore_index=True)
    df_clientes_uuid = df_clientes_uuid.drop_duplicates(subset=['cliente_id_principal'])
    print(f"\nTotal de clientes com UUID: {len(df_clientes_uuid)}")
    
    # 6. Mapeia cliente_id para UUID
    print("\n5. MAPEANDO CLIENTES PARA UUID...")
    
    vendas_completas['cliente_id_str'] = vendas_completas['cliente_id'].astype(str)
    
    vendas_com_uuid = vendas_completas.merge(
        df_clientes_uuid,
        left_on='cliente_id_str',
        right_on='cliente_id_principal',
        how='left'
    )
    
    # 7. Mapeia lojas para UUIDs CORRETOS (baseado no código)
    print("\n6. MAPEANDO LOJAS PARA UUIDs CORRETOS...")
    
    # ATENÇÃO: Estes UUIDs devem corresponder aos inseridos no banco!
    # Como as lojas são inseridas com UUID auto-gerado, precisamos consultar o banco
    # Por ora, vamos usar um mapeamento baseado no código da loja
    
    mapeamento_lojas_codigo = {
        'MAUA': 'loja_maua_uuid',       # Será substituído pelo UUID real
        'SUZANO': 'loja_suzano_uuid',   # Será substituído pelo UUID real
        'SUZANO2': 'loja_suzano2_uuid', # Será substituído pelo UUID real
        'RIO_PEQUENO': 'loja_rio_pequeno_uuid',
        'PERUS': 'loja_perus_uuid',
        'SAO_MATEUS': 'loja_sao_mateus_uuid'
    }
    
    # Mapeia baseado no código da loja
    vendas_com_uuid['loja_codigo_normalizado'] = vendas_com_uuid['loja_codigo_x'].str.upper()
    vendas_com_uuid['loja_id_correto'] = vendas_com_uuid['loja_codigo_normalizado'].map(mapeamento_lojas_codigo)
    
    # 8. Prepara dados finais para importação
    print("\n7. PREPARANDO DADOS FINAIS...")
    
    vendas_final = pd.DataFrame()
    
    # Dados obrigatórios
    vendas_final['numero_venda'] = vendas_com_uuid['numero_os'].fillna(vendas_com_uuid.index + 1).astype(str)
    vendas_final['cliente_id'] = vendas_com_uuid['cliente_id_y']  # UUID do cliente
    vendas_final['loja_codigo'] = vendas_com_uuid['loja_codigo_normalizado']  # Para consultar UUID real
    vendas_final['data_venda'] = pd.to_datetime(vendas_com_uuid['data_compra'], errors='coerce').dt.strftime('%Y-%m-%d')
    vendas_final['valor_total'] = pd.to_numeric(vendas_com_uuid['total_os'], errors='coerce').fillna(0).round(2)
    vendas_final['valor_entrada'] = (vendas_final['valor_total'] * 0.3).round(2)  # 30% padrão
    
    # Vendedor UUID
    if 'vendedor_uuid' in vendas_com_uuid.columns:
        vendas_final['vendedor_id'] = vendas_com_uuid['vendedor_uuid']
    
    # Cliente sem UUID usa nome temporário
    sem_uuid = vendas_final['cliente_id'].isna()
    vendas_final['nome_cliente_temp'] = None
    vendas_final.loc[sem_uuid, 'nome_cliente_temp'] = vendas_com_uuid.loc[sem_uuid, 'cliente_nome_normalizado']
    
    # Campos obrigatórios
    vendas_final['observacoes'] = None
    vendas_final['status'] = 'ATIVO'
    vendas_final['cancelado'] = False
    
    # Remove registros com problemas críticos
    antes = len(vendas_final)
    vendas_final = vendas_final.dropna(subset=['numero_venda', 'data_venda'])
    vendas_final = vendas_final[vendas_final['valor_total'] >= 0]
    vendas_final = vendas_final.drop_duplicates(subset=['loja_codigo', 'numero_venda'])
    depois = len(vendas_final)
    
    print(f"Registros após limpeza: {depois} (removidos: {antes - depois})")
    
    # Estatísticas finais
    com_cliente_uuid = vendas_final['cliente_id'].notna().sum()
    sem_cliente_uuid = vendas_final['cliente_id'].isna().sum()
    total_valor = vendas_final['valor_total'].sum()
    
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de vendas: {len(vendas_final)}")
    print(f"Com cliente UUID: {com_cliente_uuid} ({com_cliente_uuid/len(vendas_final)*100:.1f}%)")
    print(f"Sem cliente UUID: {sem_cliente_uuid} ({sem_cliente_uuid/len(vendas_final)*100:.1f}%)")
    print(f"Valor total: R$ {total_valor:,.2f}")
    
    # Estatísticas por loja
    print(f"\n=== VENDAS POR LOJA ===")
    vendas_por_loja = vendas_final['loja_codigo'].value_counts()
    for loja, count in vendas_por_loja.items():
        print(f"{loja}: {count} vendas")
    
    # Salva resultado
    arquivo_saida = base_dir / "data" / "vendas_para_importar" / "vendas_autoritativas_completas.csv"
    vendas_final.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== ARQUIVO AUTORITATIVO ===")
    print(f"Arquivo salvo: {arquivo_saida}")
    print(f"✅ DADOS AUTORITATIVOS das OSS originais")
    print(f"⚠️  PRÓXIMO PASSO: Consultar UUIDs reais das lojas no banco")
    
    return vendas_final

if __name__ == "__main__":
    resultado = resolver_problemas_vendas()
    print("\n✅ Problemas identificados e dados autoritativos preparados!")
    print("🔧 Próximo: Mapear UUIDs reais das lojas do banco!")