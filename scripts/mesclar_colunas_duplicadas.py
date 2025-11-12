"""
Script para mesclar colunas duplicadas em consolidadas.csv
"""

import pandas as pd
from pathlib import Path

def main():
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_consolidadas = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("MESCLANDO COLUNAS DUPLICADAS")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_consolidadas, sep=';', encoding='utf-8')
    df.columns = df.columns.str.strip()
    print(f"   Total de registros: {len(df):,}")
    print(f"   Total de colunas: {len(df.columns):,}")
    print()
    
    # Identificar colunas duplicadas
    print("Identificando colunas duplicadas...")
    colunas_unicas = df.columns.value_counts()
    duplicadas = colunas_unicas[colunas_unicas > 1]
    
    print(f"   Colunas duplicadas: {len(duplicadas)}")
    for col, qtd in duplicadas.items():
        print(f"      - {col}: {qtd}x")
    print()
    
    # Mesclar cada coluna duplicada
    print("="*80)
    print("MESCLANDO COLUNAS")
    print("="*80)
    print()
    
    # Renomear colunas duplicadas temporariamente
    novo_nomes = []
    contador = {}
    for col in df.columns:
        if col not in contador:
            contador[col] = 0
            novo_nomes.append(col)
        else:
            contador[col] += 1
            novo_nomes.append(f"{col}__DUP{contador[col]}")
    
    df.columns = novo_nomes
    
    for col_name in duplicadas.index:
        print(f"Mesclando: {col_name}")
        print("-"*80)
        
        # Pegar nomes das colunas (original e duplicadas)
        colunas_nomes = [col for col in df.columns if col == col_name or col.startswith(f"{col_name}__DUP")]
        print(f"   Colunas encontradas: {colunas_nomes}")
        
        # Primeira coluna é a principal
        col_principal = colunas_nomes[0]
        
        # Preencher vazios da principal com dados das outras
        total_preenchido = 0
        for col_sec in colunas_nomes[1:]:
            mask_vazio = df[col_principal].isna()
            preenchimentos = mask_vazio.sum()
            
            if preenchimentos > 0:
                df.loc[mask_vazio, col_principal] = df.loc[mask_vazio, col_sec].values
                total_preenchido += preenchimentos
                print(f"   Preenchidos {preenchimentos} valores de {col_sec}")
        
        # Remover colunas duplicadas (manter apenas a principal)
        df = df.drop(columns=colunas_nomes[1:])
        print(f"   ✅ Total preenchido: {total_preenchido}")
        print(f"   ✅ Removidas {len(colunas_nomes)-1} colunas duplicadas")
        print()
    
    print("="*80)
    print("📊 RESULTADO")
    print("="*80)
    print(f"Total de colunas após mesclagem: {len(df.columns):,}")
    print()
    
    # Salvar arquivo
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_consolidadas, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_consolidadas}")
    print()
    
    print("="*80)
    print("✅ MESCLAGEM CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()


if __name__ == '__main__':
    main()
