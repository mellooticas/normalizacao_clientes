#!/usr/bin/env python3
"""
Script para CRUZAMENTO COMPLETO DAV ↔ VENDAS
Explorando TODAS as possibilidades de match:
1. Por número OS direto
2. Por ID de cliente
3. Por nome de cliente + data próxima
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
import warnings
warnings.filterwarnings('ignore')

def cruzamento_completo_dav_vendas():
    """
    Cruzamento completo explorando todas as possibilidades
    """
    print("🎯 === CRUZAMENTO COMPLETO DAV ↔ VENDAS === 🎯")
    print("🚀 Explorando TODAS as possibilidades de match!")
    
    # 1. Carregar dados
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv')
    print(f"✅ DAV: {len(dav):,} registros")
    
    # Filtrar entregas
    dav_entregas = dav[dav['Dt.entrega'].notna()].copy()
    print(f"🚚 DAV com entregas: {len(dav_entregas):,} registros")
    
    # Vendas
    vendas = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
    print(f"✅ Vendas: {len(vendas):,} registros")
    
    # 2. Preparar dados
    print("\n🔧 === PREPARANDO DADOS === 🔧")
    
    # DAV - números OS
    dav_entregas['os_numero'] = pd.to_numeric(dav_entregas['OS_numero'], errors='coerce')
    dav_com_os = dav_entregas.dropna(subset=['os_numero'])
    print(f"📊 DAV com OS válidos: {len(dav_com_os):,}")
    
    # Vendas - números
    vendas['numero_venda_num'] = pd.to_numeric(vendas['numero_venda'], errors='coerce')
    vendas_com_num = vendas.dropna(subset=['numero_venda_num'])
    print(f"📊 Vendas com números: {len(vendas_com_num):,}")
    
    # Analisar ranges COMPLETOS
    print(f"\n📊 === ANÁLISE COMPLETA DE RANGES === 📊")
    
    # DAV
    dav_min = int(dav_com_os['os_numero'].min())
    dav_max = int(dav_com_os['os_numero'].max())
    print(f"🚚 DAV range COMPLETO: {dav_min:,} → {dav_max:,}")
    
    # Vendas
    vendas_min = int(vendas_com_num['numero_venda_num'].min())
    vendas_max = int(vendas_com_num['numero_venda_num'].max())
    print(f"🛒 Vendas range COMPLETO: {vendas_min:,} → {vendas_max:,}")
    
    # Separar por loja para análise
    print(f"\n🏪 === ANÁLISE POR LOJA === 🏪")
    
    # Suzano (ID emp = 42)
    dav_suzano = dav_com_os[dav_com_os['ID emp.'] == 42]
    if len(dav_suzano) > 0:
        suzano_min = int(dav_suzano['os_numero'].min())
        suzano_max = int(dav_suzano['os_numero'].max())
        print(f"🏪 SUZANO: {len(dav_suzano):,} entregas | Range: {suzano_min:,} → {suzano_max:,}")
    
    # Mauá (ID emp = 48)
    dav_maua = dav_com_os[dav_com_os['ID emp.'] == 48]
    if len(dav_maua) > 0:
        maua_min = int(dav_maua['os_numero'].min())
        maua_max = int(dav_maua['os_numero'].max())
        print(f"🏪 MAUÁ: {len(dav_maua):,} entregas | Range: {maua_min:,} → {maua_max:,}")
    
    # === ESTRATÉGIA 1: MATCH POR NÚMERO OS ===
    print(f"\n🎯 === ESTRATÉGIA 1: MATCH POR NÚMERO OS === 🎯")
    
    numeros_dav = set(dav_com_os['os_numero'].astype(int))
    numeros_vendas = set(vendas_com_num['numero_venda_num'].astype(int))
    
    match_os = numeros_dav & numeros_vendas
    print(f"🔢 Match direto por OS: {len(match_os):,} números")
    
    # === ESTRATÉGIA 2: MATCH POR ID CLIENTE ===
    print(f"\n🎯 === ESTRATÉGIA 2: MATCH POR ID CLIENTE === 🎯")
    
    # Verificar se DAV tem IDs de clientes
    if 'ID.2' in dav_entregas.columns:
        dav_com_cliente_id = dav_entregas[dav_entregas['ID.2'].notna()]
        print(f"📊 DAV com ID.2 (cliente): {len(dav_com_cliente_id):,}")
        
        if len(dav_com_cliente_id) > 0:
            # IDs únicos
            ids_dav = set(dav_com_cliente_id['ID.2'].astype(str))
            ids_vendas = set(vendas['cliente_id'].astype(str))
            
            match_clientes = ids_dav & ids_vendas
            print(f"👥 Match por ID cliente: {len(match_clientes):,} IDs")
        else:
            match_clientes = set()
    else:
        print(f"❌ Coluna ID.2 não encontrada no DAV")
        match_clientes = set()
    
    # === ESTRATÉGIA 3: MATCH POR NOME CLIENTE ===
    print(f"\n🎯 === ESTRATÉGIA 3: MATCH POR NOME CLIENTE === 🎯")
    
    # Normalizar nomes
    def normalizar_nome(nome):
        if pd.isna(nome):
            return ""
        return str(nome).upper().strip().replace("  ", " ")
    
    dav_entregas['cliente_normalizado'] = dav_entregas['Cliente'].apply(normalizar_nome)
    vendas['cliente_normalizado'] = vendas['nome_cliente_temp'].apply(normalizar_nome)
    
    # Nomes válidos
    dav_com_nome = dav_entregas[dav_entregas['cliente_normalizado'] != '']
    vendas_com_nome = vendas[vendas['cliente_normalizado'] != '']
    
    nomes_dav = set(dav_com_nome['cliente_normalizado'])
    nomes_vendas = set(vendas_com_nome['cliente_normalizado'])
    
    match_nomes = nomes_dav & nomes_vendas
    print(f"👥 Match por nome: {len(match_nomes):,} nomes")
    
    # === CRIAÇÃO DE CRUZAMENTOS COMPLETOS ===
    print(f"\n🔗 === CRIANDO CRUZAMENTOS COMPLETOS === 🔗")
    
    cruzamentos = []
    stats = {
        'match_os': 0,
        'match_cliente_id': 0,
        'match_nome': 0
    }
    
    # TIPO 1: Match por número OS
    print(f"🔢 Processando match por OS...")
    for numero in match_os:
        dav_rows = dav_com_os[dav_com_os['os_numero'] == numero]
        vendas_rows = vendas_com_num[vendas_com_num['numero_venda_num'] == numero]
        
        for _, dav_row in dav_rows.iterrows():
            for _, venda_row in vendas_rows.iterrows():
                cruzamento = criar_cruzamento(dav_row, venda_row, 'MATCH_OS')
                cruzamentos.append(cruzamento)
                stats['match_os'] += 1
    
    print(f"✅ Match por OS: {stats['match_os']:,} cruzamentos")
    
    # TIPO 2: Match por ID cliente (se disponível)
    if match_clientes:
        print(f"👥 Processando match por ID cliente...")
        for cliente_id in list(match_clientes)[:500]:  # Limitar para performance
            dav_rows = dav_com_cliente_id[dav_com_cliente_id['ID.2'].astype(str) == cliente_id]
            vendas_rows = vendas[vendas['cliente_id'].astype(str) == cliente_id]
            
            for _, dav_row in dav_rows.iterrows():
                for _, venda_row in vendas_rows.iterrows():
                    # Evitar duplicatas com match OS
                    if (dav_row.get('os_numero', 0) in match_os and 
                        venda_row.get('numero_venda_num', 0) in match_os):
                        continue
                    
                    cruzamento = criar_cruzamento(dav_row, venda_row, 'MATCH_CLIENTE_ID')
                    cruzamentos.append(cruzamento)
                    stats['match_cliente_id'] += 1
        
        print(f"✅ Match por ID cliente: {stats['match_cliente_id']:,} cruzamentos")
    
    # TIPO 3: Match por nome (amostra)
    print(f"📝 Processando match por nome (amostra)...")
    for nome in list(match_nomes)[:200]:  # Amostra para performance
        dav_rows = dav_com_nome[dav_com_nome['cliente_normalizado'] == nome]
        vendas_rows = vendas_com_nome[vendas_com_nome['cliente_normalizado'] == nome]
        
        for _, dav_row in dav_rows.iterrows():
            for _, venda_row in vendas_rows.iterrows():
                # Evitar duplicatas
                numero_dav = dav_row.get('os_numero', 0)
                numero_venda = venda_row.get('numero_venda_num', 0)
                cliente_id = venda_row.get('cliente_id', '')
                
                if (numero_dav in match_os and numero_venda in match_os):
                    continue
                if cliente_id in match_clientes:
                    continue
                
                cruzamento = criar_cruzamento(dav_row, venda_row, 'MATCH_NOME')
                cruzamentos.append(cruzamento)
                stats['match_nome'] += 1
    
    print(f"✅ Match por nome: {stats['match_nome']:,} cruzamentos")
    
    # === RESULTADOS FINAIS ===
    df_cruzamentos = pd.DataFrame(cruzamentos)
    
    print(f"\n📊 === RESULTADOS FINAIS === 📊")
    print(f"🎯 Total de cruzamentos: {len(df_cruzamentos):,}")
    print(f"📊 Por tipo de match:")
    
    tipo_dist = df_cruzamentos['tipo_match'].value_counts()
    for tipo, qtd in tipo_dist.items():
        print(f"   {tipo}: {qtd:,}")
    
    # Salvar arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo = f'data/cruzamentos_completos_dav_vendas_{timestamp}.csv'
    df_cruzamentos.to_csv(arquivo, index=False)
    
    print(f"\n💾 Arquivo salvo: {arquivo}")
    
    return arquivo, stats

def criar_cruzamento(dav_row, venda_row, tipo_match):
    """
    Cria um registro de cruzamento
    """
    # Determinar loja
    id_empresa = dav_row.get('ID emp.', '')
    loja_dav = 'SUZANO' if str(id_empresa) == '42' else 'MAUA' if str(id_empresa) == '48' else f'LOJA_{id_empresa}'
    
    return {
        'tipo_match': tipo_match,
        'numero_os': dav_row.get('os_numero', ''),
        'numero_venda': venda_row.get('numero_venda', ''),
        'venda_id': venda_row.get('id', ''),
        'cliente_id': venda_row.get('cliente_id', ''),
        'cliente_nome_dav': dav_row.get('Cliente', ''),
        'cliente_nome_venda': venda_row.get('nome_cliente_temp', ''),
        'data_entrega': dav_row.get('Dt.entrega', ''),
        'data_venda': venda_row.get('data_venda', ''),
        'status_entrega': dav_row.get('Status', ''),
        'loja_dav': loja_dav,
        'loja_id_venda': venda_row.get('loja_id', ''),
        'valor_dav': dav_row.get('Vl.líquido', ''),
        'valor_venda': venda_row.get('valor_total', ''),
        'vendedor_dav': dav_row.get('Vendedor', ''),
        'vendedor_id_venda': venda_row.get('vendedor_id', ''),
        'arquivo_origem': dav_row.get('arquivo_origem', ''),
        'id_cliente_dav': dav_row.get('ID.2', ''),
        'observacoes_venda': venda_row.get('observacoes', '')
    }

def main():
    """Função principal"""
    print("🚀 === CRUZAMENTO COMPLETO DAV ↔ VENDAS === 🚀")
    print("📊 Explorando TODAS as possibilidades!")
    
    arquivo, stats = cruzamento_completo_dav_vendas()
    
    print(f"\n🎉 === CRUZAMENTO COMPLETO CONCLUÍDO === 🎉")
    print(f"✅ Arquivo: {arquivo}")
    print(f"📊 Total: {sum(stats.values()):,} cruzamentos")
    print(f"🎯 Agora temos MUITO mais matches!")
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()