#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
from datetime import datetime

def analise_detalhada_controles_gerais():
    """Análise detalhada dos controles gerais VIXEN"""
    
    print('🔍 ANÁLISE DETALHADA - CONTROLES GERAIS VIXEN')
    print('=' * 55)
    print(f'📅 Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    base_path = 'data/originais/controles_gerais'
    
    # Amostras CSV criadas na análise anterior
    amostras = {
        'conf_dav': {
            'descricao': 'Configurações DAV (Documentos de Autorização de Venda)',
            'arquivos': ['ABR21_Planilha1.csv', 'ABR22_Planilha1.csv', 'ABR23_Planilha1.csv']
        },
        'lista_dav': {
            'descricao': 'Listas DAV (Ordens de Serviço e Vendas)',
            'arquivos': ['ABR_21_Planilha1.csv', 'ABR_22_Planilha1.csv', 'ABR_23_Planilha1.csv']
        },
        'mov_cx': {
            'descricao': 'Movimentações de Caixa',
            'arquivos': ['ABR_21_Planilha1.csv', 'ABR_22_Planilha1.csv', 'ABR_23_Planilha1.csv']
        },
        'trans_financ': {
            'descricao': 'Transações Financeiras Completas',
            'arquivos': ['ABR_21_Planilha1.csv', 'ABR_22_Planilha1.csv', 'ABR_23_Planilha1.csv']
        }
    }
    
    resultado_analise = {
        'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sistemas_identificados': {},
        'potencial_integracao': {},
        'resumo_executivo': {}
    }
    
    # Analisar cada tipo de controle
    for pasta, info in amostras.items():
        print(f'\n📊 ANALISANDO: {pasta.upper()}')
        print(f'📝 Descrição: {info["descricao"]}')
        print('-' * 60)
        
        pasta_path = os.path.join(base_path, pasta)
        analise_pasta = {
            'descricao': info['descricao'],
            'amostras_analisadas': [],
            'colunas_identificadas': [],
            'campos_chave': [],
            'potencial_cruzamento': []
        }
        
        # Analisar cada amostra
        for arquivo in info['arquivos']:
            arquivo_path = os.path.join(pasta_path, arquivo)
            
            if not os.path.exists(arquivo_path):
                print(f'   ❌ Arquivo não encontrado: {arquivo}')
                continue
            
            try:
                df = pd.read_csv(arquivo_path)
                
                # Análise da estrutura
                colunas = list(df.columns)
                amostra_info = {
                    'arquivo': arquivo,
                    'registros': len(df),
                    'colunas': len(colunas),
                    'colunas_nomes': colunas,
                    'campos_importantes': []
                }
                
                print(f'   📄 {arquivo}: {len(df)} registros x {len(colunas)} colunas')
                
                # Identificar campos importantes baseado no tipo
                if pasta == 'conf_dav':
                    # Configurações DAV - Items/Produtos
                    campos_importantes = ['Nro.DAV', 'Produto', 'Modelo', 'Qtd.', 'Vl.Total', 'Dt.DAV']
                    
                elif pasta == 'lista_dav':
                    # Listas DAV - Ordens de Serviço
                    campos_importantes = ['Nro.DAV', 'Cliente', 'Vendedor', 'Vl.líquido', 'Dh.DAV', 'Status']
                    
                elif pasta == 'mov_cx':
                    # Movimentações Caixa
                    campos_importantes = ['ID caixa', 'Dh.movimento', 'Histórico', 'Vl.líquido', 'Fornecedor/cliente']
                    
                elif pasta == 'trans_financ':
                    # Transações Financeiras
                    campos_importantes = ['Cliente', 'Vl.líquido', 'Dh.transação', 'Pagamento', 'Vendedor']
                
                # Verificar presença dos campos importantes
                campos_presentes = [campo for campo in campos_importantes if campo in colunas]
                amostra_info['campos_importantes'] = campos_presentes
                
                print(f'      ✅ Campos-chave: {len(campos_presentes)}/{len(campos_importantes)}')
                print(f'      📋 Presentes: {", ".join(campos_presentes[:3])}{"..." if len(campos_presentes) > 3 else ""}')
                
                # Identificar potenciais de cruzamento
                potenciais_cruzamento = []
                
                if 'Cliente' in colunas:
                    potenciais_cruzamento.append('VIXEN (Cliente)')
                if 'Nro.DAV' in colunas:
                    potenciais_cruzamento.append('OSS (Número OS)')
                if 'Vendedor' in colunas:
                    potenciais_cruzamento.append('VIXEN (Vendedor)')
                
                amostra_info['potenciais_cruzamento'] = potenciais_cruzamento
                
                if potenciais_cruzamento:
                    print(f'      🔗 Cruzamentos: {", ".join(potenciais_cruzamento)}')
                
                analise_pasta['amostras_analisadas'].append(amostra_info)
                
                # Adicionar colunas únicas à lista geral
                for col in colunas:
                    if col not in analise_pasta['colunas_identificadas']:
                        analise_pasta['colunas_identificadas'].append(col)
                
            except Exception as e:
                print(f'   ❌ Erro ao analisar {arquivo}: {str(e)[:50]}')
        
        # Consolidar análise da pasta
        if analise_pasta['amostras_analisadas']:
            # Campos mais comuns
            todos_campos = []
            for amostra in analise_pasta['amostras_analisadas']:
                todos_campos.extend(amostra['campos_importantes'])
            
            # Contar frequência
            freq_campos = {}
            for campo in todos_campos:
                freq_campos[campo] = freq_campos.get(campo, 0) + 1
            
            analise_pasta['campos_chave'] = sorted(freq_campos.keys(), key=lambda x: freq_campos[x], reverse=True)
            
            # Potencial de cruzamento
            todos_cruzamentos = []
            for amostra in analise_pasta['amostras_analisadas']:
                todos_cruzamentos.extend(amostra['potenciais_cruzamento'])
            
            analise_pasta['potencial_cruzamento'] = list(set(todos_cruzamentos))
        
        print(f'   🎯 Resumo: {len(analise_pasta["colunas_identificadas"])} colunas únicas identificadas')
        
        resultado_analise['sistemas_identificados'][pasta] = analise_pasta
    
    # Análise de integração
    print(f'\n🔗 ANÁLISE DE POTENCIAL DE INTEGRAÇÃO')
    print('=' * 50)
    
    # Mapeamento de integrações possíveis
    integracoes = {
        'VIXEN_Cliente': {
            'sistema_origem': 'Controles Gerais',
            'sistema_destino': 'VIXEN',
            'campo_chave': 'Cliente',
            'sistemas_com_campo': []
        },
        'OSS_NumeroDAV': {
            'sistema_origem': 'Controles Gerais', 
            'sistema_destino': 'OSS',
            'campo_chave': 'Nro.DAV',
            'sistemas_com_campo': []
        },
        'CXS_Transacoes': {
            'sistema_origem': 'Controles Gerais',
            'sistema_destino': 'CXS',
            'campo_chave': 'Vl.líquido',
            'sistemas_com_campo': []
        }
    }
    
    # Verificar quais sistemas têm cada campo
    for pasta, analise in resultado_analise['sistemas_identificados'].items():
        for integracao, info in integracoes.items():
            if info['campo_chave'] in analise['colunas_identificadas']:
                info['sistemas_com_campo'].append(pasta)
    
    # Mostrar potencial de integração
    for integracao, info in integracoes.items():
        sistemas = info['sistemas_com_campo']
        if sistemas:
            print(f'✅ {integracao}: {len(sistemas)} sistemas ({", ".join(sistemas)})')
        else:
            print(f'❌ {integracao}: Nenhum sistema compatível')
    
    resultado_analise['potencial_integracao'] = integracoes
    
    # Resumo executivo
    print(f'\n🎯 RESUMO EXECUTIVO - CONTROLES GERAIS VIXEN')
    print('=' * 55)
    
    total_sistemas = len(resultado_analise['sistemas_identificados'])
    total_arquivos_originais = 159  # Do script anterior
    total_amostras = sum(len(info['amostras_analisadas']) for info in resultado_analise['sistemas_identificados'].values())
    
    print(f'📊 Sistemas de Controle: {total_sistemas}')
    print(f'📄 Arquivos Excel originais: {total_arquivos_originais}')
    print(f'📋 Amostras CSV analisadas: {total_amostras}')
    
    # Análise por sistema
    print(f'\n📋 ANÁLISE POR SISTEMA:')
    
    for pasta, info in resultado_analise['sistemas_identificados'].items():
        total_campos = len(info['colunas_identificadas'])
        campos_chave = len(info['campos_chave'])
        potencial_cruzamento = len(info['potencial_cruzamento'])
        
        print(f'\n   📂 {pasta.upper()}:')
        print(f'      📝 {info["descricao"]}')
        print(f'      📊 Campos identificados: {total_campos}')
        print(f'      🔑 Campos-chave: {campos_chave}')
        print(f'      🔗 Potencial de cruzamento: {potencial_cruzamento}')
        
        if info['campos_chave']:
            print(f'      📋 Principais campos: {", ".join(info["campos_chave"][:5])}')
        
        if info['potencial_cruzamento']:
            print(f'      🎯 Integrações possíveis: {", ".join(info["potencial_cruzamento"])}')
    
    # Próximos passos estratégicos
    print(f'\n🚀 PRÓXIMOS PASSOS ESTRATÉGICOS')
    print('=' * 40)
    
    print(f'🔄 FASE 1 - NORMALIZAÇÃO:')
    print(f'   1. Converter todos os 159 Excel para CSV')
    print(f'   2. Padronizar estruturas de dados')
    print(f'   3. Organizar cronologicamente (2020-2024)')
    
    print(f'\n🔗 FASE 2 - INTEGRAÇÃO:')
    print(f'   1. Cruzar dados de Cliente com VIXEN')
    print(f'   2. Conectar Nro.DAV com OSS')
    print(f'   3. Integrar transações com CXS')
    
    print(f'\n📈 FASE 3 - ANÁLISES:')
    print(f'   1. Dashboard de controles operacionais')
    print(f'   2. Análise temporal de performance')
    print(f'   3. Integração com sistema principal')
    
    # Valor estratégico
    print(f'\n💎 VALOR ESTRATÉGICO IDENTIFICADO:')
    print(f'✅ Controle completo de DAVs e Ordens de Serviço')
    print(f'✅ Rastreamento de movimentações de caixa')
    print(f'✅ Transações financeiras detalhadas')
    print(f'✅ Histórico temporal de 4 anos (2020-2024)')
    print(f'✅ Potencial de integração com VIXEN+OSS+CXS')
    
    resultado_analise['resumo_executivo'] = {
        'total_sistemas': total_sistemas,
        'total_arquivos': total_arquivos_originais,
        'amostras_analisadas': total_amostras,
        'valor_estrategico': 'Alto - Controles operacionais completos com histórico temporal',
        'prioridade_integracao': 'Alta - Dados complementares aos sistemas principais'
    }
    
    # Salvar análise
    import json
    analise_file = os.path.join(base_path, 'analise_detalhada_controles_gerais.json')
    
    with open(analise_file, 'w', encoding='utf-8') as f:
        json.dump(resultado_analise, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Análise detalhada salva: {analise_file}')
    
    print(f'\n🏆 CONTROLES GERAIS VIXEN - ANÁLISE FINALIZADA!')
    print(f'✅ {total_sistemas} sistemas de controle identificados')
    print(f'✅ Estruturas mapeadas e potencial de integração avaliado')
    print(f'✅ Próximos passos definidos para implementação')

if __name__ == "__main__":
    analise_detalhada_controles_gerais()