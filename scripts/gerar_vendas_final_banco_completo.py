#!/usr/bin/env python3
"""
Gerar vendas finais para importação usando dados com UUIDs completos
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def carregar_vendas_completas():
    """Carrega todas as vendas com UUIDs enriquecidos"""
    print("📊 CARREGANDO VENDAS COM UUIDs COMPLETOS")
    print("=" * 50)
    
    base_path = Path("data/originais/cxs/extraidos_corrigidos/vendas")
    
    vendas_completas = []
    
    arquivos_completos = [
        "vendas_maua_com_uuids_enriquecido_completo.csv",
        "vendas_perus_com_uuids_enriquecido_completo.csv", 
        "vendas_rio_pequeno_com_uuids_enriquecido_completo.csv",
        "vendas_sao_mateus_com_uuids_enriquecido_completo.csv",
        "vendas_suzano2_com_uuids_enriquecido_completo.csv",
        "vendas_suzano_com_uuids_enriquecido_completo.csv"
    ]
    
    for arquivo in arquivos_completos:
        arquivo_path = base_path / arquivo
        if arquivo_path.exists():
            print(f"📥 Carregando: {arquivo}")
            df = pd.read_csv(arquivo_path)
            print(f"   Registros: {len(df):,}")
            vendas_completas.append(df)
    
    if vendas_completas:
        vendas_final = pd.concat(vendas_completas, ignore_index=True)
        print(f"\n✅ Total consolidado: {len(vendas_final):,} vendas")
        return vendas_final
    else:
        print("❌ Nenhum arquivo encontrado")
        return None

def carregar_vendedores_uuid():
    """Carrega mapeamento de vendedores para UUID"""
    print("\n📊 CARREGANDO VENDEDORES UUID")
    print("=" * 30)
    
    vendedores_path = Path("VENDEDORES_UNICOS_UUID.csv")
    
    if not vendedores_path.exists():
        print("❌ Arquivo de vendedores UUID não encontrado")
        return None
    
    vendedores = pd.read_csv(vendedores_path)
    print(f"✅ {len(vendedores):,} vendedores com UUID carregados")
    print(f"Colunas: {list(vendedores.columns)}")
    
    # Criar mapeamento nome -> UUID
    mapeamento = {}
    for _, row in vendedores.iterrows():
        vendedor_nome = str(row['nome_padronizado']).strip().upper()
        mapeamento[vendedor_nome] = row['uuid']
    
    print(f"✅ Mapeamento criado: {len(mapeamento):,} vendedores")
    return mapeamento

def mapear_vendedor_uuid(vendedor_nome, mapeamento_vendedores):
    """Mapeia vendedor para UUID"""
    if pd.isna(vendedor_nome) or not mapeamento_vendedores:
        return None
    
    vendedor_normalizado = str(vendedor_nome).strip().upper()
    return mapeamento_vendedores.get(vendedor_normalizado)

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
    
    print(f"✅ Mapeamento criado: {len(mapeamento):,} nomes")
    return mapeamento

def mapear_cliente_uuid(nome_cliente, mapeamento_clientes):
    """Mapeia nome do cliente para UUID"""
    if pd.isna(nome_cliente) or not mapeamento_clientes:
        return None
    
    nome_normalizado = str(nome_cliente).strip().upper()
    return mapeamento_clientes.get(nome_normalizado)

def processar_vendas_para_banco(vendas_df, mapeamento_clientes, mapeamento_vendedores):
    """Processa vendas para formato final do banco"""
    print("\n🔄 PROCESSANDO VENDAS PARA BANCO")
    print("=" * 40)
    
    # Preparar DataFrame final
    vendas_banco = []
    
    for _, venda in vendas_df.iterrows():
        # Gerar ID único para venda
        venda_id = str(uuid.uuid4())
        
        # Mapear cliente UUID
        cliente_uuid = mapear_cliente_uuid(venda['cliente'], mapeamento_clientes)
        
        # Por enquanto vendedor_uuid será None, pois precisa cruzar com OSs
        # Isso será feito em uma segunda etapa
        vendedor_uuid = None
        
        # Converter data
        try:
            if pd.notna(venda['data_movimento']):
                data_venda = pd.to_datetime(venda['data_movimento'], dayfirst=True).date()
            else:
                # Usar data padrão se não tiver data
                data_venda = datetime(2024, 1, 1).date()
        except:
            # Usar data padrão em caso de erro
            data_venda = datetime(2024, 1, 1).date()
        
        # Converter valores
        try:
            valor = float(venda['valor_venda']) if pd.notna(venda['valor_venda']) else 0.0
        except:
            valor = 0.0
        
        try:
            entrada = float(venda['entrada']) if pd.notna(venda['entrada']) else 0.0
        except:
            entrada = 0.0
        
        venda_final = {
            'id': venda_id,
            'numero_venda': str(venda['nn_venda']),
            'cliente_id': cliente_uuid,
            'vendedor_id': vendedor_uuid,
            'loja_id': venda.get('loja_id'),
            'forma_pagamento_id': venda.get('forma_pagamento_uuid'),
            'canal_captacao_id': venda.get('canal_captacao_uuid'),
            'data_venda': data_venda,
            'valor_total': valor,
            'valor_entrada': entrada,
            'observacoes': f"Origem: {venda.get('arquivo_origem', 'N/A')}",
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        vendas_banco.append(venda_final)
    
    df_final = pd.DataFrame(vendas_banco)
    
    print(f"✅ Processadas: {len(df_final):,} vendas")
    
    # Estatísticas
    with_cliente_uuid = df_final['cliente_id'].notna().sum()
    with_vendedor_uuid = df_final['vendedor_id'].notna().sum()
    with_loja_id = df_final['loja_id'].notna().sum()
    
    print(f"📊 Com cliente UUID: {with_cliente_uuid:,} ({with_cliente_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com vendedor UUID: {with_vendedor_uuid:,} ({with_vendedor_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com loja ID: {with_loja_id:,} ({with_loja_id/len(df_final)*100:.1f}%)")
    
    return df_final

def validar_constrainsts(vendas_df):
    """Valida constraints da tabela vendas.vendas"""
    print("\n🔍 VALIDANDO CONSTRAINTS")
    print("=" * 30)
    
    errors = []
    
    # Valores únicos para vendas (considerando que vendedor_id pode ser null)
    required_fields = ['id', 'numero_venda', 'loja_id', 'data_venda', 'valor_total']
    for field in required_fields:
        nulls = vendas_df[field].isna().sum()
        if nulls > 0:
            errors.append(f"❌ {field}: {nulls} valores nulos")
        else:
            print(f"✅ {field}: todos preenchidos")
    
    # Valores únicos
    duplicated_ids = vendas_df['id'].duplicated().sum()
    if duplicated_ids > 0:
        errors.append(f"❌ IDs duplicados: {duplicated_ids}")
    else:
        print("✅ IDs únicos")
    
    # Valores positivos
    negative_values = (vendas_df['valor_total'] < 0).sum()
    if negative_values > 0:
        errors.append(f"❌ Valores negativos: {negative_values}")
    else:
        print("✅ Valores não negativos")
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n✅ TODAS AS CONSTRAINTS VÁLIDAS")
        return True

def main():
    print("🚀 GERAÇÃO FINAL DE VENDAS PARA BANCO")
    print("=" * 50)
    
    # 1. Carregar vendas completas
    vendas_df = carregar_vendas_completas()
    if vendas_df is None:
        return
    
    # 2. Carregar mapeamentos
    mapeamento_clientes = carregar_clientes_uuid()
    mapeamento_vendedores = carregar_vendedores_uuid()
    
    # 3. Processar vendas
    vendas_banco = processar_vendas_para_banco(vendas_df, mapeamento_clientes, mapeamento_vendedores)
    
    # 4. Validar constraints
    if not validar_constrainsts(vendas_banco):
        print("❌ Falha na validação. Corrigir erros antes de continuar.")
        return
    
    # 5. Salvar resultado
    output_path = Path("data/vendas_para_importar/vendas_final_banco_completo.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    vendas_banco.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO SALVO: {output_path}")
    print(f"📊 Total de vendas: {len(vendas_banco):,}")
    print(f"💰 Valor total: R$ {vendas_banco['valor_total'].sum():,.2f}")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Revisar arquivo gerado")
    print("2. Importar para tabela vendas.vendas")
    print("3. Validar dados no banco")

if __name__ == "__main__":
    main()