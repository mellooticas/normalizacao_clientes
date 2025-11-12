"""
Separa arquivo OSS.csv em 2 arquivos baseado na coluna LOJA:
1. OSS_SUZANO_MAUA.csv - Lojas SUZANO e MAUÁ
2. OSS_OUTRAS_LOJAS.csv - Demais lojas
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
OSS_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'OSS.csv'
OUTPUT_DIR = OSS_PATH.parent

print("=" * 80)
print("SEPARANDO OSS.CSV POR LOJAS")
print("=" * 80)

# 1. Ler arquivo OSS.csv
print(f"\n1. Lendo arquivo: {OSS_PATH.name}")
df = pd.read_csv(OSS_PATH, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip()
print(f"   ✓ {len(df):,} registros")
print(f"   ✓ {len(df.columns)} colunas")

# 2. Analisar distribuição de lojas
print(f"\n2. Analisando distribuição de lojas...")
if 'LOJA' in df.columns:
    distribuicao_lojas = df['LOJA'].value_counts()
    print(f"\n   Distribuição atual:")
    for loja, count in distribuicao_lojas.items():
        print(f"   - {loja}: {count:,} OSS ({count/len(df)*100:.1f}%)")
else:
    print("   ⚠️ Coluna LOJA não encontrada!")
    exit(1)

# 3. Separar em 2 grupos
print(f"\n3. Separando em 2 grupos...")

# Grupo 1: SUZANO e MAUÁ
grupo1_lojas = ['SUZANO', 'MAUÁ']
mask_grupo1 = df['LOJA'].str.upper().isin([loja.upper() for loja in grupo1_lojas])
df_suzano_maua = df[mask_grupo1].copy()

# Grupo 2: Restante
df_outras = df[~mask_grupo1].copy()

print(f"\n   GRUPO 1 - SUZANO + MAUÁ:")
print(f"   ✓ {len(df_suzano_maua):,} OSS ({len(df_suzano_maua)/len(df)*100:.1f}%)")
if len(df_suzano_maua) > 0:
    dist_g1 = df_suzano_maua['LOJA'].value_counts()
    for loja, count in dist_g1.items():
        print(f"     - {loja}: {count:,} OSS")
    print(f"   ✓ {df_suzano_maua['ID_CLIENTE'].nunique():,} clientes únicos")

print(f"\n   GRUPO 2 - OUTRAS LOJAS:")
print(f"   ✓ {len(df_outras):,} OSS ({len(df_outras)/len(df)*100:.1f}%)")
if len(df_outras) > 0:
    dist_g2 = df_outras['LOJA'].value_counts()
    for loja, count in dist_g2.items():
        print(f"     - {loja}: {count:,} OSS")
    print(f"   ✓ {df_outras['ID_CLIENTE'].nunique():,} clientes únicos")

# 4. Salvar arquivos
print(f"\n4. Salvando arquivos...")

# Arquivo 1: SUZANO + MAUÁ
arquivo1 = OUTPUT_DIR / 'OSS_SUZANO_MAUA.csv'
df_suzano_maua.to_csv(arquivo1, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo 1 salvo: {arquivo1.name}")
print(f"     - {len(df_suzano_maua):,} registros")
print(f"     - {len(df_suzano_maua.columns)} colunas")

# Arquivo 2: Outras lojas
arquivo2 = OUTPUT_DIR / 'OSS_OUTRAS_LOJAS.csv'
df_outras.to_csv(arquivo2, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo 2 salvo: {arquivo2.name}")
print(f"     - {len(df_outras):,} registros")
print(f"     - {len(df_outras.columns)} colunas")

# 5. Verificação final
print(f"\n5. Verificação final...")
total_separado = len(df_suzano_maua) + len(df_outras)
print(f"   ✓ Total original: {len(df):,} OSS")
print(f"   ✓ Total separado: {total_separado:,} OSS")
print(f"   ✓ Diferença: {len(df) - total_separado} OSS")

if len(df) == total_separado:
    print(f"   ✅ Todos os registros foram separados corretamente!")
else:
    print(f"   ⚠️ ATENÇÃO: Há diferença no total de registros!")

print("\n" + "=" * 80)
print("✅ SEPARAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 80)
print(f"\nArquivos criados:")
print(f"  1. {arquivo1.name} ({len(df_suzano_maua):,} OSS)")
print(f"  2. {arquivo2.name} ({len(df_outras):,} OSS)")
print(f"\nArquivo original mantido: {OSS_PATH.name}")
print("=" * 80)
