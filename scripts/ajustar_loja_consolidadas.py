"""
Script para ajustar a coluna LOJA no arquivo consolidadas.csv
- Vazio → Suzano
- 1 → Suzano 2
"""

import pandas as pd
from pathlib import Path

def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("AJUSTANDO COLUNA LOJA")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    col_name = 'LOJA'
    
    # Situação ANTES
    print("="*80)
    print("📊 SITUAÇÃO ANTES")
    print("="*80)
    print(f"Valores vazios: {df[col_name].isna().sum():,}")
    print(f"Valores = '1': {(df[col_name].astype(str) == '1').sum():,}")
    print()
    print("DISTRIBUIÇÃO:")
    print("-"*80)
    dist_antes = df[col_name].value_counts(dropna=False)
    for val, qtd in dist_antes.items():
        print(f"   [{qtd:4}x] {val}")
    print()
    
    # Contar alterações
    vazios = df[col_name].isna().sum()
    valor_1 = (df[col_name].astype(str) == '1').sum()
    
    # 1. Preencher vazios com "Suzano"
    print("="*80)
    print("🔧 1. PREENCHENDO VAZIOS COM 'Suzano'")
    print("="*80)
    if vazios > 0:
        print(f"   Registros que serão preenchidos: {vazios:,}")
        df[col_name] = df[col_name].fillna('Suzano')
        print(f"   ✅ {vazios:,} registros preenchidos com 'Suzano'")
    else:
        print("   ℹ️  Nenhum registro vazio encontrado")
    print()
    
    # 2. Substituir "1" por "Suzano 2"
    print("="*80)
    print("🔧 2. SUBSTITUINDO '1' POR 'Suzano 2'")
    print("="*80)
    if valor_1 > 0:
        print(f"   Registros que serão substituídos: {valor_1:,}")
        df.loc[df[col_name].astype(str) == '1', col_name] = 'Suzano 2'
        print(f"   ✅ {valor_1:,} registros alterados para 'Suzano 2'")
    else:
        print("   ℹ️  Nenhum registro com valor '1' encontrado")
    print()
    
    # Situação DEPOIS
    print("="*80)
    print("📊 SITUAÇÃO DEPOIS")
    print("="*80)
    print(f"Valores vazios: {df[col_name].isna().sum():,}")
    print(f"Valores = '1': {(df[col_name].astype(str) == '1').sum():,}")
    print()
    print("DISTRIBUIÇÃO:")
    print("-"*80)
    dist_depois = df[col_name].value_counts(dropna=False)
    for val, qtd in dist_depois.items():
        print(f"   [{qtd:4}x] {val}")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_entrada, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_entrada}")
    print()
    
    print("="*80)
    print("✅ AJUSTE CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print()
    print(f"📊 TOTAL DE ALTERAÇÕES: {vazios + valor_1}")
    print(f"   - Vazios → Suzano: {vazios}")
    print(f"   - '1' → Suzano 2: {valor_1}")
    print()


if __name__ == '__main__':
    main()
