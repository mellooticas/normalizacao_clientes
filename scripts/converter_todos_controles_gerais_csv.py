#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import glob
from datetime import datetime

def converter_todos_excel_para_csv():
    """Converte todos os arquivos Excel dos controles gerais para CSV"""
    
    print('🔄 CONVERTENDO TODOS EXCEL → CSV - CONTROLES GERAIS')
    print('=' * 60)
    print(f'📅 Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    base_path = 'data/originais/controles_gerais'
    
    # 4 pastas para processar
    pastas = {
        'conf_dav': 'Configurações DAV',
        'lista_dav': 'Listas DAV',
        'mov_cx': 'Movimentações Caixa',
        'trans_financ': 'Transações Financeiras'
    }
    
    resultado_conversao = {
        'data_conversao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pastas_processadas': {},
        'totais': {
            'arquivos_excel_encontrados': 0,
            'arquivos_convertidos': 0,
            'arquivos_com_erro': 0,
            'csvs_criados': 0
        }
    }
    
    # Processar cada pasta
    for pasta_nome, pasta_descricao in pastas.items():
        print(f'\n📂 PROCESSANDO: {pasta_nome.upper()} ({pasta_descricao})')
        print('-' * 70)
        
        pasta_path = os.path.join(base_path, pasta_nome)
        
        if not os.path.exists(pasta_path):
            print(f'   ❌ Pasta não encontrada: {pasta_path}')
            continue
        
        # Buscar todos os arquivos Excel
        excel_files = glob.glob(os.path.join(pasta_path, '*.xlsx')) + glob.glob(os.path.join(pasta_path, '*.XLSX'))
        
        print(f'   📊 Arquivos Excel encontrados: {len(excel_files)}')
        
        pasta_info = {
            'descricao': pasta_descricao,
            'excel_encontrados': len(excel_files),
            'csvs_criados': 0,
            'arquivos_com_erro': 0,
            'detalhes_conversao': [],
            'erros': []
        }
        
        resultado_conversao['totais']['arquivos_excel_encontrados'] += len(excel_files)
        
        # Converter cada arquivo Excel
        for i, arquivo_excel in enumerate(excel_files, 1):
            nome_arquivo = os.path.basename(arquivo_excel)
            nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
            
            print(f'   🔄 [{i:3d}/{len(excel_files)}] Convertendo: {nome_arquivo}')
            
            try:
                # Ler arquivo Excel
                excel_data = pd.ExcelFile(arquivo_excel)
                
                # Processar cada aba
                for aba_nome in excel_data.sheet_names:
                    try:
                        # Ler dados da aba
                        df = pd.read_excel(arquivo_excel, sheet_name=aba_nome)
                        
                        # Definir nome do CSV
                        if len(excel_data.sheet_names) == 1:
                            # Se só tem 1 aba, usar nome do arquivo
                            nome_csv = f'{nome_sem_extensao}.csv'
                        else:
                            # Se tem múltiplas abas, incluir nome da aba
                            nome_csv = f'{nome_sem_extensao}_{aba_nome}.csv'
                        
                        # Caminho completo do CSV
                        caminho_csv = os.path.join(pasta_path, nome_csv)
                        
                        # Salvar como CSV
                        df.to_csv(caminho_csv, index=False, encoding='utf-8')
                        
                        # Registrar conversão
                        detalhe = {
                            'arquivo_excel': nome_arquivo,
                            'aba': aba_nome,
                            'arquivo_csv': nome_csv,
                            'registros': len(df),
                            'colunas': len(df.columns),
                            'tamanho_kb': round(os.path.getsize(caminho_csv) / 1024, 2) if os.path.exists(caminho_csv) else 0
                        }
                        
                        pasta_info['detalhes_conversao'].append(detalhe)
                        pasta_info['csvs_criados'] += 1
                        resultado_conversao['totais']['csvs_criados'] += 1
                        
                        print(f'      ✅ CSV criado: {nome_csv} ({len(df)} linhas x {len(df.columns)} colunas)')
                        
                    except Exception as e:
                        erro_msg = f'Erro na aba {aba_nome}: {str(e)[:50]}'
                        print(f'      ❌ {erro_msg}')
                        pasta_info['erros'].append(f'{nome_arquivo} - {erro_msg}')
                        pasta_info['arquivos_com_erro'] += 1
                        resultado_conversao['totais']['arquivos_com_erro'] += 1
                
                resultado_conversao['totais']['arquivos_convertidos'] += 1
                
            except Exception as e:
                erro_msg = f'Erro geral no arquivo: {str(e)[:50]}'
                print(f'      ❌ {erro_msg}')
                pasta_info['erros'].append(f'{nome_arquivo} - {erro_msg}')
                pasta_info['arquivos_com_erro'] += 1
                resultado_conversao['totais']['arquivos_com_erro'] += 1
        
        # Resumo da pasta
        print(f'   📊 Resumo da pasta:')
        print(f'      📄 Excel processados: {len(excel_files)}')
        print(f'      📋 CSVs criados: {pasta_info["csvs_criados"]}')
        if pasta_info['arquivos_com_erro'] > 0:
            print(f'      ❌ Arquivos com erro: {pasta_info["arquivos_com_erro"]}')
        
        resultado_conversao['pastas_processadas'][pasta_nome] = pasta_info
    
    # Relatório final consolidado
    print(f'\n🎯 RELATÓRIO FINAL - CONVERSÃO EXCEL → CSV')
    print('=' * 55)
    
    total_excel = resultado_conversao['totais']['arquivos_excel_encontrados']
    total_convertidos = resultado_conversao['totais']['arquivos_convertidos']
    total_csvs = resultado_conversao['totais']['csvs_criados']
    total_erros = resultado_conversao['totais']['arquivos_com_erro']
    
    print(f'📊 TOTAIS GERAIS:')
    print(f'   📄 Arquivos Excel encontrados: {total_excel}')
    print(f'   ✅ Arquivos Excel processados: {total_convertidos}')
    print(f'   📋 CSVs criados: {total_csvs}')
    print(f'   ❌ Arquivos com erro: {total_erros}')
    print(f'   📈 Taxa de sucesso: {(total_convertidos/total_excel)*100:.1f}%')
    
    print(f'\n📊 DETALHES POR PASTA:')
    for pasta, info in resultado_conversao['pastas_processadas'].items():
        print(f'\n   📂 {pasta.upper()}:')
        print(f'      📝 {info["descricao"]}')
        print(f'      📄 Excel: {info["excel_encontrados"]}')
        print(f'      📋 CSVs: {info["csvs_criados"]}')
        if info['arquivos_com_erro'] > 0:
            print(f'      ❌ Erros: {info["arquivos_com_erro"]}')
        
        # Mostrar alguns exemplos de conversão
        if info['detalhes_conversao']:
            print(f'      📋 Exemplos de conversão:')
            for detalhe in info['detalhes_conversao'][:3]:  # Primeiros 3
                print(f'         • {detalhe["arquivo_csv"]} ({detalhe["registros"]} linhas, {detalhe["tamanho_kb"]} KB)')
    
    # Verificar estrutura final
    print(f'\n📁 ESTRUTURA FINAL CRIADA:')
    print(f'📂 {base_path}/')
    
    for pasta_nome in pastas.keys():
        pasta_path = os.path.join(base_path, pasta_nome)
        if os.path.exists(pasta_path):
            # Contar CSVs criados
            csvs = glob.glob(os.path.join(pasta_path, '*.csv'))
            excels = glob.glob(os.path.join(pasta_path, '*.xlsx')) + glob.glob(os.path.join(pasta_path, '*.XLSX'))
            
            print(f'├── {pasta_nome}/')
            print(f'│   ├── 📄 {len(excels)} arquivos Excel (originais)')
            print(f'│   └── 📋 {len(csvs)} arquivos CSV (convertidos)')
    
    # Análise de padrões nos dados convertidos
    print(f'\n🔍 ANÁLISE DE PADRÕES IDENTIFICADOS:')
    
    # Analisar padrões de nomenclatura
    todos_csvs = []
    for pasta, info in resultado_conversao['pastas_processadas'].items():
        for detalhe in info['detalhes_conversao']:
            todos_csvs.append(detalhe['arquivo_csv'])
    
    # Padrões de data
    padroes_mes = {}
    padroes_ano = {}
    
    for csv in todos_csvs:
        nome_upper = csv.upper()
        
        # Identificar meses
        meses = {'JAN': 'Janeiro', 'FEV': 'Fevereiro', 'MAR': 'Março', 'ABR': 'Abril', 
                'MAI': 'Maio', 'JUN': 'Junho', 'JUL': 'Julho', 'AGO': 'Agosto',
                'SET': 'Setembro', 'OUT': 'Outubro', 'NOV': 'Novembro', 'DEZ': 'Dezembro'}
        
        for mes_abrev, mes_nome in meses.items():
            if mes_abrev in nome_upper:
                padroes_mes[mes_nome] = padroes_mes.get(mes_nome, 0) + 1
        
        # Identificar anos
        for ano in ['2020', '2021', '2022', '2023', '2024']:
            if ano[-2:] in nome_upper:  # Procurar últimos 2 dígitos
                padroes_ano[ano] = padroes_ano.get(ano, 0) + 1
    
    if padroes_mes:
        print(f'📅 Distribuição temporal por mês:')
        for mes, qtd in sorted(padroes_mes.items(), key=lambda x: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'].index(x[0])):
            print(f'   • {mes}: {qtd} arquivos')
    
    if padroes_ano:
        print(f'📅 Distribuição temporal por ano:')
        for ano, qtd in sorted(padroes_ano.items()):
            print(f'   • {ano}: {qtd} arquivos')
    
    # Salvar resultado
    import json
    resultado_file = os.path.join(base_path, 'resultado_conversao_excel_csv.json')
    
    with open(resultado_file, 'w', encoding='utf-8') as f:
        json.dump(resultado_conversao, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Resultado da conversão salvo: {resultado_file}')
    
    # Próximos passos
    print(f'\n🚀 PRÓXIMOS PASSOS DISPONÍVEIS:')
    print(f'1. 📊 Análise temporal dos dados (2020-2024)')
    print(f'2. 🔗 Início das integrações com VIXEN/OSS/CXS')
    print(f'3. 📈 Criação de dashboards de controles gerais')
    print(f'4. 🔄 Normalização e padronização de estruturas')
    
    print(f'\n🎉 CONVERSÃO CONCLUÍDA!')
    print(f'✅ {total_csvs} arquivos CSV criados e organizados')
    print(f'✅ Todos os dados prontos para análise')
    print(f'✅ Estrutura mantida dentro de cada pasta')

if __name__ == "__main__":
    converter_todos_excel_para_csv()