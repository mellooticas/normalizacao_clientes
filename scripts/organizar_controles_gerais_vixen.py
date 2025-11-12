#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import glob
import pandas as pd
from datetime import datetime

def organizar_controles_gerais_vixen():
    """Organiza as 4 pastas de controles gerais do VIXEN"""
    
    print('📁 ORGANIZANDO CONTROLES GERAIS VIXEN')
    print('=' * 50)
    print(f'📅 Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Pasta de origem no OneDrive
    origem_base = r'D:\OneDrive - Óticas Taty Mello\VENDAS\oticas\vendasprojecoes'
    
    # Pasta de destino
    destino_base = 'data/originais/controles_gerais'
    
    # 4 pastas a serem organizadas
    pastas_controles = {
        'conf_dav': 'Configurações DAV',
        'lista_dav': 'Listas DAV', 
        'mov_cx': 'Movimentações Caixa',
        'trans_financ': 'Transações Financeiras'
    }
    
    print(f'\n🎯 ORIGEM: {origem_base}')
    print(f'🎯 DESTINO: {destino_base}')
    
    # Criar estrutura de destino
    os.makedirs(destino_base, exist_ok=True)
    
    resumo_organizacao = {
        'data_organizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'origem': origem_base,
        'destino': destino_base,
        'pastas_processadas': {},
        'totais': {
            'pastas_criadas': 0,
            'arquivos_copiados': 0,
            'arquivos_csv': 0,
            'erro_arquivos': 0
        }
    }
    
    # Processar cada pasta
    for pasta_nome, pasta_descricao in pastas_controles.items():
        print(f'\n📂 PROCESSANDO: {pasta_nome.upper()} ({pasta_descricao})')
        print('-' * 60)
        
        # Caminhos
        origem_pasta = os.path.join(origem_base, pasta_nome)
        destino_pasta = os.path.join(destino_base, pasta_nome)
        
        # Criar pasta de destino
        os.makedirs(destino_pasta, exist_ok=True)
        resumo_organizacao['totais']['pastas_criadas'] += 1
        
        pasta_info = {
            'descricao': pasta_descricao,
            'origem': origem_pasta,
            'destino': destino_pasta,
            'arquivos_encontrados': 0,
            'arquivos_copiados': 0,
            'arquivos_csv': 0,
            'arquivos_com_erro': 0,
            'lista_arquivos': []
        }
        
        print(f'   📁 Origem: {origem_pasta}')
        print(f'   📁 Destino: {destino_pasta}')
        
        # Verificar se pasta de origem existe
        if not os.path.exists(origem_pasta):
            print(f'   ⚠️ Pasta de origem não encontrada: {origem_pasta}')
            pasta_info['erro'] = 'Pasta origem não encontrada'
            resumo_organizacao['pastas_processadas'][pasta_nome] = pasta_info
            continue
        
        # Buscar todos os arquivos (com foco em CSV)
        todos_arquivos = []
        
        # Buscar CSVs primeiro
        csvs = glob.glob(os.path.join(origem_pasta, '**', '*.csv'), recursive=True)
        excels = glob.glob(os.path.join(origem_pasta, '**', '*.xlsx'), recursive=True)
        outros = glob.glob(os.path.join(origem_pasta, '**', '*.*'), recursive=True)
        
        # Filtrar apenas arquivos relevantes
        todos_arquivos = csvs + excels
        
        print(f'   📊 Arquivos encontrados: {len(todos_arquivos)}')
        print(f'   📄 CSVs: {len(csvs)}')
        print(f'   📄 Excel: {len(excels)}')
        
        pasta_info['arquivos_encontrados'] = len(todos_arquivos)
        
        # Copiar arquivos
        for arquivo_origem in todos_arquivos:
            try:
                # Nome do arquivo
                nome_arquivo = os.path.basename(arquivo_origem)
                arquivo_destino = os.path.join(destino_pasta, nome_arquivo)
                
                # Evitar sobrescrever - adicionar sufixo se necessário
                contador = 1
                arquivo_destino_final = arquivo_destino
                while os.path.exists(arquivo_destino_final):
                    nome_base, extensao = os.path.splitext(nome_arquivo)
                    arquivo_destino_final = os.path.join(destino_pasta, f'{nome_base}_{contador}{extensao}')
                    contador += 1
                
                # Copiar arquivo
                shutil.copy2(arquivo_origem, arquivo_destino_final)
                
                # Contabilizar
                pasta_info['arquivos_copiados'] += 1
                resumo_organizacao['totais']['arquivos_copiados'] += 1
                
                if arquivo_origem.lower().endswith('.csv'):
                    pasta_info['arquivos_csv'] += 1
                    resumo_organizacao['totais']['arquivos_csv'] += 1
                
                # Adicionar à lista
                pasta_info['lista_arquivos'].append({
                    'nome': nome_arquivo,
                    'origem': arquivo_origem,
                    'destino': arquivo_destino_final,
                    'tipo': 'CSV' if arquivo_origem.lower().endswith('.csv') else 'Excel',
                    'tamanho': os.path.getsize(arquivo_origem) if os.path.exists(arquivo_origem) else 0
                })
                
                print(f'   ✅ Copiado: {nome_arquivo}')
                
            except Exception as e:
                print(f'   ❌ Erro ao copiar {nome_arquivo}: {e}')
                pasta_info['arquivos_com_erro'] += 1
                resumo_organizacao['totais']['erro_arquivos'] += 1
        
        print(f'   📊 Resultado: {pasta_info["arquivos_copiados"]} arquivos copiados')
        print(f'   📄 CSVs copiados: {pasta_info["arquivos_csv"]}')
        
        resumo_organizacao['pastas_processadas'][pasta_nome] = pasta_info
    
    # Gerar relatório final
    print(f'\n🎯 RESUMO FINAL - CONTROLES GERAIS VIXEN')
    print('=' * 55)
    
    total_pastas = resumo_organizacao['totais']['pastas_criadas']
    total_arquivos = resumo_organizacao['totais']['arquivos_copiados']
    total_csvs = resumo_organizacao['totais']['arquivos_csv']
    total_erros = resumo_organizacao['totais']['erro_arquivos']
    
    print(f'📁 Pastas criadas: {total_pastas}')
    print(f'📄 Arquivos copiados: {total_arquivos}')
    print(f'📊 CSVs importados: {total_csvs}')
    print(f'❌ Erros: {total_erros}')
    
    print(f'\n📊 DETALHES POR PASTA:')
    for pasta, info in resumo_organizacao['pastas_processadas'].items():
        if 'erro' in info:
            print(f'   ❌ {pasta.upper()}: {info["erro"]}')
        else:
            print(f'   ✅ {pasta.upper()}: {info["arquivos_copiados"]} arquivos ({info["arquivos_csv"]} CSVs)')
    
    # Verificar estrutura criada
    print(f'\n📁 ESTRUTURA CRIADA:')
    print(f'📂 {destino_base}/')
    
    for pasta_nome in pastas_controles.keys():
        pasta_path = os.path.join(destino_base, pasta_nome)
        if os.path.exists(pasta_path):
            arquivos_na_pasta = len([f for f in os.listdir(pasta_path) if os.path.isfile(os.path.join(pasta_path, f))])
            print(f'├── {pasta_nome}/ ({arquivos_na_pasta} arquivos)')
        else:
            print(f'├── {pasta_nome}/ (pasta não criada)')
    
    # Salvar resumo
    import json
    resumo_file = os.path.join(destino_base, 'resumo_organizacao_controles_gerais.json')
    
    # Converter info para formato JSON serializable
    resumo_json = resumo_organizacao.copy()
    for pasta, info in resumo_json['pastas_processadas'].items():
        if 'lista_arquivos' in info:
            # Simplificar lista de arquivos para JSON
            info['lista_arquivos'] = [
                {
                    'nome': arq['nome'],
                    'tipo': arq['tipo'],
                    'tamanho_kb': round(arq['tamanho'] / 1024, 2)
                }
                for arq in info['lista_arquivos']
            ]
    
    with open(resumo_file, 'w', encoding='utf-8') as f:
        json.dump(resumo_json, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Resumo salvo: {resumo_file}')
    
    # Próximos passos
    print(f'\n🚀 PRÓXIMOS PASSOS:')
    print(f'1. 📊 Analisar estrutura dos CSVs importados')
    print(f'2. 🔄 Normalizar dados de controles gerais')
    print(f'3. 🔗 Integrar com dados VIXEN existentes')
    print(f'4. 📈 Criar análises de controles operacionais')
    
    print(f'\n✅ CONTROLES GERAIS VIXEN ORGANIZADOS!')
    print(f'🎯 {total_arquivos} arquivos prontos para análise')
    print(f'📊 {total_csvs} CSVs disponíveis para processamento')

if __name__ == "__main__":
    organizar_controles_gerais_vixen()