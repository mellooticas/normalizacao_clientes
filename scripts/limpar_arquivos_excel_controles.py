#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
from datetime import datetime

def limpar_arquivos_excel():
    """Remove arquivos Excel após conversão para CSV para evitar confusão"""
    
    print('🗑️ LIMPEZA - REMOVENDO ARQUIVOS EXCEL')
    print('=' * 50)
    print(f'📅 Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    base_path = 'data/originais/controles_gerais'
    
    # 4 pastas para limpar
    pastas = {
        'conf_dav': 'Configurações DAV',
        'lista_dav': 'Listas DAV',
        'mov_cx': 'Movimentações Caixa',
        'trans_financ': 'Transações Financeiras'
    }
    
    resultado_limpeza = {
        'data_limpeza': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pastas_limpas': {},
        'totais': {
            'arquivos_excel_encontrados': 0,
            'arquivos_excel_removidos': 0,
            'csvs_mantidos': 0,
            'erros_remocao': 0
        }
    }
    
    # Processar cada pasta
    for pasta_nome, pasta_descricao in pastas.items():
        print(f'\n📂 LIMPANDO: {pasta_nome.upper()} ({pasta_descricao})')
        print('-' * 60)
        
        pasta_path = os.path.join(base_path, pasta_nome)
        
        if not os.path.exists(pasta_path):
            print(f'   ❌ Pasta não encontrada: {pasta_path}')
            continue
        
        # Buscar arquivos Excel e CSV
        excel_files = glob.glob(os.path.join(pasta_path, '*.xlsx')) + glob.glob(os.path.join(pasta_path, '*.XLSX'))
        csv_files = glob.glob(os.path.join(pasta_path, '*.csv'))
        
        print(f'   📊 Arquivos encontrados:')
        print(f'      📄 Excel: {len(excel_files)}')
        print(f'      📋 CSV: {len(csv_files)}')
        
        pasta_info = {
            'descricao': pasta_descricao,
            'excel_encontrados': len(excel_files),
            'excel_removidos': 0,
            'csvs_mantidos': len(csv_files),
            'erros_remocao': 0,
            'arquivos_removidos': [],
            'erros': []
        }
        
        resultado_limpeza['totais']['arquivos_excel_encontrados'] += len(excel_files)
        resultado_limpeza['totais']['csvs_mantidos'] += len(csv_files)
        
        # Remover arquivos Excel
        for i, arquivo_excel in enumerate(excel_files, 1):
            nome_arquivo = os.path.basename(arquivo_excel)
            
            try:
                print(f'   🗑️ [{i:3d}/{len(excel_files)}] Removendo: {nome_arquivo}')
                
                # Verificar se existe pelo menos um CSV correspondente antes de remover
                nome_base = os.path.splitext(nome_arquivo)[0]
                csv_correspondente = False
                
                for csv_file in csv_files:
                    nome_csv = os.path.basename(csv_file)
                    if nome_base in nome_csv:
                        csv_correspondente = True
                        break
                
                if csv_correspondente or len(csv_files) > 0:  # Se tem CSV correspondente ou qualquer CSV
                    os.remove(arquivo_excel)
                    pasta_info['excel_removidos'] += 1
                    pasta_info['arquivos_removidos'].append(nome_arquivo)
                    resultado_limpeza['totais']['arquivos_excel_removidos'] += 1
                    print(f'      ✅ Removido: {nome_arquivo}')
                else:
                    print(f'      ⚠️ Mantido (sem CSV correspondente): {nome_arquivo}')
                    pasta_info['erros'].append(f'Sem CSV correspondente: {nome_arquivo}')
                
            except Exception as e:
                erro_msg = f'Erro ao remover {nome_arquivo}: {str(e)[:50]}'
                print(f'      ❌ {erro_msg}')
                pasta_info['erros'].append(erro_msg)
                pasta_info['erros_remocao'] += 1
                resultado_limpeza['totais']['erros_remocao'] += 1
        
        # Resumo da pasta
        print(f'   📊 Resultado da limpeza:')
        print(f'      🗑️ Excel removidos: {pasta_info["excel_removidos"]}')
        print(f'      📋 CSVs mantidos: {pasta_info["csvs_mantidos"]}')
        if pasta_info['erros_remocao'] > 0:
            print(f'      ❌ Erros: {pasta_info["erros_remocao"]}')
        
        resultado_limpeza['pastas_limpas'][pasta_nome] = pasta_info
    
    # Relatório final consolidado
    print(f'\n🎯 RELATÓRIO FINAL - LIMPEZA EXCEL')
    print('=' * 45)
    
    total_excel_encontrados = resultado_limpeza['totais']['arquivos_excel_encontrados']
    total_excel_removidos = resultado_limpeza['totais']['arquivos_excel_removidos']
    total_csvs_mantidos = resultado_limpeza['totais']['csvs_mantidos']
    total_erros = resultado_limpeza['totais']['erros_remocao']
    
    print(f'📊 TOTAIS GERAIS:')
    print(f'   📄 Arquivos Excel encontrados: {total_excel_encontrados}')
    print(f'   🗑️ Arquivos Excel removidos: {total_excel_removidos}')
    print(f'   📋 Arquivos CSV mantidos: {total_csvs_mantidos}')
    print(f'   ❌ Erros de remoção: {total_erros}')
    if total_excel_encontrados > 0:
        print(f'   📈 Taxa de limpeza: {(total_excel_removidos/total_excel_encontrados)*100:.1f}%')
    
    print(f'\n📊 DETALHES POR PASTA:')
    for pasta, info in resultado_limpeza['pastas_limpas'].items():
        print(f'\n   📂 {pasta.upper()}:')
        print(f'      📝 {info["descricao"]}')
        print(f'      🗑️ Excel removidos: {info["excel_removidos"]}/{info["excel_encontrados"]}')
        print(f'      📋 CSVs mantidos: {info["csvs_mantidos"]}')
        
        if info['erros_remocao'] > 0:
            print(f'      ❌ Erros: {info["erros_remocao"]}')
            for erro in info['erros'][:3]:  # Mostrar primeiros 3 erros
                print(f'         • {erro}')
    
    # Verificar estrutura final limpa
    print(f'\n📁 ESTRUTURA FINAL LIMPA:')
    print(f'📂 {base_path}/')
    
    total_csvs_finais = 0
    total_excels_restantes = 0
    
    for pasta_nome in pastas.keys():
        pasta_path = os.path.join(base_path, pasta_nome)
        if os.path.exists(pasta_path):
            # Contar arquivos restantes
            csvs_restantes = len(glob.glob(os.path.join(pasta_path, '*.csv')))
            excels_restantes = len(glob.glob(os.path.join(pasta_path, '*.xlsx')) + glob.glob(os.path.join(pasta_path, '*.XLSX')))
            
            total_csvs_finais += csvs_restantes
            total_excels_restantes += excels_restantes
            
            print(f'├── {pasta_nome}/')
            print(f'│   ├── 📋 {csvs_restantes} arquivos CSV (dados)')
            if excels_restantes > 0:
                print(f'│   └── ⚠️ {excels_restantes} arquivos Excel (restantes)')
            else:
                print(f'│   └── ✅ Limpo (apenas CSVs)')
    
    print(f'\n📊 RESUMO ESTRUTURAL:')
    print(f'✅ Total de CSVs mantidos: {total_csvs_finais}')
    if total_excels_restantes > 0:
        print(f'⚠️ Excel restantes: {total_excels_restantes}')
    else:
        print(f'🎉 100% Limpo - apenas CSVs!')
    
    # Calcular economia de espaço (estimativa)
    if total_excel_removidos > 0:
        economia_estimada_mb = total_excel_removidos * 0.5  # Estimativa de 500KB por Excel
        print(f'\n💾 ECONOMIA DE ESPAÇO:')
        print(f'📉 Arquivos removidos: {total_excel_removidos}')
        print(f'💽 Espaço economizado (estimado): ~{economia_estimada_mb:.1f} MB')
    
    # Salvar resultado
    import json
    resultado_file = os.path.join(base_path, 'resultado_limpeza_excel.json')
    
    with open(resultado_file, 'w', encoding='utf-8') as f:
        json.dump(resultado_limpeza, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Resultado da limpeza salvo: {resultado_file}')
    
    # Status final
    print(f'\n✅ LIMPEZA CONCLUÍDA!')
    if total_excels_restantes == 0:
        print(f'🎉 Estrutura 100% limpa - apenas CSVs organizados!')
        print(f'📊 {total_csvs_finais} arquivos CSV prontos para análise')
        print(f'🚀 Sem confusão - dados organizados e limpos!')
    else:
        print(f'⚠️ {total_excels_restantes} arquivos Excel restantes')
        print(f'📋 {total_csvs_finais} arquivos CSV organizados')
        print(f'🔄 Limpeza parcial concluída')
    
    print(f'\n🎯 PRÓXIMOS PASSOS:')
    print(f'1. 📊 Análise temporal dos CSVs (2020-2024)')
    print(f'2. 🔗 Integrações com VIXEN/OSS/CXS')
    print(f'3. 📈 Dashboard de controles gerais')
    print(f'4. 🔄 Normalização de estruturas')

if __name__ == "__main__":
    limpar_arquivos_excel()