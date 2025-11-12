"""
Script para consolidar todos os arquivos CSV da pasta originais/oss/consolidadas
em um único arquivo: consolidadas.csv

Arquivos a consolidar:
- MAUA_consolidado.csv
- PERUS_consolidado.csv
- RIO_PEQUENO_consolidado.csv
- SAO_MATEUS_consolidado.csv
- SUZANO2_consolidado.csv
- SUZANO_consolidado.csv
"""

import pandas as pd
from pathlib import Path
import glob

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas'
OUTPUT_FILE = INPUT_DIR / 'consolidadas.csv'

def main():
    print("="*80)
    print("CONSOLIDAÇÃO DE ARQUIVOS CSV - OSS")
    print("="*80)
    print()
    
    # Listar todos os arquivos CSV (exceto o consolidadas.csv se já existir)
    csv_files = sorted([f for f in INPUT_DIR.glob('*.csv') if f.name != 'consolidadas.csv'])
    
    print(f"Pasta: {INPUT_DIR.name}")
    print(f"Arquivos encontrados: {len(csv_files)}")
    print()
    
    if len(csv_files) == 0:
        print("⚠️  Nenhum arquivo CSV encontrado para consolidar!")
        return
    
    print("ARQUIVOS A CONSOLIDAR:")
    print("-"*80)
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file.name}")
    print()
    
    # Lista para armazenar os DataFrames
    dfs = []
    total_registros = 0
    
    print("LENDO ARQUIVOS:")
    print("-"*80)
    
    for file in csv_files:
        try:
            # Ler arquivo
            df = pd.read_csv(file, sep=';', encoding='utf-8')
            qtd_registros = len(df)
            qtd_colunas = len(df.columns)
            
            print(f"  ✓ {file.name:30} - {qtd_registros:6,} registros x {qtd_colunas:2} colunas")
            
            dfs.append(df)
            total_registros += qtd_registros
            
        except Exception as e:
            print(f"  ✗ {file.name:30} - ERRO: {e}")
    
    print()
    print(f"Total de registros a consolidar: {total_registros:,}")
    print()
    
    if len(dfs) == 0:
        print("⚠️  Nenhum arquivo foi lido com sucesso!")
        return
    
    # Consolidar todos os DataFrames
    print("Consolidando arquivos...")
    df_consolidado = pd.concat(dfs, ignore_index=True)
    print(f"  ✓ {len(df_consolidado):,} registros consolidados")
    print()
    
    # Verificar colunas
    print("ESTRUTURA DO ARQUIVO CONSOLIDADO:")
    print("-"*80)
    print(f"  Total de registros: {len(df_consolidado):,}")
    print(f"  Total de colunas: {len(df_consolidado.columns)}")
    print()
    print("  Colunas:")
    for i, col in enumerate(df_consolidado.columns, 1):
        valores_preenchidos = df_consolidado[col].notna().sum()
        percentual = (valores_preenchidos / len(df_consolidado)) * 100
        print(f"    {i:2}. {col:40} - {valores_preenchidos:6,} preenchidos ({percentual:5.1f}%)")
    print()
    
    # Salvar arquivo consolidado
    print(f"Salvando arquivo consolidado: {OUTPUT_FILE.name}")
    df_consolidado.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo salvo com sucesso")
    print()
    
    # Estatísticas finais
    print("="*80)
    print("CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo gerado: {OUTPUT_FILE}")
    print()
    print("📊 Resumo:")
    print(f"   - Arquivos consolidados: {len(csv_files)}")
    print(f"   - Total de registros: {len(df_consolidado):,}")
    print(f"   - Total de colunas: {len(df_consolidado.columns)}")
    print()
    
    # Mostrar distribuição por loja (se houver coluna identificadora)
    colunas_loja = [col for col in df_consolidado.columns if 'loja' in col.lower()]
    if colunas_loja:
        print("DISTRIBUIÇÃO POR LOJA:")
        print("-"*80)
        col_loja = colunas_loja[0]
        distribuicao = df_consolidado[col_loja].value_counts().sort_index()
        for loja, qtd in distribuicao.items():
            print(f"  {loja:30} : {qtd:6,} registros")
        print()

if __name__ == '__main__':
    main()
