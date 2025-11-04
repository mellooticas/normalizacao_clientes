#!/usr/bin/env python3
"""
Script para análise detalhada das abas de caixa
Sistema Carne Fácil - Análise de dados de caixa
"""

import pandas as pd
import openpyxl
from pathlib import Path
import json
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

def analisar_aba_detalhada(caminho_arquivo, nome_aba):
    """
    Análise detalhada de uma aba específica
    """
    resultado = {
        'aba': nome_aba,
        'arquivo': os.path.basename(caminho_arquivo),
        'estrutura': {},
        'dados_amostra': [],
        'colunas_identificadas': [],
        'tipo_dados': 'indefinido'
    }
    
    try:
        # Carregar com pandas
        df = pd.read_excel(caminho_arquivo, sheet_name=nome_aba, header=None)
        
        # Informações básicas
        resultado['estrutura'] = {
            'total_linhas': len(df),
            'total_colunas': len(df.columns),
            'linhas_com_dados': len(df.dropna(how='all')),
            'colunas_com_dados': len(df.dropna(how='all', axis=1).columns)
        }
        
        # Primeiras 10 linhas não vazias
        df_limpo = df.dropna(how='all')
        if len(df_limpo) > 0:
            # Converter para strings e limitar tamanho
            amostra = []
            for i, row in df_limpo.head(10).iterrows():
                linha = []
                for val in row:
                    if pd.isna(val):
                        linha.append('')
                    else:
                        str_val = str(val)[:50]  # Limitar tamanho
                        linha.append(str_val)
                amostra.append(linha)
            
            resultado['dados_amostra'] = amostra
            
            # Tentar identificar tipo de dados
            primeira_linha = amostra[0] if amostra else []
            
            # Verificar se é dados de caixa (tem datas, valores, etc.)
            if any('2024' in str(cell) or '2025' in str(cell) or '2023' in str(cell) for cell in primeira_linha):
                resultado['tipo_dados'] = 'movimentacao_diaria'
            elif any('total' in str(cell).lower() or 'resumo' in str(cell).lower() for cell in primeira_linha):
                resultado['tipo_dados'] = 'resumo'
            elif len([x for x in primeira_linha if x and x.strip()]) > 5:
                resultado['tipo_dados'] = 'tabela_dados'
            else:
                resultado['tipo_dados'] = 'outros'
        
    except Exception as e:
        resultado['erro'] = str(e)
    
    return resultado

def analisar_padroes_caixa():
    """
    Analisa padrões específicos dos arquivos de caixa
    """
    
    # Selecionar arquivos de amostra de diferentes lojas
    arquivos_amostra = [
        ("MAUA", "D:/OneDrive - Óticas Taty Mello/LOJAS/MAUA/CAIXA/jan_25.xlsx"),
        ("PERUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/PERUS/CAIXA/jan_25.xlsx"),
        ("SUZANO", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO/CAIXA/jan_25.xlsx")
    ]
    
    resultado_geral = {
        'data_analise': datetime.now().isoformat(),
        'analise_detalhada': {},
        'padroes_identificados': {
            'abas_numericas': [],  # 01, 02, 03...
            'abas_especiais': [],  # resumo_cx, base, base_OS
            'estruturas_comuns': {}
        }
    }
    
    print("🔍 Análise detalhada das estruturas de caixa...")
    
    for nome_loja, caminho_arquivo in arquivos_amostra:
        if not os.path.exists(caminho_arquivo):
            print(f"⚠️  Arquivo não encontrado: {caminho_arquivo}")
            continue
        
        print(f"\n📁 Analisando {nome_loja}: {os.path.basename(caminho_arquivo)}")
        
        resultado_geral['analise_detalhada'][nome_loja] = {
            'arquivo': caminho_arquivo,
            'abas': {}
        }
        
        # Analisar abas específicas
        abas_interesse = ['resumo_cx', 'base', 'base_OS', '01', '15', '31']
        
        for nome_aba in abas_interesse:
            try:
                print(f"   📄 Analisando aba: {nome_aba}")
                resultado_aba = analisar_aba_detalhada(caminho_arquivo, nome_aba)
                resultado_geral['analise_detalhada'][nome_loja]['abas'][nome_aba] = resultado_aba
                
                # Identificar padrões
                if nome_aba.isdigit():
                    if nome_aba not in resultado_geral['padroes_identificados']['abas_numericas']:
                        resultado_geral['padroes_identificados']['abas_numericas'].append(nome_aba)
                else:
                    if nome_aba not in resultado_geral['padroes_identificados']['abas_especiais']:
                        resultado_geral['padroes_identificados']['abas_especiais'].append(nome_aba)
                
            except Exception as e:
                print(f"   ❌ Erro ao analisar aba {nome_aba}: {str(e)}")
    
    return resultado_geral

def main():
    """Função principal"""
    print("🚀 ANÁLISE DETALHADA DE ESTRUTURAS DE CAIXA")
    print("=" * 60)
    
    # Executar análise
    resultado = analisar_padroes_caixa()
    
    # Salvar resultado detalhado
    caminho_resultado = 'data/originais/cxs/analise_detalhada_caixa.json'
    
    with open(caminho_resultado, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise detalhada salva em: {caminho_resultado}")
    
    # Mostrar resumo dos padrões
    print("\n📊 PADRÕES IDENTIFICADOS:")
    print(f"   📄 Abas numéricas: {resultado['padroes_identificados']['abas_numericas']}")
    print(f"   📄 Abas especiais: {resultado['padroes_identificados']['abas_especiais']}")
    
    print("\n📋 AMOSTRA DE DADOS POR LOJA:")
    for nome_loja, dados_loja in resultado['analise_detalhada'].items():
        print(f"\n   🏪 {nome_loja}:")
        for nome_aba, dados_aba in dados_loja['abas'].items():
            if 'estrutura' in dados_aba:
                print(f"      📄 {nome_aba}: {dados_aba['estrutura']['linhas_com_dados']} linhas, {dados_aba['estrutura']['colunas_com_dados']} colunas, tipo: {dados_aba.get('tipo_dados', 'N/A')}")
                
                # Mostrar primeira linha de dados
                if dados_aba.get('dados_amostra'):
                    primeira_linha = dados_aba['dados_amostra'][0]
                    print(f"         Primeira linha: {primeira_linha[:5]}...")
    
    print("\n✅ Análise detalhada concluída!")
    return resultado

if __name__ == "__main__":
    main()