"""
Script para normalizar a coluna 'OS N°' do arquivo consolidadas.csv
Remove tudo após vírgula ou ponto, deixando apenas números inteiros.

Exemplos:
- 4028.0 → 4028
- 4030.0 → 4030
- 5000,5 → 5000
"""

import pandas as pd
import re
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

def normalizar_os_numero(valor):
    """Normaliza um número de OS, removendo tudo após vírgula/ponto"""
    if pd.isna(valor):
        return None
    
    # Converter para string e remover espaços
    os_str = str(valor).strip()
    
    # Se for vazio, retornar None
    if not os_str:
        return None
    
    # Remover tudo após vírgula ou ponto (inclusive o separador)
    # Pega apenas a parte antes do primeiro . ou ,
    os_limpo = re.split(r'[,.]', os_str)[0]
    
    # Remover caracteres não numéricos
    apenas_numeros = re.sub(r'\D', '', os_limpo)
    
    # Se não sobrou nada, retornar None
    if not apenas_numeros:
        return None
    
    # Retornar como número inteiro (sem zeros à esquerda desnecessários)
    return str(int(apenas_numeros))

def main():
    print("="*80)
    print("NORMALIZAÇÃO DA COLUNA 'OS N°'")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    print()
    
    col_name = 'OS N°'
    
    # Estatísticas antes
    print("ANTES da normalização:")
    print(f"  OS N° preenchidos: {df[col_name].notna().sum():,}")
    print(f"  OS N° vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Análise de padrões antes
    valores = df[col_name].dropna().astype(str)
    com_ponto = valores.str.contains(r'\.', na=False, regex=True)
    com_virgula = valores.str.contains(',', na=False)
    apenas_numeros = valores.str.match(r'^\d+$')
    
    print("PADRÕES IDENTIFICADOS:")
    print(f"  Com ponto (.): {com_ponto.sum():,}")
    print(f"  Com vírgula (,): {com_virgula.sum():,}")
    print(f"  Apenas números (correto): {apenas_numeros.sum():,}")
    print()
    
    # Mostrar exemplos antes
    print("EXEMPLOS ANTES DA NORMALIZAÇÃO (primeiros 10):")
    print("-"*80)
    for i, val in enumerate(valores.head(10), 1):
        print(f"  {i:2}. {val}")
    print()
    
    # Backup da coluna original
    df['OS N°_original'] = df[col_name].copy()
    
    # Aplicar normalização
    print("Aplicando normalizações...")
    df[col_name] = df[col_name].apply(normalizar_os_numero)
    print("  ✓ Concluído")
    print()
    
    # Estatísticas depois
    print("DEPOIS da normalização:")
    print(f"  OS N° preenchidos: {df[col_name].notna().sum():,}")
    print(f"  OS N° vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Mostrar exemplos depois
    valores_depois = df[col_name].dropna().astype(str)
    print("EXEMPLOS DEPOIS DA NORMALIZAÇÃO (primeiros 10):")
    print("-"*80)
    for i, val in enumerate(valores_depois.head(10), 1):
        print(f"  {i:2}. {val}")
    print()
    
    # Análise de mudanças
    mudancas = df[df[col_name] != df['OS N°_original']]
    print(f"Total de registros modificados: {len(mudancas):,}")
    print()
    
    # Mostrar exemplos de mudanças
    if len(mudancas) > 0:
        print("EXEMPLOS DE MUDANÇAS (primeiros 20):")
        print("-"*80)
        for i, (idx, row) in enumerate(mudancas.head(20).iterrows(), 1):
            original = row['OS N°_original']
            novo = row[col_name]
            original_str = str(original) if pd.notna(original) else 'None'
            novo_str = str(novo) if pd.notna(novo) else 'None'
            print(f"{i:2}. {original_str:20} → {novo_str}")
        print()
    
    # Verificar se todos são apenas números agora
    valores_finais = df[col_name].dropna().astype(str)
    apenas_numeros_final = valores_finais.str.match(r'^\d+$')
    
    print("RESULTADO FINAL:")
    print("-"*80)
    print(f"  OS N° apenas com números: {apenas_numeros_final.sum():,} ({apenas_numeros_final.sum()/len(valores_finais)*100:.1f}%)")
    
    # Verificar se algum ficou fora do padrão
    nao_numerico = valores_finais[~valores_finais.str.match(r'^\d+$')]
    if len(nao_numerico) > 0:
        print(f"  OS N° com caracteres inválidos: {len(nao_numerico):,}")
        print("\n  Exemplos de valores inválidos:")
        for i, val in enumerate(nao_numerico.head(10), 1):
            print(f"    {i}. {val}")
    else:
        print("  ✓ Todos os OS N° estão apenas com números!")
    
    print()
    
    # Remover coluna backup
    df = df.drop(columns=['OS N°_original'])
    
    # Salvar arquivo (sobrescrever)
    print(f"Salvando alterações no arquivo original...")
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo atualizado: {INPUT_FILE}")
    print()

if __name__ == '__main__':
    main()
