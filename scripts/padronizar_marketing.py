#!/usr/bin/env python3
"""
Script para padronizar dados de marketing com UUIDs corretos
Mapear origens_marketing → canais_aquisicao
Mapear lojas_antigas → lojas
Padronizar leads_marketing com novos UUIDs
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analisar_estruturas():
    """
    Analisa as estruturas dos arquivos de marketing
    """
    print("🎯 === ANÁLISE ESTRUTURAS MARKETING === 🎯")
    
    # Carregar todos os arquivos
    arquivos = {
        'canais_aquisicao': 'data/originais/leads/canais_aquisicao.csv',
        'origens_marketing': 'data/originais/leads/origens_marketing.csv', 
        'leads_marketing': 'data/originais/leads/leads_marketing.csv',
        'lojas': 'data/originais/leads/lojas.csv',
        'lojas_antigas': 'data/originais/leads/lojas_antigas.csv'
    }
    
    dados = {}
    
    for nome, arquivo in arquivos.items():
        try:
            df = pd.read_csv(arquivo)
            dados[nome] = df
            print(f"\n📄 {nome.upper()}:")
            print(f"   Registros: {len(df):,}")
            print(f"   Colunas: {', '.join(df.columns)}")
        except Exception as e:
            print(f"❌ Erro carregando {nome}: {e}")
    
    return dados

def mapear_origens_para_canais(dados):
    """
    Mapeia origens_marketing para canais_aquisicao usando código/descrição
    """
    print(f"\n🔗 === MAPEAMENTO ORIGENS → CANAIS === 🔗")
    
    df_origens = dados['origens_marketing']
    df_canais = dados['canais_aquisicao']
    
    print(f"📊 Origens: {len(df_origens):,}")
    print(f"📊 Canais: {len(df_canais):,}")
    
    # Análise dos campos de matching
    print(f"\n🔍 Campos para matching:")
    print(f"   Origens: 'codigo', 'descricao'")
    print(f"   Canais: 'codigo', 'nome', 'descricao'")
    
    # Criar mapeamento baseado em código
    mapeamento_codigo = []
    mapeamento_nome = []
    
    for _, origem in df_origens.iterrows():
        codigo_origem = origem.get('codigo')
        desc_origem = str(origem.get('descricao', '')).upper().strip()
        
        # 1. Tentar match por código
        match_codigo = df_canais[df_canais['codigo'] == codigo_origem]
        if not match_codigo.empty:
            mapeamento_codigo.append({
                'origem_id': origem['id'],
                'origem_codigo': codigo_origem,
                'origem_descricao': desc_origem,
                'canal_id': match_codigo.iloc[0]['id'],
                'canal_codigo': match_codigo.iloc[0]['codigo'],
                'canal_nome': match_codigo.iloc[0]['nome'],
                'tipo_match': 'CODIGO'
            })
            continue
        
        # 2. Tentar match por nome/descrição
        matches_nome = df_canais[
            (df_canais['nome'].str.upper().str.contains(desc_origem, na=False)) |
            (df_canais['descricao'].str.upper().str.contains(desc_origem, na=False))
        ]
        
        if not matches_nome.empty:
            mapeamento_nome.append({
                'origem_id': origem['id'],
                'origem_codigo': codigo_origem,
                'origem_descricao': desc_origem,
                'canal_id': matches_nome.iloc[0]['id'],
                'canal_codigo': matches_nome.iloc[0]['codigo'],
                'canal_nome': matches_nome.iloc[0]['nome'],
                'tipo_match': 'NOME'
            })
        else:
            # Sem match - precisará de intervenção manual
            mapeamento_nome.append({
                'origem_id': origem['id'],
                'origem_codigo': codigo_origem,
                'origem_descricao': desc_origem,
                'canal_id': None,
                'canal_codigo': None,
                'canal_nome': None,
                'tipo_match': 'SEM_MATCH'
            })
    
    # Consolidar mapeamentos
    mapeamento_total = mapeamento_codigo + mapeamento_nome
    df_mapeamento = pd.DataFrame(mapeamento_total)
    
    print(f"\n📊 === RESULTADOS MAPEAMENTO === 📊")
    match_stats = df_mapeamento['tipo_match'].value_counts()
    for tipo, count in match_stats.items():
        print(f"   {tipo}: {count:,}")
    
    # Salvar mapeamento
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_mapeamento = f'data/mapeamento_origens_canais_{timestamp}.csv'
    df_mapeamento.to_csv(arquivo_mapeamento, index=False)
    
    print(f"\n💾 Mapeamento salvo: {arquivo_mapeamento}")
    
    return df_mapeamento

def mapear_lojas_antigas_para_novas(dados):
    """
    Mapeia lojas_antigas para lojas novas usando nome
    """
    print(f"\n🔗 === MAPEAMENTO LOJAS ANTIGAS → NOVAS === 🔗")
    
    df_antigas = dados['lojas_antigas']
    df_novas = dados['lojas']
    
    print(f"📊 Lojas antigas: {len(df_antigas):,}")
    print(f"📊 Lojas novas: {len(df_novas):,}")
    
    mapeamento_lojas = []
    
    for _, antiga in df_antigas.iterrows():
        nome_antigo = str(antiga.get('nome', '')).upper().strip()
        id_antigo = antiga['id']
        
        # Lógica de matching por nome
        match_encontrado = False
        
        # Matching patterns
        patterns = {
            'SUZANO': ['SUZANO'],
            'MAUÁ': ['MAUÁ', 'MAUA'],
            'RIO PEQUENO': ['RIO PEQUENO', 'RIO_PEQUENO'],
            'PERUS': ['PERUS'],
            'SÃO MATEUS': ['SAO MATEUS', 'SÃO MATEUS'],
            'SUZANO CENTRO': ['SUZANO 2', 'SUZANO2', 'SUZANO_2']
        }
        
        for loja_pattern, keywords in patterns.items():
            if any(keyword in nome_antigo for keyword in keywords):
                # Buscar na nova base
                match_nova = df_novas[
                    df_novas['nome'].str.upper().str.contains('|'.join(keywords), na=False)
                ]
                
                if not match_nova.empty:
                    mapeamento_lojas.append({
                        'loja_antiga_id': id_antigo,
                        'loja_antiga_nome': nome_antigo,
                        'loja_nova_id': match_nova.iloc[0]['id'],
                        'loja_nova_nome': match_nova.iloc[0]['nome'],
                        'loja_nova_codigo': match_nova.iloc[0]['codigo'],
                        'tipo_match': 'NOME_PATTERN'
                    })
                    match_encontrado = True
                    break
        
        if not match_encontrado:
            mapeamento_lojas.append({
                'loja_antiga_id': id_antigo,
                'loja_antiga_nome': nome_antigo,
                'loja_nova_id': None,
                'loja_nova_nome': None,
                'loja_nova_codigo': None,
                'tipo_match': 'SEM_MATCH'
            })
    
    df_map_lojas = pd.DataFrame(mapeamento_lojas)
    
    print(f"\n📊 === RESULTADOS MAPEAMENTO LOJAS === 📊")
    match_stats = df_map_lojas['tipo_match'].value_counts()
    for tipo, count in match_stats.items():
        print(f"   {tipo}: {count}")
    
    # Mostrar mapeamentos encontrados
    matches = df_map_lojas[df_map_lojas['tipo_match'] == 'NOME_PATTERN']
    print(f"\n🔍 Mapeamentos encontrados:")
    for _, row in matches.iterrows():
        print(f"   {row['loja_antiga_nome']} → {row['loja_nova_nome']}")
    
    # Salvar mapeamento
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_map_lojas = f'data/mapeamento_lojas_antigas_novas_{timestamp}.csv'
    df_map_lojas.to_csv(arquivo_map_lojas, index=False)
    
    print(f"\n💾 Mapeamento lojas salvo: {arquivo_map_lojas}")
    
    return df_map_lojas

def padronizar_leads_marketing(dados, map_origens, map_lojas):
    """
    Padroniza leads_marketing com novos UUIDs de canais e lojas
    """
    print(f"\n🔧 === PADRONIZANDO LEADS MARKETING === 🔧")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_leads = dados['leads_marketing'].copy()
    
    print(f"📊 Leads originais: {len(df_leads):,}")
    
    # Criar dicionários de mapeamento
    map_origens_dict = dict(zip(map_origens['origem_id'], map_origens['canal_id']))
    map_lojas_dict = dict(zip(map_lojas['loja_antiga_id'], map_lojas['loja_nova_id']))
    
    # Aplicar mapeamentos
    print(f"\n🔄 Aplicando mapeamentos...")
    
    # Backup das colunas originais
    df_leads['origem_original'] = df_leads['origem'].copy()
    df_leads['loja_id_original'] = df_leads['loja_id'].copy()
    
    # Mapear origem para canal
    df_leads['canal_novo'] = df_leads['origem'].map(map_origens_dict)
    
    # Mapear loja_id para nova loja
    df_leads['loja_id_novo'] = df_leads['loja_id'].map(map_lojas_dict)
    
    # Estatísticas de mapeamento
    origens_mapeadas = df_leads['canal_novo'].notna().sum()
    lojas_mapeadas = df_leads['loja_id_novo'].notna().sum()
    
    print(f"📊 Origens mapeadas: {origens_mapeadas:,} / {len(df_leads):,} ({origens_mapeadas/len(df_leads)*100:.1f}%)")
    print(f"📊 Lojas mapeadas: {lojas_mapeadas:,} / {len(df_leads):,} ({lojas_mapeadas/len(df_leads)*100:.1f}%)")
    
    # Substituir pelos novos valores onde disponível
    df_leads['origem'] = df_leads['canal_novo'].fillna(df_leads['origem'])
    df_leads['loja_id'] = df_leads['loja_id_novo'].fillna(df_leads['loja_id'])
    
    # Renomear coluna origem para canal (padronização)
    df_leads['canal'] = df_leads['origem']
    
    # Limpar colunas auxiliares
    df_leads = df_leads.drop(['canal_novo', 'loja_id_novo'], axis=1)
    
    # Salvar leads padronizados
    arquivo_leads = f'data/leads_marketing_padronizados_{timestamp}.csv'
    df_leads.to_csv(arquivo_leads, index=False)
    
    print(f"\n💾 Leads padronizados salvos: {arquivo_leads}")
    
    return df_leads

def gerar_relatorio_final(map_origens, map_lojas, leads_padronizados):
    """
    Gera relatório final da padronização
    """
    print(f"\n📋 === RELATÓRIO FINAL === 📋")
    
    print(f"\n🔗 MAPEAMENTO ORIGENS → CANAIS:")
    print(f"   Total origens: {len(map_origens):,}")
    match_origens = map_origens['tipo_match'].value_counts()
    for tipo, count in match_origens.items():
        print(f"   {tipo}: {count}")
    
    print(f"\n🔗 MAPEAMENTO LOJAS ANTIGAS → NOVAS:")
    print(f"   Total lojas antigas: {len(map_lojas):,}")
    match_lojas = map_lojas['tipo_match'].value_counts()
    for tipo, count in match_lojas.items():
        print(f"   {tipo}: {count}")
    
    print(f"\n📊 LEADS MARKETING PADRONIZADOS:")
    print(f"   Total leads: {len(leads_padronizados):,}")
    print(f"   Com canal válido: {leads_padronizados['canal'].notna().sum():,}")
    print(f"   Com loja válida: {leads_padronizados['loja_id'].notna().sum():,}")
    
    # Análise por período
    if 'data_cadastro' in leads_padronizados.columns:
        leads_padronizados['ano'] = pd.to_datetime(leads_padronizados['data_cadastro']).dt.year
        leads_por_ano = leads_padronizados['ano'].value_counts().sort_index()
        print(f"\n📅 Leads por ano:")
        for ano, count in leads_por_ano.items():
            if not pd.isna(ano):
                print(f"   {int(ano)}: {count:,}")

def main():
    """Função principal"""
    print("🎯 === PADRONIZAÇÃO MARKETING COMPLETA === 🎯")
    
    # 1. Analisar estruturas
    dados = analisar_estruturas()
    
    if not dados:
        print("❌ Falha no carregamento dos dados")
        return
    
    # 2. Mapear origens para canais
    map_origens = mapear_origens_para_canais(dados)
    
    # 3. Mapear lojas antigas para novas
    map_lojas = mapear_lojas_antigas_para_novas(dados)
    
    # 4. Padronizar leads
    leads_padronizados = padronizar_leads_marketing(dados, map_origens, map_lojas)
    
    # 5. Gerar relatório
    gerar_relatorio_final(map_origens, map_lojas, leads_padronizados)
    
    print(f"\n🎉 === PADRONIZAÇÃO CONCLUÍDA === 🎉")
    print(f"✅ Arquivos gerados na pasta data/")
    print(f"✅ Mapeamentos salvos para auditoria")
    print(f"✅ Leads prontos com UUIDs padronizados")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()