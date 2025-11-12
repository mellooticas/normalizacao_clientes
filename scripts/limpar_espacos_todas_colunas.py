"""
Script para remover espaços em branco no início e fim de TODAS as colunas de texto
do arquivo clientes_vixen_completo.csv

Remove apenas espaços no início/fim (strip), sem alterar a estrutura interna das palavras.
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'vixen' / 'extraidos_corrigidos' / 'clientes_vixen_completo.csv'

def main():
    print("="*80)
    print("LIMPEZA DE ESPAÇOS EM BRANCO - TODAS AS COLUNAS")
    print("="*80)
    print()
    
    # Ler arquivo (todas as colunas como string para preservar dados)
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8', dtype=str)
    print(f"  Total de registros: {len(df):,}")
    print(f"  Total de colunas: {len(df.columns)}")
    print()
    
    # Identificar colunas com espaços
    print("Identificando colunas com espaços desnecessários...")
    colunas_com_espacos = []
    total_mudancas = 0
    
    for col in df.columns:
        # Verificar se há valores com espaços no início ou fim
        tem_espacos = df[col].notna() & (df[col] != df[col].str.strip())
        qtd_espacos = tem_espacos.sum()
        
        if qtd_espacos > 0:
            colunas_com_espacos.append((col, qtd_espacos))
            total_mudancas += qtd_espacos
    
    print(f"  Encontradas {len(colunas_com_espacos)} colunas com espaços")
    print(f"  Total de células a limpar: {total_mudancas:,}")
    print()
    
    if len(colunas_com_espacos) == 0:
        print("✓ Nenhuma coluna precisa de limpeza!")
        return
    
    # Mostrar quais colunas serão limpas
    print("COLUNAS QUE SERÃO LIMPAS:")
    print("-"*80)
    for col, qtd in sorted(colunas_com_espacos, key=lambda x: x[1], reverse=True):
        print(f"  {col:40} : {qtd:,} registros")
    print()
    
    # Aplicar strip em todas as colunas de texto
    print("Aplicando limpeza...")
    colunas_limpas = 0
    
    for col in df.columns:
        if df[col].dtype == 'object':  # Apenas colunas de texto
            # Aplicar strip mantendo NaN como NaN
            df[col] = df[col].apply(lambda x: x.strip() if pd.notna(x) and isinstance(x, str) else x)
            colunas_limpas += 1
    
    print(f"  ✓ {colunas_limpas} colunas processadas")
    print()
    
    # Verificar resultado
    print("Verificando resultado...")
    colunas_ainda_com_espacos = []
    
    for col in df.columns:
        tem_espacos = df[col].notna() & (df[col] != df[col].str.strip())
        qtd_espacos = tem_espacos.sum()
        if qtd_espacos > 0:
            colunas_ainda_com_espacos.append((col, qtd_espacos))
    
    if len(colunas_ainda_com_espacos) == 0:
        print("  ✓ Todas as colunas foram limpas com sucesso!")
    else:
        print(f"  ⚠️  Ainda restam {len(colunas_ainda_com_espacos)} colunas com espaços")
    print()
    
    # Mostrar exemplos de mudanças
    print("EXEMPLOS DE MUDANÇAS (primeiras 10):")
    print("-"*80)
    exemplos_mostrados = 0
    
    for col, qtd in colunas_com_espacos[:5]:  # Primeiras 5 colunas
        # Ler arquivo original para comparar
        df_original = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8', dtype=str)
        
        # Encontrar primeiro registro que mudou
        diferentes = df_original[col] != df[col]
        if diferentes.any():
            idx = diferentes.idxmax()
            original = df_original.loc[idx, col]
            novo = df.loc[idx, col]
            
            print(f"  Coluna: {col}")
            print(f"    Antes: [{original}]")
            print(f"    Depois: [{novo}]")
            print()
            exemplos_mostrados += 1
            
            if exemplos_mostrados >= 10:
                break
    
    # Salvar arquivo
    print(f"Salvando alterações no arquivo original...")
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo atualizado: {INPUT_FILE}")
    print(f"📊 Resumo:")
    print(f"   - Colunas limpas: {len(colunas_com_espacos)}")
    print(f"   - Células modificadas: {total_mudancas:,}")
    print()

if __name__ == '__main__':
    main()
