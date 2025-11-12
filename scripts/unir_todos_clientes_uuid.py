#!/usr/bin/env python3
"""
Script para unir todos os arquivos de clientes UUID em um único arquivo consolidado
Combina dados de todas as lojas em: data/clientes_uuid/clientes_todos_consolidado.csv
"""

import pandas as pd
import os
from pathlib import Path

def unir_todos_clientes_uuid():
    """Une todos os arquivos de clientes UUID em um único arquivo"""
    
    # Diretórios
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    clientes_dir = base_dir / "data" / "clientes_uuid"
    
    print("=== UNIÃO DE TODOS OS CLIENTES UUID ===")
    print(f"Diretório fonte: {clientes_dir}")
    
    # Lista todos os arquivos CSV na pasta
    arquivos_clientes = list(clientes_dir.glob("clientes_*.csv"))
    print(f"\nArquivos encontrados: {len(arquivos_clientes)}")
    
    todos_clientes = []
    estatisticas = {}
    
    # Processa cada arquivo
    for arquivo in sorted(arquivos_clientes):
        print(f"\nProcessando: {arquivo.name}")
        
        try:
            df = pd.read_csv(arquivo)
            print(f"  Registros: {len(df)}")
            print(f"  Colunas: {list(df.columns)}")
            
            # Adiciona coluna de origem se não existir
            if 'arquivo_origem' not in df.columns:
                df['arquivo_origem'] = arquivo.stem
            
            todos_clientes.append(df)
            estatisticas[arquivo.stem] = len(df)
            
        except Exception as e:
            print(f"  ERRO ao processar {arquivo.name}: {e}")
    
    if not todos_clientes:
        print("ERRO: Nenhum arquivo válido encontrado!")
        return
    
    # Combina todos os DataFrames
    print(f"\n=== CONSOLIDAÇÃO ===")
    df_consolidado = pd.concat(todos_clientes, ignore_index=True)
    
    print(f"Total de registros antes da união: {sum(estatisticas.values())}")
    print(f"Total de registros após união: {len(df_consolidado)}")
    print(f"Colunas finais: {list(df_consolidado.columns)}")
    
    # Verifica duplicatas por UUID
    if 'cliente_uuid' in df_consolidado.columns:
        duplicatas_uuid = df_consolidado.duplicated(subset=['cliente_uuid']).sum()
        print(f"Duplicatas por cliente_uuid: {duplicatas_uuid}")
        
        if duplicatas_uuid > 0:
            print("Removendo duplicatas por cliente_uuid...")
            df_consolidado = df_consolidado.drop_duplicates(subset=['cliente_uuid'])
            print(f"Registros após remoção de duplicatas: {len(df_consolidado)}")
    
    # Verifica duplicatas por nome+telefone
    colunas_dedup = []
    if 'nome_normalizado' in df_consolidado.columns:
        colunas_dedup.append('nome_normalizado')
    if 'telefone_principal' in df_consolidado.columns:
        colunas_dedup.append('telefone_principal')
        
    if colunas_dedup:
        duplicatas_dados = df_consolidado.duplicated(subset=colunas_dedup).sum()
        print(f"Duplicatas por {'+'.join(colunas_dedup)}: {duplicatas_dados}")
    
    # Salva arquivo consolidado
    arquivo_saida = clientes_dir / "clientes_todos_consolidado.csv"
    df_consolidado.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== RESULTADO ===")
    print(f"Arquivo consolidado salvo: {arquivo_saida}")
    print(f"Total de clientes únicos: {len(df_consolidado)}")
    
    # Estatísticas por origem
    print(f"\n=== ESTATÍSTICAS POR ORIGEM ===")
    if 'arquivo_origem' in df_consolidado.columns:
        origem_stats = df_consolidado['arquivo_origem'].value_counts()
        for origem, count in origem_stats.items():
            print(f"  {origem}: {count} clientes")
    
    # Amostra dos dados
    print(f"\n=== AMOSTRA DOS DADOS ===")
    print(df_consolidado.head(3).to_string())
    
    return df_consolidado

if __name__ == "__main__":
    resultado = unir_todos_clientes_uuid()
    print("\n✅ União de clientes UUID concluída!")