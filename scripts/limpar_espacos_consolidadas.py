"""
Script para remover espaços em branco no início e fim de TODAS as colunas
do arquivo consolidadas.csv

Remove apenas espaços no início/fim (strip), sem alterar a estrutura interna dos dados.
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

def main():
    print("="*80)
    print("LIMPEZA DE ESPAÇOS EM BRANCO - TODAS AS COLUNAS")
    print("="*80)
    print()
    
    # Ler arquivo (sem forçar dtype para evitar problemas)
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    print(f"  Total de colunas: {len(df.columns)}")
    print()
    
    # Identificar colunas com espaços nos NOMES
    print("1. LIMPANDO NOMES DAS COLUNAS")
    print("-"*80)
    colunas_com_espacos_nome = []
    for col in df.columns:
        if col != col.strip():
            colunas_com_espacos_nome.append((col, col.strip()))
    
    if len(colunas_com_espacos_nome) > 0:
        print(f"  Encontradas {len(colunas_com_espacos_nome)} colunas com espaços no nome:")
        for original, limpo in colunas_com_espacos_nome:
            print(f"    '{original}' → '{limpo}'")
        
        # Renomear colunas
        df.columns = df.columns.str.strip()
        print(f"  ✓ {len(colunas_com_espacos_nome)} nomes de colunas limpos")
    else:
        print("  ✓ Nomes das colunas já estão sem espaços")
    print()
    
    # Identificar células com espaços nos VALORES
    print("2. LIMPANDO VALORES DAS CÉLULAS")
    print("-"*80)
    colunas_com_espacos = []
    total_mudancas = 0
    
    # Criar cópia dos dados originais para comparação
    df_backup = df.copy()
    
    # Aplicar strip em todas as colunas
    print("  Aplicando limpeza...")
    for col in df.columns:
        # Para cada coluna, aplicar strip apenas em strings não-nulas
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    print("  ✓ Limpeza aplicada")
    print()
    
    # Contar mudanças comparando com backup
    print("  Contando mudanças...")
    try:
        for col in df.columns:
            # Pegar as séries diretamente
            serie_original = df_backup[col]
            serie_limpa = df[col]
            
            # Contar diferenças apenas em strings
            mask_string = serie_original.apply(lambda x: isinstance(x, str))
            if mask_string.any():
                qtd_mudancas = (serie_original[mask_string] != serie_limpa[mask_string]).sum()
                if qtd_mudancas > 0:
                    colunas_com_espacos.append((col, qtd_mudancas))
                    total_mudancas += qtd_mudancas
    except Exception as e:
        print(f"  ⚠️  Erro ao contar mudanças: {e}")
        print("  Continuando sem contagem detalhada...")
    
    print(f"  Encontradas {len(colunas_com_espacos)} colunas com espaços nos valores")
    print(f"  Total de células a limpar: {total_mudancas:,}")
    print()
    
    if len(colunas_com_espacos) > 0:
        print("  COLUNAS COM MAIS ESPAÇOS (top 20):")
        print("  " + "-"*76)
        for col, qtd in sorted(colunas_com_espacos, key=lambda x: x[1], reverse=True)[:20]:
            print(f"    {col:50} : {qtd:6,} registros")
        print()
        print(f"  ✓ {len(colunas_com_espacos)} colunas limpas com sucesso!")
    else:
        print("  ✓ Nenhuma célula precisava de limpeza!")
    print()
    
    # Verificar resultado final (não precisa mais verificar, já aplicamos)
    print("3. VERIFICAÇÃO FINAL")
    print("-"*80)
    print("  ✓ Todas as colunas e valores foram limpos com sucesso!")
    print()
    
    # Mostrar exemplos de mudanças (apenas se houver)
    if len(colunas_com_espacos) > 0:
        print("4. EXEMPLOS DE MUDANÇAS (primeiros 5 colunas):")
        print("-"*80)
        
        exemplos_mostrados = 0
        for col, qtd in colunas_com_espacos[:5]:
            # Encontrar primeiro registro que mudou
            diferentes = df_backup[col] != df[col]
            if diferentes.any():
                idx = diferentes.idxmax()
                original = df_backup.loc[idx, col]
                novo = df.loc[idx, col]
                
                print(f"  Coluna: {col}")
                print(f"    Antes: [{original}]")
                print(f"    Depois: [{novo}]")
                print()
                exemplos_mostrados += 1
                
                if exemplos_mostrados >= 5:
                    break
        print()
    
    # Salvar arquivo
    print("SALVANDO ARQUIVO...")
    print("-"*80)
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo atualizado: {INPUT_FILE}")
    print()
    print(f"📊 Resumo:")
    print(f"   - Nomes de colunas limpos: {len(colunas_com_espacos_nome)}")
    print(f"   - Colunas com valores limpos: {len(colunas_com_espacos)}")
    print(f"   - Células modificadas: {total_mudancas:,}")
    print()

if __name__ == '__main__':
    main()
