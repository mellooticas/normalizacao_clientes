#!/usr/bin/env python3
"""
Script para criar estrutura final de cruzamento
Gera arquivo consolidado DAV vs Vendas com todas as informações
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def criar_estrutura_cruzamento():
    """
    Cria estrutura final para cruzamento DAV vs Vendas
    """
    print("🔗 === CRIANDO ESTRUTURA DE CRUZAMENTO === 🔗")
    
    # 1. Carregar dados consolidados
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    # DAV consolidado
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_final_20251104_234859.csv')
    print(f"✅ DAV carregado: {len(dav):,} registros, {dav['OS'].nunique():,} OS únicas")
    
    # Vendas com OS
    vendas_os = pd.read_csv('data_backup/vendas_os_completo.csv')
    vendas_os_clean = vendas_os[vendas_os['os_n'].notna() & (vendas_os['os_n'] != '')]
    vendas_os_clean['os_num'] = pd.to_numeric(vendas_os_clean['os_n'], errors='coerce')
    vendas_os_clean = vendas_os_clean[vendas_os_clean['os_num'].notna()]
    print(f"✅ Vendas carregadas: {len(vendas_os_clean):,} registros, {vendas_os_clean['os_num'].nunique():,} OS únicas")
    
    # 2. Identificar OS em comum
    print("\n🎯 === IDENTIFICANDO CRUZAMENTOS === 🎯")
    
    dav_os_set = set(dav['OS'].dropna())
    vendas_os_set = set(vendas_os_clean['os_num'].dropna())
    os_comuns = dav_os_set & vendas_os_set
    
    print(f"📊 OS em comum: {len(os_comuns):,}")
    print(f"📊 Cobertura DAV: {len(os_comuns)/len(dav_os_set)*100:.1f}%")
    print(f"📊 Cobertura Vendas: {len(os_comuns)/len(vendas_os_set)*100:.1f}%")
    
    # 3. Criar estrutura de cruzamento
    print("\n🔄 === GERANDO CRUZAMENTOS === 🔄")
    
    cruzamentos = []
    
    for os_numero in sorted(os_comuns):
        # Dados DAV para esta OS
        dav_matches = dav[dav['OS'] == os_numero]
        vendas_matches = vendas_os_clean[vendas_os_clean['os_num'] == os_numero]
        
        # Para cada combinação DAV x Venda
        for _, dav_row in dav_matches.iterrows():
            for _, venda_row in vendas_matches.iterrows():
                
                # Identificar loja DAV
                id_empresa = dav_row.get('ID emp.', '')
                if str(id_empresa) == '42':
                    loja_dav = 'SUZANO'
                elif str(id_empresa) == '48':
                    loja_dav = 'MAUA'
                else:
                    loja_dav = f'LOJA_{id_empresa}'
                
                cruzamento = {
                    # === IDENTIFICAÇÃO ===
                    'os_numero': int(os_numero),
                    'arquivo_dav': dav_row.get('arquivo_origem', ''),
                    
                    # === DADOS DAV ===
                    'dav_id_empresa': dav_row.get('ID emp.', ''),
                    'dav_loja': loja_dav,
                    'dav_cliente_nome': dav_row.get('Cliente', ''),
                    'dav_vendedor': dav_row.get('Vendedor', ''),
                    'dav_data_os': dav_row.get('Dh.DAV', dav_row.get('Dh.O.S.', '')),
                    'dav_data_entrega': dav_row.get('Dt.entrega', ''),
                    'dav_data_prev_entrega': dav_row.get('Dt.prev.entrega', ''),
                    'dav_valor_bruto': dav_row.get('Vl.bruto', ''),
                    'dav_valor_liquido': dav_row.get('Vl.líquido', ''),
                    'dav_valor_desconto': dav_row.get('Vl.desconto', ''),
                    'dav_status': dav_row.get('Status', ''),
                    'dav_origem': dav_row.get('Origem', ''),
                    'dav_descricao': dav_row.get('Descrição', ''),
                    'dav_operador': dav_row.get('Operador', ''),
                    
                    # === DADOS VENDAS ===
                    'venda_loja': venda_row.get('loja', ''),
                    'venda_data': venda_row.get('data_de_compra', ''),
                    'venda_consultor': venda_row.get('consultor', ''),
                    'venda_cliente_nome': venda_row.get('nome', ''),
                    'venda_cpf': venda_row.get('cpf', ''),
                    'venda_telefone': venda_row.get('telefone', ''),
                    'venda_celular': venda_row.get('celular', ''),
                    'venda_email': venda_row.get('email', ''),
                    'venda_endereco': venda_row.get('end', ''),
                    'venda_bairro': venda_row.get('bairro', ''),
                    'venda_prev_entrega': venda_row.get('prev_de_entr', ''),
                    'venda_como_conheceu': venda_row.get('como_conheceu', ''),
                    'venda_total': venda_row.get('total', ''),
                    'venda_pagto_1': venda_row.get('pagto_1', ''),
                    'venda_sinal_1': venda_row.get('sinal_1', ''),
                    'venda_resta': venda_row.get('resta', ''),
                    'venda_origem': venda_row.get('origem', ''),
                    
                    # === RECEITA ===
                    'receita_adicao': venda_row.get('adicao', ''),
                    'receita_obs': venda_row.get('obs', ''),
                    
                    # === PRODUTOS ===
                    'produto_descricao_1': venda_row.get('descricao', ''),
                    'produto_valor_1': venda_row.get('valor', ''),
                    'produto_descricao_2': venda_row.get('descricao18', ''),
                    'produto_valor_2': venda_row.get('valor19', ''),
                    'produto_descricao_3': venda_row.get('descricao21', ''),
                    'produto_valor_3': venda_row.get('valor22', ''),
                }
                
                cruzamentos.append(cruzamento)
    
    # 4. Criar DataFrame final
    df_cruzamento = pd.DataFrame(cruzamentos)
    
    print(f"✅ Cruzamentos gerados: {len(df_cruzamento):,}")
    
    # 5. Análises da estrutura
    print("\n📊 === ANÁLISES DA ESTRUTURA === 📊")
    
    # Por loja
    print("🏪 Distribuição por loja:")
    loja_summary = df_cruzamento.groupby(['dav_loja', 'venda_loja']).size().reset_index(name='count')
    for _, row in loja_summary.iterrows():
        print(f"   {row['dav_loja']} ↔ {row['venda_loja']}: {row['count']:,} OS")
    
    # Valores financeiros
    print("\n💰 Valores:")
    df_cruzamento['dav_valor_num'] = pd.to_numeric(df_cruzamento['dav_valor_liquido'], errors='coerce')
    df_cruzamento['venda_valor_num'] = pd.to_numeric(df_cruzamento['venda_total'], errors='coerce')
    
    valor_dav = df_cruzamento['dav_valor_num'].sum()
    valor_venda = df_cruzamento['venda_valor_num'].sum()
    print(f"   DAV total: R$ {valor_dav:,.2f}")
    print(f"   Vendas total: R$ {valor_venda:,.2f}")
    print(f"   Diferença: R$ {abs(valor_dav - valor_venda):,.2f}")
    
    # Período
    print("\n📅 Período:")
    df_cruzamento['dav_data_dt'] = pd.to_datetime(df_cruzamento['dav_data_os'], errors='coerce')
    df_cruzamento['venda_data_dt'] = pd.to_datetime(df_cruzamento['venda_data'], errors='coerce')
    
    print(f"   DAV: {df_cruzamento['dav_data_dt'].min().strftime('%Y-%m-%d')} → {df_cruzamento['dav_data_dt'].max().strftime('%Y-%m-%d')}")
    print(f"   Vendas: {df_cruzamento['venda_data_dt'].min().strftime('%Y-%m-%d')} → {df_cruzamento['venda_data_dt'].max().strftime('%Y-%m-%d')}")
    
    # 6. Análise de qualidade
    print("\n🔍 === QUALIDADE DOS DADOS === 🔍")
    
    # Nomes similares
    df_cruzamento['nomes_similares'] = df_cruzamento.apply(
        lambda row: 1 if str(row['dav_cliente_nome']).upper().strip()[:20] == str(row['venda_cliente_nome']).upper().strip()[:20] else 0,
        axis=1
    )
    
    nomes_similares = df_cruzamento['nomes_similares'].sum()
    print(f"📝 Nomes similares: {nomes_similares:,} de {len(df_cruzamento):,} ({nomes_similares/len(df_cruzamento)*100:.1f}%)")
    
    # Datas próximas (±30 dias)
    df_cruzamento['diferenca_dias'] = (df_cruzamento['dav_data_dt'] - df_cruzamento['venda_data_dt']).dt.days
    datas_proximas = (abs(df_cruzamento['diferenca_dias']) <= 30).sum()
    print(f"📅 Datas próximas (±30 dias): {datas_proximas:,} de {len(df_cruzamento):,} ({datas_proximas/len(df_cruzamento)*100:.1f}%)")
    
    # Valores similares (±10%)
    df_cruzamento['diferenca_valor'] = abs(df_cruzamento['dav_valor_num'] - df_cruzamento['venda_valor_num']) / df_cruzamento['venda_valor_num'] * 100
    valores_similares = (df_cruzamento['diferenca_valor'] <= 10).sum()
    print(f"💰 Valores similares (±10%): {valores_similares:,} de {len(df_cruzamento):,} ({valores_similares/len(df_cruzamento)*100:.1f}%)")
    
    # 7. Salvar arquivo final
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_cruzamento = f"data/originais/controles_gerais/cruzamento_estruturado_{timestamp}.csv"
    
    df_cruzamento.to_csv(arquivo_cruzamento, index=False)
    
    print(f"\n💾 === ARQUIVO FINAL === 💾")
    print(f"📁 Arquivo: {arquivo_cruzamento}")
    print(f"📊 Registros: {len(df_cruzamento):,}")
    print(f"📋 Colunas: {len(df_cruzamento.columns)}")
    print(f"🎯 OS únicas: {df_cruzamento['os_numero'].nunique():,}")
    
    # 8. Gerar arquivo de não cruzados
    print(f"\n📋 === DADOS NÃO CRUZADOS === 📋")
    
    # DAV não cruzados
    dav_nao_cruzados = dav[~dav['OS'].isin(os_comuns)].copy()
    arquivo_dav_nao_cruzados = f"data/originais/controles_gerais/dav_nao_cruzados_{timestamp}.csv"
    dav_nao_cruzados.to_csv(arquivo_dav_nao_cruzados, index=False)
    print(f"📄 DAV não cruzados: {len(dav_nao_cruzados):,} OS → {arquivo_dav_nao_cruzados}")
    
    # Vendas não cruzadas
    vendas_nao_cruzadas = vendas_os_clean[~vendas_os_clean['os_num'].isin(os_comuns)].copy()
    arquivo_vendas_nao_cruzadas = f"data/originais/controles_gerais/vendas_nao_cruzadas_{timestamp}.csv"
    vendas_nao_cruzadas.to_csv(arquivo_vendas_nao_cruzadas, index=False)
    print(f"📄 Vendas não cruzadas: {len(vendas_nao_cruzadas):,} OS → {arquivo_vendas_nao_cruzadas}")
    
    # 9. Resumo estatístico
    print(f"\n📊 === RESUMO ESTATÍSTICO === 📊")
    
    stats = {
        'total_os_dav': len(dav_os_set),
        'total_os_vendas': len(vendas_os_set),
        'os_cruzadas': len(os_comuns),
        'registros_cruzamento': len(df_cruzamento),
        'cobertura_dav_pct': len(os_comuns)/len(dav_os_set)*100,
        'cobertura_vendas_pct': len(os_comuns)/len(vendas_os_set)*100,
        'valor_dav_total': valor_dav,
        'valor_vendas_total': valor_venda,
        'nomes_similares_pct': nomes_similares/len(df_cruzamento)*100,
        'datas_proximas_pct': datas_proximas/len(df_cruzamento)*100,
        'valores_similares_pct': valores_similares/len(df_cruzamento)*100
    }
    
    arquivo_stats = f"data/originais/controles_gerais/estatisticas_cruzamento_{timestamp}.json"
    import json
    with open(arquivo_stats, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"📊 Estatísticas salvas: {arquivo_stats}")
    
    return arquivo_cruzamento, stats

if __name__ == "__main__":
    print("🚀 === CRIAÇÃO DE ESTRUTURA DE CRUZAMENTO === 🚀")
    
    arquivo_final, stats = criar_estrutura_cruzamento()
    
    print(f"\n🎯 === MISSÃO CUMPRIDA === 🎯")
    print(f"✅ Estrutura criada: {arquivo_final}")
    print(f"📊 {stats['os_cruzadas']:,} OS cruzadas de {stats['total_os_dav']:,} DAV e {stats['total_os_vendas']:,} Vendas")
    print(f"💰 R$ {stats['valor_dav_total']:,.2f} (DAV) vs R$ {stats['valor_vendas_total']:,.2f} (Vendas)")
    print(f"🔍 Qualidade: {stats['nomes_similares_pct']:.1f}% nomes, {stats['datas_proximas_pct']:.1f}% datas, {stats['valores_similares_pct']:.1f}% valores")
    print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")