#!/usr/bin/env python3
"""
Consolidador Trans Financ - Fase 1
Consolida todos os CSVs da pasta trans_financ em um único arquivo
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import re

def consolidar_trans_financ():
    """Consolida todos os arquivos trans_financ em um único CSV"""
    
    print("🔄 CONSOLIDAÇÃO TRANS FINANC - FASE 1")
    print("=" * 50)
    
    # Definir pastas
    pasta_origem = Path("data/originais/controles_gerais/trans_financ")
    pasta_destino = Path("data/originais/controles_gerais/trans_financ_consolidado")
    
    # Criar pasta destino
    pasta_destino.mkdir(exist_ok=True)
    
    # Lista para armazenar todos os DataFrames
    todos_dataframes = []
    arquivos_processados = []
    arquivos_com_erro = []
    total_registros = 0
    
    print(f"📂 Origem: {pasta_origem}")
    print(f"📁 Destino: {pasta_destino}")
    
    # Processar todos os arquivos CSV
    arquivos_csv = sorted([f for f in pasta_origem.glob("*.csv") 
                          if not f.name.endswith('_Planilha1.csv')])  # Evitar duplicados
    
    print(f"📊 Encontrados {len(arquivos_csv)} arquivos para consolidar")
    print()
    
    for arquivo in arquivos_csv:
        print(f"📄 Processando: {arquivo.name}")
        
        try:
            # Ler arquivo
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Adicionar metadados de origem
            df['arquivo_origem'] = arquivo.name
            df['mes_origem'] = extrair_mes_ano(arquivo.name)
            df['data_processamento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Adicionar à lista
            todos_dataframes.append(df)
            arquivos_processados.append(arquivo.name)
            total_registros += len(df)
            
            print(f"   ✅ {len(df):,} registros adicionados")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            arquivos_com_erro.append(arquivo.name)
    
    print(f"\n📊 CONSOLIDAÇÃO:")
    print("-" * 20)
    print(f"✅ Arquivos processados: {len(arquivos_processados)}")
    print(f"❌ Arquivos com erro: {len(arquivos_com_erro)}")
    print(f"📊 Total de registros: {total_registros:,}")
    
    if todos_dataframes:
        # Concatenar todos os DataFrames
        print(f"\n🔄 Concatenando {len(todos_dataframes)} DataFrames...")
        df_consolidado = pd.concat(todos_dataframes, ignore_index=True)
        
        # Salvar arquivo consolidado
        arquivo_consolidado = pasta_destino / "trans_financ_consolidado_completo.csv"
        df_consolidado.to_csv(arquivo_consolidado, index=False, encoding='utf-8')
        
        print(f"✅ Arquivo consolidado criado: {arquivo_consolidado}")
        print(f"📊 Total final: {len(df_consolidado):,} registros")
        
        # Criar relatório de consolidação
        criar_relatorio_consolidacao(df_consolidado, arquivos_processados, 
                                   arquivos_com_erro, pasta_destino)
        
        # Analisar estrutura do arquivo consolidado
        analisar_estrutura_consolidado(df_consolidado, pasta_destino)
        
        return df_consolidado, arquivo_consolidado
    
    else:
        print("❌ Nenhum arquivo foi processado com sucesso!")
        return None, None

def extrair_mes_ano(nome_arquivo):
    """Extrai mês e ano do nome do arquivo"""
    # Padrões possíveis: ABR_21, JAN_22, etc.
    padrao = r'([A-Z]{3})_?(\d{2})'
    match = re.search(padrao, nome_arquivo.upper())
    
    if match:
        mes_abrev = match.group(1)
        ano = match.group(2)
        
        # Converter mês para número
        meses = {
            'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
            'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
            'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
        }
        
        mes_num = meses.get(mes_abrev, '00')
        ano_completo = f"20{ano}"
        
        return f"{ano_completo}-{mes_num}"
    
    return "INDEFINIDO"

def criar_relatorio_consolidacao(df, arquivos_ok, arquivos_erro, pasta_destino):
    """Cria relatório detalhado da consolidação"""
    
    relatorio = {
        'resumo_consolidacao': {
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_registros': len(df),
            'arquivos_processados': len(arquivos_ok),
            'arquivos_com_erro': len(arquivos_erro),
            'periodo_abrangido': f"{df['mes_origem'].min()} a {df['mes_origem'].max()}",
            'colunas_totais': len(df.columns)
        },
        'arquivos_processados': arquivos_ok,
        'arquivos_com_erro': arquivos_erro,
        'estatisticas_por_origem': df['arquivo_origem'].value_counts().to_dict(),
        'estatisticas_por_mes': df['mes_origem'].value_counts().to_dict(),
        'origens_encontradas': df['Origem'].value_counts().to_dict() if 'Origem' in df.columns else {},
        'estrutura_colunas': list(df.columns)
    }
    
    # Salvar relatório
    import json
    arquivo_relatorio = pasta_destino / "relatorio_consolidacao_trans_financ.json"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Relatório salvo: {arquivo_relatorio}")

def analisar_estrutura_consolidado(df, pasta_destino):
    """Analisa a estrutura do arquivo consolidado"""
    
    print(f"\n📊 ANÁLISE ESTRUTURA CONSOLIDADO:")
    print("-" * 40)
    
    print(f"📏 Dimensões: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    print(f"📅 Período: {df['mes_origem'].min()} a {df['mes_origem'].max()}")
    print(f"🗂️ Arquivos origem: {df['arquivo_origem'].nunique()}")
    
    if 'Origem' in df.columns:
        print(f"🎯 Origens únicas: {df['Origem'].nunique()}")
        
        print(f"\n🔍 Top 5 Origens:")
        for origem, count in df['Origem'].value_counts().head().items():
            percentual = (count / len(df)) * 100
            print(f"   • {origem}: {count:,} ({percentual:.1f}%)")
    
    # Análise de qualidade dos dados
    print(f"\n🔍 QUALIDADE DOS DADOS:")
    print("-" * 25)
    
    colunas_principais = ['Origem', 'Cliente', 'Vl.líquido', 'Dh.emissão']
    
    for coluna in colunas_principais:
        if coluna in df.columns:
            nulos = df[coluna].isnull().sum()
            vazios = (df[coluna] == '').sum() if df[coluna].dtype == 'object' else 0
            total_problemas = nulos + vazios
            percentual = (total_problemas / len(df)) * 100
            
            status = "✅" if percentual < 5 else "⚠️" if percentual < 15 else "❌"
            print(f"   {status} {coluna}: {total_problemas:,} problemas ({percentual:.1f}%)")
    
    # Salvar amostra dos dados
    arquivo_amostra = pasta_destino / "amostra_consolidado_trans_financ.csv"
    df.head(1000).to_csv(arquivo_amostra, index=False, encoding='utf-8')
    print(f"\n📄 Amostra salva: {arquivo_amostra}")

if __name__ == "__main__":
    df_consolidado, arquivo_final = consolidar_trans_financ()
    
    if df_consolidado is not None:
        print(f"\n🎉 CONSOLIDAÇÃO CONCLUÍDA!")
        print(f"📄 Arquivo: {arquivo_final}")
        print(f"📊 {len(df_consolidado):,} registros consolidados")
        print(f"\n🚀 Próximo passo: Divisão em documentos menores")
    else:
        print(f"\n❌ Consolidação falhou!")