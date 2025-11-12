"""
Normaliza nomes de consultores na coluna CONSULTOR (2ª etapa)
- TATY → TATIANA MELLO DE CAMARGO
- ARIANI → ARIANI DIAS FERNANDES CARDOSO
- ERIKA → ÉRIKA
- FELIPE → FELIPE MIRANDA
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("NORMALIZANDO NOMES DE CONSULTORES - 2ª ETAPA")
print("=" * 80)

# Leitura
print(f"\n1. Lendo arquivo: {CSV_PATH.name}")
df = pd.read_csv(CSV_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros, {len(df.columns)} colunas")

# Limpar nomes das colunas
df.columns = df.columns.str.strip()

# Verificar coluna CONSULTOR
print(f"\n2. Analisando coluna CONSULTOR")
if 'CONSULTOR' in df.columns:
    # Mostrar valores únicos ANTES
    print(f"\n3. Valores únicos ANTES da normalização:")
    valores_antes = df['CONSULTOR'].value_counts()
    for valor, count in valores_antes.items():
        print(f"   {count:>5,} - {valor}")
    
    # Mapeamento de nomes
    mapeamento = {
        'TATY': 'TATIANA MELLO DE CAMARGO',
        'Taty': 'TATIANA MELLO DE CAMARGO',
        'taty': 'TATIANA MELLO DE CAMARGO',
        'ARIANI': 'ARIANI DIAS FERNANDES CARDOSO',
        'Ariani': 'ARIANI DIAS FERNANDES CARDOSO',
        'ariani': 'ARIANI DIAS FERNANDES CARDOSO',
        'ERIKA': 'ÉRIKA',
        'Erika': 'ÉRIKA',
        'erika': 'ÉRIKA',
        'FELIPE': 'FELIPE MIRANDA',
        'Felipe': 'FELIPE MIRANDA',
        'felipe': 'FELIPE MIRANDA'
    }
    
    # Aplicar mapeamento
    print(f"\n4. Aplicando normalizações...")
    total_alteracoes = 0
    
    for nome_antigo, nome_novo in mapeamento.items():
        mask = df['CONSULTOR'] == nome_antigo
        qtd = mask.sum()
        if qtd > 0:
            df.loc[mask, 'CONSULTOR'] = nome_novo
            total_alteracoes += qtd
            print(f"   ✓ {qtd:>5,} registros: '{nome_antigo}' → '{nome_novo}'")
    
    print(f"\n   Total de alterações: {total_alteracoes:,}")
    
    # Mostrar valores únicos DEPOIS
    print(f"\n5. Valores únicos DEPOIS da normalização:")
    valores_depois = df['CONSULTOR'].value_counts()
    for valor, count in valores_depois.items():
        print(f"   {count:>5,} - {valor}")
    
    # Salvar
    print(f"\n6. Salvando arquivo...")
    df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
    print(f"   ✓ Arquivo salvo: {CSV_PATH.name}")
    print(f"   ✓ {len(df):,} registros mantidos")
    
    print("\n" + "=" * 80)
    print("✅ NORMALIZAÇÃO DE CONSULTORES CONCLUÍDA!")
    print("=" * 80)
else:
    print("   ⚠️ Coluna 'CONSULTOR' não encontrada!")
