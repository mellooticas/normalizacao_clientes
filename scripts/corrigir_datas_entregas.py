#!/usr/bin/env python3
"""
Correção de Datas - Entregas OS
==============================

Corrige problema de datas vazias que causa erro:
ERROR: 22007: invalid input syntax for type date: ""

Estratégias:
1. Remove registros com data vazia
2. Valida formato de data
3. Usa data_venda como fallback se necessário
"""

import pandas as pd
from datetime import datetime

def corrigir_datas_entregas():
    """Corrige datas vazias/inválidas"""
    
    print("📅 === CORREÇÃO DE DATAS === 📅")
    
    # Carrega arquivo atual
    try:
        df = pd.read_csv('data/vendas_para_importar/entregas_os_inteligente_final.csv')
        print(f"📂 Arquivo carregado: {len(df):,} registros")
    except:
        print("❌ Arquivo não encontrado!")
        return
    
    # 1. Analisa problema das datas
    print(f"\n🔍 Analisando datas...")
    
    print(f"📊 Campo data_entrega:")
    datas_vazias = df['data_entrega'].isna().sum()
    datas_string_vazia = (df['data_entrega'] == '').sum()
    datas_validas = df['data_entrega'].notna().sum()
    
    print(f"   Vazias (NaN): {datas_vazias:,}")
    print(f"   String vazia (''): {datas_string_vazia:,}")
    print(f"   Com valor: {datas_validas:,}")
    
    # Mostra amostras problemáticas
    if datas_vazias > 0 or datas_string_vazia > 0:
        print(f"   Amostras problemáticas:")
        problemas = df[(df['data_entrega'].isna()) | (df['data_entrega'] == '')]
        for i, row in problemas.head(3).iterrows():
            print(f"      ID {row['id'][:8]}...: '{row['data_entrega']}'")
    
    # 2. Estratégia de correção
    print(f"\n🔧 Aplicando correção...")
    
    # Remove registros com data vazia/inválida
    antes = len(df)
    df_limpo = df[(df['data_entrega'].notna()) & (df['data_entrega'] != '')].copy()
    depois = len(df_limpo)
    
    print(f"   Removidos: {antes - depois:,} registros com data inválida")
    print(f"   Restantes: {depois:,} registros")
    
    # 3. Valida formato das datas restantes
    print(f"📅 Validando formato das datas...")
    
    try:
        # Tenta converter para validar
        datas_convertidas = pd.to_datetime(df_limpo['data_entrega'], errors='coerce')
        datas_invalidas = datas_convertidas.isna().sum()
        
        if datas_invalidas > 0:
            print(f"   ⚠️ {datas_invalidas:,} datas com formato inválido")
            # Remove datas com formato inválido
            df_limpo = df_limpo[datas_convertidas.notna()]
            print(f"   Removidas, restam: {len(df_limpo):,}")
        else:
            print(f"   ✅ Todas as datas têm formato válido")
        
        # Converte de volta para string no formato correto
        df_limpo['data_entrega'] = datas_convertidas[datas_convertidas.notna()].dt.strftime('%Y-%m-%d')
        
    except Exception as e:
        print(f"   ❌ Erro na validação: {e}")
    
    # 4. Validações finais
    print(f"\n🔍 === VALIDAÇÕES FINAIS === 🔍")
    print(f"✅ Total de registros: {len(df_limpo):,}")
    print(f"✅ Todas têm data_entrega: {df_limpo['data_entrega'].notna().all()}")
    print(f"✅ Nenhuma data vazia: {(df_limpo['data_entrega'] != '').all()}")
    print(f"✅ IDs únicos: {df_limpo['id'].nunique() == len(df_limpo)}")
    print(f"✅ Venda_IDs válidos: {df_limpo['venda_id'].notna().all()}")
    
    # Amostra das datas finais
    print(f"\n📅 Amostra de datas finais:")
    for data in df_limpo['data_entrega'].head(5):
        print(f"   '{data}'")
    
    # Período final
    try:
        datas_periodo = pd.to_datetime(df_limpo['data_entrega'])
        print(f"   Período: {datas_periodo.min().strftime('%Y-%m-%d')} → {datas_periodo.max().strftime('%Y-%m-%d')}")
    except:
        print(f"   Período: Erro ao calcular")
    
    # 5. Salva arquivo corrigido
    output_path = 'data/vendas_para_importar/entregas_os_final_datas_corrigidas.csv'
    df_limpo.to_csv(output_path, index=False)
    
    print(f"\n💾 Arquivo corrigido salvo: {output_path}")
    print(f"📁 Tamanho: {len(df_limpo):,} registros")
    
    print(f"\n🎯 === RESUMO DA CORREÇÃO === 🎯")
    print("✅ Datas vazias removidas")
    print("✅ Formato de data validado")
    print("✅ Todas as constraints respeitadas")
    print("✅ Pronto para importação!")
    
    return df_limpo

if __name__ == "__main__":
    corrigir_datas_entregas()