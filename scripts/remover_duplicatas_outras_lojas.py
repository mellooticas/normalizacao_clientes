#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicatas entre OSS+VIXEN e OUTRAS_LOJAS (já importado no banco)
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
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_FINAL_SEM_DUPLICATAS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("REMOÇÃO DE DUPLICATAS COM DADOS JÁ IMPORTADOS")
print("="*80)

# Lê arquivo já importado
print("\n1. Lendo arquivo já importado (OUTRAS_LOJAS)...")
df_outras = pd.read_csv(ARQUIVO_OUTRAS, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df_outras)} registros já no banco")

# Lê arquivo novo
print("\n2. Lendo arquivo novo (OSS+VIXEN)...")
df_novo = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   ✓ {len(df_novo)} registros no arquivo")

# Identifica IDs já existentes
print("\n3. Identificando duplicatas...")
ids_no_banco = set(df_outras['id_legado'])
duplicatas = df_novo['id_legado'].isin(ids_no_banco)
qtd_duplicatas = duplicatas.sum()

if qtd_duplicatas > 0:
    print(f"   ❌ Encontrados {qtd_duplicatas} IDs que já existem no banco")
    
    # Mostra quais serão removidos
    print(f"\n4. IDs que serão removidos:")
    ids_remover = df_novo[duplicatas]['id_legado'].unique()
    for i, id_rem in enumerate(sorted(ids_remover), 1):
        nome_novo = df_novo[df_novo['id_legado']==id_rem]['nome'].iloc[0]
        origem_novo = df_novo[df_novo['id_legado']==id_rem]['origem'].iloc[0]
        print(f"   {i}. {id_rem} - {nome_novo} ({origem_novo})")
    
    # Remove duplicatas
    print(f"\n5. Removendo duplicatas...")
    df_limpo = df_novo[~duplicatas].copy()
    print(f"   ✓ {len(df_limpo)} registros restantes ({qtd_duplicatas} removidos)")
    
else:
    print("   ✓ Nenhuma duplicata encontrada")
    df_limpo = df_novo.copy()

# Salva arquivo limpo
print(f"\n6. Salvando arquivo sem duplicatas...")
df_limpo.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✓ Arquivo salvo: {ARQUIVO_SAIDA}")

# Resumo
print("\n" + "="*80)
print("RESUMO")
print("="*80)
print(f"\nRegistros já no banco (OUTRAS_LOJAS): {len(df_outras)}")
print(f"Registros no arquivo original: {len(df_novo)}")
print(f"Duplicatas removidas: {qtd_duplicatas}")
print(f"Registros finais para importar: {len(df_limpo)}")

print("\n" + "="*80)
print("✅ ARQUIVO PRONTO PARA IMPORTAÇÃO!")
print("="*80)
print(f"\n📁 Arquivo: {ARQUIVO_SAIDA.name}")
