#!/usr/bin/env python3
"""
Script final para cruzamento completo DAV vs Vendas
Com normalização correta dos números de OS
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def normalizar_numero_os(numero):
    """Normaliza números de OS removendo prefixos e zeros à esquerda"""
    if pd.isna(numero):
        return None
    
    numero_str = str(numero).strip()
    
    # Remove .0 se existir
    if numero_str.endswith('.0'):
        numero_str = numero_str[:-2]
    
    # Remove prefixos 4200 e 4800
    if numero_str.startswith('4200'):
        numero_str = numero_str[4:]
    elif numero_str.startswith('4800'):
        numero_str = numero_str[4:]
    
    # Remove zeros à esquerda para cruzamento
    return numero_str.lstrip('0') if numero_str else None

def cruzamento_final_dav_vendas():
    """Cruzamento final e completo entre DAV e Vendas"""
    
    print("🎯 === CRUZAMENTO FINAL DAV vs VENDAS === 🎯")
    
    # 1. Carregar dados
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    # DAV
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_normalizada_20251104_224904.csv')
    dav['os_normalizada'] = dav['nro_os_original'].apply(normalizar_numero_os)
    print(f"✅ DAV: {len(dav):,} registros, {dav['os_normalizada'].nunique():,} OS únicas")
    
    # Vendas com OS
    vendas_os = pd.read_csv('data_backup/vendas_os_completo.csv')
    vendas_os_clean = vendas_os[vendas_os['os_n'].notna() & (vendas_os['os_n'] != '')]
    vendas_os_clean['os_normalizada'] = vendas_os_clean['os_n'].astype(str)
    print(f"✅ Vendas OS: {len(vendas_os_clean):,} registros, {vendas_os_clean['os_normalizada'].nunique():,} OS únicas")
    
    # 2. Fazer cruzamento
    print("\n🔗 === REALIZANDO CRUZAMENTO === 🔗")
    
    dav_os_set = set(dav['os_normalizada'].dropna())
    vendas_os_set = set(vendas_os_clean['os_normalizada'].dropna())
    os_comuns = dav_os_set & vendas_os_set
    
    print(f"📊 OS em comum encontradas: {len(os_comuns):,}")
    print(f"📊 Cobertura DAV: {len(os_comuns)/len(dav_os_set)*100:.1f}%")
    print(f"📊 Cobertura Vendas: {len(os_comuns)/len(vendas_os_set)*100:.1f}%")
    
    # 3. Criar arquivo de cruzamento
    if len(os_comuns) > 0:
        print(f"\n💾 === GERANDO ARQUIVO DE CRUZAMENTO === 💾")
        
        cruzamentos = []
        
        for os_numero in os_comuns:
            # Pegar dados DAV
            dav_matches = dav[dav['os_normalizada'] == os_numero]
            vendas_matches = vendas_os_clean[vendas_os_clean['os_normalizada'] == os_numero]
            
            # Para cada combinação
            for _, dav_row in dav_matches.iterrows():
                for _, venda_row in vendas_matches.iterrows():
                    cruzamento = {
                        # Dados básicos
                        'os_numero': os_numero,
                        'os_original_dav': dav_row['nro_os_original'],
                        'os_original_venda': venda_row['os_n'],
                        
                        # Dados DAV
                        'dav_arquivo': dav_row['arquivo_origem'],
                        'dav_cliente_id': dav_row['cliente_id'],
                        'dav_cliente_nome': dav_row['cliente_nome'],
                        'dav_data_os': dav_row['data_os'],
                        'dav_data_entrega': dav_row['data_entrega'],
                        'dav_valor_bruto': dav_row['valor_bruto'],
                        'dav_valor_liquido': dav_row['valor_liquido'],
                        'dav_loja': dav_row['loja_nome'],
                        'dav_vendedor_id': dav_row['vendedor_id'],
                        'dav_vendedor_nome': dav_row['vendedor_nome'],
                        'dav_status': dav_row['status'],
                        'dav_origem': dav_row['origem'],
                        'dav_descricao': dav_row['descricao'],
                        
                        # Dados Vendas
                        'venda_loja': venda_row['loja'],
                        'venda_data': venda_row['data_de_compra'],
                        'venda_consultor': venda_row['consultor'],
                        'venda_cliente_nome': venda_row['nome'],
                        'venda_cpf': venda_row['cpf'],
                        'venda_telefone': venda_row['telefone'],
                        'venda_celular': venda_row['celular'],
                        'venda_email': venda_row['email'],
                        'venda_prev_entrega': venda_row['prev_de_entr'],
                        'venda_como_conheceu': venda_row['como_conheceu'],
                        'venda_total': venda_row['total'],
                        'venda_pagto_1': venda_row['pagto_1'],
                        'venda_sinal_1': venda_row['sinal_1'],
                        'venda_resta': venda_row['resta'],
                        'venda_origem': venda_row['origem']
                    }
                    
                    cruzamentos.append(cruzamento)
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_cruzamento = f"data/originais/controles_gerais/cruzamento_final_dav_vendas_{timestamp}.csv"
        
        df_cruzamento = pd.DataFrame(cruzamentos)
        df_cruzamento.to_csv(arquivo_cruzamento, index=False)
        
        print(f"✅ Arquivo salvo: {arquivo_cruzamento}")
        print(f"📁 Total de registros: {len(df_cruzamento):,}")
        
        # 4. Análise dos dados cruzados
        print(f"\n📊 === ANÁLISE DOS DADOS CRUZADOS === 📊")
        
        print(f"📋 Lojas em comum:")
        loja_summary = df_cruzamento.groupby(['dav_loja', 'venda_loja']).size().reset_index(name='count')
        for _, row in loja_summary.iterrows():
            print(f"   {row['dav_loja']} ↔ {row['venda_loja']}: {row['count']:,} OS")
        
        print(f"\n💰 Valores:")
        valor_dav = pd.to_numeric(df_cruzamento['dav_valor_liquido'], errors='coerce').sum()
        valor_venda = pd.to_numeric(df_cruzamento['venda_total'], errors='coerce').sum()
        print(f"   DAV valor total: R$ {valor_dav:,.2f}")
        print(f"   Venda valor total: R$ {valor_venda:,.2f}")
        print(f"   Diferença: R$ {abs(valor_dav - valor_venda):,.2f}")
        
        print(f"\n📅 Período:")
        datas_dav = pd.to_datetime(df_cruzamento['dav_data_os'], errors='coerce')
        datas_venda = pd.to_datetime(df_cruzamento['venda_data'], errors='coerce')
        print(f"   DAV: {datas_dav.min().strftime('%Y-%m-%d')} → {datas_dav.max().strftime('%Y-%m-%d')}")
        print(f"   Vendas: {datas_venda.min().strftime('%Y-%m-%d')} → {datas_venda.max().strftime('%Y-%m-%d')}")
        
        # 5. Análise de qualidade dos dados
        print(f"\n🔍 === QUALIDADE DOS DADOS === 🔍")
        
        # Comparar nomes de clientes
        df_cruzamento['nomes_similares'] = df_cruzamento.apply(
            lambda row: 1 if str(row['dav_cliente_nome']).upper().strip() == str(row['venda_cliente_nome']).upper().strip() else 0,
            axis=1
        )
        
        nomes_iguais = df_cruzamento['nomes_similares'].sum()
        print(f"📝 Nomes de clientes iguais: {nomes_iguais:,} de {len(df_cruzamento):,} ({nomes_iguais/len(df_cruzamento)*100:.1f}%)")
        
        # Comparar datas
        df_cruzamento['datas_proximas'] = df_cruzamento.apply(
            lambda row: 1 if abs((pd.to_datetime(row['dav_data_os'], errors='coerce') - 
                                 pd.to_datetime(row['venda_data'], errors='coerce')).days) <= 30 else 0,
            axis=1
        )
        
        datas_proximas = df_cruzamento['datas_proximas'].sum()
        print(f"📅 Datas próximas (±30 dias): {datas_proximas:,} de {len(df_cruzamento):,} ({datas_proximas/len(df_cruzamento)*100:.1f}%)")
        
        # 6. Gerar arquivo de OS não encontradas
        print(f"\n📋 === OS NÃO ENCONTRADAS === 📋")
        
        # DAV sem match
        dav_sem_match = dav[~dav['os_normalizada'].isin(os_comuns)].copy()
        print(f"📊 DAV sem match: {len(dav_sem_match):,} OS")
        
        arquivo_dav_sem_match = f"data/originais/controles_gerais/dav_sem_match_{timestamp}.csv"
        dav_sem_match.to_csv(arquivo_dav_sem_match, index=False)
        print(f"💾 Salvo: {arquivo_dav_sem_match}")
        
        # Vendas sem match
        vendas_sem_match = vendas_os_clean[~vendas_os_clean['os_normalizada'].isin(os_comuns)].copy()
        print(f"📊 Vendas sem match: {len(vendas_sem_match):,} OS")
        
        arquivo_vendas_sem_match = f"data/originais/controles_gerais/vendas_sem_match_{timestamp}.csv"
        vendas_sem_match.to_csv(arquivo_vendas_sem_match, index=False)
        print(f"💾 Salvo: {arquivo_vendas_sem_match}")
    
    else:
        print("❌ Nenhuma OS em comum encontrada")
    
    # 7. Resumo final
    print(f"\n🎯 === RESUMO FINAL === 🎯")
    print(f"✅ Processamento concluído com sucesso!")
    print(f"📊 {len(os_comuns):,} OS cruzadas de {len(dav_os_set):,} DAV e {len(vendas_os_set):,} Vendas")
    print(f"💾 Arquivos gerados na pasta: data/originais/controles_gerais/")
    print(f"🕐 Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    cruzamento_final_dav_vendas()