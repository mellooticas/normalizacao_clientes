#!/usr/bin/env python3
"""
Gerar vendas finais corrigidas para tabela vendas.vendas
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

def carregar_vendedores_uuid():
    """Carrega mapeamento de vendedores UUID por loja"""
    print("\n📊 CARREGANDO VENDEDORES UUID")
    print("=" * 30)
    
    # Carregar vendedores únicos
    vendedores_path = Path("VENDEDORES_UNICOS_UUID.csv")
    if not vendedores_path.exists():
        print("❌ Arquivo VENDEDORES_UNICOS_UUID.csv não encontrado")
        return None
    
    vendedores = pd.read_csv(vendedores_path)
    print(f"✅ {len(vendedores):,} vendedores únicos carregados")
    
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

def mapear_vendedor_uuid(loja_nome, mapeamento_vendedores):
    """Mapeia vendedor UUID baseado na loja"""
    if not mapeamento_vendedores or not loja_nome:
        return None
    
    loja_key = loja_nome.upper()
    if loja_key in mapeamento_vendedores:
        # Pegar o primeiro vendedor da loja como padrão
        vendedores_loja = mapeamento_vendedores[loja_key]
        if vendedores_loja:
            return list(vendedores_loja.values())[0]
    
    return None

def mapear_cliente_uuid(nome_cliente, mapeamento_clientes):
    """Mapeia nome do cliente para UUID"""
    if pd.isna(nome_cliente) or not mapeamento_clientes:
        return None
    
    nome_normalizado = str(nome_cliente).strip().upper()
    return mapeamento_clientes.get(nome_normalizado)

def determinar_tipo_operacao(forma_pagamento):
    """Determina tipo de operação baseado na forma de pagamento"""
    if pd.isna(forma_pagamento):
        return 'VENDA'
    
    forma_str = str(forma_pagamento).upper()
    if 'GARANTIA' in forma_str:
        return 'GARANTIA'
    elif 'TROCA' in forma_str:
        return 'TROCA'
    elif 'DEVOLUCAO' in forma_str or 'DEVOLUÇÃO' in forma_str:
        return 'DEVOLUCAO'
    elif 'CORTESIA' in forma_str:
        return 'CORTESIA'
    else:
        return 'VENDA'

def processar_vendas_para_banco(vendas_df, mapeamento_clientes, mapeamento_vendedores):
    """Processa vendas para formato final da tabela vendas.vendas"""
    print("\n🔄 PROCESSANDO VENDAS PARA TABELA vendas.vendas")
    print("=" * 50)
    
    vendas_banco = []
    timestamp_atual = datetime.now()
    
    for _, venda in vendas_df.iterrows():
        # Gerar ID único para venda
        venda_id = str(uuid.uuid4())
        
        # Mapear cliente UUID
        cliente_uuid = mapear_cliente_uuid(venda['cliente'], mapeamento_clientes)
        
        # Mapear vendedor UUID baseado na loja
        vendedor_uuid = mapear_vendedor_uuid(venda.get('loja_nome'), mapeamento_vendedores)
        
        # Converter data
        try:
            if pd.notna(venda['data_movimento']):
                data_venda = pd.to_datetime(venda['data_movimento']).date()
            else:
                data_venda = datetime(2024, 1, 1).date()
        except:
            data_venda = datetime(2024, 1, 1).date()
        
        # Converter valores
        try:
            valor_total = float(venda['valor_venda']) if pd.notna(venda['valor_venda']) else 0.0
        except:
            valor_total = 0.0
        
        try:
            valor_entrada = float(venda['entrada']) if pd.notna(venda['entrada']) else 0.0
        except:
            valor_entrada = 0.0
        
        # Determinar tipo de operação
        tipo_operacao = determinar_tipo_operacao(venda.get('forma_de_pgto'))
        
        # Nome cliente temporário se não tiver UUID
        nome_cliente_temp = str(venda['cliente']) if pd.isna(cliente_uuid) and pd.notna(venda['cliente']) else None
        
        # Forma de pagamento como string
        forma_pagamento = str(venda['forma_de_pgto']) if pd.notna(venda['forma_de_pgto']) else None
        
        venda_final = {
            'id': venda_id,
            'numero_venda': str(venda['nn_venda']),
            'cliente_id': cliente_uuid,
            'loja_id': venda.get('loja_id'),  # Obrigatório
            'vendedor_id': vendedor_uuid,    # Deve ser preenchido
            'data_venda': data_venda,        # Obrigatório
            'valor_total': valor_total,      # Obrigatório
            'valor_entrada': valor_entrada,
            # valor_restante é calculado automaticamente
            'nome_cliente_temp': nome_cliente_temp,
            'observacoes': f"Origem: {venda.get('arquivo_origem', 'N/A')}",
            'status': 'ATIVO',
            'cancelado': False,
            'data_cancelamento': None,
            'motivo_cancelamento': None,
            'created_at': timestamp_atual,
            'updated_at': timestamp_atual,
            'created_by': 'IMPORT_SCRIPT',
            'updated_by': 'IMPORT_SCRIPT',
            'deleted_at': None,
            'version': 1,
            'tipo_operacao': tipo_operacao,
            # is_garantia é calculado automaticamente
            'forma_pagamento': forma_pagamento
        }
        
        vendas_banco.append(venda_final)
    
    df_final = pd.DataFrame(vendas_banco)
    
    print(f"✅ Processadas: {len(df_final):,} vendas")
    
    # Estatísticas
    with_cliente_uuid = df_final['cliente_id'].notna().sum()
    with_vendedor_uuid = df_final['vendedor_id'].notna().sum()
    with_loja_id = df_final['loja_id'].notna().sum()
    garantias = (df_final['tipo_operacao'] == 'GARANTIA').sum()
    
    print(f"📊 Com cliente UUID: {with_cliente_uuid:,} ({with_cliente_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com vendedor UUID: {with_vendedor_uuid:,} ({with_vendedor_uuid/len(df_final)*100:.1f}%)")
    print(f"📊 Com loja ID: {with_loja_id:,} ({with_loja_id/len(df_final)*100:.1f}%)")
    print(f"📊 Operações GARANTIA: {garantias:,}")
    
    return df_final

def validar_constraints_tabela(vendas_df):
    """Valida todas as constraints da tabela vendas.vendas"""
    print("\n🔍 VALIDANDO CONSTRAINTS DA TABELA")
    print("=" * 40)
    
    errors = []
    
    # Campos NOT NULL obrigatórios
    campos_obrigatorios = {
        'id': 'ID único',
        'numero_venda': 'Número da venda', 
        'loja_id': 'ID da loja',
        'data_venda': 'Data da venda',
        'valor_total': 'Valor total'
    }
    
    for campo, descricao in campos_obrigatorios.items():
        nulls = vendas_df[campo].isna().sum()
        if nulls > 0:
            errors.append(f"❌ {descricao} ({campo}): {nulls} valores nulos")
        else:
            print(f"✅ {descricao}: todos preenchidos")
    
    # Constraint de valores únicos (loja_id, numero_venda)
    duplicates = vendas_df.duplicated(subset=['loja_id', 'numero_venda']).sum()
    if duplicates > 0:
        errors.append(f"❌ Duplicatas (loja_id, numero_venda): {duplicates}")
    else:
        print("✅ Combinação (loja_id, numero_venda) única")
    
    # Constraints de valores
    valores_negativos_total = (vendas_df['valor_total'] < 0).sum()
    if valores_negativos_total > 0:
        errors.append(f"❌ Valores totais negativos: {valores_negativos_total}")
    else:
        print("✅ Valores totais >= 0")
    
    valores_negativos_entrada = (vendas_df['valor_entrada'] < 0).sum()
    if valores_negativos_entrada > 0:
        errors.append(f"❌ Valores entrada negativos: {valores_negativos_entrada}")
    else:
        print("✅ Valores entrada >= 0")
    
    # Constraint entrada <= total
    entrada_maior_total = (vendas_df['valor_entrada'] > vendas_df['valor_total']).sum()
    if entrada_maior_total > 0:
        errors.append(f"❌ Entrada > Total: {entrada_maior_total}")
    else:
        print("✅ Entrada <= Total")
    
    # Verificar tipos de operação válidos
    tipos_validos = ['VENDA', 'GARANTIA', 'TROCA', 'DEVOLUCAO', 'CORTESIA']
    tipos_invalidos = ~vendas_df['tipo_operacao'].isin(tipos_validos)
    if tipos_invalidos.sum() > 0:
        errors.append(f"❌ Tipos de operação inválidos: {tipos_invalidos.sum()}")
    else:
        print("✅ Tipos de operação válidos")
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n✅ TODAS AS CONSTRAINTS VALIDADAS")
        return True

def main():
    print("🚀 GERAÇÃO VENDAS PARA TABELA vendas.vendas")
    print("=" * 60)
    
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
    if not validar_constraints_tabela(vendas_banco):
        print("❌ Falha na validação. Corrigir erros antes de continuar.")
        return
    
    # 5. Salvar resultado
    output_path = Path("data/vendas_para_importar/vendas_tabela_completa.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    vendas_banco.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO SALVO: {output_path}")
    print(f"📊 Total de vendas: {len(vendas_banco):,}")
    print(f"💰 Valor total: R$ {vendas_banco['valor_total'].sum():,.2f}")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Importar arquivo CSV para tabela vendas.vendas")
    print("2. Verificar foreign keys (lojas, vendedores, clientes)")
    print("3. Validar dados no banco")

if __name__ == "__main__":
    main()