#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolida TODAS as bases em um único arquivo para importação
Remove duplicatas de CPF dando prioridade para OSS+VIXEN
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent

# Arquivos de entrada
ARQUIVO_OSS_VIXEN = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_SEM_CPF_DUPLICADO_20251109_135420.csv'
ARQUIVO_OUTRAS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

# Arquivo de saída
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_TODAS_BASES_CONSOLIDADO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("CONSOLIDAÇÃO FINAL - TODAS AS BASES")
print("="*80)

# Lê OSS+VIXEN
print("\n1. Lendo OSS+VIXEN (já limpo)...")
df_oss_vixen = pd.read_csv(ARQUIVO_OSS_VIXEN, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df_oss_vixen)} registros")
print(f"   ✓ {df_oss_vixen['cpf'].notna().sum()} CPFs preenchidos")

# Lê OUTRAS_LOJAS
print("\n2. Lendo OUTRAS_LOJAS...")
df_outras = pd.read_csv(ARQUIVO_OUTRAS, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df_outras)} registros")
print(f"   ✓ {df_outras['cpf'].notna().sum()} CPFs preenchidos")

# Remove duplicatas de CPF em OUTRAS_LOJAS
print("\n3. Removendo duplicatas de CPF...")
cpfs_oss_vixen = set(df_oss_vixen[df_oss_vixen['cpf'].notna()]['cpf'])
cpfs_duplicados_outras = df_outras['cpf'].isin(cpfs_oss_vixen)
qtd_duplicados = cpfs_duplicados_outras.sum()

if qtd_duplicados > 0:
    print(f"   ⚠️  {qtd_duplicados} registros de OUTRAS_LOJAS tem CPF duplicado com OSS+VIXEN")
    print(f"   Removendo (prioridade para OSS+VIXEN)...")
    
    # Mostra quais serão removidos
    print(f"\n   Registros de OUTRAS_LOJAS que serão REMOVIDOS:")
    for idx, row in df_outras[cpfs_duplicados_outras].iterrows():
        cpf = row['cpf']
        nome_outras = row['nome']
        # Busca no OSS+VIXEN
        match = df_oss_vixen[df_oss_vixen['cpf'] == cpf]
        if len(match) > 0:
            nome_oss = match.iloc[0]['nome']
            origem_oss = match.iloc[0]['origem']
            print(f"      CPF {cpf}: '{nome_outras}' (removido) ← mantido '{nome_oss}' de {origem_oss}")
    
    df_outras_limpo = df_outras[~cpfs_duplicados_outras].copy()
else:
    print("   ✓ Nenhuma duplicata encontrada")
    df_outras_limpo = df_outras.copy()

# Concatena tudo
print(f"\n4. Consolidando arquivos...")
df_final = pd.concat([df_oss_vixen, df_outras_limpo], ignore_index=True)
print(f"   ✓ {len(df_final)} registros totais")

# Verifica duplicatas finais
print(f"\n5. Verificações finais...")
print(f"   IDs únicos: {df_final['id_legado'].nunique() == len(df_final)} {'✅' if df_final['id_legado'].nunique() == len(df_final) else '❌'}")
cpfs_final = df_final[df_final['cpf'].notna()]
print(f"   CPFs únicos: {cpfs_final['cpf'].nunique() == len(cpfs_final)} {'✅' if cpfs_final['cpf'].nunique() == len(cpfs_final) else '❌'}")

# Salva arquivo final
print(f"\n6. Salvando arquivo consolidado...")
df_final.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✓ Arquivo salvo: {ARQUIVO_SAIDA}")

# Estatísticas
print("\n" + "="*80)
print("ESTATÍSTICAS DO ARQUIVO FINAL")
print("="*80)

print(f"\nTotal de registros: {len(df_final)}")
print(f"\nPor origem:")
for origem, count in df_final['origem'].value_counts().items():
    print(f"   {origem}: {count}")

print(f"\nCobertura de dados:")
print(f"   CPF: {df_final['cpf'].notna().sum()} ({df_final['cpf'].notna().sum()/len(df_final)*100:.1f}%)")
print(f"   Email: {df_final['email'].notna().sum()} ({df_final['email'].notna().sum()/len(df_final)*100:.1f}%)")
print(f"   Data Nasc: {df_final['data_nascimento'].notna().sum()} ({df_final['data_nascimento'].notna().sum()/len(df_final)*100:.1f}%)")
print(f"   Sexo: {df_final['sexo'].notna().sum()} ({df_final['sexo'].notna().sum()/len(df_final)*100:.1f}%)")

print("\n" + "="*80)
print("✅ ARQUIVO ÚNICO PRONTO PARA IMPORTAÇÃO!")
print("="*80)
print(f"\n📁 Arquivo: {ARQUIVO_SAIDA.name}")
print(f"📊 Total: {len(df_final)} clientes")
print(f"🔄 Duplicatas removidas: {qtd_duplicados}")
print(f"\n💡 Importe APENAS este arquivo após TRUNCATE no banco!")
