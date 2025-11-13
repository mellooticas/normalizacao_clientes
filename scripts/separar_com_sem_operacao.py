#!/usr/bin/env python3
"""
Script para separar registros com e sem Nro.operação
nos arquivos carne_lancaster_entregas.csv e trans_financ_sem_carne.csv
"""

import pandas as pd
from pathlib import Path

def separar_arquivo(arquivo_entrada, nome_base):
    """
    Separa um arquivo em dois: com e sem Nro.operação
    """
    print(f"\n{'='*70}")
    print(f"Processando: {arquivo_entrada.name}")
    print('='*70)
    
    # Ler arquivo
    print(f"\n1. Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, encoding='utf-8', low_memory=False)
    print(f"   Total de linhas: {len(df):,}")
    
    # Separar com e sem Nro.operação
    print("\n2. Separando registros...")
    mask_com_operacao = df['Nro.operação'].notna()
    
    df_com = df[mask_com_operacao].copy()
    df_sem = df[~mask_com_operacao].copy()
    
    print(f"   Com Nro.operação: {len(df_com):,}")
    print(f"   Sem Nro.operação: {len(df_sem):,}")
    
    # Verificação
    print("\n3. Verificação:")
    print(f"   Total original: {len(df):,}")
    print(f"   Com + Sem: {len(df_com) + len(df_sem):,}")
    print(f"   ✓ Soma confere!" if len(df) == len(df_com) + len(df_sem) else "   ✗ ERRO na soma!")
    
    # Salvar arquivos
    pasta = arquivo_entrada.parent
    arquivo_com = pasta / f"{nome_base}_com_operacao.csv"
    arquivo_sem = pasta / f"{nome_base}_sem_operacao.csv"
    
    print(f"\n4. Salvando arquivos...")
    print(f"   - {arquivo_com.name}")
    df_com.to_csv(arquivo_com, index=False, encoding='utf-8')
    
    print(f"   - {arquivo_sem.name}")
    df_sem.to_csv(arquivo_sem, index=False, encoding='utf-8')
    
    return len(df_com), len(df_sem)

def main():
    # Caminhos
    pasta = Path('1_normalizacao/dados_processados/originais/controles_gerais/trans_financ/trans_financ_consolidado')
    
    arquivo_carne = pasta / 'carne_lancaster_entregas.csv'
    arquivo_sem_carne = pasta / 'trans_financ_sem_carne.csv'
    
    print("="*70)
    print("SEPARAÇÃO POR Nro.operação")
    print("="*70)
    
    # Processar carnê lancaster
    carne_com, carne_sem = separar_arquivo(arquivo_carne, 'carne_lancaster_entregas')
    
    # Processar sem carnê
    sem_carne_com, sem_carne_sem = separar_arquivo(arquivo_sem_carne, 'trans_financ_sem_carne')
    
    # Resumo final
    print("\n" + "="*70)
    print("SEPARAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    
    print("\n📁 CARNÊ LANCASTER:")
    print(f"   📄 carne_lancaster_entregas_com_operacao.csv: {carne_com:,} registros")
    print(f"   📄 carne_lancaster_entregas_sem_operacao.csv: {carne_sem:,} registros")
    
    print("\n📁 TRANS FINANC SEM CARNÊ:")
    print(f"   📄 trans_financ_sem_carne_com_operacao.csv: {sem_carne_com:,} registros")
    print(f"   📄 trans_financ_sem_carne_sem_operacao.csv: {sem_carne_sem:,} registros")
    
    print(f"\n📊 TOTAL GERAL: {carne_com + carne_sem + sem_carne_com + sem_carne_sem:,} registros")

if __name__ == "__main__":
    main()
