#!/usr/bin/env python3
"""
Script para separar registros de CARNÊ LANCASTER dos demais pagamentos
no arquivo trans_financ_consolidado_completo.csv
"""

import pandas as pd
from pathlib import Path

def main():
    # Caminhos
    arquivo_entrada = Path('1_normalizacao/dados_processados/originais/controles_gerais/trans_financ/trans_financ_consolidado/trans_financ_consolidado_completo.csv')
    arquivo_carne = Path('1_normalizacao/dados_processados/originais/controles_gerais/trans_financ/trans_financ_consolidado/carne_lancaster_entregas.csv')
    arquivo_sem_carne = Path('1_normalizacao/dados_processados/originais/controles_gerais/trans_financ/trans_financ_consolidado/trans_financ_sem_carne.csv')
    
    print("="*70)
    print("SEPARAÇÃO CARNÊ LANCASTER")
    print("="*70)
    
    # Ler arquivo
    print(f"\n1. Lendo arquivo: {arquivo_entrada.name}")
    df = pd.read_csv(arquivo_entrada, encoding='utf-8', low_memory=False)
    print(f"   Total de linhas: {len(df):,}")
    
    # Análise da coluna Pagamento
    print("\n2. Análise da coluna Pagamento:")
    print(f"   Total com Pagamento preenchido: {df['Pagamento'].notna().sum():,}")
    
    # Separar carnê lancaster (case insensitive e com trim)
    print("\n3. Separando registros de CARNÊ LANCASTER...")
    mask_carne = df['Pagamento'].str.strip().str.upper().str.contains('CARNE LANCASTER', na=False)
    
    df_carne = df[mask_carne].copy()
    df_sem_carne = df[~mask_carne].copy()
    
    print(f"\n   Registros com CARNÊ LANCASTER: {len(df_carne):,}")
    print(f"   Registros sem CARNÊ LANCASTER: {len(df_sem_carne):,}")
    
    # Verificação
    print("\n4. Verificação:")
    print(f"   Total original: {len(df):,}")
    print(f"   Carnê + Sem carnê: {len(df_carne) + len(df_sem_carne):,}")
    print(f"   ✓ Soma confere!" if len(df) == len(df_carne) + len(df_sem_carne) else "   ✗ ERRO na soma!")
    
    # Mostrar valores de pagamento no arquivo carnê
    print("\n5. Valores de Pagamento no arquivo CARNÊ LANCASTER:")
    print(df_carne['Pagamento'].value_counts())
    
    # Mostrar primeiros valores no arquivo sem carnê
    print("\n6. Primeiros valores de Pagamento no arquivo SEM CARNÊ:")
    print(df_sem_carne['Pagamento'].value_counts().head(10))
    
    # Salvar arquivos
    print(f"\n7. Salvando arquivos...")
    print(f"   - {arquivo_carne.name}")
    df_carne.to_csv(arquivo_carne, index=False, encoding='utf-8')
    
    print(f"   - {arquivo_sem_carne.name}")
    df_sem_carne.to_csv(arquivo_sem_carne, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("SEPARAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f"\n📄 {arquivo_carne.name}: {len(df_carne):,} registros")
    print(f"📄 {arquivo_sem_carne.name}: {len(df_sem_carne):,} registros")

if __name__ == "__main__":
    main()
