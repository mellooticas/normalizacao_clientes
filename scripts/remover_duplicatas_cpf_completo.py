#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove TODAS as duplicatas de CPF mantendo apenas a primeira ocorrência
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

DIR_BASE = Path(__file__).parent.parent
ARQUIVO_ENTRADA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_TODAS_BASES_CONSOLIDADO_20251109_140102.csv'
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_SEM_DUPLICATAS_CPF_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("REMOCAO COMPLETA DE DUPLICATAS DE CPF")
print("="*80)

# Lê arquivo
print("\n1. Lendo arquivo...")
df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   Total: {len(df)} registros")
print(f"   CPFs preenchidos: {df['cpf'].notna().sum()}")

# Remove duplicatas de CPF (mantém a primeira ocorrência)
print("\n2. Removendo duplicatas de CPF...")
antes = len(df)

# Registros SEM CPF (mantém todos)
df_sem_cpf = df[df['cpf'].isna()].copy()

# Registros COM CPF (remove duplicatas)
df_com_cpf = df[df['cpf'].notna()].copy()
df_com_cpf_unico = df_com_cpf.drop_duplicates(subset=['cpf'], keep='first')

duplicatas_removidas = len(df_com_cpf) - len(df_com_cpf_unico)

if duplicatas_removidas > 0:
    print(f"   Duplicatas removidas: {duplicatas_removidas}")
    
    # Mostra quais foram removidos
    cpfs_duplicados = df_com_cpf[df_com_cpf.duplicated(subset=['cpf'], keep='first')]
    print(f"\n   CPFs duplicados removidos:")
    for idx, row in cpfs_duplicados.iterrows():
        print(f"      CPF {row['cpf']}: {row['nome']} (ID: {row['id_legado']}, {row['origem']})")
else:
    print("   Nenhuma duplicata encontrada")

# Reconstrói DataFrame
df_final = pd.concat([df_com_cpf_unico, df_sem_cpf], ignore_index=True)
print(f"\n3. Total final: {len(df_final)} registros")

# Verifica duplicatas finais
print("\n4. Verificação final...")
cpfs_final = df_final[df_final['cpf'].notna()]
if cpfs_final['cpf'].duplicated().sum() > 0:
    print("   ❌ AINDA HÁ DUPLICATAS!")
else:
    print("   ✅ Nenhuma duplicata de CPF")

# Verifica IDs
if df_final['id_legado'].duplicated().sum() > 0:
    print("   ❌ HÁ DUPLICATAS DE ID!")
else:
    print("   ✅ Nenhuma duplicata de ID")

# Salva
print(f"\n5. Salvando arquivo...")
df_final.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✅ Arquivo salvo: {ARQUIVO_SAIDA}")

# Estatísticas
print("\n" + "="*80)
print("ESTATÍSTICAS FINAIS")
print("="*80)
print(f"\nTotal de registros: {len(df_final)}")
print(f"CPFs preenchidos: {df_final['cpf'].notna().sum()}")
print(f"CPFs únicos: {df_final[df_final['cpf'].notna()]['cpf'].nunique()}")

print(f"\nPor origem:")
for origem, count in df_final['origem'].value_counts().items():
    print(f"   {origem}: {count}")

print("\n" + "="*80)
print("✅ ARQUIVO PRONTO!")
print("="*80)
print(f"\n📁 {ARQUIVO_SAIDA.name}")
print(f"📊 {len(df_final)} registros")
print(f"🔄 {duplicatas_removidas} duplicatas removidas")
