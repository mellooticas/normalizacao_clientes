#!/usr/bin/env python3
"""
Script para normalizar coluna Nro.operação do arquivo trans_financ_consolidado_completo.csv
Remove prefixos das lojas (9, 10, 11, 12, 42, 48) e zeros à esquerda
"""

import pandas as pd
import numpy as np
from pathlib import Path

def remover_prefixo_loja(nro_operacao):
    """
    Remove prefixos das lojas do número de operação
    Prefixos: 048, 042, 012, 011, 010, 09, 48, 42, 12, 11, 10, 9
    """
    if pd.isna(nro_operacao):
        return np.nan
    
    # Converter para string e remover .0 se for float
    nro_str = str(nro_operacao)
    if '.0' in nro_str:
        nro_str = nro_str.replace('.0', '')
    
    # Remover hífens
    nro_str = nro_str.replace('-', '')
    
    # Remover caracteres especiais, manter apenas dígitos
    nro_str = ''.join(c for c in nro_str if c.isdigit())
    
    if not nro_str:
        return np.nan
    
    # Lista de prefixos ordenada por tamanho (maior primeiro)
    # Primeiro tenta com zero à esquerda (048, 042, 012, 011, 010, 09)
    # Depois sem zero (48, 42, 12, 11, 10, 9)
    prefixos = ['048', '042', '012', '011', '010', '09', '48', '42', '12', '11', '10', '9']
    
    # Tentar remover cada prefixo
    for prefixo in prefixos:
        if nro_str.startswith(prefixo):
            nro_str = nro_str[len(prefixo):]
            break
    
    # Remover zeros à esquerda restantes
    nro_str = nro_str.lstrip('0')
    
    # Se ficou vazio após remover zeros, retornar 0
    if not nro_str:
        return '0'
    
    return nro_str

def main():
    # Caminhos
    arquivo_entrada = Path('1_normalizacao/dados_processados/originais/controles_gerais/trans_financ/trans_financ_consolidado/trans_financ_consolidado_completo.csv')
    arquivo_saida = arquivo_entrada  # Substituir o arquivo original
    
    print("="*70)
    print("NORMALIZAÇÃO DE Nro.operação - trans_financ")
    print("="*70)
    
    # Ler arquivo
    print(f"\n1. Lendo arquivo: {arquivo_entrada.name}")
    df = pd.read_csv(arquivo_entrada, encoding='utf-8')
    print(f"   Total de linhas: {len(df):,}")
    
    # Análise antes
    print("\n2. Análise ANTES da normalização:")
    print(f"   Valores não nulos em Nro.operação: {df['Nro.operação'].notna().sum():,}")
    print(f"   Valores nulos em Nro.operação: {df['Nro.operação'].isna().sum():,}")
    
    print("\n   Exemplos de valores originais:")
    exemplos = df[df['Nro.operação'].notna()]['Nro.operação'].head(10)
    for i, valor in enumerate(exemplos, 1):
        print(f"   {i}. {valor}")
    
    # Substituir valores na coluna original
    print("\n3. Normalizando coluna Nro.operação...")
    valores_originais = df['Nro.operação'].copy()
    df['Nro.operação'] = df['Nro.operação'].apply(remover_prefixo_loja)
    
    # Análise após
    print("\n4. Análise DEPOIS da normalização:")
    print(f"   Valores não nulos normalizados: {df['Nro.operação'].notna().sum():,}")
    
    print("\n   Exemplos de valores normalizados:")
    exemplos_df = pd.DataFrame({
        'Original': valores_originais[valores_originais.notna()].head(15),
        'Normalizado': df['Nro.operação'][valores_originais.notna()].head(15)
    })
    for idx, row in exemplos_df.iterrows():
        original = row['Original']
        normalizado = row['Normalizado']
        print(f"   {original} → {normalizado}")
    
    # Estatísticas de transformação
    print("\n5. Estatísticas de transformação:")
    df_com_dados = df[df['Nro.operação'].notna()].copy()
    
    # Contar quantos tiveram cada prefixo removido
    prefixos_contagem = {
        '048': 0, '042': 0, '012': 0, '011': 0, '010': 0, '09': 0,
        '48': 0, '42': 0, '12': 0, '11': 0, '10': 0, '9': 0, 
        'sem_prefixo': 0
    }
    
    for idx in df_com_dados.index:
        original = str(valores_originais[idx]).replace('.0', '')
        normalizado = df.loc[idx, 'Nro.operação']
        
        if pd.notna(normalizado):
            if original.startswith('048'):
                prefixos_contagem['048'] += 1
            elif original.startswith('042'):
                prefixos_contagem['042'] += 1
            elif original.startswith('012'):
                prefixos_contagem['012'] += 1
            elif original.startswith('011'):
                prefixos_contagem['011'] += 1
            elif original.startswith('010'):
                prefixos_contagem['010'] += 1
            elif original.startswith('09') and not original.startswith('090'):
                prefixos_contagem['09'] += 1
            elif original.startswith('48'):
                prefixos_contagem['48'] += 1
            elif original.startswith('42'):
                prefixos_contagem['42'] += 1
            elif original.startswith('12'):
                prefixos_contagem['12'] += 1
            elif original.startswith('11'):
                prefixos_contagem['11'] += 1
            elif original.startswith('10'):
                prefixos_contagem['10'] += 1
            elif original.startswith('9') and not original.startswith('90'):
                prefixos_contagem['9'] += 1
            else:
                prefixos_contagem['sem_prefixo'] += 1
    
    print(f"\n   Prefixo 048 removido: {prefixos_contagem['048']:,} registros")
    print(f"   Prefixo 042 removido: {prefixos_contagem['042']:,} registros")
    print(f"   Prefixo 012 removido: {prefixos_contagem['012']:,} registros")
    print(f"   Prefixo 011 removido: {prefixos_contagem['011']:,} registros")
    print(f"   Prefixo 010 removido: {prefixos_contagem['010']:,} registros")
    print(f"   Prefixo 09 removido: {prefixos_contagem['09']:,} registros")
    print(f"   Prefixo 48 removido: {prefixos_contagem['48']:,} registros")
    print(f"   Prefixo 42 removido: {prefixos_contagem['42']:,} registros")
    print(f"   Prefixo 12 removido: {prefixos_contagem['12']:,} registros")
    print(f"   Prefixo 11 removido: {prefixos_contagem['11']:,} registros")
    print(f"   Prefixo 10 removido: {prefixos_contagem['10']:,} registros")
    print(f"   Prefixo 9 removido: {prefixos_contagem['9']:,} registros")
    print(f"   Sem prefixo: {prefixos_contagem['sem_prefixo']:,} registros")
    
    # Salvar arquivo
    print(f"\n6. Salvando arquivo normalizado: {arquivo_saida.name}")
    df.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f"\nArquivo atualizado: {arquivo_saida.name}")
    print(f"Total de linhas: {len(df):,}")
    print(f"Coluna Nro.operação substituída com valores normalizados")

if __name__ == "__main__":
    main()
