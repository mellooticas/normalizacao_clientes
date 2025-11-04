#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import glob
from datetime import datetime

def analisar_estrutura_controles_gerais():
    """Analisa a estrutura dos arquivos Excel dos controles gerais e converte amostras para CSV"""
    
    print('🔍 ANÁLISE ESTRUTURA - CONTROLES GERAIS VIXEN')
    print('=' * 55)
    print(f'📅 Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    base_path = 'data/originais/controles_gerais'
    
    # 4 pastas para analisar
    pastas = {
        'conf_dav': 'Configurações DAV',
        'lista_dav': 'Listas DAV',
        'mov_cx': 'Movimentações Caixa', 
        'trans_financ': 'Transações Financeiras'
    }
    
    resultado_analise = {
        'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pastas_analisadas': {},
        'resumo_geral': {
            'total_arquivos': 0,
            'arquivos_analisados': 0,
            'arquivos_convertidos': 0,
            'erros_conversao': 0
        }
    }
    
    # Analisar cada pasta
    for pasta_nome, pasta_descricao in pastas.items():
        print(f'\n📂 ANALISANDO: {pasta_nome.upper()} ({pasta_descricao})')
        print('-' * 60)
        
        pasta_path = os.path.join(base_path, pasta_nome)
        
        if not os.path.exists(pasta_path):
            print(f'   ❌ Pasta não encontrada: {pasta_path}')
            continue
        
        # Buscar arquivos Excel
        excel_files = glob.glob(os.path.join(pasta_path, '*.xlsx'))
        
        print(f'   📊 Arquivos Excel encontrados: {len(excel_files)}')
        resultado_analise['resumo_geral']['total_arquivos'] += len(excel_files)
        
        pasta_info = {
            'descricao': pasta_descricao,
            'total_arquivos': len(excel_files),
            'arquivos_analisados': 0,
            'estruturas_encontradas': {},
            'amostras_convertidas': [],
            'erros': []
        }
        
        # Analisar estrutura de alguns arquivos (amostra)
        amostras = excel_files[:3]  # Primeiros 3 arquivos como amostra
        
        for arquivo in amostras:
            nome_arquivo = os.path.basename(arquivo)
            print(f'   🔍 Analisando: {nome_arquivo}')
            
            try:
                # Ler Excel e verificar estrutura
                excel_data = pd.ExcelFile(arquivo)
                
                info_arquivo = {
                    'nome': nome_arquivo,
                    'abas': excel_data.sheet_names,
                    'total_abas': len(excel_data.sheet_names),
                    'estrutura_abas': {}
                }
                
                # Analisar cada aba
                for aba in excel_data.sheet_names:
                    try:
                        df = pd.read_excel(arquivo, sheet_name=aba)
                        
                        info_aba = {
                            'linhas': len(df),
                            'colunas': len(df.columns),
                            'colunas_nomes': list(df.columns)[:10],  # Primeiras 10 colunas
                            'tem_dados': len(df) > 0
                        }
                        
                        info_arquivo['estrutura_abas'][aba] = info_aba
                        
                        print(f'      📄 Aba "{aba}": {len(df)} linhas x {len(df.columns)} colunas')
                        
                        # Converter aba principal para CSV (primeira aba com dados)
                        if len(df) > 0 and aba == excel_data.sheet_names[0]:
                            nome_csv = f'{os.path.splitext(nome_arquivo)[0]}_{aba}.csv'
                            caminho_csv = os.path.join(pasta_path, nome_csv)
                            
                            df.to_csv(caminho_csv, index=False)
                            
                            pasta_info['amostras_convertidas'].append({
                                'arquivo_original': nome_arquivo,
                                'aba': aba,
                                'arquivo_csv': nome_csv,
                                'linhas': len(df),
                                'colunas': len(df.columns)
                            })
                            
                            resultado_analise['resumo_geral']['arquivos_convertidos'] += 1
                            print(f'      ✅ Convertido para CSV: {nome_csv}')
                    
                    except Exception as e:
                        print(f'      ❌ Erro na aba {aba}: {str(e)[:50]}')
                        pasta_info['erros'].append(f'Aba {aba} de {nome_arquivo}: {str(e)[:50]}')
                
                # Armazenar estrutura
                chave_estrutura = f'{info_arquivo["total_abas"]}_abas'
                if chave_estrutura not in pasta_info['estruturas_encontradas']:
                    pasta_info['estruturas_encontradas'][chave_estrutura] = []
                
                pasta_info['estruturas_encontradas'][chave_estrutura].append(info_arquivo)
                pasta_info['arquivos_analisados'] += 1
                resultado_analise['resumo_geral']['arquivos_analisados'] += 1
                
            except Exception as e:
                print(f'   ❌ Erro ao analisar {nome_arquivo}: {str(e)[:50]}')
                pasta_info['erros'].append(f'{nome_arquivo}: {str(e)[:50]}')
                resultado_analise['resumo_geral']['erros_conversao'] += 1
        
        print(f'   📊 Análise concluída: {pasta_info["arquivos_analisados"]} arquivos')
        print(f'   📄 CSVs criados: {len(pasta_info["amostras_convertidas"])}')
        if pasta_info['erros']:
            print(f'   ❌ Erros: {len(pasta_info["erros"])}')
        
        resultado_analise['pastas_analisadas'][pasta_nome] = pasta_info
    
    # Relatório consolidado
    print(f'\n🎯 RELATÓRIO CONSOLIDADO - ESTRUTURAS IDENTIFICADAS')
    print('=' * 65)
    
    total_arquivos = resultado_analise['resumo_geral']['total_arquivos']
    analisados = resultado_analise['resumo_geral']['arquivos_analisados']
    convertidos = resultado_analise['resumo_geral']['arquivos_convertidos']
    erros = resultado_analise['resumo_geral']['erros_conversao']
    
    print(f'📊 Total de arquivos: {total_arquivos}')
    print(f'🔍 Arquivos analisados: {analisados}')
    print(f'📄 CSVs criados: {convertidos}')
    print(f'❌ Erros de conversão: {erros}')
    
    print(f'\n📊 DETALHES POR PASTA:')
    for pasta, info in resultado_analise['pastas_analisadas'].items():
        print(f'\n   📂 {pasta.upper()}:')
        print(f'      📄 Arquivos: {info["total_arquivos"]} (analisados: {info["arquivos_analisados"]})')
        print(f'      📊 CSVs criados: {len(info["amostras_convertidas"])}')
        
        # Mostrar estruturas encontradas
        if info['estruturas_encontradas']:
            print(f'      🔍 Estruturas identificadas:')
            for estrutura, arquivos in info['estruturas_encontradas'].items():
                print(f'         • {estrutura}: {len(arquivos)} arquivos')
                
                # Mostrar exemplo de estrutura
                if arquivos:
                    exemplo = arquivos[0]
                    print(f'           Exemplo: {exemplo["total_abas"]} abas ({", ".join(exemplo["abas"][:3])}{"..." if len(exemplo["abas"]) > 3 else ""})')
        
        # Mostrar CSVs criados
        if info['amostras_convertidas']:
            print(f'      📄 Amostras CSV criadas:')
            for csv in info['amostras_convertidas']:
                print(f'         • {csv["arquivo_csv"]} ({csv["linhas"]} linhas x {csv["colunas"]} colunas)')
    
    # Identificar padrões comuns
    print(f'\n🔍 PADRÕES IDENTIFICADOS:')
    
    # Analisar padrões de datas nos nomes dos arquivos
    todos_arquivos = []
    for pasta, info in resultado_analise['pastas_analisadas'].items():
        if 'estruturas_encontradas' in info:
            for estrutura, arquivos in info['estruturas_encontradas'].items():
                todos_arquivos.extend([arq['nome'] for arq in arquivos])
    
    # Padrões de nomenclatura
    padroes_mes = {}
    padroes_ano = {}
    
    for arquivo in todos_arquivos:
        nome_upper = arquivo.upper()
        
        # Identificar meses
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        for mes in meses:
            if mes in nome_upper:
                padroes_mes[mes] = padroes_mes.get(mes, 0) + 1
        
        # Identificar anos
        anos = ['20', '21', '22', '23', '24']
        for ano in anos:
            if ano in nome_upper:
                padroes_ano[f'20{ano}'] = padroes_ano.get(f'20{ano}', 0) + 1
    
    print(f'📅 Distribuição por mês:')
    for mes, qtd in sorted(padroes_mes.items()):
        print(f'   • {mes}: {qtd} arquivos')
    
    print(f'📅 Distribuição por ano:')
    for ano, qtd in sorted(padroes_ano.items()):
        print(f'   • {ano}: {qtd} arquivos')
    
    # Salvar análise completa
    import json
    analise_file = os.path.join(base_path, 'analise_estrutura_controles_gerais.json')
    
    with open(analise_file, 'w', encoding='utf-8') as f:
        json.dump(resultado_analise, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Análise completa salva: {analise_file}')
    
    # Próximos passos
    print(f'\n🚀 PRÓXIMOS PASSOS RECOMENDADOS:')
    print(f'1. 📊 Converter todos os arquivos Excel para CSV')
    print(f'2. 🔄 Normalizar estruturas de dados')
    print(f'3. 📅 Organizar dados cronologicamente (2020-2024)')
    print(f'4. 🔗 Integrar com dados VIXEN existentes')
    print(f'5. 📈 Criar análises temporais de controles')
    
    print(f'\n✅ ANÁLISE DE ESTRUTURA CONCLUÍDA!')
    print(f'🎯 {convertidos} amostras CSV criadas para análise')
    print(f'📊 Padrões identificados em {total_arquivos} arquivos')

if __name__ == "__main__":
    analisar_estrutura_controles_gerais()