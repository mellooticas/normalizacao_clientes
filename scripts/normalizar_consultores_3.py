"""
Normaliza nomes de consultores na coluna CONSULTOR (3ª etapa)
- VAZIOS → TATIANA MELLO DE CAMARGO
- BRUNA → WEVILLY
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("NORMALIZANDO NOMES DE CONSULTORES - 3ª ETAPA")
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
    # Contar vazios
    mask_vazio = df['CONSULTOR'].isna() | (df['CONSULTOR'] == '') | (df['CONSULTOR'].str.strip() == '')
    qtd_vazios = mask_vazio.sum()
    
    # Contar BRUNA
    mask_bruna = df['CONSULTOR'] == 'BRUNA'
    qtd_bruna = mask_bruna.sum()
    
    # Mostrar valores únicos ANTES
    print(f"\n3. Valores únicos ANTES da normalização:")
    print(f"   {qtd_vazios:>5,} - (vazios)")
    valores_antes = df['CONSULTOR'].value_counts()
    for valor, count in valores_antes.items():
        print(f"   {count:>5,} - {valor}")
    
    # Aplicar normalizações
    print(f"\n4. Aplicando normalizações...")
    total_alteracoes = 0
    
    # Preencher vazios com TATIANA MELLO DE CAMARGO
    if qtd_vazios > 0:
        df.loc[mask_vazio, 'CONSULTOR'] = 'TATIANA MELLO DE CAMARGO'
        print(f"   ✓ {qtd_vazios:>5,} registros: (vazios) → 'TATIANA MELLO DE CAMARGO'")
        total_alteracoes += qtd_vazios
    
    # BRUNA → WEVILLY
    if qtd_bruna > 0:
        df.loc[mask_bruna, 'CONSULTOR'] = 'WEVILLY'
        print(f"   ✓ {qtd_bruna:>5,} registros: 'BRUNA' → 'WEVILLY'")
        total_alteracoes += qtd_bruna
    
    print(f"\n   Total de alterações: {total_alteracoes:,}")
    
    # Mostrar valores únicos DEPOIS
    print(f"\n5. Valores únicos DEPOIS da normalização:")
    valores_depois = df['CONSULTOR'].value_counts()
    for valor, count in valores_depois.items():
        print(f"   {count:>5,} - {valor}")
    
    # Verificar se ainda tem vazios
    vazios_depois = df['CONSULTOR'].isna().sum() + (df['CONSULTOR'] == '').sum()
    if vazios_depois == 0:
        print(f"\n   ✅ Nenhum registro vazio restante!")
    else:
        print(f"\n   ⚠️ Ainda existem {vazios_depois:,} registros vazios")
    
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
