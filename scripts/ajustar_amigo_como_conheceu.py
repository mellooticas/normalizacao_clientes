"""
Ajusta coluna COMO CONHECEU: substitui "Amigo (Ind)" por "Indicação"
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("AJUSTANDO 'AMIGO (IND)' → 'INDICAÇÃO' NA COLUNA COMO CONHECEU")
print("=" * 80)

# Leitura
print(f"\n1. Lendo arquivo: {CSV_PATH.name}")
df = pd.read_csv(CSV_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros, {len(df.columns)} colunas")

# Limpar nomes das colunas
df.columns = df.columns.str.strip()

# Verificar valores atuais
print(f"\n2. Analisando coluna COMO CONHECEU")
if 'COMO CONHECEU' in df.columns:
    # Contar "Amigo (Ind)" (case-insensitive)
    mask_amigo = df['COMO CONHECEU'].str.lower() == 'amigo (ind)'
    qtd_amigo = mask_amigo.sum()
    
    # Contar "Indicação" atual
    mask_indicacao_antes = df['COMO CONHECEU'] == 'Indicação'
    qtd_indicacao_antes = mask_indicacao_antes.sum()
    
    print(f"   ✓ Registros com 'Amigo (Ind)': {qtd_amigo:,}")
    print(f"   ✓ Registros com 'Indicação' (antes): {qtd_indicacao_antes:,}")
    
    # Substituir "Amigo (Ind)" por "Indicação"
    df.loc[mask_amigo, 'COMO CONHECEU'] = 'Indicação'
    
    # Contar "Indicação" depois
    mask_indicacao_depois = df['COMO CONHECEU'] == 'Indicação'
    qtd_indicacao_depois = mask_indicacao_depois.sum()
    
    print(f"\n3. Substituindo valores...")
    print(f"   ✓ {qtd_amigo:,} registros alterados: 'Amigo (Ind)' → 'Indicação'")
    print(f"   ✓ Total 'Indicação' agora: {qtd_indicacao_depois:,} ({qtd_indicacao_antes:,} + {qtd_amigo:,})")
    
    # Mostrar valores únicos depois
    print(f"\n4. Valores únicos DEPOIS da alteração (top 15):")
    valores_depois = df['COMO CONHECEU'].value_counts()
    for valor, count in valores_depois.head(15).items():
        print(f"   {count:>5,} - {valor}")
    
    # Salvar
    print(f"\n5. Salvando arquivo...")
    df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
    print(f"   ✓ Arquivo salvo: {CSV_PATH.name}")
    print(f"   ✓ {len(df):,} registros mantidos")
    
    print("\n" + "=" * 80)
    print("✅ AJUSTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
else:
    print("   ⚠️ Coluna 'COMO CONHECEU' não encontrada!")
