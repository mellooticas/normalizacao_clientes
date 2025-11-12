"""
Script para preencher valores vazios de COMO CONHECEU com "Já É Cliente"
"""

import pandas as pd
from pathlib import Path

def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("PREENCHENDO 'COMO CONHECEU' VAZIO COM 'Já É Cliente'")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    col_name = 'COMO CONHECEU'
    
    # Situação ANTES
    vazios_antes = df[col_name].isna().sum()
    print(f"📊 ANTES:")
    print(f"   Valores vazios: {vazios_antes:,}")
    print(f"   Valores preenchidos: {df[col_name].notna().sum():,}")
    print()
    
    # Mostrar alguns exemplos de registros vazios
    if vazios_antes > 0:
        print("📝 EXEMPLOS DE REGISTROS VAZIOS (primeiros 5):")
        print("-"*80)
        exemplos_idx = df[df[col_name].isna()].head(5).index
        for idx in exemplos_idx:
            print(f"   Registro {idx}: Como conheceu = {df.loc[idx, col_name]}")
        print()
    
    # Preencher vazios
    print("🔧 Preenchendo valores vazios com 'Já É Cliente'...")
    df[col_name] = df[col_name].fillna('Já É Cliente')
    
    # Situação DEPOIS
    vazios_depois = df[col_name].isna().sum()
    ja_cliente = (df[col_name] == 'Já É Cliente').sum()
    print()
    print(f"📊 DEPOIS:")
    print(f"   Valores vazios: {vazios_depois:,}")
    print(f"   'Já É Cliente': {ja_cliente:,}")
    print(f"   Total preenchidos: {df[col_name].notna().sum():,}")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_entrada, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_entrada}")
    print()
    
    print("="*80)
    print("✅ PREENCHIMENTO CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print()
    
    # Mostrar distribuição final
    print("DISTRIBUIÇÃO FINAL 'COMO CONHECEU':")
    print("-"*80)
    dist = df[col_name].value_counts()
    for val, qtd in dist.items():
        print(f"   [{qtd:4}x] {val}")
    print()


if __name__ == '__main__':
    main()
