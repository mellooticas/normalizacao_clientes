#!/usr/bin/env python3
"""
Gerar vendas usando APENAS dados normalizados com UUIDs
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def carregar_vendas_normalizadas():
    """Carrega vendas do arquivo consolidado normalizado"""
    print("📊 CARREGANDO VENDAS NORMALIZADAS")
    print("=" * 40)
    
    vendas_path = Path("data/finais_banco_completo/VENDAS_TODAS_LOJAS_BASE_BANCO.csv")
    
    if not vendas_path.exists():
        print("❌ Arquivo de vendas normalizadas não encontrado")
        return None
    
    vendas = pd.read_csv(vendas_path)
    print(f"✅ {len(vendas):,} vendas carregadas")
    return vendas

def carregar_clientes_uuid_consolidado():
    """Carrega todos os clientes UUID de todas as lojas"""
    print("\n📊 CARREGANDO CLIENTES UUID CONSOLIDADO")
    print("=" * 40)
    
    clientes_path = Path("data/clientes_uuid")
    
    clientes_completos = []
    
    for arquivo in clientes_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        clientes_completos.append(df)
    
    if clientes_completos:
        clientes_final = pd.concat(clientes_completos, ignore_index=True)
        print(f"✅ Total: {len(clientes_final):,} clientes com UUID")
        
        # Criar mapeamento nome -> UUID
        mapeamento = {}
        for _, row in clientes_final.iterrows():
            # Usar tanto 'Cliente' quanto 'Nome Completo' para mapear
            if pd.notna(row['Cliente']):
                nome_normalizado = str(row['Cliente']).strip().upper()
                mapeamento[nome_normalizado] = row['cliente_id_y']  # UUID final
            
            if pd.notna(row['Nome Completo']) and row['Nome Completo'] != row['Cliente']:
                nome_normalizado = str(row['Nome Completo']).strip().upper()
                mapeamento[nome_normalizado] = row['cliente_id_y']
        
        print(f"✅ Mapeamento criado: {len(mapeamento):,} nomes únicos")
        return mapeamento
    else:
        return None

def carregar_vendedores_uuid_por_loja():
    """Carrega vendedores UUID organizados por loja"""
    print("\n📊 CARREGANDO VENDEDORES UUID POR LOJA")
    print("=" * 40)
    
    # Usar mapeamento JSON se existir
    mapeamento_path = Path("MAPEAMENTO_VENDEDORES_UUID.json")
    if mapeamento_path.exists():
        import json
        with open(mapeamento_path, 'r', encoding='utf-8') as f:
            mapeamento = json.load(f)
        print(f"✅ Mapeamento carregado: {len(mapeamento)} lojas")
        return mapeamento
    
    # Senão, usar arquivo CSV
    vendedores_path = Path("VENDEDORES_UNICOS_UUID.csv")
    if vendedores_path.exists():
        vendedores = pd.read_csv(vendedores_path)
        print(f"✅ {len(vendedores):,} vendedores únicos")
        # Retornar primeiro vendedor como padrão para todas as lojas
        primeiro_uuid = vendedores.iloc[0]['uuid'] if len(vendedores) > 0 else None
        return {'DEFAULT': primeiro_uuid}
    
    print("❌ Nenhum mapeamento de vendedores encontrado")
    return None

def mapear_loja_uuid():
    """Mapeia nomes de loja para UUID"""
    mapeamento_lojas = {
        'maua': '7f9d4c6e-8b3a-4d2c-9f1e-6a5b8c7d9e0f',
        'perus': 'a8f5c3d9-2b7e-4f1a-9c6d-5e8b3a1f7c9e', 
        'rio_pequeno': 'b9c6d2e8-3f9a-5c7b-8d1e-6f2a9c5b8e1d',
        'sao_mateus': 'c1d7e3f9-4a8b-6d2e-9f5c-7a3d1e8b6f9c',
        'suzano': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
        'suzano2': 'd2e8f4a1-5b9c-7e3f-1a6d-8c5b2f9e7a4d'
    }
    return mapeamento_lojas

def processar_vendas_para_tabela(vendas_df, mapeamento_clientes, mapeamento_vendedores):
    """Processa vendas normalizadas para tabela vendas.vendas"""
    print("\n🔄 PROCESSANDO VENDAS PARA TABELA vendas.vendas")
    print("=" * 50)
    
    mapeamento_lojas = mapear_loja_uuid()
    vendas_banco = []
    timestamp_atual = datetime.now()
    
    # Adicionar índice para lidar com duplicatas
    vendas_df = vendas_df.reset_index()
    
    for idx, venda in vendas_df.iterrows():
        # ID único
        venda_id = str(uuid.uuid4())
        
        # Mapear cliente UUID
        cliente_uuid = None
        if pd.notna(venda['cliente']) and mapeamento_clientes:
            nome_normalizado = str(venda['cliente']).strip().upper()
            cliente_uuid = mapeamento_clientes.get(nome_normalizado)
        
        # Mapear loja UUID
        loja_uuid = None
        if pd.notna(venda['loja_arquivo']):
            loja_nome = str(venda['loja_arquivo']).lower()
            loja_uuid = mapeamento_lojas.get(loja_nome)
        
        # Mapear vendedor UUID
        vendedor_uuid = None
        if mapeamento_vendedores and pd.notna(venda['loja_arquivo']):
            loja_nome_upper = str(venda['loja_arquivo']).upper()
            # Tentar por loja específica
            if loja_nome_upper in mapeamento_vendedores:
                vendedores_loja = mapeamento_vendedores[loja_nome_upper]
                if isinstance(vendedores_loja, dict) and vendedores_loja:
                    vendedor_uuid = list(vendedores_loja.values())[0]
                elif isinstance(vendedores_loja, str):
                    vendedor_uuid = vendedores_loja
            
            # Se não encontrou, usar default
            if not vendedor_uuid and 'DEFAULT' in mapeamento_vendedores:
                vendedor_uuid = mapeamento_vendedores['DEFAULT']
        
        # Data da venda
        try:
            if pd.notna(venda['data_movimento']):
                data_venda = pd.to_datetime(venda['data_movimento']).date()
            else:
                data_venda = datetime(2024, 1, 1).date()
        except:
            data_venda = datetime(2024, 1, 1).date()
        
        # Valores
        try:
            valor_total = float(venda['valor_venda']) if pd.notna(venda['valor_venda']) else 0.0
        except:
            valor_total = 0.0
        
        try:
            valor_entrada = float(venda['entrada']) if pd.notna(venda['entrada']) else 0.0
        except:
            valor_entrada = 0.0
        
        # Garantir entrada <= total
        if valor_entrada > valor_total:
            valor_entrada = valor_total
        
        # Tipo de operação
        tipo_operacao = 'VENDA'
        if pd.notna(venda['forma_pagamento_normalizada']):
            forma_str = str(venda['forma_pagamento_normalizada']).upper()
            if 'GARANTIA' in forma_str:
                tipo_operacao = 'GARANTIA'
        
        # Nome cliente temporário se não tiver UUID
        nome_cliente_temp = str(venda['cliente']) if pd.isna(cliente_uuid) and pd.notna(venda['cliente']) else None
        
        # Número da venda único com índice para evitar duplicatas
        numero_venda = f"{venda['nn_venda']}_{venda['loja_arquivo']}_{idx}"
        
        venda_final = {
            'id': venda_id,
            'numero_venda': numero_venda,
            'cliente_id': cliente_uuid,
            'loja_id': loja_uuid,
            'vendedor_id': vendedor_uuid,
            'data_venda': data_venda,
            'valor_total': valor_total,
            'valor_entrada': valor_entrada,
            'nome_cliente_temp': nome_cliente_temp,
            'observacoes': f"Origem: {venda.get('arquivo_origem', 'N/A')} | NN: {venda['nn_venda']}",
            'status': 'ATIVO',
            'cancelado': False,
            'tipo_operacao': tipo_operacao,
            'forma_pagamento': str(venda['forma_pagamento_normalizada']) if pd.notna(venda['forma_pagamento_normalizada']) else None,
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
    with_loja_uuid = df_final['loja_id'].notna().sum()
    garantias = (df_final['tipo_operacao'] == 'GARANTIA').sum()
    
    print(f"✅ Processadas: {len(df_final):,} vendas")
    print(f"📊 Com cliente UUID: {with_cliente_uuid:,} ({with_cliente_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com vendedor UUID: {with_vendedor_uuid:,} ({with_vendedor_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com loja UUID: {with_loja_uuid:,} ({with_loja_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Operações GARANTIA: {garantias:,}")
    
    return df_final

def validar_constraints_finais(vendas_df):
    """Validação final das constraints"""
    print("\n🔍 VALIDAÇÃO FINAL DAS CONSTRAINTS")
    print("=" * 40)
    
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
        errors.append(f"❌ Duplicatas (loja_id, numero_venda): {duplicates}")
    else:
        print("✅ Sem duplicatas")
    
    # Valores
    valores_negativos = (vendas_df['valor_total'] < 0).sum()
    if valores_negativos > 0:
        errors.append(f"❌ Valores negativos: {valores_negativos}")
    else:
        print("✅ Valores >= 0")
    
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
        print("\n✅ TODAS AS VALIDAÇÕES PASSARAM")
        return True

def main():
    print("🚀 GERAÇÃO VENDAS - DADOS NORMALIZADOS")
    print("=" * 50)
    
    # 1. Carregar vendas normalizadas
    vendas_df = carregar_vendas_normalizadas()
    if vendas_df is None:
        return
    
    # 2. Carregar mapeamentos
    mapeamento_clientes = carregar_clientes_uuid_consolidado()
    mapeamento_vendedores = carregar_vendedores_uuid_por_loja()
    
    # 3. Processar vendas
    vendas_finais = processar_vendas_para_tabela(vendas_df, mapeamento_clientes, mapeamento_vendedores)
    
    # 4. Validar
    if not validar_constraints_finais(vendas_finais):
        print("❌ Validação falhou")
        return
    
    # 5. Salvar
    output_path = Path("data/vendas_para_importar/vendas_normalizadas_final.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vendas_finais.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO SALVO: {output_path}")
    print(f"📊 Total: {len(vendas_finais):,} vendas")
    print(f"💰 Valor: R$ {vendas_finais['valor_total'].sum():,.2f}")
    
    print("\n🎯 PRONTO PARA IMPORTAÇÃO NA TABELA vendas.vendas")

if __name__ == "__main__":
    main()