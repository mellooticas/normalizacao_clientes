#!/usr/bin/env python3
"""
Script ULTRA-COMPLETO para maximizar matches DAV ↔ VENDAS
Explorando TODOS os números de Suzano e Mauá + clientes
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analise_completa_numeros():
    """
    Análise completa de todos os números disponíveis
    """
    print("🔍 === ANÁLISE ULTRA-COMPLETA === 🔍")
    
    # Carregar dados
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv')
    vendas = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
    
    print(f"📊 DAV: {len(dav):,} | Vendas: {len(vendas):,}")
    
    # === ANÁLISE COMPLETA DOS NÚMEROS ===
    print(f"\n🔢 === ANÁLISE COMPLETA DOS NÚMEROS === 🔢")
    
    # DAV - todos os números
    dav_entregas = dav[dav['Dt.entrega'].notna()].copy()
    dav_entregas['os_numero'] = pd.to_numeric(dav_entregas['OS_numero'], errors='coerce')
    dav_com_os = dav_entregas.dropna(subset=['os_numero'])
    
    # Vendas - todos os números
    vendas['numero_venda_num'] = pd.to_numeric(vendas['numero_venda'], errors='coerce')
    vendas_com_num = vendas.dropna(subset=['numero_venda_num'])
    
    print(f"📊 DAV com OS: {len(dav_com_os):,}")
    print(f"📊 Vendas com números: {len(vendas_com_num):,}")
    
    # === ANÁLISE POR FAIXAS ===
    print(f"\n📊 === ANÁLISE POR FAIXAS === 📊")
    
    # DAV por faixas
    dav_nums = dav_com_os['os_numero'].astype(int)
    
    faixas_dav = {
        '0-999': (dav_nums < 1000).sum(),
        '1k-2k': ((dav_nums >= 1000) & (dav_nums < 2000)).sum(),
        '2k-3k': ((dav_nums >= 2000) & (dav_nums < 3000)).sum(),
        '3k-4k': ((dav_nums >= 3000) & (dav_nums < 4000)).sum(),
        '4k-5k': ((dav_nums >= 4000) & (dav_nums < 5000)).sum(),
        '5k-6k': ((dav_nums >= 5000) & (dav_nums < 6000)).sum(),
        '6k-7k': ((dav_nums >= 6000) & (dav_nums < 7000)).sum(),
        '7k-8k': ((dav_nums >= 7000) & (dav_nums < 8000)).sum(),
        '8k+': (dav_nums >= 8000).sum()
    }
    
    print(f"📊 DAV por faixas:")
    for faixa, qtd in faixas_dav.items():
        if qtd > 0:
            print(f"   {faixa}: {qtd:,} entregas")
    
    # Vendas por faixas (só até 10k para comparar)
    vendas_nums = vendas_com_num['numero_venda_num'].astype(int)
    vendas_relevantes = vendas_nums[vendas_nums <= 10000]
    
    faixas_vendas = {
        '0-999': (vendas_relevantes < 1000).sum(),
        '1k-2k': ((vendas_relevantes >= 1000) & (vendas_relevantes < 2000)).sum(),
        '2k-3k': ((vendas_relevantes >= 2000) & (vendas_relevantes < 3000)).sum(),
        '3k-4k': ((vendas_relevantes >= 3000) & (vendas_relevantes < 4000)).sum(),
        '4k-5k': ((vendas_relevantes >= 4000) & (vendas_relevantes < 5000)).sum(),
        '5k-6k': ((vendas_relevantes >= 5000) & (vendas_relevantes < 6000)).sum(),
        '6k-7k': ((vendas_relevantes >= 6000) & (vendas_relevantes < 7000)).sum(),
        '7k-8k': ((vendas_relevantes >= 7000) & (vendas_relevantes < 8000)).sum(),
        '8k-10k': ((vendas_relevantes >= 8000) & (vendas_relevantes <= 10000)).sum()
    }
    
    print(f"\n📊 Vendas por faixas (≤10k):")
    for faixa, qtd in faixas_vendas.items():
        if qtd > 0:
            print(f"   {faixa}: {qtd:,} vendas")
    
    # === POTENCIAL DE MATCH POR FAIXA ===
    print(f"\n🎯 === POTENCIAL DE MATCH POR FAIXA === 🎯")
    
    for faixa in faixas_dav:
        dav_qtd = faixas_dav[faixa]
        vendas_qtd = faixas_vendas.get(faixa, 0)
        
        if dav_qtd > 0 and vendas_qtd > 0:
            print(f"🔗 {faixa}: {dav_qtd:,} DAV × {vendas_qtd:,} Vendas = Potencial match")
    
    # === ANÁLISE ESPECÍFICA POR LOJA ===
    print(f"\n🏪 === ANÁLISE ESPECÍFICA POR LOJA === 🏪")
    
    # Suzano
    suzano_dav = dav_com_os[dav_com_os['ID emp.'] == 42]
    if len(suzano_dav) > 0:
        suzano_nums = suzano_dav['os_numero'].astype(int)
        print(f"🏪 SUZANO:")
        print(f"   Entregas: {len(suzano_dav):,}")
        print(f"   Range: {suzano_nums.min():,} → {suzano_nums.max():,}")
        print(f"   Mais comum: {suzano_nums.mode().iloc[0]:,}")
    
    # Mauá
    maua_dav = dav_com_os[dav_com_os['ID emp.'] == 48]
    if len(maua_dav) > 0:
        maua_nums = maua_dav['os_numero'].astype(int)
        print(f"🏪 MAUÁ:")
        print(f"   Entregas: {len(maua_dav):,}")
        print(f"   Range: {maua_nums.min():,} → {maua_nums.max():,}")
        print(f"   Mais comum: {maua_nums.mode().iloc[0]:,}")
    
    # === ANÁLISE DE MATCH REAL ===
    print(f"\n🔍 === MATCH REAL POR FAIXA === 🔍")
    
    for faixa, (min_val, max_val) in [
        ('0-999', (0, 999)),
        ('1k-2k', (1000, 1999)),
        ('2k-3k', (2000, 2999)),
        ('3k-4k', (3000, 3999)),
        ('4k-5k', (4000, 4999)),
        ('5k-6k', (5000, 5999)),
        ('6k-7k', (6000, 6999)),
        ('7k-8k', (7000, 7999)),
        ('8k-9k', (8000, 8999))
    ]:
        # DAV nesta faixa
        dav_faixa = set(dav_nums[(dav_nums >= min_val) & (dav_nums <= max_val)])
        
        # Vendas nesta faixa
        vendas_faixa = set(vendas_nums[(vendas_nums >= min_val) & (vendas_nums <= max_val)])
        
        # Match
        match_faixa = dav_faixa & vendas_faixa
        
        if len(match_faixa) > 0:
            print(f"🎯 {faixa}: {len(match_faixa):,} matches diretos")
    
    return {
        'dav_total': len(dav_com_os),
        'vendas_total': len(vendas_com_num),
        'faixas_dav': faixas_dav,
        'faixas_vendas': faixas_vendas
    }

def main():
    """Função principal"""
    print("🚀 === ANÁLISE ULTRA-COMPLETA DE POTENCIAL === 🚀")
    
    resultado = analise_completa_numeros()
    
    print(f"\n📊 === RESUMO === 📊")
    print(f"📊 Total DAV com entregas: {resultado['dav_total']:,}")
    print(f"📊 Total vendas com números: {resultado['vendas_total']:,}")
    print(f"🎯 CONCLUSÃO: Há muito potencial ainda não explorado!")
    print(f"💡 Próximo passo: Expandir ranges de cruzamento")

if __name__ == "__main__":
    main()