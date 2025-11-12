"""
Script para preencher linhas vazias em arquivos de vendas
Quando nn_vendas e cliente estão vazios, preenche com dados da linha anterior
"""

import pandas as pd
from pathlib import Path
import numpy as np

# Diretório das vendas
diretorio_vendas = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao/dados_processados/originais/cxs/finais_postgresql_prontos/vendas')

# Listar todos os arquivos
arquivos = sorted(diretorio_vendas.glob('vendas_*_final.csv'))

print("=" * 80)
print("ANÁLISE E PREENCHIMENTO DE LINHAS VAZIAS - VENDAS")
print("=" * 80)

for arquivo in arquivos:
    print(f"\n{'=' * 80}")
    print(f"ARQUIVO: {arquivo.name}")
    print("=" * 80)
    
    # Ler arquivo
    try:
        df = pd.read_csv(arquivo, sep=',', dtype=str, encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        print("⏭️  Pulando para próximo arquivo...")
        continue
    
    print(f"\n📊 Total de registros: {len(df)}")
    
    # Verificar colunas disponíveis
    print(f"\n📋 Colunas disponíveis: {', '.join(df.columns.tolist())}")
    
    # Identificar coluna de número da venda (pode ter nomes diferentes)
    col_nn_venda = None
    for possivel_nome in ['nn_venda', 'nn_vendas', 'numero_venda', 'os', 'os_numero']:
        if possivel_nome in df.columns:
            col_nn_venda = possivel_nome
            break
    
    # Identificar coluna de cliente
    col_cliente = None
    for possivel_nome in ['cliente', 'nome_cliente', 'cliente_nome']:
        if possivel_nome in df.columns:
            col_cliente = possivel_nome
            break
    
    if not col_nn_venda:
        print("❌ Coluna de número da venda não encontrada!")
        continue
    
    if not col_cliente:
        print("❌ Coluna de cliente não encontrada!")
        continue
    
    print(f"\n🔍 Usando colunas:")
    print(f"   - Número venda: {col_nn_venda}")
    print(f"   - Cliente: {col_cliente}")
    
    # Criar cópia para trabalhar
    df_original = df.copy()
    
    # Identificar linhas vazias em AMBAS as colunas
    mask_vazio = (
        (df[col_nn_venda].isna() | (df[col_nn_venda].str.strip() == '')) &
        (df[col_cliente].isna() | (df[col_cliente].str.strip() == ''))
    )
    
    linhas_vazias = mask_vazio.sum()
    print(f"\n🔴 Linhas com {col_nn_venda} E {col_cliente} vazios: {linhas_vazias}")
    
    if linhas_vazias == 0:
        print("✅ Nenhuma linha vazia encontrada!")
        continue
    
    # Mostrar exemplos de linhas vazias
    print(f"\n📋 Exemplos de linhas vazias (primeiras 5):")
    linhas_vazias_idx = df[mask_vazio].head(5).index.tolist()
    for idx in linhas_vazias_idx:
        print(f"   Linha {idx}: {col_nn_venda}='{df.loc[idx, col_nn_venda]}', {col_cliente}='{df.loc[idx, col_cliente]}'")
    
    # Preencher com forward fill (dados da linha anterior)
    print(f"\n🔄 Preenchendo com dados da linha anterior (forward fill)...")
    
    # Forward fill apenas para as colunas específicas
    df[col_nn_venda] = df[col_nn_venda].replace('', np.nan).fillna(method='ffill')
    df[col_cliente] = df[col_cliente].replace('', np.nan).fillna(method='ffill')
    
    # Verificar quantas foram preenchidas
    ainda_vazias = (
        (df[col_nn_venda].isna() | (df[col_nn_venda].str.strip() == '')) &
        (df[col_cliente].isna() | (df[col_cliente].str.strip() == ''))
    ).sum()
    
    preenchidas = linhas_vazias - ainda_vazias
    
    print(f"✅ Preenchidas: {preenchidas}")
    print(f"⚠️  Ainda vazias: {ainda_vazias}")
    
    # Mostrar exemplos de preenchimento
    if preenchidas > 0:
        print(f"\n📋 Exemplos de preenchimento:")
        for idx in linhas_vazias_idx[:3]:
            if idx < len(df):
                antes_nn = df_original.loc[idx, col_nn_venda] if idx in df_original.index else 'N/A'
                depois_nn = df.loc[idx, col_nn_venda]
                antes_cli = df_original.loc[idx, col_cliente] if idx in df_original.index else 'N/A'
                depois_cli = df.loc[idx, col_cliente]
                
                print(f"\n   Linha {idx}:")
                print(f"      {col_nn_venda}: '{antes_nn}' → '{depois_nn}'")
                print(f"      {col_cliente}: '{antes_cli}' → '{depois_cli}'")
    
    # Salvar no mesmo arquivo
    print(f"\n💾 Salvando alterações no arquivo original...")
    df.to_csv(arquivo, sep=',', index=False, encoding='utf-8-sig')
    print(f"✅ Arquivo salvo: {arquivo.name}")
    
    # Estatísticas finais
    print(f"\n📊 RESUMO:")
    print(f"   - Registros totais: {len(df)}")
    print(f"   - Linhas preenchidas: {preenchidas}")
    print(f"   - Linhas ainda vazias: {ainda_vazias}")

print(f"\n{'=' * 80}")
print("✅ PROCESSAMENTO CONCLUÍDO!")
print("=" * 80)
