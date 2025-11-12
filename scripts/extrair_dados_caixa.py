#!/usr/bin/env python3
"""
Script para extração completa dos dados de caixa com estruturas dinâmicas
Sistema Carne Fácil - Extração de dados normalizados
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

def extrair_dados_estrutura(worksheet, config_estrutura, data_movimento, loja_normalizada, arquivo_origem, aba):
    """
    Extrai dados de uma estrutura específica (VENDAS, RECEBIMENTO_CARNE, etc.)
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
            
            registros.append(registro)
            
            # Se encontramos uma linha vazia após ter dados, parar
            if not any(registro[col] for col in registro if col not in ['data_movimento', 'loja', 'arquivo_origem', 'aba', 'tipo_estrutura', 'linha_arquivo']):
                break
    
    except Exception as e:
        print(f"   ⚠️  Erro ao extrair estrutura {config_estrutura['nome']}: {str(e)}")
    
    return registros

def extrair_dados_arquivo_caixa(caminho_arquivo):
    """
    Extrai todos os dados de um arquivo de caixa
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
        
        print(f"   📊 Processando {len(abas_numericas)} abas: {abas_numericas[:5]}{'...' if len(abas_numericas) > 5 else ''}")
        
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
                    registros_estrutura = extrair_dados_estrutura(
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

def extrair_todos_dados_caixa():
    """
    Extrai dados de todos os arquivos de caixa
    """
    
    # Definir lojas e seus caminhos
    lojas_caminhos = [
        ("MAUA", "D:/OneDrive - Óticas Taty Mello/LOJAS/MAUA/CAIXA"),
        ("PERUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/PERUS/CAIXA"),
        ("RIO_PEQUENO", "D:/OneDrive - Óticas Taty Mello/LOJAS/RIO_PEQUENO/CAIXA"),
        ("SAO_MATEUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/SAO_MATEUS/CAIXA"),
        ("SUZANO", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO/CAIXA"),
        ("SUZANO2", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO2/CAIXA")
    ]
    
    resultado_geral = {
        'data_extracao': datetime.now().isoformat(),
        'total_arquivos_processados': 0,
        'total_registros_extraidos': 0,
        'dados_por_loja': {},
        'todos_registros': [],
        'resumo_por_estrutura': {},
        'arquivos_com_erro': []
    }
    
    print("🚀 EXTRAÇÃO COMPLETA DOS DADOS DE CAIXA")
    print("=" * 60)
    
    for nome_loja, caminho_loja in lojas_caminhos:
        if not os.path.exists(caminho_loja):
            print(f"⚠️  Pasta não encontrada: {caminho_loja}")
            continue
        
        print(f"\n📁 Processando loja: {nome_loja}")
        
        # Buscar arquivos Excel (limitando para teste)
        arquivos_excel = []
        for root, dirs, files in os.walk(caminho_loja):
            for file in files:
                if file.endswith('.xlsx') and not file.startswith('~$'):
                    arquivos_excel.append(os.path.join(root, file))
        
        # Processar apenas alguns arquivos para teste
        arquivos_teste = sorted(arquivos_excel)[-3:]  # Últimos 3 arquivos
        print(f"   📊 Processando {len(arquivos_teste)} arquivos de teste")
        
        resultado_geral['dados_por_loja'][nome_loja] = {
            'total_arquivos': len(arquivos_excel),
            'arquivos_processados': len(arquivos_teste),
            'registros_extraidos': 0,
            'arquivos': {}
        }
        
        for caminho_arquivo in arquivos_teste:
            nome_arquivo = os.path.basename(caminho_arquivo)
            print(f"   📄 Processando: {nome_arquivo}")
            
            resultado_arquivo = extrair_dados_arquivo_caixa(caminho_arquivo)
            resultado_geral['dados_por_loja'][nome_loja]['arquivos'][nome_arquivo] = resultado_arquivo
            
            if resultado_arquivo.get('erro'):
                resultado_geral['arquivos_com_erro'].append({
                    'loja': nome_loja,
                    'arquivo': nome_arquivo,
                    'erro': resultado_arquivo['erro']
                })
            else:
                registros = resultado_arquivo.get('todos_registros', [])
                resultado_geral['dados_por_loja'][nome_loja]['registros_extraidos'] += len(registros)
                resultado_geral['todos_registros'].extend(registros)
                
                print(f"      ✅ {len(registros)} registros extraídos")
        
        resultado_geral['total_arquivos_processados'] += len(arquivos_teste)
    
    # Compilar resumo por estrutura
    for registro in resultado_geral['todos_registros']:
        tipo_estrutura = registro.get('tipo_estrutura', 'INDEFINIDO')
        if tipo_estrutura not in resultado_geral['resumo_por_estrutura']:
            resultado_geral['resumo_por_estrutura'][tipo_estrutura] = 0
        resultado_geral['resumo_por_estrutura'][tipo_estrutura] += 1
    
    resultado_geral['total_registros_extraidos'] = len(resultado_geral['todos_registros'])
    
    return resultado_geral

def main():
    """Função principal"""
    resultado = extrair_todos_dados_caixa()
    
    # Salvar resultado completo
    caminho_resultado = 'data/originais/cxs/dados_caixa_extraidos.json'
    os.makedirs(os.path.dirname(caminho_resultado), exist_ok=True)
    
    with open(caminho_resultado, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dados extraídos salvos em: {caminho_resultado}")
    
    # Criar CSV consolidado
    if resultado['todos_registros']:
        df_todos = pd.DataFrame(resultado['todos_registros'])
        caminho_csv = 'data/originais/cxs/movimentacoes_caixa_extraidas.csv'
        df_todos.to_csv(caminho_csv, index=False, encoding='utf-8')
        print(f"💾 CSV consolidado salvo em: {caminho_csv}")
    
    # Mostrar resumo
    print(f"\n📊 RESUMO DA EXTRAÇÃO:")
    print(f"   📁 Arquivos processados: {resultado['total_arquivos_processados']}")
    print(f"   📋 Total de registros: {resultado['total_registros_extraidos']}")
    print(f"   ❌ Arquivos com erro: {len(resultado['arquivos_com_erro'])}")
    
    print("\n📈 REGISTROS POR ESTRUTURA:")
    for estrutura, count in resultado['resumo_por_estrutura'].items():
        print(f"   • {estrutura}: {count}")
    
    print("\n📋 REGISTROS POR LOJA:")
    for loja, dados in resultado['dados_por_loja'].items():
        print(f"   🏪 {loja}: {dados['registros_extraidos']} registros")
    
    print("\n✅ Extração concluída!")
    return resultado

if __name__ == "__main__":
    main()