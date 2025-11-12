#!/usr/bin/env python3
"""
Diagnóstico do Baixo Cruzamento - Sistema Carne Fácil
====================================================

Investiga por que só 460 de 7.076 entregas têm venda_id válido:

1. Analisa períodos das entregas vs vendas
2. Compara formatos de OS números
3. Verifica padrões por loja
4. Identifica possíveis soluções

Objetivo: Aumentar o cruzamento de 6.5% para muito mais
"""

import pandas as pd
import numpy as np

def analisar_cruzamento_detalhado():
    """Analisa detalhadamente o cruzamento"""
    
    print("🔍 === DIAGNÓSTICO DO BAIXO CRUZAMENTO === 🔍")
    
    # Carrega dados
    try:
        entregas_df = pd.read_csv('data/originais/cxs/finais_postgresql_prontos/os_entregues_dia_suzano_final.csv')
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"📂 Entregas carregadas: {len(entregas_df):,}")
        print(f"📂 Vendas carregadas: {len(vendas_df):,}")
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return
    
    # 1. Análise de períodos
    print(f"\n📅 === ANÁLISE DE PERÍODOS === 📅")
    
    entregas_df['data_movimento'] = pd.to_datetime(entregas_df['data_movimento'], errors='coerce')
    vendas_df['data_venda'] = pd.to_datetime(vendas_df['data_venda'], errors='coerce')
    
    print(f"🚚 ENTREGAS:")
    print(f"   Período: {entregas_df['data_movimento'].min()} → {entregas_df['data_movimento'].max()}")
    print(f"   Registros com data: {entregas_df['data_movimento'].notna().sum():,}")
    
    print(f"💰 VENDAS:")
    print(f"   Período: {vendas_df['data_venda'].min()} → {vendas_df['data_venda'].max()}")
    print(f"   Registros com data: {vendas_df['data_venda'].notna().sum():,}")
    
    # 2. Análise de formatos de OS
    print(f"\n🔢 === ANÁLISE DE FORMATOS OS === 🔢")
    
    # Amostras de OS numbers
    entregas_os = entregas_df['os_numero'].dropna().astype(str)
    vendas_os = vendas_df['numero_venda'].dropna().astype(str)
    
    print(f"🚚 ENTREGAS - Amostras de OS:")
    amostras_entregas = entregas_os.head(10).tolist()
    for os_num in amostras_entregas:
        print(f"   '{os_num}' (tipo: {type(os_num)}, len: {len(os_num)})")
    
    print(f"💰 VENDAS - Amostras de OS:")
    amostras_vendas = vendas_os.head(10).tolist()
    for os_num in amostras_vendas:
        print(f"   '{os_num}' (tipo: {type(os_num)}, len: {len(os_num)})")
    
    # 3. Análise de ranges
    print(f"\n📊 === ANÁLISE DE RANGES === 📊")
    
    try:
        entregas_numericas = pd.to_numeric(entregas_os, errors='coerce').dropna()
        vendas_numericas = pd.to_numeric(vendas_os, errors='coerce').dropna()
        
        print(f"🚚 ENTREGAS - Range numérico:")
        print(f"   Min: {entregas_numericas.min():.0f}")
        print(f"   Max: {entregas_numericas.max():.0f}")
        print(f"   Média: {entregas_numericas.mean():.0f}")
        print(f"   Valores únicos: {len(entregas_numericas):,}")
        
        print(f"💰 VENDAS - Range numérico:")
        print(f"   Min: {vendas_numericas.min():.0f}")
        print(f"   Max: {vendas_numericas.max():.0f}")
        print(f"   Média: {vendas_numericas.mean():.0f}")
        print(f"   Valores únicos: {len(vendas_numericas):,}")
        
        # Overlap de ranges
        entregas_set = set(entregas_numericas.astype(int))
        vendas_set = set(vendas_numericas.astype(int))
        
        overlap = entregas_set.intersection(vendas_set)
        print(f"\n🔗 OVERLAP:")
        print(f"   OS comuns: {len(overlap):,}")
        print(f"   % das entregas: {len(overlap)/len(entregas_set)*100:.1f}%")
        print(f"   % das vendas: {len(overlap)/len(vendas_set)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Erro na análise numérica: {e}")
    
    # 4. Análise por loja específica
    print(f"\n🏪 === ANÁLISE POR LOJA (SUZANO) === 🏪")
    
    # Filtra vendas de Suzano
    vendas_suzano = vendas_df[vendas_df['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722']
    print(f"💰 Vendas Suzano: {len(vendas_suzano):,}")
    
    if len(vendas_suzano) > 0:
        suzano_os = vendas_suzano['numero_venda'].dropna().astype(str)
        suzano_numericas = pd.to_numeric(suzano_os, errors='coerce').dropna()
        
        print(f"   Range: {suzano_numericas.min():.0f} → {suzano_numericas.max():.0f}")
        print(f"   Amostras: {suzano_os.head(5).tolist()}")
        
        # Cruzamento específico Suzano
        suzano_set = set(suzano_numericas.astype(int))
        suzano_overlap = entregas_set.intersection(suzano_set)
        print(f"   Overlap com entregas: {len(suzano_overlap):,}")

def testar_estrategias_melhoramento():
    """Testa estratégias para melhorar cruzamento"""
    
    print(f"\n🛠️ === ESTRATÉGIAS DE MELHORAMENTO === 🛠️")
    
    try:
        # Carrega todas as entregas (consolidado)
        entregas_todas = pd.read_csv('data/originais/cxs/extraidos_corrigidos/os_entregues_dia/os_entregues_dia_todas_lojas_com_uuids_enriquecido_completo.csv')
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        
        print(f"📂 Testando com dados consolidados:")
        print(f"   Entregas: {len(entregas_todas):,}")
        print(f"   Vendas: {len(vendas_df):,}")
        
        # 1. Cruzamento por loja_id
        print(f"\n🏪 ESTRATÉGIA 1: Cruzamento por loja_id")
        
        if 'loja_id' in entregas_todas.columns:
            loja_stats = entregas_todas['loja_id'].value_counts()
            print(f"   Entregas por loja_id:")
            for loja_id, count in loja_stats.head().items():
                vendas_loja = vendas_df[vendas_df['loja_id'] == loja_id]
                print(f"      {loja_id[:8]}...: {count:,} entregas, {len(vendas_loja):,} vendas")
        
        # 2. Cruzamento flexível de OS
        print(f"\n🔢 ESTRATÉGIA 2: Cruzamento flexível OS")
        
        entregas_os = entregas_todas['os_numero'].dropna().astype(str)
        vendas_os = vendas_df['numero_venda'].dropna().astype(str)
        
        # Remove zeros à esquerda e testa
        entregas_clean = set(entregas_os.str.lstrip('0'))
        vendas_clean = set(vendas_os.str.lstrip('0'))
        
        overlap_clean = entregas_clean.intersection(vendas_clean)
        print(f"   Sem zeros à esquerda: {len(overlap_clean):,} matches")
        
        # Testa apenas números
        entregas_num_only = set(entregas_os.str.replace(r'[^\d]', '', regex=True))
        vendas_num_only = set(vendas_os.str.replace(r'[^\d]', '', regex=True))
        
        overlap_num = entregas_num_only.intersection(vendas_num_only)
        print(f"   Apenas números: {len(overlap_num):,} matches")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Diagnóstico completo"""
    
    print("🔍 === DIAGNÓSTICO COMPLETO === 🔍")
    
    # 1. Análise detalhada do cruzamento
    analisar_cruzamento_detalhado()
    
    # 2. Testa estratégias de melhoramento
    testar_estrategias_melhoramento()
    
    print(f"\n💡 === CONCLUSÕES === 💡")
    print("1. Verificar se períodos das entregas vs vendas coincidem")
    print("2. Testar formatos alternativos de OS números")
    print("3. Considerar cruzamento por loja + período")
    print("4. Investigar se são sistemas/bases diferentes")

if __name__ == "__main__":
    main()