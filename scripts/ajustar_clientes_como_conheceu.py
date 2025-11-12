"""
Ajusta coluna COMO CONHECEU: substitui "Clientes" por "Já É Cliente"
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("AJUSTANDO 'CLIENTES' → 'JÁ É CLIENTE' NA COLUNA COMO CONHECEU")
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
    # Contar "Clientes" (case-insensitive)
    mask_clientes = df['COMO CONHECEU'].str.lower() == 'clientes'
    qtd_clientes = mask_clientes.sum()
    
    print(f"   ✓ Registros com 'Clientes': {qtd_clientes:,}")
    
    # Mostrar valores únicos antes
    print(f"\n3. Valores únicos ANTES da alteração:")
    valores_antes = df['COMO CONHECEU'].value_counts()
    for valor, count in valores_antes.head(15).items():
        print(f"   {count:>5,} - {valor}")
    
    # Substituir "Clientes" por "Já É Cliente" (case-insensitive)
    df.loc[mask_clientes, 'COMO CONHECEU'] = 'Já É Cliente'
    
    print(f"\n4. Substituindo valores...")
    print(f"   ✓ {qtd_clientes:,} registros alterados: 'Clientes' → 'Já É Cliente'")
    
    # Mostrar valores únicos depois
    print(f"\n5. Valores únicos DEPOIS da alteração:")
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
