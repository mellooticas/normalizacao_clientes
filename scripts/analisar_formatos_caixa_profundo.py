#!/usr/bin/env python3
"""
Script para análise profunda das estruturas dinâmicas de caixa
Sistema Carne Fácil - Análise de layouts e células específicas
"""

import pandas as pd
import openpyxl
from pathlib import Path
import json
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

def extrair_valor_celula(worksheet, celula):
    """
    Extrai valor de uma célula específica
    """
    try:
        valor = worksheet[celula].value
        return str(valor).strip() if valor else ""
    except Exception:
        return ""

def analisar_estrutura_dinamica(caminho_arquivo, nome_aba):
    """
    Análise específica da estrutura dinâmica de uma aba de caixa
    """
    resultado = {
        'arquivo': os.path.basename(caminho_arquivo),
        'aba': nome_aba,
        'data_movimento': '',
        'loja': '',
        'estruturas_identificadas': {},
        'colunas_por_estrutura': {},
        'linhas_dados_por_estrutura': {},
        'erro': None
    }
    
    try:
        # Carregar workbook
        workbook = openpyxl.load_workbook(caminho_arquivo, data_only=True)
        worksheet = workbook[nome_aba]
        
        # Extrair data (B1) e loja (L1)
        resultado['data_movimento'] = extrair_valor_celula(worksheet, 'B1')
        resultado['loja'] = extrair_valor_celula(worksheet, 'L1')
        
        # Estruturas fixas identificadas pelo usuário
        estruturas_caixa = {
            'VENDAS': {
                'celula_inicio': 'E5',
                'titulo_esperado': 'Nº Venda',
                'colunas': ['Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada']
            },
            'RESTANTE_ENTRADA': {
                'celula_inicio': 'E25', 
                'titulo_esperado': 'Nº Venda',
                'colunas': ['Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada']
            },
            'RECEBIMENTO_CARNE': {
                'celula_inicio': 'E34',
                'titulo_esperado': 'OS',
                'colunas': ['OS', 'Cliente', 'Forma de Pgto', 'Valor Parcela', 'Nº Parcela']
            },
            'OS_ENTREGUES_DIA': {
                'celula_inicio': 'K14',
                'titulo_esperado': 'OS',
                'colunas': ['OS', 'Vendedor', 'CARNÊ']
            },
            'ENTREGA_CARNE': {
                'celula_inicio': 'K34',
                'titulo_esperado': 'OS',
                'colunas': ['OS', 'Parcelas', 'Valor Total']
            }
        }
        
        # Analisar cada estrutura
        for nome_estrutura, config in estruturas_caixa.items():
            try:
                celula_inicio = config['celula_inicio']
                
                # Verificar se existe conteúdo na célula de início
                valor_celula = extrair_valor_celula(worksheet, celula_inicio)
                
                if valor_celula and config['titulo_esperado'].lower() in valor_celula.lower():
                    # Estrutura encontrada
                    resultado['estruturas_identificadas'][nome_estrutura] = {
                        'encontrada': True,
                        'celula_inicio': celula_inicio,
                        'valor_celula': valor_celula
                    }
                    
                    # Extrair cabeçalhos das colunas
                    linha_inicio = int(celula_inicio[1:])
                    coluna_inicio_letra = celula_inicio[0]
                    coluna_inicio_num = ord(coluna_inicio_letra.upper()) - ord('A') + 1
                    
                    colunas_encontradas = []
                    for i, col_esperada in enumerate(config['colunas']):
                        col_letra = chr(ord(coluna_inicio_letra.upper()) + i)
                        celula_col = f"{col_letra}{linha_inicio}"
                        valor_col = extrair_valor_celula(worksheet, celula_col)
                        colunas_encontradas.append({
                            'celula': celula_col,
                            'esperado': col_esperada,
                            'encontrado': valor_col,
                            'match': col_esperada.lower() in valor_col.lower() if valor_col else False
                        })
                    
                    resultado['colunas_por_estrutura'][nome_estrutura] = colunas_encontradas
                    
                    # Contar linhas com dados (procurar até 20 linhas abaixo)
                    linhas_dados = []
                    for linha_offset in range(1, 21):  # Verificar até 20 linhas
                        linha_atual = linha_inicio + linha_offset
                        primeira_coluna = f"{coluna_inicio_letra}{linha_atual}"
                        valor_linha = extrair_valor_celula(worksheet, primeira_coluna)
                        
                        if valor_linha and valor_linha.strip():
                            # Extrair dados de todas as colunas desta linha
                            dados_linha = []
                            for i in range(len(config['colunas'])):
                                col_letra = chr(ord(coluna_inicio_letra.upper()) + i)
                                celula_dados = f"{col_letra}{linha_atual}"
                                valor_dados = extrair_valor_celula(worksheet, celula_dados)
                                dados_linha.append(valor_dados)
                            
                            linhas_dados.append({
                                'linha': linha_atual,
                                'dados': dados_linha
                            })
                        elif len(linhas_dados) > 0:
                            # Se já encontramos dados e agora está vazio, provavelmente acabou
                            break
                    
                    resultado['linhas_dados_por_estrutura'][nome_estrutura] = linhas_dados
                    
                else:
                    resultado['estruturas_identificadas'][nome_estrutura] = {
                        'encontrada': False,
                        'celula_inicio': celula_inicio,
                        'valor_celula': valor_celula
                    }
                    
            except Exception as e:
                resultado['estruturas_identificadas'][nome_estrutura] = {
                    'encontrada': False,
                    'erro': str(e)
                }
        
        workbook.close()
        
    except Exception as e:
        resultado['erro'] = str(e)
    
    return resultado

def analisar_padroes_caixa_profundo():
    """
    Análise profunda dos padrões de caixa com estruturas dinâmicas
    """
    
    # Arquivos de amostra para análise profunda
    arquivos_amostra = [
        ("MAUA", "D:/OneDrive - Óticas Taty Mello/LOJAS/MAUA/CAIXA/jan_25.xlsx", ["01", "15", "31"]),
        ("PERUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/PERUS/CAIXA/jan_25.xlsx", ["01", "15"]),
        ("SUZANO", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO/CAIXA/jan_25.xlsx", ["01", "31"])
    ]
    
    resultado_geral = {
        'data_analise': datetime.now().isoformat(),
        'analise_profunda': {},
        'estatisticas_estruturas': {},
        'padroes_identificados': {
            'estruturas_consistentes': [],
            'variacoes_por_loja': {},
            'datas_extraidas': [],
            'lojas_extraidas': []
        }
    }
    
    print("🔍 ANÁLISE PROFUNDA DAS ESTRUTURAS DINÂMICAS DE CAIXA...")
    
    # Contadores para estatísticas
    contador_estruturas = {}
    
    for nome_loja, caminho_arquivo, abas_teste in arquivos_amostra:
        if not os.path.exists(caminho_arquivo):
            print(f"⚠️  Arquivo não encontrado: {caminho_arquivo}")
            continue
        
        print(f"\n📁 Analisando {nome_loja}: {os.path.basename(caminho_arquivo)}")
        
        resultado_geral['analise_profunda'][nome_loja] = {
            'arquivo': caminho_arquivo,
            'abas_analisadas': {}
        }
        
        for nome_aba in abas_teste:
            try:
                print(f"   📄 Análise profunda da aba: {nome_aba}")
                resultado_aba = analisar_estrutura_dinamica(caminho_arquivo, nome_aba)
                resultado_geral['analise_profunda'][nome_loja]['abas_analisadas'][nome_aba] = resultado_aba
                
                # Coletar estatísticas
                if resultado_aba.get('data_movimento'):
                    resultado_geral['padroes_identificados']['datas_extraidas'].append(resultado_aba['data_movimento'])
                
                if resultado_aba.get('loja'):
                    resultado_geral['padroes_identificados']['lojas_extraidas'].append(resultado_aba['loja'])
                
                # Contar estruturas encontradas
                for nome_estrutura, dados_estrutura in resultado_aba.get('estruturas_identificadas', {}).items():
                    if dados_estrutura.get('encontrada'):
                        if nome_estrutura not in contador_estruturas:
                            contador_estruturas[nome_estrutura] = 0
                        contador_estruturas[nome_estrutura] += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao analisar aba {nome_aba}: {str(e)}")
    
    # Compilar estatísticas
    resultado_geral['estatisticas_estruturas'] = contador_estruturas
    
    # Identificar estruturas consistentes (aparecem em todas as análises)
    total_abas_analisadas = sum(len(dados['abas_analisadas']) for dados in resultado_geral['analise_profunda'].values())
    for estrutura, count in contador_estruturas.items():
        if count >= total_abas_analisadas * 0.7:  # Aparece em pelo menos 70% das abas
            resultado_geral['padroes_identificados']['estruturas_consistentes'].append(estrutura)
    
    return resultado_geral

def main():
    """Função principal"""
    print("🚀 ANÁLISE PROFUNDA DE ESTRUTURAS DINÂMICAS DE CAIXA")
    print("=" * 70)
    
    # Executar análise profunda
    resultado = analisar_padroes_caixa_profundo()
    
    # Salvar resultado detalhado
    caminho_resultado = 'data/originais/cxs/analise_profunda_estruturas_caixa.json'
    
    with open(caminho_resultado, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise profunda salva em: {caminho_resultado}")
    
    # Mostrar resumo dos padrões
    print("\n📊 ESTRUTURAS CONSISTENTES IDENTIFICADAS:")
    for estrutura in resultado['padroes_identificados']['estruturas_consistentes']:
        count = resultado['estatisticas_estruturas'].get(estrutura, 0)
        print(f"   ✅ {estrutura}: encontrada em {count} abas")
    
    print(f"\n📅 DATAS EXTRAÍDAS: {len(set(resultado['padroes_identificados']['datas_extraidas']))} únicas")
    print(f"🏪 LOJAS EXTRAÍDAS: {len(set(resultado['padroes_identificados']['lojas_extraidas']))} únicas")
    
    print("\n📋 AMOSTRA DE DADOS POR LOJA:")
    for nome_loja, dados_loja in resultado['analise_profunda'].items():
        print(f"\n   🏪 {nome_loja}:")
        for nome_aba, dados_aba in dados_loja['abas_analisadas'].items():
            print(f"      📄 Aba {nome_aba}:")
            print(f"         📅 Data: {dados_aba.get('data_movimento', 'N/A')}")
            print(f"         🏪 Loja: {dados_aba.get('loja', 'N/A')}")
            
            estruturas_encontradas = [k for k, v in dados_aba.get('estruturas_identificadas', {}).items() if v.get('encontrada')]
            print(f"         📊 Estruturas: {len(estruturas_encontradas)} encontradas")
            
            for estrutura in estruturas_encontradas:
                linhas_dados = len(dados_aba.get('linhas_dados_por_estrutura', {}).get(estrutura, []))
                print(f"            • {estrutura}: {linhas_dados} registros")
    
    print("\n✅ Análise profunda concluída!")
    return resultado

if __name__ == "__main__":
    main()