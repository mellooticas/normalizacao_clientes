"""
Ajusta coluna COMO CONHECEU: substitui "Redes Socias" por "Rede Social"
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("AJUSTANDO 'REDES SOCIAS' → 'REDE SOCIAL' NA COLUNA COMO CONHECEU")
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
    # Contar "Redes Socias" (case-insensitive, também pega variações)
    mask_redes = df['COMO CONHECEU'].str.lower().str.contains('redes? socia[is]?', regex=True, na=False)
    qtd_redes = mask_redes.sum()
    
    # Mostrar variações encontradas
    print(f"   ✓ Registros encontrados: {qtd_redes:,}")
    if qtd_redes > 0:
        print(f"\n3. Variações encontradas:")
        for valor in df.loc[mask_redes, 'COMO CONHECEU'].unique():
            count = (df['COMO CONHECEU'] == valor).sum()
            print(f"   {count:>5,} - '{valor}'")
    
    # Substituir por "Rede Social"
    df.loc[mask_redes, 'COMO CONHECEU'] = 'Rede Social'
    
    print(f"\n4. Substituindo valores...")
    print(f"   ✓ {qtd_redes:,} registros alterados → 'Rede Social'")
    
    # Mostrar valores únicos depois
    print(f"\n5. Valores únicos DEPOIS da alteração (top 15):")
    valores_depois = df['COMO CONHECEU'].value_counts()
    for valor, count in valores_depois.head(15).items():
        print(f"   {count:>5,} - {valor}")
    
    # Salvar
    print(f"\n6. Salvando arquivo...")
    df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
    print(f"   ✓ Arquivo salvo: {CSV_PATH.name}")
    print(f"   ✓ {len(df):,} registros mantidos")
    
    print("\n" + "=" * 80)
    print("✅ AJUSTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
else:
    print("   ⚠️ Coluna 'COMO CONHECEU' não encontrada!")
