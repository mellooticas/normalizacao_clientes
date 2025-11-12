"""
Script para consolidar TELEFONE → CELULAR no arquivo consolidadas.csv
Preenche campos vazios de CELULAR com dados de TELEFONE quando disponíveis
"""

import pandas as pd
from pathlib import Path

def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("CONSOLIDAÇÃO TELEFONE → CELULAR")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    # Mostrar situação ANTES
    print("="*80)
    print("📊 SITUAÇÃO ANTES DA CONSOLIDAÇÃO")
    print("="*80)
    print(f"TELEFONE :: {df['TELEFONE :'].notna().sum():,} preenchidos | {df['TELEFONE :'].isna().sum():,} vazios")
    print(f"CELULAR:: {df['CELULAR:'].notna().sum():,} preenchidos | {df['CELULAR:'].isna().sum():,} vazios")
    print(f"CELULAR:.1: {df['CELULAR:.1'].notna().sum():,} preenchidos | {df['CELULAR:.1'].isna().sum():,} vazios")
    print(f"CELULAR: {df['CELULAR'].notna().sum():,} preenchidos | {df['CELULAR'].isna().sum():,} vazios")
    print()
    
    # Contar consolidações possíveis
    total_consolidacoes = 0
    
    # 1. Consolidar TELEFONE : → CELULAR:
    print("="*80)
    print("🔧 1. CONSOLIDANDO TELEFONE : → CELULAR:")
    print("="*80)
    mask1 = df['CELULAR:'].isna() & df['TELEFONE :'].notna()
    qtd1 = mask1.sum()
    print(f"   Registros que serão preenchidos: {qtd1:,}")
    
    if qtd1 > 0:
        # Mostrar exemplos ANTES
        print("\n   Exemplos ANTES:")
        exemplos_antes = df[mask1][['TELEFONE :', 'CELULAR:']].head(5)
        for idx, row in exemplos_antes.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR: {row['CELULAR:']}")
        
        # Aplicar consolidação
        df.loc[mask1, 'CELULAR:'] = df.loc[mask1, 'TELEFONE :']
        
        # Mostrar exemplos DEPOIS
        print("\n   Exemplos DEPOIS:")
        exemplos_depois = df[mask1][['TELEFONE :', 'CELULAR:']].head(5)
        for idx, row in exemplos_depois.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR: {row['CELULAR:']}")
        
        print(f"\n   ✅ {qtd1:,} registros consolidados")
        total_consolidacoes += qtd1
    print()
    
    # 2. Consolidar TELEFONE : → CELULAR:.1
    print("="*80)
    print("🔧 2. CONSOLIDANDO TELEFONE : → CELULAR:.1")
    print("="*80)
    mask2 = df['CELULAR:.1'].isna() & df['TELEFONE :'].notna()
    qtd2 = mask2.sum()
    print(f"   Registros que serão preenchidos: {qtd2:,}")
    
    if qtd2 > 0:
        # Mostrar exemplos ANTES
        print("\n   Exemplos ANTES:")
        exemplos_antes = df[mask2][['TELEFONE :', 'CELULAR:.1']].head(5)
        for idx, row in exemplos_antes.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR.1: {row['CELULAR:.1']}")
        
        # Aplicar consolidação
        df.loc[mask2, 'CELULAR:.1'] = df.loc[mask2, 'TELEFONE :']
        
        # Mostrar exemplos DEPOIS
        print("\n   Exemplos DEPOIS:")
        exemplos_depois = df[mask2][['TELEFONE :', 'CELULAR:.1']].head(5)
        for idx, row in exemplos_depois.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR.1: {row['CELULAR:.1']}")
        
        print(f"\n   ✅ {qtd2:,} registros consolidados")
        total_consolidacoes += qtd2
    print()
    
    # 3. Consolidar TELEFONE : → CELULAR
    print("="*80)
    print("🔧 3. CONSOLIDANDO TELEFONE : → CELULAR")
    print("="*80)
    mask3 = df['CELULAR'].isna() & df['TELEFONE :'].notna()
    qtd3 = mask3.sum()
    print(f"   Registros que serão preenchidos: {qtd3:,}")
    
    if qtd3 > 0:
        # Mostrar exemplos ANTES
        print("\n   Exemplos ANTES:")
        exemplos_antes = df[mask3][['TELEFONE :', 'CELULAR']].head(5)
        for idx, row in exemplos_antes.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR: {row['CELULAR']}")
        
        # Aplicar consolidação
        df.loc[mask3, 'CELULAR'] = df.loc[mask3, 'TELEFONE :']
        
        # Mostrar exemplos DEPOIS
        print("\n   Exemplos DEPOIS:")
        exemplos_depois = df[mask3][['TELEFONE :', 'CELULAR']].head(5)
        for idx, row in exemplos_depois.iterrows():
            print(f"      TELEFONE: {row['TELEFONE :']} | CELULAR: {row['CELULAR']}")
        
        print(f"\n   ✅ {qtd3:,} registros consolidados")
        total_consolidacoes += qtd3
    print()
    
    # Mostrar situação DEPOIS
    print("="*80)
    print("📊 SITUAÇÃO DEPOIS DA CONSOLIDAÇÃO")
    print("="*80)
    print(f"TELEFONE :: {df['TELEFONE :'].notna().sum():,} preenchidos | {df['TELEFONE :'].isna().sum():,} vazios")
    print(f"CELULAR:: {df['CELULAR:'].notna().sum():,} preenchidos | {df['CELULAR:'].isna().sum():,} vazios")
    print(f"CELULAR:.1: {df['CELULAR:.1'].notna().sum():,} preenchidos | {df['CELULAR:.1'].isna().sum():,} vazios")
    print(f"CELULAR: {df['CELULAR'].notna().sum():,} preenchidos | {df['CELULAR'].isna().sum():,} vazios")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_entrada, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_entrada}")
    print()
    
    print("="*80)
    print("✅ CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📊 TOTAL DE REGISTROS CONSOLIDADOS: {total_consolidacoes:,}")
    print()
    print("RESUMO:")
    print("-"*80)
    print(f"   CELULAR: → {qtd1:,} preenchidos")
    print(f"   CELULAR:.1 → {qtd2:,} preenchidos")
    print(f"   CELULAR → {qtd3:,} preenchidos")
    print()


if __name__ == '__main__':
    main()
