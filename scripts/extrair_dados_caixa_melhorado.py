#!/usr/bin/env python3
"""
Script melhorado para extração de dados de caixa
Sistema Carne Fácil - Extração corrigida e normalizada
"""

import pandas as pd
import openpyxl
from pathlib import Path
import json
from datetime import datetime
import os
import warnings
import re
warnings.filterwarnings('ignore')

def extrair_valor_celula(worksheet, celula):
    """Extrai valor de uma célula específica"""
    try:
        valor = worksheet[celula].value
        if valor is None:
            return ""
        if isinstance(valor, datetime):
            return valor.strftime('%Y-%m-%d')
        return str(valor).strip()
    except Exception:
        return ""

def normalizar_loja(nome_loja):
    """Normaliza nome da loja"""
    if not nome_loja:
        return ""
    
    nome_limpo = str(nome_loja).upper().strip()
    
    # Mapeamento de nomes conhecidos
    mapeamento = {
        'MAUÁ': 'MAUA',
        'MAUA': 'MAUA',
        'PERUS': 'PERUS',
        'RIO PEQUENO': 'RIO_PEQUENO',
        'SAO MATEUS': 'SAO_MATEUS',
        'SUZANO 1': 'SUZANO',
        'SUZANO': 'SUZANO',
        'SUZANO 2': 'SUZANO2',
        'SUZANO2': 'SUZANO2'
    }
    
    for original, normalizado in mapeamento.items():
        if original in nome_limpo:
            return normalizado
    
    return nome_limpo

def is_valor_numerico(valor):
    """Verifica se um valor pode ser convertido para número"""
    if not valor or str(valor).strip() == "":
        return False
    try:
        float(str(valor).replace(',', '.'))
        return True
    except:
        return False

def is_linha_cabecalho(registro):
    """
    Identifica se uma linha é cabeçalho baseado no conteúdo
    """
    # Verificar se contém palavras típicas de cabeçalho
    cabecalhos_tipicos = [
        'nº venda', 'numero venda', 'cliente', 'forma de pgto', 'valor venda', 'entrada',
        'os', 'vendedor', 'carnê', 'carne', 'valor parcela', 'nº parcela', 'parcelas', 'valor total',
        'restante de entrada', 'recebimento', 'entrega', 'entregues no dia'
    ]
    
    # Verificar valores das colunas principais
    valores_para_verificar = [
        registro.get('nn_venda', ''),
        registro.get('cliente', ''),
        registro.get('os', ''),
        registro.get('vendedor', '')
    ]
    
    for valor in valores_para_verificar:
        valor_lower = str(valor).lower()
        for cabecalho in cabecalhos_tipicos:
            if cabecalho in valor_lower:
                return True
    
    return False

def is_linha_dados_valida(registro):
    """
    Verifica se uma linha contém dados válidos (não é cabeçalho nem linha vazia)
    """
    if is_linha_cabecalho(registro):
        return False
    
    # Verificar se tem pelo menos um campo principal preenchido
    campos_principais = ['nn_venda', 'os', 'cliente', 'valor_venda', 'valor_parcela', 'valor_total']
    
    for campo in campos_principais:
        valor = registro.get(campo, '')
        if valor and str(valor).strip() and str(valor).strip() != "":
            # Se for um dos campos de valor, verificar se é numérico
            if 'valor' in campo:
                if is_valor_numerico(valor):
                    return True
            else:
                # Para outros campos, aceitar se não é palavra de cabeçalho
                if not any(palavra in str(valor).lower() for palavra in ['cliente', 'venda', 'parcela', 'total', 'forma']):
                    return True
    
    return False

def extrair_dados_estrutura_melhorado(worksheet, config_estrutura, data_movimento, loja_normalizada, arquivo_origem, aba):
    """
    Extrai dados de uma estrutura específica com validação melhorada
    """
    registros = []
    
    try:
        celula_inicio = config_estrutura['celula_inicio']
        linha_inicio = int(re.findall(r'\d+', celula_inicio)[0])
        coluna_inicio_letra = re.findall(r'[A-Z]+', celula_inicio)[0]
        
        # Verificar se a estrutura existe
        valor_cabecalho = extrair_valor_celula(worksheet, celula_inicio)
        if not valor_cabecalho or config_estrutura['titulo_esperado'].lower() not in valor_cabecalho.lower():
            return registros
        
        # Extrair dados linha por linha
        for linha_offset in range(1, 21):  # Máximo 20 linhas
            linha_atual = linha_inicio + linha_offset
            primeira_coluna = f"{coluna_inicio_letra}{linha_atual}"
            valor_primeira = extrair_valor_celula(worksheet, primeira_coluna)
            
            if not valor_primeira or valor_primeira.strip() == "":
                continue
                
            # Extrair dados de todas as colunas
            registro = {
                'data_movimento': data_movimento,
                'loja': loja_normalizada,
                'arquivo_origem': arquivo_origem,
                'aba': aba,
                'tipo_estrutura': config_estrutura['nome'],
                'linha_arquivo': linha_atual
            }
            
            # Mapear cada coluna
            for i, nome_coluna in enumerate(config_estrutura['colunas']):
                col_letra = chr(ord(coluna_inicio_letra) + i)
                celula_dados = f"{col_letra}{linha_atual}"
                valor = extrair_valor_celula(worksheet, celula_dados)
                
                # Normalizar nome da coluna para o banco
                nome_normalizado = nome_coluna.lower().replace(' ', '_').replace('º', 'n').replace('ª', 'a')
                nome_normalizado = re.sub(r'[^a-z0-9_]', '', nome_normalizado)
                
                registro[nome_normalizado] = valor
            
            # Validar se é uma linha de dados válida
            if is_linha_dados_valida(registro):
                registros.append(registro)
            
            # Se encontramos muitas linhas consecutivas inválidas, parar
            if linha_offset > 5 and len(registros) == 0:
                break
    
    except Exception as e:
        print(f"   ⚠️  Erro ao extrair estrutura {config_estrutura['nome']}: {str(e)}")
    
    return registros

def extrair_dados_arquivo_caixa_melhorado(caminho_arquivo):
    """
    Extrai todos os dados de um arquivo de caixa com validação melhorada
    """
    resultado = {
        'arquivo': os.path.basename(caminho_arquivo),
        'caminho_completo': caminho_arquivo,
        'total_registros': 0,
        'registros_por_estrutura': {},
        'todos_registros': [],
        'erro': None
    }
    
    # Configurações das estruturas
    estruturas_caixa = {
        'VENDAS': {
            'nome': 'VENDAS',
            'celula_inicio': 'E5',
            'titulo_esperado': 'Nº Venda',
            'colunas': ['Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada']
        },
        'RESTANTE_ENTRADA': {
            'nome': 'RESTANTE_ENTRADA', 
            'celula_inicio': 'E25',
            'titulo_esperado': 'Nº Venda',
            'colunas': ['Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada']
        },
        'RECEBIMENTO_CARNE': {
            'nome': 'RECEBIMENTO_CARNE',
            'celula_inicio': 'E34',
            'titulo_esperado': 'OS',
            'colunas': ['OS', 'Cliente', 'Forma de Pgto', 'Valor Parcela', 'Nº Parcela']
        },
        'OS_ENTREGUES_DIA': {
            'nome': 'OS_ENTREGUES_DIA',
            'celula_inicio': 'K14',
            'titulo_esperado': 'OS',
            'colunas': ['OS', 'Vendedor', 'CARNÊ']
        },
        'ENTREGA_CARNE': {
            'nome': 'ENTREGA_CARNE',
            'celula_inicio': 'K34',
            'titulo_esperado': 'OS',
            'colunas': ['OS', 'Parcelas', 'Valor Total']
        }
    }
    
    try:
        workbook = openpyxl.load_workbook(caminho_arquivo, data_only=True)
        
        # Analisar apenas abas numéricas (01-31)
        abas_numericas = [nome for nome in workbook.sheetnames if nome.isdigit() and 1 <= int(nome) <= 31]
        
        for nome_aba in abas_numericas:
            try:
                worksheet = workbook[nome_aba]
                
                # Extrair data e loja
                data_movimento = extrair_valor_celula(worksheet, 'B1')
                loja_extraida = extrair_valor_celula(worksheet, 'L1')
                loja_normalizada = normalizar_loja(loja_extraida)
                
                if not data_movimento:
                    continue
                
                # Processar cada estrutura
                for nome_estrutura, config in estruturas_caixa.items():
                    registros_estrutura = extrair_dados_estrutura_melhorado(
                        worksheet, config, data_movimento, loja_normalizada, 
                        os.path.basename(caminho_arquivo), nome_aba
                    )
                    
                    if registros_estrutura:
                        if nome_estrutura not in resultado['registros_por_estrutura']:
                            resultado['registros_por_estrutura'][nome_estrutura] = []
                        
                        resultado['registros_por_estrutura'][nome_estrutura].extend(registros_estrutura)
                        resultado['todos_registros'].extend(registros_estrutura)
                
            except Exception as e:
                print(f"   ❌ Erro na aba {nome_aba}: {str(e)}")
        
        workbook.close()
        
        resultado['total_registros'] = len(resultado['todos_registros'])
        
    except Exception as e:
        resultado['erro'] = str(e)
        print(f"   ❌ Erro no arquivo: {str(e)}")
    
    return resultado

def main():
    """Função principal para teste em arquivo único"""
    print("🚀 TESTE DE EXTRAÇÃO MELHORADA - ARQUIVO ÚNICO")
    print("=" * 60)
    
    # Testar com um arquivo específico
    arquivo_teste = "D:/OneDrive - Óticas Taty Mello/LOJAS/MAUA/CAIXA/jan_25.xlsx"
    
    if not os.path.exists(arquivo_teste):
        print(f"❌ Arquivo não encontrado: {arquivo_teste}")
        return
    
    resultado = extrair_dados_arquivo_caixa_melhorado(arquivo_teste)
    
    # Filtrar apenas registros válidos
    registros_validos = [r for r in resultado['todos_registros'] if is_linha_dados_valida(r)]
    
    print(f"\n📊 RESUMO:")
    print(f"   📄 Arquivo: {resultado['arquivo']}")
    print(f"   📋 Total extraído: {resultado['total_registros']}")
    print(f"   ✅ Registros válidos: {len(registros_validos)}")
    
    if registros_validos:
        # Salvar apenas registros válidos
        df_validos = pd.DataFrame(registros_validos)
        caminho_csv = 'data/originais/cxs/teste_extracao_melhorada.csv'
        df_validos.to_csv(caminho_csv, index=False, encoding='utf-8')
        print(f"💾 Teste salvo em: {caminho_csv}")
        
        # Mostrar amostra
        print(f"\n📋 AMOSTRA DOS DADOS VÁLIDOS:")
        for i, registro in enumerate(registros_validos[:5]):
            print(f"   {i+1}. {registro['tipo_estrutura']}: {registro.get('nn_venda', registro.get('os', 'N/A'))} - {registro.get('cliente', 'N/A')}")

if __name__ == "__main__":
    main()