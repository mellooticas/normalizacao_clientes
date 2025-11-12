#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Divide arquivo grande em lotes menores para importação incremental
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent
ARQUIVO_ENTRADA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_SEM_DUPLICATAS_CPF_20251109_141916.csv'
DIR_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar'

TAMANHO_LOTE = 1000  # Registros por arquivo

print("="*80)
print("DIVISÃO DO ARQUIVO EM LOTES")
print("="*80)

# Cria diretório de saída
DIR_SAIDA.mkdir(parents=True, exist_ok=True)
print(f"\nDiretório de saída: {DIR_SAIDA}")

# Lê arquivo completo
print(f"\n1. Lendo arquivo completo...")
df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'id_legado': str, 'cpf': str})
print(f"   Total: {len(df)} registros")

# Calcula número de lotes
num_lotes = (len(df) + TAMANHO_LOTE - 1) // TAMANHO_LOTE
print(f"\n2. Dividindo em lotes de {TAMANHO_LOTE} registros...")
print(f"   Total de lotes: {num_lotes}")

# Divide em lotes
arquivos_criados = []
for i in range(num_lotes):
    inicio = i * TAMANHO_LOTE
    fim = min((i + 1) * TAMANHO_LOTE, len(df))
    
    lote = df.iloc[inicio:fim]
    
    # Nome do arquivo
    nome_arquivo = f'lote_{i+1:03d}_registros_{inicio+1}_a_{fim}.csv'
    caminho_arquivo = DIR_SAIDA / nome_arquivo
    
    # Salva lote
    lote.to_csv(caminho_arquivo, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
    
    arquivos_criados.append({
        'lote': i + 1,
        'arquivo': nome_arquivo,
        'registros': len(lote),
        'id_inicial': lote.iloc[0]['id_legado'],
        'id_final': lote.iloc[-1]['id_legado']
    })
    
    print(f"   ✓ Lote {i+1:2d}: {len(lote):4d} registros (IDs: {lote.iloc[0]['id_legado']} → {lote.iloc[-1]['id_legado']})")

# Resumo
print("\n" + "="*80)
print("RESUMO DOS LOTES CRIADOS")
print("="*80)

print(f"\nTotal de arquivos: {len(arquivos_criados)}")
print(f"Total de registros: {sum(a['registros'] for a in arquivos_criados)}")

print("\n📁 Arquivos criados em:")
print(f"   {DIR_SAIDA}")

print("\n" + "="*80)
print("INSTRUÇÕES DE IMPORTAÇÃO")
print("="*80)
print("\n1. Faça TRUNCATE no banco:")
print("   TRUNCATE TABLE core.clientes CASCADE;")
print("\n2. Importe os lotes NA ORDEM:")
for arq in arquivos_criados:
    print(f"   {arq['lote']:2d}. {arq['arquivo']}")
print("\n3. Se der erro em algum lote:")
print("   - Anote qual lote deu erro")
print("   - Verifique quantos registros foram importados")
print("   - Podemos dividir esse lote em arquivos menores (500)")
print("\n4. Após importar todos os lotes:")
print("   SELECT COUNT(*) FROM core.clientes;")
print("   -- Deve retornar: 12480")

print("\n" + "="*80)
print("✅ DIVISÃO CONCLUÍDA!")
print("="*80)
