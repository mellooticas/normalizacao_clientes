#!/usr/bin/env python3
"""
Integrar UUIDs das OS já normalizadas nos dados de caixa
Estratégia: Cruzar por numero_os (OSS) + loja para trazer UUIDs
"""

import pandas as pd
import glob
import os
from pathlib import Path

def carregar_os_normalizadas():
    """Carrega todas as OS normalizadas com UUIDs"""
    print("🔄 Carregando OS normalizadas...")
    
    caminho_os = "data/originais/oss/finais_postgresql_prontos/*.csv"
    arquivos_os = glob.glob(caminho_os)
    
    dfs_os = []
    for arquivo in arquivos_os:
        df = pd.read_csv(arquivo)
        print(f"   📁 {Path(arquivo).name}: {len(df)} registros")
        dfs_os.append(df)
    
    # Consolidar todas as OS
    df_os_total = pd.concat(dfs_os, ignore_index=True)
    
    # Preparar campos para cruzamento
    df_os_total['os_numero'] = pd.to_numeric(df_os_total['numero_os'], errors='coerce')
    df_os_total['loja_nome_padrao'] = df_os_total['loja_nome'].str.upper()
    
    # Remover linhas com OS inválidas
    antes = len(df_os_total)
    df_os_total = df_os_total.dropna(subset=['os_numero'])
    depois = len(df_os_total)
    if antes != depois:
        print(f"   ⚠️  Removidas {antes-depois} linhas com OS inválidas")
    
    # Selecionar campos necessários para o cruzamento
    campos_uuid = [
        'os_numero', 'loja_nome_padrao', 'loja_id', 
        'vendedor_uuid', 'vendedor_nome_normalizado',
        'canal_captacao_uuid', 'canal_captacao_nome'
    ]
    
    df_os_uuid = df_os_total[campos_uuid].drop_duplicates()
    
    print(f"✅ Total OS normalizadas: {len(df_os_uuid)} (únicas por OS+loja)")
    return df_os_uuid

def mapear_nomes_lojas():
    """Mapeamento entre nomes de arquivos e nomes padrão"""
    return {
        'maua': 'MAUA',
        'perus': 'PERUS', 
        'rio_pequeno': 'RIO_PEQUENO',
        'sao_mateus': 'SAO_MATEUS',
        'suzano': 'SUZANO',
        'suzano2': 'SUZANO2'
    }

def integrar_uuids_vendas():
    """Integra UUIDs nas vendas do caixa"""
    print("\n🔄 Integrando UUIDs nas vendas...")
    
    # Carregar OS normalizadas
    df_os_uuid = carregar_os_normalizadas()
    
    # Mapeamento de lojas
    mapa_lojas = mapear_nomes_lojas()
    
    caminho_vendas = "data/originais/cxs/extraidos_corrigidos/vendas/*.csv"
    arquivos_vendas = glob.glob(caminho_vendas)
    
    resultados = {}
    
    for arquivo in arquivos_vendas:
        nome_arquivo = Path(arquivo).stem
        loja_arquivo = nome_arquivo.replace('vendas_', '')
        loja_padrao = mapa_lojas.get(loja_arquivo, loja_arquivo.upper())
        
        print(f"\n📊 Processando: {nome_arquivo}")
        print(f"   🏪 Loja mapeada: {loja_arquivo} → {loja_padrao}")
        
        # Carregar vendas
        df_vendas = pd.read_csv(arquivo)
        print(f"   📈 Vendas originais: {len(df_vendas)}")
        
        # Preparar para cruzamento
        df_vendas['os_numero'] = df_vendas['nn_venda'].astype(float)
        df_vendas['loja_nome_padrao'] = loja_padrao
        
        # Filtrar OS da loja específica
        df_os_loja = df_os_uuid[df_os_uuid['loja_nome_padrao'] == loja_padrao].copy()
        print(f"   🎯 OS disponíveis para {loja_padrao}: {len(df_os_loja)}")
        
        # Fazer o cruzamento
        df_vendas_uuid = df_vendas.merge(
            df_os_loja,
            on=['os_numero', 'loja_nome_padrao'],
            how='left'
        )
        
        # Verificar resultados do cruzamento
        com_uuid = df_vendas_uuid['vendedor_uuid'].notna().sum()
        sem_uuid = df_vendas_uuid['vendedor_uuid'].isna().sum()
        
        print(f"   ✅ Cruzadas com UUID: {com_uuid}")
        print(f"   ⚠️  Sem UUID: {sem_uuid}")
        print(f"   📊 Taxa sucesso: {(com_uuid/len(df_vendas)*100):.1f}%")
        
        # Salvar resultado
        arquivo_saida = arquivo.replace('.csv', '_com_uuids.csv')
        df_vendas_uuid.to_csv(arquivo_saida, index=False)
        print(f"   💾 Salvo: {Path(arquivo_saida).name}")
        
        resultados[loja_padrao] = {
            'total': len(df_vendas),
            'com_uuid': com_uuid,
            'sem_uuid': sem_uuid,
            'taxa_sucesso': com_uuid/len(df_vendas)*100
        }
    
    return resultados

def integrar_uuids_outras_tabelas():
    """Integra UUIDs nas outras tabelas do caixa"""
    print("\n🔄 Integrando UUIDs nas outras tabelas...")
    
    # Carregar OS normalizadas
    df_os_uuid = carregar_os_normalizadas()
    
    # Mapeamento de lojas
    mapa_lojas = mapear_nomes_lojas()
    
    # Outras tabelas para processar
    tabelas = [
        'restante_entrada',
        'recebimento_carne', 
        'os_entregues_dia',
        'entrega_carne'
    ]
    
    resultados_geral = {}
    
    for tabela in tabelas:
        print(f"\n📋 Processando tabela: {tabela.upper()}")
        
        caminho_tabela = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*.csv"
        arquivos_tabela = glob.glob(caminho_tabela)
        
        resultados_tabela = {}
        
        for arquivo in arquivos_tabela:
            nome_arquivo = Path(arquivo).stem
            loja_arquivo = nome_arquivo.replace(f'{tabela}_', '')
            loja_padrao = mapa_lojas.get(loja_arquivo, loja_arquivo.upper())
            
            print(f"   📁 {nome_arquivo} ({loja_padrao})")
            
            # Carregar dados
            df_dados = pd.read_csv(arquivo)
            
            # Identificar campo OS na tabela
            campo_os = None
            if 'nn_venda' in df_dados.columns:
                campo_os = 'nn_venda'
            elif 'os' in df_dados.columns:
                campo_os = 'os'
            elif 'OS N°' in df_dados.columns:
                campo_os = 'OS N°'
            
            if campo_os:
                # Preparar para cruzamento
                df_dados['os_numero'] = pd.to_numeric(df_dados[campo_os], errors='coerce')
                df_dados['loja_nome_padrao'] = loja_padrao
                
                # Filtrar OS da loja
                df_os_loja = df_os_uuid[df_os_uuid['loja_nome_padrao'] == loja_padrao].copy()
                
                # Cruzamento
                df_dados_uuid = df_dados.merge(
                    df_os_loja,
                    on=['os_numero', 'loja_nome_padrao'],
                    how='left'
                )
                
                # Estatísticas
                com_uuid = df_dados_uuid['vendedor_uuid'].notna().sum()
                total = len(df_dados)
                
                print(f"      ✅ {com_uuid}/{total} ({(com_uuid/total*100):.1f}%)")
                
                # Salvar
                arquivo_saida = arquivo.replace('.csv', '_com_uuids.csv')
                df_dados_uuid.to_csv(arquivo_saida, index=False)
                
                resultados_tabela[loja_padrao] = {
                    'total': total,
                    'com_uuid': com_uuid,
                    'taxa_sucesso': com_uuid/total*100
                }
            else:
                print(f"      ⚠️  Campo OS não identificado")
        
        resultados_geral[tabela] = resultados_tabela
    
    return resultados_geral

def exibir_relatorio_final(resultados_vendas, resultados_outras):
    """Exibe relatório consolidado"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL - INTEGRAÇÃO DE UUIDs")
    print("="*60)
    
    print("\n🛒 VENDAS:")
    total_vendas = 0
    total_com_uuid = 0
    
    for loja, stats in resultados_vendas.items():
        print(f"   {loja}: {stats['com_uuid']}/{stats['total']} ({stats['taxa_sucesso']:.1f}%)")
        total_vendas += stats['total']
        total_com_uuid += stats['com_uuid']
    
    print(f"   TOTAL VENDAS: {total_com_uuid}/{total_vendas} ({(total_com_uuid/total_vendas*100):.1f}%)")
    
    print("\n📋 OUTRAS TABELAS:")
    for tabela, lojas in resultados_outras.items():
        print(f"\n   {tabela.upper()}:")
        for loja, stats in lojas.items():
            print(f"      {loja}: {stats['com_uuid']}/{stats['total']} ({stats['taxa_sucesso']:.1f}%)")

if __name__ == "__main__":
    print("🚀 INICIANDO INTEGRAÇÃO DE UUIDs DAS OS NORMALIZADAS")
    print("="*60)
    
    # Executar integrações
    resultados_vendas = integrar_uuids_vendas()
    resultados_outras = integrar_uuids_outras_tabelas()
    
    # Relatório final
    exibir_relatorio_final(resultados_vendas, resultados_outras)
    
    print("\n✅ INTEGRAÇÃO CONCLUÍDA!")
    print("🎯 Todos os arquivos '_com_uuids.csv' foram gerados!")