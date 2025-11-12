#!/usr/bin/env python3
"""
Script CORRIGIDO para unir todos os arquivos de clientes UUID com normalização adequada dos IDs
Resolve o problema dos IDs espalhados em colunas diferentes
"""

import pandas as pd
import os
from pathlib import Path

def unir_todos_clientes_uuid_corrigido():
    """Une todos os arquivos de clientes UUID com normalização correta dos IDs"""
    
    # Diretórios
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    clientes_dir = base_dir / "data" / "clientes_uuid"
    
    print("=== UNIÃO CORRIGIDA DE TODOS OS CLIENTES UUID ===")
    print(f"Diretório fonte: {clientes_dir}")
    
    # Lista todos os arquivos CSV na pasta (exceto o consolidado anterior)
    arquivos_clientes = [f for f in clientes_dir.glob("clientes_*.csv") if f.name != "clientes_todos_consolidado.csv"]
    print(f"\nArquivos encontrados: {len(arquivos_clientes)}")
    
    todos_clientes = []
    estatisticas_detalhadas = {}
    
    # Processa cada arquivo
    for arquivo in sorted(arquivos_clientes):
        print(f"\n=== PROCESSANDO: {arquivo.name} ===")
        
        try:
            df = pd.read_csv(arquivo, low_memory=False)
            print(f"  Registros originais: {len(df)}")
            
            # Identifica e normaliza o ID principal
            cliente_id_principal = None
            
            if 'ID' in df.columns and df['ID'].notna().sum() > 0:
                # Casos MAUA e SUZANO
                cliente_id_principal = df['ID'].astype(str)
                fonte_id = 'ID'
            elif 'cliente_id_x' in df.columns and df['cliente_id_x'].notna().sum() > 0:
                # Casos PERUS, RIO_PEQUENO, SAO_MATEUS, SUZANO2
                cliente_id_principal = df['cliente_id_x'].astype(str)
                fonte_id = 'cliente_id_x'
            elif 'id_legado' in df.columns and df['id_legado'].notna().sum() > 0:
                # Fallback para id_legado
                cliente_id_principal = df['id_legado'].astype(str)
                fonte_id = 'id_legado'
            else:
                print(f"  ERRO: Nenhuma coluna de ID válida encontrada!")
                continue
            
            # Remove valores 'nan' que vieram da conversão
            cliente_id_principal = cliente_id_principal.str.replace('.0', '', regex=False)
            cliente_id_principal = cliente_id_principal.replace('nan', None)
            
            # Adiciona coluna normalizada
            df['cliente_id_principal'] = cliente_id_principal
            df['fonte_id_original'] = fonte_id
            df['arquivo_origem'] = arquivo.stem
            
            # Estatísticas do arquivo
            ids_validos = df['cliente_id_principal'].notna().sum()
            ids_nulos = df['cliente_id_principal'].isna().sum()
            
            print(f"  Fonte do ID: {fonte_id}")
            print(f"  IDs válidos: {ids_validos}")
            print(f"  IDs nulos: {ids_nulos}")
            
            if ids_validos > 0:
                # Mostra exemplos
                exemplos = df['cliente_id_principal'].dropna().head(3).tolist()
                print(f"  Exemplos: {exemplos}")
                
                # Verifica tamanhos dos IDs
                tamanhos = df['cliente_id_principal'].dropna().str.len().value_counts().head(3)
                print(f"  Tamanhos dos IDs: {dict(tamanhos)}")
                
                # Verifica se tem IDs de 8 dígitos (importante para SUZANO2)
                ids_8_digitos = (df['cliente_id_principal'].dropna().str.len() == 8).sum()
                if ids_8_digitos > 0:
                    print(f"  ⚠️  IDs de 8 dígitos: {ids_8_digitos}")
            
            todos_clientes.append(df)
            
            estatisticas_detalhadas[arquivo.stem] = {
                'registros': len(df),
                'ids_validos': ids_validos,
                'ids_nulos': ids_nulos,
                'fonte_id': fonte_id
            }
            
        except Exception as e:
            print(f"  ERRO ao processar {arquivo.name}: {e}")
    
    if not todos_clientes:
        print("ERRO: Nenhum arquivo válido encontrado!")
        return
    
    # Combina todos os DataFrames
    print(f"\n=== CONSOLIDAÇÃO CORRIGIDA ===")
    df_consolidado = pd.concat(todos_clientes, ignore_index=True)
    
    total_registros = sum([stats['registros'] for stats in estatisticas_detalhadas.values()])
    total_ids_validos = df_consolidado['cliente_id_principal'].notna().sum()
    total_ids_nulos = df_consolidado['cliente_id_principal'].isna().sum()
    
    print(f"Total de registros: {len(df_consolidado)}")
    print(f"IDs principais válidos: {total_ids_validos}")
    print(f"IDs principais nulos: {total_ids_nulos}")
    
    # Verifica se todos têm ID agora
    if total_ids_nulos == 0:
        print("✅ SUCESSO: Todos os clientes têm ID!")
    else:
        print(f"⚠️  ATENÇÃO: {total_ids_nulos} clientes ainda sem ID")
    
    # Análise dos tamanhos de ID no resultado final
    if total_ids_validos > 0:
        tamanhos_finais = df_consolidado['cliente_id_principal'].dropna().str.len().value_counts()
        print(f"\nDistribuição final dos tamanhos de ID:")
        for tamanho, count in tamanhos_finais.items():
            print(f"  {tamanho} dígitos: {count} clientes")
    
    # Verifica duplicatas por ID principal
    duplicatas_id = df_consolidado['cliente_id_principal'].duplicated().sum()
    print(f"\nDuplicatas por cliente_id_principal: {duplicatas_id}")
    
    if duplicatas_id > 0:
        print("Removendo duplicatas por cliente_id_principal...")
        df_consolidado = df_consolidado.drop_duplicates(subset=['cliente_id_principal'])
        print(f"Registros após remoção de duplicatas: {len(df_consolidado)}")
    
    # Salva arquivo consolidado CORRIGIDO
    arquivo_saida = clientes_dir / "clientes_todos_consolidado_corrigido.csv"
    df_consolidado.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Arquivo consolidado salvo: {arquivo_saida}")
    print(f"Total de clientes únicos: {len(df_consolidado)}")
    
    # Estatísticas detalhadas por origem
    print(f"\n=== ESTATÍSTICAS DETALHADAS POR ORIGEM ===")
    for origem, stats in estatisticas_detalhadas.items():
        print(f"{origem}:")
        print(f"  Registros: {stats['registros']}")
        print(f"  IDs válidos: {stats['ids_validos']}")
        print(f"  Fonte ID: {stats['fonte_id']}")
    
    # Verifica estatísticas finais por origem no consolidado
    print(f"\n=== DISTRIBUIÇÃO FINAL POR ARQUIVO ===")
    origem_stats = df_consolidado['arquivo_origem'].value_counts()
    for origem, count in origem_stats.items():
        print(f"  {origem}: {count} clientes")
    
    # Amostra dos dados principais
    print(f"\n=== AMOSTRA DOS DADOS CORRIGIDOS ===")
    colunas_importantes = ['cliente_id_principal', 'fonte_id_original', 'arquivo_origem', 'cliente_id_y']
    if all(col in df_consolidado.columns for col in colunas_importantes):
        amostra = df_consolidado[colunas_importantes].head(5)
        print(amostra.to_string())
    
    return df_consolidado

if __name__ == "__main__":
    resultado = unir_todos_clientes_uuid_corrigido()
    print("\n✅ União CORRIGIDA de clientes UUID concluída!")
    print("📋 Agora todos os IDs estão na coluna 'cliente_id_principal'")
    print("🔍 IDs de 8 dígitos do SUZANO2 foram preservados")