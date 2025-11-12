#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera novos IDs únicos para evitar conflitos com dados já importados
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent

# Arquivo já no banco
ARQUIVO_OUTRAS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

# Arquivo a ser importado
ARQUIVO_ENTRADA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_FINAL_CORRIGIDO_20251109_133814.csv'

# Arquivo de saída
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_NOVOS_IDS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("GERAÇÃO DE NOVOS IDs ÚNICOS")
print("="*80)

# Lê arquivo já importado
print("\n1. Analisando IDs já no banco...")
df_outras = pd.read_csv(ARQUIVO_OUTRAS, sep=';', dtype={'id_legado': str, 'cpf': str})
ids_numericos_banco = [int(id) for id in df_outras['id_legado'] if id.isdigit()]
if ids_numericos_banco:
    maior_id_banco = max(ids_numericos_banco)
    print(f"   ✓ {len(df_outras)} registros já importados")
    print(f"   ✓ Maior ID numérico no banco: {maior_id_banco}")
else:
    maior_id_banco = 2000000

# Define ID inicial seguro (maior + 10.000 para margem)
id_inicial = maior_id_banco + 10000
print(f"   ✓ ID inicial para novos registros: {id_inicial}")

# Lê arquivo novo
print("\n2. Lendo arquivo atual (OSS+VIXEN)...")
df_novo = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df_novo)} registros no arquivo")

# Gera novos IDs sequenciais
print("\n3. Gerando novos IDs únicos...")
novos_ids = [str(id_inicial + i) for i in range(len(df_novo))]
df_novo['id_legado'] = novos_ids
print(f"   ✓ Novos IDs: {novos_ids[0]} até {novos_ids[-1]}")

# Verifica se há conflitos
print("\n4. Verificando conflitos...")
ids_banco = set(df_outras['id_legado'])
ids_novos = set(df_novo['id_legado'])
conflitos = ids_banco.intersection(ids_novos)

if conflitos:
    print(f"   ❌ ATENÇÃO: {len(conflitos)} conflitos encontrados!")
    print(f"   IDs conflitantes: {list(conflitos)[:10]}")
else:
    print("   ✓ Nenhum conflito - todos os IDs são únicos!")

# Salva arquivo com novos IDs
print("\n5. Salvando arquivo com novos IDs...")
df_novo.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✓ Arquivo salvo: {ARQUIVO_SAIDA}")

# Estatísticas por origem
print("\n" + "="*80)
print("ESTATÍSTICAS DO ARQUIVO FINAL")
print("="*80)

print(f"\nTotal de registros: {len(df_novo)}")
print(f"\nPor origem:")
for origem, count in df_novo['origem'].value_counts().items():
    ids_origem = df_novo[df_novo['origem']==origem]['id_legado']
    print(f"   {origem}: {count} registros")
    print(f"      IDs: {ids_origem.min()} até {ids_origem.max()}")

print(f"\nCobertura de dados:")
print(f"   CPF: {df_novo['cpf'].notna().sum()} ({df_novo['cpf'].notna().sum()/len(df_novo)*100:.1f}%)")
print(f"   Email: {df_novo['email'].notna().sum()} ({df_novo['email'].notna().sum()/len(df_novo)*100:.1f}%)")
print(f"   Data Nasc: {df_novo['data_nascimento'].notna().sum()} ({df_novo['data_nascimento'].notna().sum()/len(df_novo)*100:.1f}%)")
print(f"   Sexo: {df_novo['sexo'].notna().sum()} ({df_novo['sexo'].notna().sum()/len(df_novo)*100:.1f}%)")
print(f"   Cliente Desde: {df_novo['cliente_desde'].notna().sum()} ({df_novo['cliente_desde'].notna().sum()/len(df_novo)*100:.1f}%)")

print("\n" + "="*80)
print("✅ ARQUIVO PRONTO PARA IMPORTAÇÃO!")
print("="*80)
print(f"\n📁 Arquivo: {ARQUIVO_SAIDA.name}")
print(f"🔢 IDs: {id_inicial} até {id_inicial + len(df_novo) - 1}")
print(f"📊 Total: {len(df_novo)} registros")
