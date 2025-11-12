"""
Script para verificar dados perdidos de Suzano 2 e estrutura dos arquivos
"""

import pandas as pd
from pathlib import Path

def main():
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    
    print("="*80)
    print("VERIFICANDO DADOS PERDIDOS DE SUZANO2")
    print("="*80)
    print()
    
    # Ler consolidadas
    consolidadas = pd.read_csv(pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv', sep=';', encoding='utf-8')
    print(f"CONSOLIDADAS.CSV:")
    print(f"   Total de registros: {len(consolidadas):,}")
    print(f"   Registros Suzano 2: {(consolidadas['LOJA'] == 'Suzano 2').sum():,}")
    print()
    
    # Verificar colunas
    print("Colunas em consolidadas.csv relacionadas:")
    colunas_rel = [col for col in consolidadas.columns if 'DATA' in col.upper() or 'COMPRA' in col.upper() or 'CONSULTOR' in col.upper()]
    for col in colunas_rel:
        preenchidos = consolidadas[col].notna().sum()
        print(f"   - {col}: {preenchidos:,} preenchidos")
    print()
    
    # Procurar suzano2.csv
    pasta_oss = pasta_base / 'dados_processados/originais/oss'
    
    # Listar todos os arquivos CSV
    print("Arquivos CSV na pasta OSS:")
    arquivos_csv = list(pasta_oss.glob('*.csv'))
    for arq in arquivos_csv:
        print(f"   - {arq.name}")
    print()
    
    # Procurar arquivo suzano2
    arquivo_suzano2 = None
    for arq in arquivos_csv:
        if 'suzano2' in arq.name.lower() or 'suzano_2' in arq.name.lower():
            arquivo_suzano2 = arq
            break
    
    if arquivo_suzano2:
        print(f"Arquivo Suzano 2 encontrado: {arquivo_suzano2.name}")
        print()
        
        suzano2 = pd.read_csv(arquivo_suzano2, sep=';', encoding='utf-8')
        print(f"SUZANO2.CSV:")
        print(f"   Total de registros: {len(suzano2):,}")
        print()
        
        print("Todas as colunas em suzano2.csv:")
        for i, col in enumerate(suzano2.columns, 1):
            valores = suzano2[col].notna().sum()
            print(f"   {i:2}. {col:40} ({valores:,} preenchidos)")
        print()
        
        # Verificar colunas alvo
        colunas_alvo = []
        for col in suzano2.columns:
            if ('DATA' in col.upper() and 'COMPRA' in col.upper()) or 'CONSULTOR' in col.upper():
                colunas_alvo.append(col)
        
        print("Colunas alvo encontradas em suzano2.csv:")
        for col in colunas_alvo:
            valores_preenchidos = suzano2[col].notna().sum()
            print(f"   - {col}: {valores_preenchidos:,} preenchidos")
        print()
        
        # Verificar coluna OS
        colunas_os = [col for col in suzano2.columns if 'OS' in col.upper() and 'N' in col.upper()]
        print("Colunas OS em suzano2.csv:")
        for col in colunas_os:
            print(f"   - {col}")
            # Mostrar exemplos
            exemplos = suzano2[col].dropna().head(5).astype(str)
            for ex in exemplos:
                print(f"      Exemplo: {ex}")
        print()
        
    else:
        print("Arquivo suzano2 NAO encontrado!")
        print()
    
    print("="*80)


if __name__ == '__main__':
    main()
