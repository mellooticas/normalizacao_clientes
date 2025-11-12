#!/usr/bin/env python3
"""
Corrigir dados de vendas antes de gerar para tabela
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def limpar_e_consolidar_vendas():
    """Limpa e consolida vendas removendo duplicatas e corrigindo valores"""
    print("🧹 LIMPEZA E CONSOLIDAÇÃO DE VENDAS")
    print("=" * 50)
    
    base_path = Path("data/originais/cxs/extraidos_corrigidos/vendas")
    
    arquivos_completos = [
        "vendas_maua_com_uuids_enriquecido_completo.csv",
        "vendas_perus_com_uuids_enriquecido_completo.csv", 
        "vendas_rio_pequeno_com_uuids_enriquecido_completo.csv",
        "vendas_sao_mateus_com_uuids_enriquecido_completo.csv",
        "vendas_suzano2_com_uuids_enriquecido_completo.csv",
        "vendas_suzano_com_uuids_enriquecido_completo.csv"
    ]
    
    vendas_limpas = []
    total_removidos = 0
    
    for arquivo in arquivos_completos:
        arquivo_path = base_path / arquivo
        if arquivo_path.exists():
            print(f"\n📥 Processando: {arquivo}")
            df = pd.read_csv(arquivo_path)
            inicial = len(df)
            
            # 1. Remover linhas com nn_venda vazio ou inválido
            df = df[df['nn_venda'].notna()]
            df = df[df['nn_venda'] != '']
            df = df[df['nn_venda'] != ',']
            
            # 2. Converter valores para numérico
            df['valor_venda_num'] = pd.to_numeric(df['valor_venda'], errors='coerce')
            df['entrada_num'] = pd.to_numeric(df['entrada'], errors='coerce')
            
            # 3. Tratar valores nulos
            df['valor_venda_num'] = df['valor_venda_num'].fillna(0)
            df['entrada_num'] = df['entrada_num'].fillna(0)
            
            # 4. Corrigir casos onde entrada > valor_venda
            # Se valor_venda = 0 e entrada > 0, usar entrada como valor_venda
            mask_valor_zero = (df['valor_venda_num'] == 0) & (df['entrada_num'] > 0)
            df.loc[mask_valor_zero, 'valor_venda_num'] = df.loc[mask_valor_zero, 'entrada_num']
            
            # Se entrada > valor_venda (e valor_venda > 0), usar valor_venda como entrada
            mask_entrada_maior = df['entrada_num'] > df['valor_venda_num']
            df.loc[mask_entrada_maior, 'entrada_num'] = df.loc[mask_entrada_maior, 'valor_venda_num']
            
            # 5. Consolidar duplicatas por (loja_id, nn_venda, data_movimento)
            # Adicionar data para diferenciar vendas com mesmo número em datas diferentes
            df['data_apenas'] = pd.to_datetime(df['data_movimento'], errors='coerce').dt.date
            
            # Somar valores das duplicatas na mesma data
            df_agrupado = df.groupby(['loja_id', 'nn_venda', 'data_apenas']).agg({
                'cliente': 'first',  # Primeiro cliente
                'forma_de_pgto': 'first',  # Primeira forma de pagamento
                'valor_venda_num': 'sum',  # Somar valores
                'entrada_num': 'sum',  # Somar entradas
                'data_movimento': 'first',  # Primeira data
                'arquivo_origem': 'first',
                'forma_pagamento_uuid': 'first',
                'forma_pagamento_normalizada': 'first',
                'loja_nome': 'first'
            }).reset_index()
            
            final = len(df_agrupado)
            removidos = inicial - final
            total_removidos += removidos
            
            print(f"   Inicial: {inicial:,}")
            print(f"   Final: {final:,}")
            print(f"   Removidos/Consolidados: {removidos:,}")
            
            vendas_limpas.append(df_agrupado)
    
    if vendas_limpas:
        vendas_final = pd.concat(vendas_limpas, ignore_index=True)
        print(f"\n✅ Total consolidado: {len(vendas_final):,} vendas")
        print(f"📊 Total removidos/consolidados: {total_removidos:,}")
        return vendas_final
    else:
        return None

def carregar_clientes_uuid():
    """Carrega mapeamento de clientes para UUID"""
    print("\n📊 CARREGANDO CLIENTES UUID")
    print("=" * 30)
    
    clientes_path = Path("data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv")
    
    if not clientes_path.exists():
        print("❌ Arquivo de clientes UUID não encontrado")
        return None
    
    clientes = pd.read_csv(clientes_path)
    print(f"✅ {len(clientes):,} clientes com UUID carregados")
    
    # Criar mapeamento nome -> UUID
    mapeamento = {}
    for _, row in clientes.iterrows():
        nome_normalizado = str(row['nome']).strip().upper()
        mapeamento[nome_normalizado] = row['id']
    
    return mapeamento

def carregar_vendedores_uuid():
    """Carrega mapeamento de vendedores UUID por loja"""
    print("\n📊 CARREGANDO VENDEDORES UUID")
    print("=" * 30)
    
    # Carregar mapeamento por loja
    mapeamento_path = Path("MAPEAMENTO_VENDEDORES_UUID.json")
    if not mapeamento_path.exists():
        print("❌ Arquivo MAPEAMENTO_VENDEDORES_UUID.json não encontrado")
        return None
    
    import json
    with open(mapeamento_path, 'r', encoding='utf-8') as f:
        mapeamento_lojas = json.load(f)
    
    print(f"✅ Mapeamento por loja carregado: {len(mapeamento_lojas)} lojas")
    return mapeamento_lojas

def processar_vendas_finais(vendas_df, mapeamento_clientes, mapeamento_vendedores):
    """Processa vendas limpas para formato final da tabela"""
    print("\n🔄 PROCESSANDO VENDAS PARA TABELA vendas.vendas")
    print("=" * 50)
    
    vendas_banco = []
    timestamp_atual = datetime.now()
    
    for _, venda in vendas_df.iterrows():
        # Gerar ID único
        venda_id = str(uuid.uuid4())
        
        # Mapear cliente UUID
        cliente_uuid = None
        if pd.notna(venda['cliente']) and mapeamento_clientes:
            nome_normalizado = str(venda['cliente']).strip().upper()
            cliente_uuid = mapeamento_clientes.get(nome_normalizado)
        
        # Mapear vendedor UUID baseado na loja
        vendedor_uuid = None
        if pd.notna(venda['loja_nome']) and mapeamento_vendedores:
            loja_key = str(venda['loja_nome']).upper()
            if loja_key in mapeamento_vendedores:
                vendedores_loja = mapeamento_vendedores[loja_key]
                if vendedores_loja:
                    vendedor_uuid = list(vendedores_loja.values())[0]
        
        # Data da venda
        try:
            if pd.notna(venda['data_movimento']):
                data_venda = pd.to_datetime(venda['data_movimento']).date()
            else:
                data_venda = datetime(2024, 1, 1).date()
        except:
            data_venda = datetime(2024, 1, 1).date()
        
        # Valores já limpos
        valor_total = float(venda['valor_venda_num'])
        valor_entrada = float(venda['entrada_num'])
        
        # Garantir que entrada <= total
        if valor_entrada > valor_total:
            valor_entrada = valor_total
        
        # Tipo de operação
        tipo_operacao = 'VENDA'
        if pd.notna(venda['forma_de_pgto']):
            forma_str = str(venda['forma_de_pgto']).upper()
            if 'GARANTIA' in forma_str:
                tipo_operacao = 'GARANTIA'
        
        # Nome cliente temporário se não tiver UUID
        nome_cliente_temp = str(venda['cliente']) if pd.isna(cliente_uuid) and pd.notna(venda['cliente']) else None
        
        venda_final = {
            'id': venda_id,
            'numero_venda': f"{venda['nn_venda']}_{venda['data_apenas']}",  # Único por data
            'cliente_id': cliente_uuid,
            'loja_id': venda['loja_id'],
            'vendedor_id': vendedor_uuid,
            'data_venda': data_venda,
            'valor_total': valor_total,
            'valor_entrada': valor_entrada,
            'nome_cliente_temp': nome_cliente_temp,
            'observacoes': f"Origem: {venda.get('arquivo_origem', 'N/A')} | Original: {venda['nn_venda']}",
            'status': 'ATIVO',
            'cancelado': False,
            'tipo_operacao': tipo_operacao,
            'forma_pagamento': str(venda['forma_de_pgto']) if pd.notna(venda['forma_de_pgto']) else None,
            'created_at': timestamp_atual,
            'updated_at': timestamp_atual,
            'created_by': 'IMPORT_SCRIPT',
            'updated_by': 'IMPORT_SCRIPT',
            'version': 1
        }
        
        vendas_banco.append(venda_final)
    
    df_final = pd.DataFrame(vendas_banco)
    
    # Estatísticas
    with_cliente_uuid = df_final['cliente_id'].notna().sum()
    with_vendedor_uuid = df_final['vendedor_id'].notna().sum()
    garantias = (df_final['tipo_operacao'] == 'GARANTIA').sum()
    
    print(f"✅ Processadas: {len(df_final):,} vendas")
    print(f"📊 Com cliente UUID: {with_cliente_uuid:,} ({with_cliente_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com vendedor UUID: {with_vendedor_uuid:,} ({with_vendedor_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Operações GARANTIA: {garantias:,}")
    
    return df_final

def validar_final(vendas_df):
    """Validação final"""
    print("\n🔍 VALIDAÇÃO FINAL")
    print("=" * 30)
    
    errors = []
    
    # Campos obrigatórios
    campos_obrigatorios = ['id', 'numero_venda', 'loja_id', 'data_venda', 'valor_total']
    for campo in campos_obrigatorios:
        nulls = vendas_df[campo].isna().sum()
        if nulls > 0:
            errors.append(f"❌ {campo}: {nulls} nulos")
        else:
            print(f"✅ {campo}: OK")
    
    # Duplicatas
    duplicates = vendas_df.duplicated(subset=['loja_id', 'numero_venda']).sum()
    if duplicates > 0:
        errors.append(f"❌ Duplicatas: {duplicates}")
    else:
        print("✅ Sem duplicatas")
    
    # Valores
    entrada_maior = (vendas_df['valor_entrada'] > vendas_df['valor_total']).sum()
    if entrada_maior > 0:
        errors.append(f"❌ Entrada > Total: {entrada_maior}")
    else:
        print("✅ Entrada <= Total")
    
    if errors:
        print("\n❌ ERROS:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n✅ VALIDAÇÃO PASSOU")
        return True

def main():
    print("🚀 CORREÇÃO E GERAÇÃO FINAL DE VENDAS")
    print("=" * 50)
    
    # 1. Limpar e consolidar
    vendas_df = limpar_e_consolidar_vendas()
    if vendas_df is None:
        return
    
    # 2. Carregar mapeamentos
    mapeamento_clientes = carregar_clientes_uuid()
    mapeamento_vendedores = carregar_vendedores_uuid()
    
    # 3. Processar
    vendas_finais = processar_vendas_finais(vendas_df, mapeamento_clientes, mapeamento_vendedores)
    
    # 4. Validar
    if not validar_final(vendas_finais):
        print("❌ Validação falhou")
        return
    
    # 5. Salvar
    output_path = Path("data/vendas_para_importar/vendas_corrigidas_final.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vendas_finais.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO SALVO: {output_path}")
    print(f"📊 Total: {len(vendas_finais):,} vendas")
    print(f"💰 Valor: R$ {vendas_finais['valor_total'].sum():,.2f}")

if __name__ == "__main__":
    main()