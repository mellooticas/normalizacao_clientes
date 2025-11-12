"""
Verifica estrutura dos arquivos OSS.csv e consolidadas.csv
"""
import pandas as pd
from pathlib import Path

print("VERIFICANDO ARQUIVOS:")

print("\n1. consolidadas.csv:")
p1 = Path('dados_processados/originais/oss/consolidadas/consolidadas.csv')
if p1.exists():
    df1 = pd.read_csv(p1, sep=';', dtype=str, nrows=2)
    print(f"   ✓ Existe: {p1}")
    print(f"   ✓ Total linhas: {len(pd.read_csv(p1, sep=';', dtype=str)):,}")
    print(f"   ✓ Total colunas: {len(df1.columns)}")
    print(f"   ✓ Tem ID_CLIENTE: {'ID_CLIENTE' in df1.columns}")
    if 'ID_CLIENTE' in df1.columns:
        print(f"   ✓ Primeiros IDs: {df1['ID_CLIENTE'].tolist()}")

print("\n2. OSS.csv:")
p2 = Path('dados_processados/originais/clientes/normalizados/OSS.csv')
if p2.exists():
    df2 = pd.read_csv(p2, sep=';', dtype=str, nrows=2)
    print(f"   ✓ Existe: {p2}")
    print(f"   ✓ Total linhas: {len(pd.read_csv(p2, sep=';', dtype=str)):,}")
    print(f"   ✓ Total colunas: {len(df2.columns)}")
    print(f"   ✓ Tem ID_CLIENTE: {'ID_CLIENTE' in df2.columns}")
    print(f"   ✓ Primeiras colunas: {df2.columns.tolist()[:8]}")
