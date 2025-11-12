#!/usr/bin/env python3
"""
Script para análise forense da cadeia de processamento
Identifica onde perdemos os cliente_ids na normalização
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def analisar_cadeia_processamento():
    """Analisa cada etapa da cadeia para encontrar onde perdemos os dados"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ANÁLISE FORENSE DA CADEIA DE PROCESSAMENTO ===")
    print(f"Data/hora: {datetime.now()}")
    
    # 1. Verificar arquivos originais OSS com cliente_id
    print("\n1. VERIFICANDO DADOS ORIGINAIS OSS:")
    
    pasta_oss = base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos"
    arquivos_oss = list(pasta_oss.glob("oss_*_clientes_ids.csv"))
    
    total_registros_originais = 0
    clientes_com_id_originais = 0
    
    for arquivo in arquivos_oss:
        df = pd.read_csv(arquivo)
        loja = arquivo.name.replace('oss_', '').replace('_clientes_ids.csv', '')
        
        print(f"  {loja}: {len(df)} registros")
        print(f"    - Com cliente_id: {df['cliente_id'].notna().sum()}")
        print(f"    - Sem cliente_id: {df['cliente_id'].isna().sum()}")
        
        total_registros_originais += len(df)
        clientes_com_id_originais += df['cliente_id'].notna().sum()
    
    print(f"\nTOTAL ORIGINAIS:")
    print(f"  - Registros: {total_registros_originais}")
    print(f"  - Com cliente_id: {clientes_com_id_originais} ({clientes_com_id_originais/total_registros_originais*100:.1f}%)")
    
    # 2. Verificar vendas_definitivo.csv atual
    print(f"\n2. VERIFICANDO VENDAS_DEFINITIVO.CSV:")
    
    vendas_def = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_definitivo.csv")
    
    print(f"  Total registros: {len(vendas_def)}")
    print(f"  Com cliente_id: {vendas_def['cliente_id'].notna().sum()}")
    print(f"  Sem cliente_id: {vendas_def['cliente_id'].isna().sum()}")
    print(f"  % com cliente_id: {vendas_def['cliente_id'].notna().sum()/len(vendas_def)*100:.1f}%")
    
    # 3. Comparar números de OS
    print(f"\n3. COMPARANDO NÚMEROS DE OS:")
    
    # Carrega uma amostra dos originais para comparação
    suzano_original = pd.read_csv(pasta_oss / "oss_suzano_clientes_ids.csv")
    
    print(f"  Suzano original - amostras de OS:")
    print(f"    - Primeiro OS: {suzano_original['numero_os'].iloc[0]}")
    print(f"    - Último OS: {suzano_original['numero_os'].iloc[-1]}")
    print(f"    - Tipo de dados: {suzano_original['numero_os'].dtype}")
    
    print(f"  Vendas definitivo - amostras de OS:")
    print(f"    - Primeiro OS: {vendas_def['numero_venda'].iloc[0]}")
    print(f"    - Último OS: {vendas_def['numero_venda'].iloc[-1]}")
    print(f"    - Tipo de dados: {vendas_def['numero_venda'].dtype}")
    
    # 4. Tentar fazer match direto por OS
    print(f"\n4. TESTANDO MATCH DIRETO POR NÚMERO OS:")
    
    # Consolida todos os clientes originais
    todos_clientes_originais = []
    for arquivo in arquivos_oss:
        df = pd.read_csv(arquivo)
        todos_clientes_originais.append(df[['numero_os', 'cliente_id', 'cliente_nome_normalizado']])
    
    clientes_consolidados = pd.concat(todos_clientes_originais, ignore_index=True)
    
    # Remove valores nulos e converte para string para comparação
    clientes_consolidados = clientes_consolidados[clientes_consolidados['cliente_id'].notna()].copy()
    clientes_consolidados['numero_os_str'] = clientes_consolidados['numero_os'].astype(str)
    vendas_def['numero_venda_str'] = vendas_def['numero_venda'].astype(str)
    
    print(f"  Total clientes originais com ID: {len(clientes_consolidados)}")
    print(f"  Números OS únicos originais: {clientes_consolidados['numero_os_str'].nunique()}")
    print(f"  Números venda únicos atuais: {vendas_def['numero_venda_str'].nunique()}")
    
    # Faz match por número
    vendas_com_match = vendas_def.merge(
        clientes_consolidados[['numero_os_str', 'cliente_id', 'cliente_nome_normalizado']], 
        left_on='numero_venda_str', 
        right_on='numero_os_str', 
        how='left',
        suffixes=('', '_original')
    )
    
    matches_encontrados = vendas_com_match['cliente_id_original'].notna().sum()
    
    print(f"  Matches diretos por OS: {matches_encontrados}")
    print(f"  % de match: {matches_encontrados/len(vendas_def)*100:.1f}%")
    
    # 5. Analisa os que não deram match
    print(f"\n5. ANALISANDO OS SEM MATCH:")
    
    sem_match = vendas_com_match[vendas_com_match['cliente_id_original'].isna()]
    
    print(f"  Total sem match: {len(sem_match)}")
    print(f"  Amostras de OS sem match:")
    for i, os_num in enumerate(sem_match['numero_venda_str'].head(10)):
        print(f"    - {os_num}")
    
    # Verifica se esses OS existem nos originais
    os_originais_set = set(clientes_consolidados['numero_os_str'])
    os_vendas_set = set(vendas_def['numero_venda_str'])
    
    os_so_em_vendas = os_vendas_set - os_originais_set
    os_so_em_originais = os_originais_set - os_vendas_set
    
    print(f"\n6. COMPARAÇÃO DE CONJUNTOS:")
    print(f"  OS só em vendas (não tem nos originais): {len(os_so_em_vendas)}")
    print(f"  OS só em originais (não tem nas vendas): {len(os_so_em_originais)}")
    
    if len(os_so_em_vendas) > 0:
        print(f"  Exemplos OS só em vendas:")
        for os_num in list(os_so_em_vendas)[:10]:
            print(f"    - {os_num}")
    
    # 7. Gera arquivo corrigido
    print(f"\n7. GERANDO ARQUIVO CORRIGIDO:")
    
    # Aplica os matches encontrados
    vendas_corrigidas = vendas_def.copy()
    
    # Merge com os dados originais
    vendas_corrigidas = vendas_corrigidas.merge(
        clientes_consolidados[['numero_os_str', 'cliente_id', 'cliente_nome_normalizado']], 
        left_on='numero_venda_str', 
        right_on='numero_os_str', 
        how='left',
        suffixes=('', '_correto')
    )
    
    # Atualiza cliente_id onde encontrou match
    mask_com_match = vendas_corrigidas['cliente_id_correto'].notna()
    vendas_corrigidas.loc[mask_com_match, 'cliente_id'] = vendas_corrigidas.loc[mask_com_match, 'cliente_id_correto']
    
    # Remove colunas auxiliares
    colunas_finais = ['numero_venda', 'cliente_id', 'loja_id', 'vendedor_id', 
                     'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
                     'observacoes', 'status', 'cancelado', 'created_at', 'updated_at']
    
    vendas_corrigidas_final = vendas_corrigidas[colunas_finais].copy()
    
    # Salva arquivo corrigido
    arquivo_corrigido = base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv"
    vendas_corrigidas_final.to_csv(arquivo_corrigido, index=False)
    
    print(f"  Arquivo corrigido salvo: {arquivo_corrigido}")
    
    # Estatísticas finais
    com_cliente_final = vendas_corrigidas_final['cliente_id'].notna().sum()
    sem_cliente_final = vendas_corrigidas_final['cliente_id'].isna().sum()
    
    print(f"\n=== RESULTADO DA CORREÇÃO ===")
    print(f"Total vendas: {len(vendas_corrigidas_final)}")
    print(f"COM cliente_id: {com_cliente_final} ({com_cliente_final/len(vendas_corrigidas_final)*100:.1f}%)")
    print(f"SEM cliente_id: {sem_cliente_final} ({sem_cliente_final/len(vendas_corrigidas_final)*100:.1f}%)")
    
    melhoria = com_cliente_final - vendas_def['cliente_id'].notna().sum()
    print(f"MELHORIA: +{melhoria} clientes com ID ({melhoria/len(vendas_corrigidas_final)*100:.1f}% a mais)")
    
    return vendas_corrigidas_final

if __name__ == "__main__":
    resultado = analisar_cadeia_processamento()
    print("\n🎉 ANÁLISE FORENSE COMPLETA!")
    print("✅ Arquivo corrigido gerado!")
    print("🔍 Problema identificado e resolvido!")