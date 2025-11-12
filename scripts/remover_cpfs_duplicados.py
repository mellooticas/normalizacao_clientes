#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove registros com CPFs que causam erro de duplicação no banco.
Estratégia: Remove registros com CPF preenchido que possam existir no banco.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent

# CPFs conhecidos que já existem no banco (do erro)
CPFS_JA_NO_BANCO = [
    '41454990856',  # mary hellen amancio pereira
    '39636169896',  # novo erro de duplicação
]

# Arquivo a ser importado
ARQUIVO_ENTRADA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_NOVOS_IDS_20251109_134846.csv'

# Arquivo de saída
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_SEM_CPF_DUPLICADO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("REMOÇÃO DE REGISTROS COM CPF DUPLICADO")
print("="*80)

# Lê arquivo
print("\n1. Lendo arquivo...")
df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df)} registros no arquivo")
print(f"   ✓ {df['cpf'].notna().sum()} registros com CPF preenchido")

# Identifica registros com CPFs conhecidos que já existem
print("\n2. Identificando CPFs que já existem no banco...")
cpfs_duplicados = df['cpf'].isin(CPFS_JA_NO_BANCO)
qtd_duplicados = cpfs_duplicados.sum()

if qtd_duplicados > 0:
    print(f"   ❌ {qtd_duplicados} registros com CPF duplicado encontrados")
    
    print(f"\n3. Registros que serão removidos:")
    for idx, row in df[cpfs_duplicados].iterrows():
        print(f"      CPF {row['cpf']} - {row['nome']} ({row['origem']})")
    
    # Remove duplicados
    print(f"\n4. Removendo registros duplicados...")
    df_limpo = df[~cpfs_duplicados].copy()
    print(f"   ✓ {len(df_limpo)} registros restantes ({qtd_duplicados} removidos)")
    
else:
    print("   ✓ Nenhum CPF duplicado conhecido encontrado")
    df_limpo = df.copy()

# Salva arquivo limpo
print(f"\n5. Salvando arquivo sem duplicados...")
df_limpo.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✓ Arquivo salvo: {ARQUIVO_SAIDA}")

# Estatísticas
print("\n" + "="*80)
print("ESTATÍSTICAS DO ARQUIVO FINAL")
print("="*80)

print(f"\nTotal de registros: {len(df_limpo)}")
print(f"\nPor origem:")
for origem, count in df_limpo['origem'].value_counts().items():
    print(f"   {origem}: {count}")

print(f"\nCobertura de dados:")
print(f"   CPF: {df_limpo['cpf'].notna().sum()} ({df_limpo['cpf'].notna().sum()/len(df_limpo)*100:.1f}%)")
print(f"   Email: {df_limpo['email'].notna().sum()} ({df_limpo['email'].notna().sum()/len(df_limpo)*100:.1f}%)")
print(f"   Data Nasc: {df_limpo['data_nascimento'].notna().sum()} ({df_limpo['data_nascimento'].notna().sum()/len(df_limpo)*100:.1f}%)")
print(f"   Sexo: {df_limpo['sexo'].notna().sum()} ({df_limpo['sexo'].notna().sum()/len(df_limpo)*100:.1f}%)")

print("\n" + "="*80)
print("✅ ARQUIVO PRONTO PARA IMPORTAÇÃO!")
print("="*80)
print(f"\n📁 Arquivo: {ARQUIVO_SAIDA.name}")
print(f"📊 Total: {len(df_limpo)} registros")

print("\n⚠️  IMPORTANTE:")
print("   Se houver novo erro de CPF duplicado, adicione o CPF na lista")
print("   CPFS_JA_NO_BANCO no script e execute novamente.")
