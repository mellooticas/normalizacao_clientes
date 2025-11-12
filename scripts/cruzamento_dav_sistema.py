#!/usr/bin/env python3
"""
Script para análise de cruzamento entre Lista DAV e Sistema atual
Objetivo: Identificar possíveis conexões entre OS (DAV) e Vendas (Sistema)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analisar_cruzamento_dav_sistema():
    """Análise completa de cruzamento entre DAV e Sistema"""
    
    print("🔍 === ANÁLISE CRUZAMENTO DAV vs SISTEMA === 🔍")
    
    # 1. Carregar dados DAV
    print("\n📊 === CARREGANDO DADOS === 📊")
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_normalizada_20251104_224904.csv')
    print(f"✅ DAV carregado: {len(dav):,} registros, {dav['nro_os_normalizado'].nunique():,} OS únicas")
    
    # 2. Carregar dados do Sistema
    vendas = pd.read_csv('data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv')
    entregas = pd.read_csv('data/vendas_para_importar/entregas_os_final_datas_corrigidas.csv')
    print(f"✅ Vendas carregadas: {len(vendas):,} registros")
    print(f"✅ Entregas carregadas: {len(entregas):,} registros")
    
    # 3. Análise temporal
    print("\n📅 === ANÁLISE TEMPORAL === 📅")
    
    # DAV
    dav['data_os_dt'] = pd.to_datetime(dav['data_os'], errors='coerce')
    dav_periodo = f"{dav['data_os_dt'].min().strftime('%Y-%m-%d')} → {dav['data_os_dt'].max().strftime('%Y-%m-%d')}"
    print(f"📊 DAV período: {dav_periodo}")
    
    # Vendas
    vendas['data_venda_dt'] = pd.to_datetime(vendas['data_venda'], errors='coerce')
    vendas_periodo = f"{vendas['data_venda_dt'].min().strftime('%Y-%m-%d')} → {vendas['data_venda_dt'].max().strftime('%Y-%m-%d')}"
    print(f"📊 Vendas período: {vendas_periodo}")
    
    # Entregas
    entregas['data_entrega_dt'] = pd.to_datetime(entregas['data_entrega'], errors='coerce')
    entregas_periodo = f"{entregas['data_entrega_dt'].min().strftime('%Y-%m-%d')} → {entregas['data_entrega_dt'].max().strftime('%Y-%m-%d')}"
    print(f"📊 Entregas período: {entregas_periodo}")
    
    # 4. Análise por loja
    print("\n🏪 === ANÁLISE POR LOJA === 🏪")
    
    print("📊 DAV por loja:")
    dav_lojas = dav['loja_nome'].value_counts()
    for loja, qtd in dav_lojas.items():
        print(f"   {loja}: {qtd:,} OS")
    
    # Mapear UUIDs das lojas para nomes
    print("\n📊 Vendas por loja (UUID → Nome):")
    loja_map = {
        '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'SUZANO',
        '5f8e7c2a-9b4d-4e6a-8f3b-1c2e5d8b9a7f': 'MAUA',
        '3a7c4f8e-2b5d-4a8c-9e1f-6d3b7c4f8e2a': 'PERUS',
        '8f3b1c2e-5d8b-4a7c-9e1f-6d3b7c4f8e2a': 'RIO_PEQUENO',
        '2e5d8b9a-7c4f-4e6a-8f3b-1c2e5d8b9a7f': 'SAO_MATEUS',
        '6d3b7c4f-8e2a-4a7c-9e1f-2e5d8b9a7c4f': 'SUZANO2'
    }
    
    vendas_lojas = vendas['loja_id'].value_counts()
    for loja_uuid, qtd in vendas_lojas.items():
        loja_nome = loja_map.get(loja_uuid, loja_uuid[:8])
        print(f"   {loja_nome}: {qtd:,} vendas")
    
    # 5. Análise de clientes
    print("\n👥 === ANÁLISE DE CLIENTES === 👥")
    
    print(f"📊 DAV clientes únicos: {dav['cliente_id'].nunique():,}")
    print(f"📊 Vendas clientes únicos: {vendas['cliente_id'].nunique():,}")
    
    # Verificar se há cliente_ids em comum
    dav_clientes = set(dav['cliente_id'].dropna())
    vendas_clientes = set(vendas['cliente_id'].dropna())
    clientes_comuns = dav_clientes & vendas_clientes
    
    print(f"📊 Clientes em comum: {len(clientes_comuns):,}")
    
    if len(clientes_comuns) > 0:
        print("✅ ENCONTRADAS CONEXÕES POR CLIENTE!")
        print(f"📋 Exemplos de clientes comuns: {list(clientes_comuns)[:5]}")
        
        # Análise detalhada dos clientes comuns
        dav_comuns = dav[dav['cliente_id'].isin(clientes_comuns)]
        vendas_comuns = vendas[vendas['cliente_id'].isin(clientes_comuns)]
        
        print(f"\n📊 OS de clientes comuns na DAV: {len(dav_comuns):,}")
        print(f"📊 Vendas de clientes comuns no Sistema: {len(vendas_comuns):,}")
        
        # Salvar dados dos clientes comuns para análise
        arquivo_comuns = f"data/originais/controles_gerais/clientes_comuns_dav_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Criar DataFrame consolidado
        consolidado = []
        
        for cliente_id in list(clientes_comuns)[:100]:  # Primeiros 100 para análise
            dav_cliente = dav[dav['cliente_id'] == cliente_id]
            vendas_cliente = vendas[vendas['cliente_id'] == cliente_id]
            
            for _, dav_row in dav_cliente.iterrows():
                for _, venda_row in vendas_cliente.iterrows():
                    consolidado.append({
                        'cliente_id': cliente_id,
                        'cliente_nome': dav_row['cliente_nome'],
                        'dav_os': dav_row['nro_os_normalizado'],
                        'dav_data': dav_row['data_os'],
                        'dav_valor': dav_row['valor_liquido'],
                        'dav_loja': dav_row['loja_nome'],
                        'venda_numero': venda_row['numero_venda'],
                        'venda_data': venda_row['data_venda'],
                        'venda_valor': venda_row['valor_total'],
                        'venda_loja_uuid': venda_row['loja_id']
                    })
        
        if consolidado:
            df_consolidado = pd.DataFrame(consolidado)
            df_consolidado.to_csv(arquivo_comuns, index=False)
            print(f"💾 Arquivo salvo: {arquivo_comuns}")
            print(f"📁 Registros salvos: {len(df_consolidado):,}")
    
    else:
        print("❌ NENHUM CLIENTE EM COMUM ENCONTRADO")
    
    # 6. Análise de valores
    print("\n💰 === ANÁLISE DE VALORES === 💰")
    
    # Converter valores para numérico
    dav['valor_liquido'] = pd.to_numeric(dav['valor_liquido'], errors='coerce')
    vendas['valor_total'] = pd.to_numeric(vendas['valor_total'], errors='coerce')
    
    dav_valor_total = dav['valor_liquido'].sum()
    vendas_valor_total = vendas['valor_total'].sum()
    
    print(f"📊 DAV valor total: R$ {dav_valor_total:,.2f}")
    print(f"📊 Vendas valor total: R$ {vendas_valor_total:,.2f}")
    
    print(f"📊 DAV valor médio: R$ {dav['valor_liquido'].mean():.2f}")
    print(f"📊 Vendas valor médio: R$ {vendas['valor_total'].mean():.2f}")
    
    # 7. Análise de vendedores
    print("\n👨‍💼 === ANÁLISE DE VENDEDORES === 👨‍💼")
    
    print(f"📊 DAV vendedores únicos: {dav['vendedor_id'].nunique():,}")
    print(f"📊 Vendas vendedores únicos: {vendas['vendedor_id'].nunique():,}")
    
    # Verificar vendedores em comum
    dav_vendedores = set(dav['vendedor_id'].dropna())
    vendas_vendedores = set(vendas['vendedor_id'].dropna())
    vendedores_comuns = dav_vendedores & vendas_vendedores
    
    print(f"📊 Vendedores em comum: {len(vendedores_comuns):,}")
    
    if len(vendedores_comuns) > 0:
        print("✅ VENDEDORES EM COMUM ENCONTRADOS!")
        print(f"📋 Exemplos: {list(vendedores_comuns)[:5]}")
    
    # 8. Resumo e recomendações
    print("\n🎯 === RESUMO E RECOMENDAÇÕES === 🎯")
    
    if len(clientes_comuns) > 0:
        print("✅ CONEXÃO POSSÍVEL: Clientes em comum identificados")
        print("📊 Próximos passos:")
        print("   1. Analisar arquivo de clientes comuns gerado")
        print("   2. Verificar se datas e valores coincidem")
        print("   3. Mapear OS para Vendas quando possível")
        print("   4. Integrar dados DAV como informação adicional")
    
    elif len(vendedores_comuns) > 0:
        print("⚠️ CONEXÃO LIMITADA: Apenas vendedores em comum")
        print("📊 Recomendação: Usar DAV como sistema independente")
    
    else:
        print("❌ SISTEMAS INDEPENDENTES: Nenhuma conexão direta")
        print("📊 Recomendação:")
        print("   1. Manter DAV como sistema separado de OS")
        print("   2. Integrar como módulo adicional")
        print("   3. Usar para análise de trabalhos técnicos")
    
    print(f"\n💾 Script executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    analisar_cruzamento_dav_sistema()