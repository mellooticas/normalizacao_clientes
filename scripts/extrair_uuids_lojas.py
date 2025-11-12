#!/usr/bin/env python3
"""
Identificar UUIDs corretos das lojas dos dados normalizados
"""

import pandas as pd
import glob

def extrair_uuids_lojas():
    """Extrai UUIDs corretos das lojas dos dados já normalizados"""
    print("🔍 EXTRAINDO UUIDs CORRETOS DAS LOJAS:")
    print("="*50)
    
    arquivos = glob.glob("data/originais/oss/finais_postgresql_prontos/*.csv")
    uuids_lojas = {}
    
    for arquivo in arquivos:
        df = pd.read_csv(arquivo)
        if len(df) > 0:
            loja_nome = df['loja_nome'].iloc[0]
            loja_id = df['loja_id'].iloc[0]
            uuids_lojas[loja_nome] = loja_id
            print(f"✅ {loja_nome}: {loja_id}")
    
    return uuids_lojas

if __name__ == "__main__":
    uuids = extrair_uuids_lojas()
    
    print(f"\n📋 DICIONÁRIO PYTHON:")
    print("uuids_lojas = {")
    for loja, uuid_val in uuids.items():
        print(f"    '{loja}': '{uuid_val}',")
    print("}")