#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise completa de todos os dados extraídos por tipo
Verificação de estrutura, qualidade e inconsistências
"""

import pandas as pd
import os
import json
from collections import defaultdict
from datetime import datetime

def analisar_dados_extraidos_completo():
    """Análise completa de todos os dados em extraidos_por_tipo"""
    
    print("🔍 ANÁLISE COMPLETA DOS DADOS EXTRAÍDOS POR TIPO")
    print("=" * 60)
    
    # Pasta base
    pasta_base = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_por_tipo"
    pasta_analises = r"d:\projetos\carne_facil\carne_facil\_analises"
    os.makedirs(pasta_analises, exist_ok=True)
    
    if not os.path.exists(pasta_base):
        print(f"❌ Pasta não encontrada: {pasta_base}")
        return
    
    print(f"📁 Analisando: {pasta_base}")
    print()
    
    # Estrutura para armazenar análises
    relatorio_completo = {
        'timestamp': datetime.now().isoformat(),
        'pasta_base': pasta_base,
        'tipos_tabela': {},
        'problemas_identificados': [],
        'resumo_geral': {},
        'recomendacoes': []
    }
    
    # Listar todas as subpastas (tipos de tabela)
    tipos_tabela = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d))]
    
    print(f"📊 TIPOS DE TABELA ENCONTRADOS: {len(tipos_tabela)}")
    print("-" * 40)
    for tipo in sorted(tipos_tabela):
        print(f"📁 {tipo}")
    print()
    
    # Analisar cada tipo
    for tipo_tabela in sorted(tipos_tabela):
        print(f"\n🔎 ANALISANDO: {tipo_tabela.upper()}")
        print("=" * 50)
        
        pasta_tipo = os.path.join(pasta_base, tipo_tabela)
        arquivos_csv = [f for f in os.listdir(pasta_tipo) if f.endswith('.csv')]
        
        tipo_info = {
            'arquivos_encontrados': len(arquivos_csv),
            'arquivos_detalhes': {},
            'problemas': [],
            'estruturas_colunas': {},
            'estatisticas': {},
            'valores_suspeitos': {}
        }
        
        print(f"📄 Arquivos CSV encontrados: {len(arquivos_csv)}")
        
        if len(arquivos_csv) == 0:
            tipo_info['problemas'].append("Nenhum arquivo CSV encontrado")
            relatorio_completo['tipos_tabela'][tipo_tabela] = tipo_info
            continue
        
        # Analisar estrutura de cada arquivo
        estruturas_diferentes = {}
        total_registros = 0
        
        for arquivo in sorted(arquivos_csv):
            caminho_arquivo = os.path.join(pasta_tipo, arquivo)
            
            try:
                print(f"  📄 {arquivo}")
                
                # Ler arquivo
                df = pd.read_csv(caminho_arquivo)
                registros = len(df)
                total_registros += registros
                
                # Analisar estrutura
                colunas = list(df.columns)
                tipos_dados = df.dtypes.to_dict()
                
                # Criar chave da estrutura para comparação
                estrutura_key = str(sorted(colunas))
                if estrutura_key not in estruturas_diferentes:
                    estruturas_diferentes[estrutura_key] = {
                        'colunas': colunas,
                        'arquivos': [],
                        'exemplo_tipos': tipos_dados
                    }
                estruturas_diferentes[estrutura_key]['arquivos'].append(arquivo)
                
                # Detalhes do arquivo
                arquivo_info = {
                    'registros': registros,
                    'colunas': colunas,
                    'colunas_count': len(colunas),
                    'memoria_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                    'valores_nulos': {},
                    'valores_vazios': {},
                    'valores_unicos_por_coluna': {},
                    'amostras_dados': {}
                }
                
                # Análise de qualidade por coluna
                for coluna in colunas:
                    # Valores nulos
                    nulos = df[coluna].isnull().sum()
                    vazios = (df[coluna] == '').sum() if df[coluna].dtype == 'object' else 0
                    unicos = df[coluna].nunique()
                    
                    arquivo_info['valores_nulos'][coluna] = int(nulos)
                    arquivo_info['valores_vazios'][coluna] = int(vazios)
                    arquivo_info['valores_unicos_por_coluna'][coluna] = int(unicos)
                    
                    # Amostra de dados (primeiros 5 valores únicos)
                    if df[coluna].dtype == 'object':
                        amostra = df[coluna].dropna().unique()[:5].tolist()
                        arquivo_info['amostras_dados'][coluna] = [str(x) for x in amostra]
                    else:
                        estatisticas_numericas = {
                            'min': float(df[coluna].min()) if pd.notnull(df[coluna].min()) else None,
                            'max': float(df[coluna].max()) if pd.notnull(df[coluna].max()) else None,
                            'media': float(df[coluna].mean()) if pd.notnull(df[coluna].mean()) else None
                        }
                        arquivo_info['amostras_dados'][coluna] = estatisticas_numericas
                
                # Verificar problemas específicos
                problemas_arquivo = []
                
                # Problema 1: Muitos valores nulos em colunas importantes
                for coluna in ['os', 'OS', 'nn_venda', 'cliente']:
                    if coluna in df.columns:
                        nulos_percent = (df[coluna].isnull().sum() / len(df)) * 100
                        if nulos_percent > 10:
                            problemas_arquivo.append(f"Coluna '{coluna}': {nulos_percent:.1f}% valores nulos")
                
                # Problema 2: Headers como dados
                for coluna in df.columns:
                    if df[coluna].dtype == 'object':
                        valores_suspeitos = df[coluna].value_counts().head(3)
                        for valor, count in valores_suspeitos.items():
                            if any(x in str(valor).lower() for x in ['coluna', 'forma', 'cliente', 'valor']):
                                problemas_arquivo.append(f"Possível header como dado: '{valor}' ({count}x)")
                
                # Problema 3: Valores zerados em excesso
                for coluna in ['valor_venda', 'valor', 'entrada']:
                    if coluna in df.columns and pd.api.types.is_numeric_dtype(df[coluna]):
                        zeros_percent = ((df[coluna] == 0).sum() / len(df)) * 100
                        if zeros_percent > 50:
                            problemas_arquivo.append(f"Coluna '{coluna}': {zeros_percent:.1f}% valores zero")
                
                arquivo_info['problemas'] = problemas_arquivo
                tipo_info['arquivos_detalhes'][arquivo] = arquivo_info
                
                print(f"    📊 {registros:,} registros | {len(colunas)} colunas | {len(problemas_arquivo)} problemas")
                
            except Exception as e:
                erro_msg = f"Erro ao processar {arquivo}: {str(e)}"
                print(f"    ❌ {erro_msg}")
                tipo_info['problemas'].append(erro_msg)
        
        # Análise consolidada do tipo
        tipo_info['estatisticas'] = {
            'total_registros': total_registros,
            'total_arquivos': len(arquivos_csv),
            'estruturas_diferentes': len(estruturas_diferentes)
        }
        
        # Verificar inconsistências de estrutura
        if len(estruturas_diferentes) > 1:
            problema = f"Estruturas diferentes encontradas: {len(estruturas_diferentes)} variações"
            tipo_info['problemas'].append(problema)
            relatorio_completo['problemas_identificados'].append(f"{tipo_tabela}: {problema}")
            
            print(f"\n⚠️  ESTRUTURAS DIFERENTES DETECTADAS:")
            for i, (key, info) in enumerate(estruturas_diferentes.items(), 1):
                print(f"    Estrutura {i}: {len(info['colunas'])} colunas")
                print(f"    Arquivos: {', '.join(info['arquivos'])}")
                print(f"    Colunas: {', '.join(info['colunas'][:5])}{'...' if len(info['colunas']) > 5 else ''}")
        
        tipo_info['estruturas_colunas'] = {
            f"estrutura_{i}": {
                'colunas': info['colunas'],
                'arquivos': info['arquivos'],
                'tipos_exemplo': {k: str(v) for k, v in info['exemplo_tipos'].items()}
            }
            for i, info in enumerate(estruturas_diferentes.values(), 1)
        }
        
        # Consolidar problemas do tipo
        todos_problemas = []
        for arquivo_info in tipo_info['arquivos_detalhes'].values():
            todos_problemas.extend(arquivo_info['problemas'])
        
        if todos_problemas:
            print(f"\n⚠️  PROBLEMAS IDENTIFICADOS ({len(todos_problemas)}):")
            problemas_unicos = list(set(todos_problemas))
            for problema in problemas_unicos[:10]:  # Mostrar top 10
                print(f"    • {problema}")
            if len(problemas_unicos) > 10:
                print(f"    ... e mais {len(problemas_unicos) - 10} problemas")
        
        relatorio_completo['tipos_tabela'][tipo_tabela] = tipo_info
        print(f"✅ Análise de {tipo_tabela} concluída")
    
    # Gerar resumo geral
    total_arquivos = 0
    total_registros = 0
    tipos_com_problemas = 0
    
    for info in relatorio_completo['tipos_tabela'].values():
        if 'estatisticas' in info:
            total_arquivos += info['estatisticas'].get('total_arquivos', 0)
            total_registros += info['estatisticas'].get('total_registros', 0)
            if len(info['problemas']) > 0:
                tipos_com_problemas += 1
    
    relatorio_completo['resumo_geral'] = {
        'total_tipos_tabela': len(tipos_tabela),
        'total_arquivos': total_arquivos,
        'total_registros': total_registros,
        'tipos_com_problemas': tipos_com_problemas,
        'tipos_sem_problemas': len(tipos_tabela) - tipos_com_problemas
    }
    
    # Gerar recomendações
    recomendacoes = []
    
    if len(relatorio_completo['problemas_identificados']) > 0:
        recomendacoes.append("CRÍTICO: Estruturas inconsistentes detectadas - necessária normalização")
    
    if total_registros == 0:
        recomendacoes.append("CRÍTICO: Nenhum registro encontrado - verificar processo de extração")
    
    for tipo, info in relatorio_completo['tipos_tabela'].items():
        if info['estatisticas']['estruturas_diferentes'] > 1:
            recomendacoes.append(f"Normalizar estrutura de {tipo} - {info['estatisticas']['estruturas_diferentes']} variações")
    
    relatorio_completo['recomendacoes'] = recomendacoes
    
    # Salvar relatório
    caminho_relatorio = os.path.join(pasta_analises, "analise_completa_extraidos_por_tipo.json")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
    
    # Exibir resumo final
    print(f"\n📋 RESUMO GERAL")
    print("=" * 50)
    print(f"📁 Tipos de tabela: {len(tipos_tabela)}")
    print(f"📄 Total de arquivos: {total_arquivos}")
    print(f"📊 Total de registros: {total_registros:,}")
    print(f"⚠️  Tipos com problemas: {tipos_com_problemas}")
    print(f"✅ Tipos sem problemas: {len(tipos_tabela) - tipos_com_problemas}")
    
    if len(recomendacoes) > 0:
        print(f"\n🚨 RECOMENDAÇÕES URGENTES:")
        for i, rec in enumerate(recomendacoes, 1):
            print(f"{i}. {rec}")
    
    print(f"\n💾 Relatório detalhado salvo em:")
    print(f"   {caminho_relatorio}")
    
    return relatorio_completo

if __name__ == "__main__":
    analisar_dados_extraidos_completo()