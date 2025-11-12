#!/usr/bin/env python3
"""
Inventário Completo de Entregas - Sistema Carne Fácil
====================================================

Verifica TODOS os arquivos de entregas disponíveis:
1. finais_postgresql_prontos/ (que já processamos)
2. extraidos_corrigidos/os_entregues_dia/ (enriquecidos com UUIDs)
3. Compara volumes e qualidade dos dados
4. Identifica melhor fonte para usar

Objetivo: Encontrar o conjunto mais completo de entregas
"""

import pandas as pd
import glob
from pathlib import Path

def analisar_pasta_finais():
    """Analisa pasta finais_postgresql_prontos (já processada)"""
    
    print("📁 === PASTA FINAIS_POSTGRESQL_PRONTOS === 📁")
    
    pattern = 'data/originais/cxs/finais_postgresql_prontos/os_entregues_dia_*_final.csv'
    arquivos = glob.glob(pattern)
    
    total_registros = 0
    os_unicas = set()
    
    for arquivo in sorted(arquivos):
        loja = arquivo.split('_')[-2]
        try:
            df = pd.read_csv(arquivo)
            registros = len(df)
            os_arquivo = set(df['os_numero'].astype(str))
            
            total_registros += registros
            os_unicas.update(os_arquivo)
            
            print(f"   {loja.upper()}: {registros:,} registros, {len(os_arquivo):,} OS únicas")
            
        except Exception as e:
            print(f"   {loja.upper()}: ERRO - {e}")
    
    print(f"   📊 TOTAL: {total_registros:,} registros, {len(os_unicas):,} OS únicas")
    return total_registros, len(os_unicas)

def analisar_pasta_extraidos():
    """Analisa pasta extraidos_corrigidos/os_entregues_dia"""
    
    print(f"\n📁 === PASTA EXTRAIDOS_CORRIGIDOS === 📁")
    
    base_path = 'data/originais/cxs/extraidos_corrigidos/os_entregues_dia'
    
    # Verifica arquivo consolidado
    arquivo_todas = f'{base_path}/os_entregues_dia_todas_lojas_com_uuids_enriquecido_completo.csv'
    
    if Path(arquivo_todas).exists():
        try:
            df_todas = pd.read_csv(arquivo_todas)
            print(f"📄 ARQUIVO CONSOLIDADO:")
            print(f"   {len(df_todas):,} registros totais")
            print(f"   {df_todas['os_numero'].nunique() if 'os_numero' in df_todas.columns else 'N/A'} OS únicas")
            print(f"   Colunas: {list(df_todas.columns)}")
            
            # Análise por loja
            if 'loja_nome' in df_todas.columns:
                print(f"   📊 Por loja:")
                loja_stats = df_todas['loja_nome'].value_counts()
                for loja, count in loja_stats.items():
                    print(f"      {loja}: {count:,}")
            
            return len(df_todas), df_todas['os_numero'].nunique() if 'os_numero' in df_todas.columns else 0
            
        except Exception as e:
            print(f"   ❌ Erro no arquivo consolidado: {e}")
    
    # Se não tem consolidado, verifica arquivos individuais
    print(f"📄 ARQUIVOS INDIVIDUAIS:")
    
    pattern = f'{base_path}/os_entregues_dia_*_com_uuids_enriquecido_completo.csv'
    arquivos = glob.glob(pattern)
    
    total_registros = 0
    os_unicas = set()
    
    for arquivo in sorted(arquivos):
        nome_arquivo = Path(arquivo).name
        loja = nome_arquivo.split('_')[3]  # Extrai nome da loja
        
        try:
            df = pd.read_csv(arquivo)
            registros = len(df)
            os_arquivo = set(df['os_numero'].astype(str)) if 'os_numero' in df.columns else set()
            
            total_registros += registros
            os_unicas.update(os_arquivo)
            
            print(f"   {loja.upper()}: {registros:,} registros, {len(os_arquivo):,} OS únicas")
            
            # Mostra estrutura do primeiro arquivo
            if total_registros == registros:  # Primeiro arquivo
                print(f"      Colunas ({len(df.columns)}): {', '.join(df.columns[:8])}...")
            
        except Exception as e:
            print(f"   {loja.upper()}: ERRO - {e}")
    
    print(f"   📊 TOTAL: {total_registros:,} registros, {len(os_unicas):,} OS únicas")
    return total_registros, len(os_unicas)

def comparar_qualidade_dados():
    """Compara qualidade entre as duas fontes"""
    
    print(f"\n🔍 === COMPARAÇÃO DE QUALIDADE === 🔍")
    
    # Amostra dos finais
    try:
        df_finais = pd.read_csv('data/originais/cxs/finais_postgresql_prontos/os_entregues_dia_suzano_final.csv')
        print(f"📊 FINAIS_POSTGRESQL (amostra Suzano):")
        print(f"   Registros: {len(df_finais):,}")
        print(f"   Colunas: {list(df_finais.columns)}")
        print(f"   Período: {df_finais['data_movimento'].min()} → {df_finais['data_movimento'].max()}")
    except Exception as e:
        print(f"   ❌ Erro finais: {e}")
    
    # Amostra dos extraídos
    try:
        df_extraidos = pd.read_csv('data/originais/cxs/extraidos_corrigidos/os_entregues_dia/os_entregues_dia_suzano_com_uuids_enriquecido_completo.csv')
        print(f"📊 EXTRAIDOS_CORRIGIDOS (amostra Suzano):")
        print(f"   Registros: {len(df_extraidos):,}")
        print(f"   Colunas: {list(df_extraidos.columns)}")
        if 'data_movimento' in df_extraidos.columns:
            print(f"   Período: {df_extraidos['data_movimento'].min()} → {df_extraidos['data_movimento'].max()}")
    except Exception as e:
        print(f"   ❌ Erro extraídos: {e}")

def recomendar_fonte():
    """Recomenda melhor fonte de dados"""
    
    print(f"\n💡 === RECOMENDAÇÃO === 💡")
    
    # Verifica se extraídos tem mais dados
    try:
        # Conta registros consolidado
        df_consolidado = pd.read_csv('data/originais/cxs/extraidos_corrigidos/os_entregues_dia/os_entregues_dia_todas_lojas_com_uuids_enriquecido_completo.csv')
        extraidos_total = len(df_consolidado)
        
        print(f"🎯 DADOS DISPONÍVEIS:")
        print(f"   Extraídos (enriquecidos): {extraidos_total:,} registros")
        print(f"   Finais (processados): ~7.076 registros")
        print(f"   Atualmente usando: 460 registros válidos")
        
        if extraidos_total > 7076:
            print(f"\n✅ RECOMENDAÇÃO: Usar EXTRAÍDOS_CORRIGIDOS")
            print(f"   💎 Mais dados ({extraidos_total:,} vs 7.076)")
            print(f"   🔗 UUIDs já mapeados")
            print(f"   📊 Dados enriquecidos")
            print(f"   🎯 Potencial para muito mais entregas!")
        else:
            print(f"\n⚠️ Manter fonte atual ou investigar diferenças")
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

def main():
    """Inventário completo"""
    
    print("📋 === INVENTÁRIO COMPLETO DE ENTREGAS === 📋")
    
    # 1. Analisa pasta atual (finais)
    finais_regs, finais_os = analisar_pasta_finais()
    
    # 2. Analisa pasta extraídos
    extraidos_regs, extraidos_os = analisar_pasta_extraidos()
    
    # 3. Compara qualidade
    comparar_qualidade_dados()
    
    # 4. Recomenda fonte
    recomendar_fonte()
    
    print(f"\n📊 === RESUMO === 📊")
    print(f"   Finais: {finais_regs:,} registros, {finais_os:,} OS")
    print(f"   Extraídos: {extraidos_regs:,} registros, {extraidos_os:,} OS") 
    print(f"   Usado atualmente: 460 entregas válidas")

if __name__ == "__main__":
    main()