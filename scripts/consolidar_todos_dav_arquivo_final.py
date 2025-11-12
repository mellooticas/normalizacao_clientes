#!/usr/bin/env python3
"""
Script para consolidar TODOS os arquivos de lista DAV em um único arquivo
Criando: data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob
import warnings
warnings.filterwarnings('ignore')

def consolidar_todos_dav():
    """
    Consolida todos os arquivos DAV em um único arquivo final
    """
    print("📁 === CONSOLIDAÇÃO COMPLETA DOS ARQUIVOS DAV === 📁")
    
    # 1. Localizar todos os arquivos CSV da lista DAV
    print("\n🔍 === LOCALIZANDO ARQUIVOS === 🔍")
    
    pasta_dav = 'data/originais/controles_gerais/lista_dav'
    pattern = os.path.join(pasta_dav, '*.csv')
    arquivos = glob.glob(pattern)
    
    print(f"✅ Encontrados: {len(arquivos)} arquivos CSV")
    
    if len(arquivos) == 0:
        print("❌ Nenhum arquivo CSV encontrado na pasta lista_dav")
        return False
    
    # Mostrar alguns arquivos encontrados
    print("📄 Primeiros arquivos:")
    for i, arquivo in enumerate(sorted(arquivos)[:10]):
        nome = os.path.basename(arquivo)
        print(f"   {i+1:2d}. {nome}")
    
    if len(arquivos) > 10:
        print(f"   ... e mais {len(arquivos)-10} arquivos")
    
    # 2. Processar cada arquivo
    print(f"\n📊 === PROCESSANDO {len(arquivos)} ARQUIVOS === 📊")
    
    todos_dados = []
    arquivos_processados = 0
    total_registros = 0
    erros = []
    
    for arquivo in sorted(arquivos):
        nome_arquivo = os.path.basename(arquivo)
        
        try:
            # Ler arquivo
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Adicionar coluna com nome do arquivo de origem
            df['arquivo_origem'] = nome_arquivo
            
            # Contar registros
            registros_arquivo = len(df)
            total_registros += registros_arquivo
            
            # Adicionar aos dados consolidados
            todos_dados.append(df)
            arquivos_processados += 1
            
            print(f"✅ {nome_arquivo}: {registros_arquivo:,} registros")
            
        except Exception as e:
            erro_msg = f"❌ {nome_arquivo}: {str(e)}"
            print(erro_msg)
            erros.append(erro_msg)
            continue
    
    # 3. Consolidar todos os dados
    print(f"\n🔗 === CONSOLIDANDO DADOS === 🔗")
    
    if len(todos_dados) == 0:
        print("❌ Nenhum arquivo foi processado com sucesso")
        return False
    
    # Unir todos os DataFrames
    df_consolidado = pd.concat(todos_dados, ignore_index=True, sort=False)
    
    print(f"✅ Arquivos processados: {arquivos_processados}/{len(arquivos)}")
    print(f"✅ Total de registros: {len(df_consolidado):,}")
    print(f"✅ Colunas únicas: {df_consolidado.shape[1]}")
    
    # 4. Análise dos dados consolidados
    print(f"\n📊 === ANÁLISE DOS DADOS CONSOLIDADOS === 📊")
    
    # Colunas disponíveis
    print(f"📋 Colunas: {', '.join(df_consolidado.columns[:10])}...")
    
    # Arquivos de origem
    origem_dist = df_consolidado['arquivo_origem'].value_counts()
    print(f"📄 Arquivos com mais registros:")
    for arquivo, qtd in origem_dist.head(5).items():
        print(f"   {arquivo}: {qtd:,} registros")
    
    # Período (se houver coluna de data)
    colunas_data = [col for col in df_consolidado.columns if any(palavra in col.lower() for palavra in ['data', 'dt', 'dh'])]
    if colunas_data:
        print(f"📅 Colunas de data encontradas: {', '.join(colunas_data)}")
        
        # Tentar analisar período
        for col_data in colunas_data[:2]:  # Primeiras 2 colunas de data
            try:
                df_consolidado[f'{col_data}_dt'] = pd.to_datetime(df_consolidado[col_data], errors='coerce')
                datas_validas = df_consolidado[f'{col_data}_dt'].dropna()
                
                if len(datas_validas) > 0:
                    inicio = datas_validas.min().strftime('%Y-%m-%d')
                    fim = datas_validas.max().strftime('%Y-%m-%d')
                    print(f"📅 {col_data}: {inicio} → {fim} ({len(datas_validas):,} registros válidos)")
                    break  # Usar apenas a primeira coluna de data válida
            except:
                continue
    
    # Campos principais (se existirem)
    campos_principais = ['OS', 'Cliente', 'Vendedor', 'Status', 'Dt.entrega']
    campos_encontrados = [campo for campo in campos_principais if campo in df_consolidado.columns]
    
    if campos_encontrados:
        print(f"🎯 Campos principais encontrados: {', '.join(campos_encontrados)}")
        
        # Análise de cada campo
        for campo in campos_encontrados:
            valores_unicos = df_consolidado[campo].nunique()
            valores_nao_nulos = df_consolidado[campo].notna().sum()
            print(f"   {campo}: {valores_unicos:,} únicos, {valores_nao_nulos:,} não-nulos")
    
    # 5. Salvar arquivo consolidado
    print(f"\n💾 === SALVANDO ARQUIVO FINAL === 💾")
    
    # Criar diretório se não existir
    pasta_destino = 'data/originais/controles_gerais/lista_dav/csv'
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Nome do arquivo final
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_final = os.path.join(pasta_destino, 'arquivo_final.csv')
    arquivo_final_com_timestamp = os.path.join(pasta_destino, f'arquivo_final_backup_{timestamp}.csv')
    
    # Salvar arquivo principal
    df_consolidado.to_csv(arquivo_final, index=False, encoding='utf-8')
    print(f"✅ Arquivo principal: {arquivo_final}")
    
    # Salvar backup com timestamp
    df_consolidado.to_csv(arquivo_final_com_timestamp, index=False, encoding='utf-8')
    print(f"✅ Backup: {arquivo_final_com_timestamp}")
    
    # 6. Relatório final
    print(f"\n📋 === RELATÓRIO FINAL === 📋")
    print(f"📊 Registros totais: {len(df_consolidado):,}")
    print(f"📄 Arquivos processados: {arquivos_processados}/{len(arquivos)}")
    print(f"📋 Colunas: {df_consolidado.shape[1]}")
    print(f"💾 Arquivo gerado: {arquivo_final}")
    print(f"📁 Tamanho aproximado: {len(df_consolidado) * df_consolidado.shape[1] * 50 / 1024 / 1024:.1f} MB")
    
    # Mostrar erros se houver
    if erros:
        print(f"\n⚠️ === ERROS ENCONTRADOS === ⚠️")
        for erro in erros:
            print(f"   {erro}")
    
    return arquivo_final

def verificar_arquivo_gerado(arquivo):
    """
    Verifica o arquivo gerado
    """
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    print(f"\n✅ === VERIFICAÇÃO DO ARQUIVO === ✅")
    
    # Informações do arquivo
    tamanho = os.path.getsize(arquivo) / 1024 / 1024
    print(f"📄 Arquivo: {arquivo}")
    print(f"💾 Tamanho: {tamanho:.1f} MB")
    
    # Ler primeiras linhas
    try:
        df_teste = pd.read_csv(arquivo, nrows=5)
        print(f"📊 Linhas de teste: {len(df_teste)}")
        print(f"📋 Colunas: {df_teste.shape[1]}")
        print(f"📋 Primeiras colunas: {', '.join(df_teste.columns[:10])}")
        
        # Contar total de linhas
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = sum(1 for _ in f) - 1  # -1 para o cabeçalho
        print(f"📊 Total de linhas de dados: {linhas:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro verificando arquivo: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 === CONSOLIDAÇÃO COMPLETA LISTA DAV === 🎯")
    print("📁 Origem: data/originais/controles_gerais/lista_dav/*.csv")
    print("📁 Destino: data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv")
    
    arquivo_final = consolidar_todos_dav()
    
    if arquivo_final:
        print(f"\n🎉 === CONSOLIDAÇÃO CONCLUÍDA === 🎉")
        
        # Verificar arquivo gerado
        if verificar_arquivo_gerado(arquivo_final):
            print(f"✅ Arquivo consolidado disponível em: {arquivo_final}")
            print(f"🔗 Todos os arquivos DAV agora estão em um único arquivo!")
            print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"⚠️ Arquivo gerado, mas com problemas na verificação")
    else:
        print(f"\n❌ === FALHA NA CONSOLIDAÇÃO === ❌")
        print("Verifique os logs acima para detalhes")

if __name__ == "__main__":
    main()