#!/usr/bin/env python3
"""
Processamento das vendas VIXEN com ligação aos clientes UUID
Suzano e Mauá - dados mais estruturados
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import uuid

def processar_vendas_vixen():
    """Processa vendas VIXEN com ligação aos UUIDs dos clientes"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🚀 === PROCESSAMENTO VENDAS VIXEN === 🚀")
    
    # 1. Carrega dados de vendas VIXEN
    print(f"\n=== FASE 1: CARREGANDO DADOS VIXEN ===")
    
    # Arquivo principal de vendas VIXEN (carnê Lancaster)
    arquivo_vixen_principal = base_dir / "data" / "originais" / "controles_gerais" / "trans_financ" / "separados_por_pagamento" / "ordem_servico_pdv_carne_lancaster.csv"
    
    if arquivo_vixen_principal.exists():
        vendas_vixen_df = pd.read_csv(arquivo_vixen_principal)
        print(f"✅ Vendas VIXEN carregadas: {len(vendas_vixen_df)} registros")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_vixen_principal}")
        return None
    
    # 2. Análise inicial dos dados
    print(f"\n=== FASE 2: ANÁLISE INICIAL ===")
    
    print(f"📊 Total registros VIXEN: {len(vendas_vixen_df)}")
    print(f"📅 Período: {vendas_vixen_df['Dh.emissão'].min()} a {vendas_vixen_df['Dh.emissão'].max()}")
    
    # Operações únicas
    operacoes_unicas = vendas_vixen_df['ID operação'].nunique()
    print(f"🎯 Operações únicas: {operacoes_unicas}")
    
    # Clientes únicos
    clientes_unicos = vendas_vixen_df['ID'].nunique()
    print(f"👥 Clientes únicos: {clientes_unicos}")
    
    # Estabelecimentos
    estabelecimentos = vendas_vixen_df['ID emp.'].unique()
    print(f"🏪 Estabelecimentos: {estabelecimentos}")
    
    # Análise por estabelecimento
    por_estabelecimento = vendas_vixen_df['ID emp.'].value_counts()
    print(f"\n📍 Por estabelecimento:")
    for estab, count in por_estabelecimento.items():
        print(f"   ID {estab}: {count} registros")
    
    # 3. Normalização dos dados
    print(f"\n=== FASE 3: NORMALIZAÇÃO DOS DADOS ===")
    
    # Agrupa por operação (uma venda = uma operação)
    vendas_agrupadas = vendas_vixen_df.groupby('ID operação').agg({
        'Nro.operação': 'first',
        'ID emp.': 'first', 
        'ID': 'first',
        'Cliente': 'first',
        'Dh.emissão': 'first',
        'Dh.transação': 'first',
        'Vl.movimento': 'sum',  # Soma todos os valores da venda
        'ID.5': 'first',  # ID vendedor
        'Vendedor': 'first',
        'arquivo_origem': 'first',
        'mes_origem': 'first'
    }).reset_index()
    
    print(f"✅ Vendas agrupadas: {len(vendas_agrupadas)} vendas únicas")
    
    # 4. Mapeamento de estabelecimentos para lojas
    print(f"\n=== FASE 4: MAPEAMENTO LOJAS ===")
    
    # Carrega UUIDs das lojas (do sistema anterior)
    lojas_map = {
        42: {  # Suzano
            'loja_id': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
            'nome': 'SUZANO'
        },
        48: {  # Mauá  
            'loja_id': 'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89',
            'nome': 'MAUA'
        }
    }
    
    # Aplica mapeamento
    vendas_agrupadas['loja_id'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('loja_id'))
    vendas_agrupadas['loja_nome'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('nome'))
    
    # Verifica mapeamento
    lojas_encontradas = vendas_agrupadas['loja_nome'].value_counts()
    print(f"📍 Distribuição por loja:")
    for loja, count in lojas_encontradas.items():
        print(f"   {loja}: {count} vendas")
    
    # 5. Ligação com clientes UUID
    print(f"\n=== FASE 5: LIGAÇÃO COM CLIENTES UUID ===")
    
    # Carrega clientes UUID consolidado
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    
    # Cria mapeamento ID → UUID
    cliente_para_uuid = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    # Aplica nas vendas
    vendas_agrupadas['cliente_id_str'] = vendas_agrupadas['ID'].astype(str)
    vendas_agrupadas['cliente_uuid'] = vendas_agrupadas['cliente_id_str'].map(cliente_para_uuid)
    
    # Estatísticas de ligação
    com_uuid = vendas_agrupadas['cliente_uuid'].notna().sum()
    sem_uuid = len(vendas_agrupadas) - com_uuid
    
    print(f"✅ Vendas COM UUID: {com_uuid} ({com_uuid/len(vendas_agrupadas)*100:.1f}%)")
    print(f"❌ Vendas SEM UUID: {sem_uuid} ({sem_uuid/len(vendas_agrupadas)*100:.1f}%)")
    
    # 6. Mapeamento de vendedores
    print(f"\n=== FASE 6: MAPEAMENTO VENDEDORES ===")
    
    # Carrega mapeamento de vendedores (do sistema anterior)
    try:
        vendedores_map = pd.read_csv(base_dir / "MAPEAMENTO_VENDEDORES_UUID.json")
        # Implementar mapeamento se arquivo existir
        print(f"ℹ️  Mapeamento vendedores será implementado depois")
    except:
        print(f"ℹ️  Mapeamento vendedores manual necessário")
    
    # Por enquanto, usa vendedor genérico
    vendas_agrupadas['vendedor_id'] = '00000000-0000-0000-0000-000000000000'  # Vendedor genérico
    
    # 7. Preparação para banco
    print(f"\n=== FASE 7: PREPARAÇÃO PARA BANCO ===")
    
    # Converte datas
    vendas_agrupadas['data_venda'] = pd.to_datetime(vendas_agrupadas['Dh.emissão']).dt.strftime('%Y-%m-%d')
    
    # Prepara campos
    vendas_agrupadas['numero_venda'] = vendas_agrupadas['Nro.operação']
    vendas_agrupadas['valor_total'] = vendas_agrupadas['Vl.movimento'].abs()  # Valor absoluto
    vendas_agrupadas['valor_entrada'] = 0  # VIXEN não tem entrada específica
    vendas_agrupadas['nome_cliente_temp'] = vendas_agrupadas['Cliente']
    vendas_agrupadas['observacoes'] = 'Importado do VIXEN - Carnê Lancaster'
    vendas_agrupadas['status'] = 'ATIVO'
    vendas_agrupadas['cancelado'] = False
    vendas_agrupadas['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_agrupadas['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 8. Separa vendas prontas vs pendentes
    vendas_prontas = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].notna()].copy()
    vendas_pendentes = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].isna()].copy()
    
    print(f"✅ Vendas prontas: {len(vendas_prontas)}")
    print(f"⏳ Vendas pendentes: {len(vendas_pendentes)}")
    
    # 9. Gera arquivos
    print(f"\n=== FASE 8: GERANDO ARQUIVOS ===")
    
    # Arquivo 1: Vendas prontas para importar
    if len(vendas_prontas) > 0:
        vendas_importar = vendas_prontas[[
            'numero_venda', 'cliente_uuid', 'loja_id', 'vendedor_id',
            'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
            'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
        ]].copy()
        
        vendas_importar.rename(columns={'cliente_uuid': 'cliente_id'}, inplace=True)
        
        # Remove duplicatas se houver
        vendas_importar = vendas_importar.drop_duplicates(subset=['loja_id', 'numero_venda'], keep='first')
        
        arquivo_vixen_pronto = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_PRONTO_PARA_IMPORTAR.csv"
        vendas_importar.to_csv(arquivo_vixen_pronto, index=False)
        
        print(f"📁 ARQUIVO VIXEN PRONTO:")
        print(f"   {arquivo_vixen_pronto}")
        print(f"   {len(vendas_importar)} vendas")
    
    # Arquivo 2: Vendas pendentes
    if len(vendas_pendentes) > 0:
        vendas_pendentes_export = vendas_pendentes[[
            'numero_venda', 'ID', 'cliente_id_str', 'Cliente', 'loja_id', 'loja_nome',
            'data_venda', 'valor_total', 'observacoes'
        ]].copy()
        
        arquivo_vixen_pendente = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_PENDENTES_UUID.csv"
        vendas_pendentes_export.to_csv(arquivo_vixen_pendente, index=False)
        
        print(f"📁 ARQUIVO VIXEN PENDENTE:")
        print(f"   {arquivo_vixen_pendente}")
        print(f"   {len(vendas_pendentes)} vendas")
    
    # 10. Comandos SQL
    if len(vendas_prontas) > 0:
        print(f"\n🛠️  COMANDOS SQL PARA VIXEN:")
        print(f"   -- Importa vendas VIXEN")
        print(f"   \\copy vendas.vendas FROM '{arquivo_vixen_pronto}' CSV HEADER;")
        print(f"   -- Verifica")
        print(f"   SELECT COUNT(*) FROM vendas.vendas WHERE observacoes LIKE '%VIXEN%';")
    
    print(f"\n🎉 PROCESSAMENTO VIXEN CONCLUÍDO!")
    print(f"✅ {com_uuid} vendas prontas ({com_uuid/len(vendas_agrupadas)*100:.1f}%)")
    print(f"⏳ {sem_uuid} vendas pendentes ({sem_uuid/len(vendas_agrupadas)*100:.1f}%)")
    
    return vendas_agrupadas

if __name__ == "__main__":
    resultado = processar_vendas_vixen()
    if resultado is not None:
        print(f"\n🚀 Vendas VIXEN processadas: {len(resultado)} operações!")