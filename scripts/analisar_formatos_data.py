#!/usr/bin/env python3
"""
Script para analisar formatos de data nos CSVs finais
"""

import pandas as pd
import os
from datetime import datetime

def analisar_formatos_data():
    """Analisa os formatos de data nos CSVs finais"""
    
    print("📅 ANÁLISE DE FORMATOS DE DATA NOS CSVS")
    print("=" * 50)
    
    # Diretório com arquivos finais
    dir_arquivos = 'data/originais/oss/finais_completos_com_todos_uuids'
    
    if not os.path.exists(dir_arquivos):
        print(f"❌ Diretório não encontrado: {dir_arquivos}")
        return
    
    arquivos = [f for f in os.listdir(dir_arquivos) if f.endswith('.csv')]
    
    colunas_data_encontradas = set()
    formatos_data = {}
    problemas_encontrados = []
    
    for arquivo in sorted(arquivos[:2]):  # Analisar apenas 2 arquivos para teste
        print(f"\n📄 Analisando: {arquivo}")
        
        caminho = os.path.join(dir_arquivos, arquivo)
        df = pd.read_csv(caminho, nrows=10)  # Ler apenas 10 linhas para análise
        
        # Identificar colunas que podem conter datas
        colunas_possiveis_data = []
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(palavra in col_lower for palavra in ['data', 'dt', 'date', 'nasc', 'entr', 'compra']):
                colunas_possiveis_data.append(col)
                colunas_data_encontradas.add(col)
        
        print(f"   📋 Colunas de data identificadas: {len(colunas_possiveis_data)}")
        
        for col in colunas_possiveis_data:
            print(f"\n   📊 Coluna: '{col}'")
            
            # Analisar valores únicos (primeiros 5)
            valores_unicos = df[col].dropna().unique()[:5]
            
            for valor in valores_unicos:
                valor_str = str(valor).strip()
                
                if valor_str and valor_str != 'nan':
                    print(f"      • Exemplo: '{valor_str}'")
                    
                    # Tentar identificar o formato
                    formato_identificado = identificar_formato_data(valor_str)
                    
                    if formato_identificado:
                        if col not in formatos_data:
                            formatos_data[col] = set()
                        formatos_data[col].add(formato_identificado)
                        print(f"        → Formato: {formato_identificado}")
                    else:
                        problemas_encontrados.append({
                            'arquivo': arquivo,
                            'coluna': col,
                            'valor': valor_str
                        })
                        print(f"        ⚠️  Formato não reconhecido")
    
    # Resumo geral
    print(f"\n📊 RESUMO DA ANÁLISE:")
    print(f"   • Colunas de data encontradas: {len(colunas_data_encontradas)}")
    print(f"   • Formatos identificados: {len(formatos_data)}")
    print(f"   • Problemas encontrados: {len(problemas_encontrados)}")
    
    if colunas_data_encontradas:
        print(f"\n📋 COLUNAS DE DATA IDENTIFICADAS:")
        for col in sorted(colunas_data_encontradas):
            print(f"   • '{col}'")
    
    if formatos_data:
        print(f"\n🔍 FORMATOS IDENTIFICADOS POR COLUNA:")
        for col, formatos in formatos_data.items():
            print(f"   📅 '{col}':")
            for formato in sorted(formatos):
                print(f"      → {formato}")
    
    if problemas_encontrados:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS:")
        for problema in problemas_encontrados[:5]:  # Mostrar apenas os primeiros 5
            print(f"   • {problema['arquivo']} | {problema['coluna']} | '{problema['valor']}'")
    
    # Recomendações para PostgreSQL
    print(f"\n🎯 RECOMENDAÇÕES PARA POSTGRESQL:")
    print(f"   📅 Formatos aceitos pelo PostgreSQL:")
    print(f"      • YYYY-MM-DD (ISO 8601) - RECOMENDADO")
    print(f"      • DD/MM/YYYY - Aceito com configuração")
    print(f"      • MM/DD/YYYY - Aceito com configuração")
    print(f"      • YYYY-MM-DD HH:MM:SS - Para timestamp")
    
    print(f"\n🔧 CONFIGURAÇÕES NECESSÁRIAS:")
    print(f"   • SET datestyle = 'DMY' para DD/MM/YYYY")
    print(f"   • SET datestyle = 'MDY' para MM/DD/YYYY")
    print(f"   • Ou converter para ISO antes da importação")
    
    return {
        'colunas_data': list(colunas_data_encontradas),
        'formatos': formatos_data,
        'problemas': problemas_encontrados
    }

def identificar_formato_data(valor_str):
    """Identifica o formato de uma string de data"""
    
    # Limpar o valor
    valor = valor_str.strip()
    
    # Formato numérico (Excel serial)
    if valor.isdigit() and len(valor) == 5:
        return "EXCEL_SERIAL (precisa conversão)"
    
    # Formato DD/MM/YYYY
    if '/' in valor and len(valor.split('/')) == 3:
        partes = valor.split('/')
        if len(partes[0]) <= 2 and len(partes[1]) <= 2 and len(partes[2]) == 4:
            return "DD/MM/YYYY"
        elif len(partes[0]) <= 2 and len(partes[1]) <= 2 and len(partes[2]) == 2:
            return "DD/MM/YY"
    
    # Formato YYYY-MM-DD
    if '-' in valor and len(valor.split('-')) == 3:
        partes = valor.split('-')
        if len(partes[0]) == 4 and len(partes[1]) <= 2 and len(partes[2]) <= 2:
            return "YYYY-MM-DD (ISO)"
    
    # Formato com espaços ou outros separadores
    if ' ' in valor:
        return "FORMATO_COMPLEXO (verificar)"
    
    return None

if __name__ == "__main__":
    analisar_formatos_data()