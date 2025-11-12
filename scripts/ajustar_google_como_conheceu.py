"""
Ajusta coluna COMO CONHECEU: substitui "Google" por "Google/Facebook/Instagram (Patrocínio)"
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("AJUSTANDO 'GOOGLE' → 'GOOGLE/FACEBOOK/INSTAGRAM (PATROCÍNIO)'")
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
    # Contar "Google" (case-insensitive)
    mask_google = df['COMO CONHECEU'].str.lower() == 'google'
    qtd_google = mask_google.sum()
    
    print(f"   ✓ Registros com 'Google': {qtd_google:,}")
    
    # Substituir "Google" por "Google/Facebook/Instagram (Patrocínio)"
    df.loc[mask_google, 'COMO CONHECEU'] = 'Google/Facebook/Instagram (Patrocínio)'
    
    print(f"\n3. Substituindo valores...")
    print(f"   ✓ {qtd_google:,} registros alterados:")
    print(f"      'Google' → 'Google/Facebook/Instagram (Patrocínio)'")
    
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
