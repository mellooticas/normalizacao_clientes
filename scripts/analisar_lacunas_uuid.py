#!/usr/bin/env python3
"""
Analisar lacunas nos cruzamentos de UUID
"""

import pandas as pd
import glob

def analisar_lacunas_uuid():
    """Analisa por que algumas OS não tiveram UUID mapeado"""
    print("🔍 ANÁLISE DE LACUNAS NOS UUIDs")
    print("="*50)
    
    # Verificar arquivos das OS normalizadas e vendas
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    for loja in lojas:
        print(f"\n📊 LOJA: {loja.upper()}")
        
        # Carregar OS normalizadas
        arquivo_os = f"data/originais/oss/finais_postgresql_prontos/{loja.upper()}_postgresql_pronto.csv"
        try:
            df_os = pd.read_csv(arquivo_os)
            os_normalizadas = pd.to_numeric(df_os['numero_os'], errors='coerce').dropna()
            print(f"   📋 OS normalizadas: {len(os_normalizadas)} ({os_normalizadas.min():.0f} - {os_normalizadas.max():.0f})")
        except FileNotFoundError:
            print(f"   ❌ Arquivo OS não encontrado: {arquivo_os}")
            continue
        
        # Carregar vendas com UUID
        arquivo_vendas = f"data/originais/cxs/extraidos_corrigidos/vendas/vendas_{loja}_com_uuids.csv"
        try:
            df_vendas = pd.read_csv(arquivo_vendas)
            
            # Separar com e sem UUID
            com_uuid = df_vendas[df_vendas['vendedor_uuid'].notna()]
            sem_uuid = df_vendas[df_vendas['vendedor_uuid'].isna()]
            
            print(f"   ✅ Vendas com UUID: {len(com_uuid)}")
            print(f"   ⚠️  Vendas sem UUID: {len(sem_uuid)}")
            
            if len(sem_uuid) > 0:
                # Analisar faixas de OS sem UUID
                os_sem_uuid = sem_uuid['os_numero'].dropna()
                if len(os_sem_uuid) > 0:
                    print(f"   📊 OS sem UUID: {os_sem_uuid.min():.0f} - {os_sem_uuid.max():.0f}")
                    
                    # Verificar se as OS sem UUID existem nas normalizadas
                    os_faltantes = set(os_sem_uuid) - set(os_normalizadas)
                    if os_faltantes:
                        print(f"   🔍 OS inexistentes nas normalizadas: {len(os_faltantes)}")
                        print(f"      Exemplos: {sorted(list(os_faltantes))[:10]}")
        
        except FileNotFoundError:
            print(f"   ❌ Arquivo vendas não encontrado: {arquivo_vendas}")

if __name__ == "__main__":
    analisar_lacunas_uuid()