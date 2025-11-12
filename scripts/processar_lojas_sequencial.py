#!/usr/bin/env python3
"""
Script para extração sequencial por loja
Sistema Carne Fácil - Análise loja por loja
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

def is_linha_dados_valida(registro):
    """Verifica se uma linha contém dados válidos"""
    # Palavras que indicam cabeçalhos
    palavras_cabecalho = [
        'nº venda', 'numero venda', 'cliente', 'forma de pgto', 'valor venda', 'entrada',
        'os', 'vendedor', 'carnê', 'carne', 'valor parcela', 'nº parcela', 'parcelas', 'valor total',
        'restante de entrada', 'recebimento', 'entrega', 'entregues no dia'
    ]
    
    # Verificar campos principais
    campos_principais = ['nn_venda', 'os', 'cliente']
    
    for campo in campos_principais:
        valor = str(registro.get(campo, '')).lower()
        if valor and valor.strip():
            # Se contém palavra de cabeçalho, não é dados válidos
            if any(palavra in valor for palavra in palavras_cabecalho):
                return False
            # Se não é vazio e não é cabeçalho, provavelmente é dados válidos
            return True
    
    return False

def extrair_dados_estrutura_por_loja(worksheet, config_estrutura, data_movimento, loja_normalizada, arquivo_origem, aba):
    """Extrai dados de uma estrutura específica"""
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
                
                # Normalizar nome da coluna
                nome_normalizado = nome_coluna.lower().replace(' ', '_').replace('º', 'n').replace('ª', 'a')
                nome_normalizado = re.sub(r'[^a-z0-9_]', '', nome_normalizado)
                
                registro[nome_normalizado] = valor
            
            # Validar se é uma linha de dados válida
            if is_linha_dados_valida(registro):
                registros.append(registro)
    
    except Exception as e:
        print(f"   ⚠️  Erro ao extrair estrutura {config_estrutura['nome']}: {str(e)}")
    
    return registros

def processar_loja_completa(nome_loja, caminho_loja):
    """
    Processa todos os arquivos de uma loja específica
    """
    print(f"\n🏪 PROCESSANDO LOJA: {nome_loja}")
    print("=" * 50)
    
    if not os.path.exists(caminho_loja):
        print(f"❌ Pasta não encontrada: {caminho_loja}")
        return None
    
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
    
    resultado_loja = {
        'loja': nome_loja,
        'caminho': caminho_loja,
        'arquivos_processados': 0,
        'total_registros': 0,
        'registros_por_estrutura': {},
        'todos_registros': [],
        'arquivos_com_erro': [],
        'resumo_mensal': {}
    }
    
    # Buscar arquivos Excel
    arquivos_excel = []
    for root, dirs, files in os.walk(caminho_loja):
        for file in files:
            if file.endswith('.xlsx') and not file.startswith('~$'):
                arquivos_excel.append(os.path.join(root, file))
    
    arquivos_teste = sorted(arquivos_excel)[-2:]  # Últimos 2 arquivos para teste
    print(f"📊 Encontrados {len(arquivos_excel)} arquivos Excel")
    print(f"📋 Processando {len(arquivos_teste)} arquivos de teste: {[os.path.basename(f) for f in arquivos_teste]}")
    
    for caminho_arquivo in arquivos_teste:
        nome_arquivo = os.path.basename(caminho_arquivo)
        print(f"\n📄 Processando: {nome_arquivo}")
        
        try:
            workbook = openpyxl.load_workbook(caminho_arquivo, data_only=True)
            
            # Analisar apenas abas numéricas (01-31)
            abas_numericas = [nome for nome in workbook.sheetnames if nome.isdigit() and 1 <= int(nome) <= 31]
            print(f"   📅 Abas encontradas: {len(abas_numericas)}")
            
            registros_arquivo = 0
            
            for nome_aba in abas_numericas[:5]:  # Primeiras 5 abas para teste
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
                        registros_estrutura = extrair_dados_estrutura_por_loja(
                            worksheet, config, data_movimento, loja_normalizada, 
                            nome_arquivo, nome_aba
                        )
                        
                        if registros_estrutura:
                            if nome_estrutura not in resultado_loja['registros_por_estrutura']:
                                resultado_loja['registros_por_estrutura'][nome_estrutura] = []
                            
                            resultado_loja['registros_por_estrutura'][nome_estrutura].extend(registros_estrutura)
                            resultado_loja['todos_registros'].extend(registros_estrutura)
                            registros_arquivo += len(registros_estrutura)
                
                except Exception as e:
                    print(f"   ❌ Erro na aba {nome_aba}: {str(e)}")
            
            workbook.close()
            print(f"   ✅ {registros_arquivo} registros extraídos")
            resultado_loja['arquivos_processados'] += 1
            
        except Exception as e:
            print(f"   ❌ Erro no arquivo {nome_arquivo}: {str(e)}")
            resultado_loja['arquivos_com_erro'].append({
                'arquivo': nome_arquivo,
                'erro': str(e)
            })
    
    resultado_loja['total_registros'] = len(resultado_loja['todos_registros'])
    
    # Salvar dados da loja
    if resultado_loja['todos_registros']:
        # Criar CSV por loja
        df_loja = pd.DataFrame(resultado_loja['todos_registros'])
        caminho_csv = f'data/originais/cxs/dados_loja_{nome_loja.lower()}.csv'
        os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
        df_loja.to_csv(caminho_csv, index=False, encoding='utf-8')
        print(f"💾 Dados da loja salvos em: {caminho_csv}")
        
        # Salvar JSON detalhado
        caminho_json = f'data/originais/cxs/analise_loja_{nome_loja.lower()}.json'
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(resultado_loja, f, indent=2, ensure_ascii=False)
        print(f"💾 Análise detalhada salva em: {caminho_json}")
    
    # Mostrar resumo da loja
    print(f"\n📊 RESUMO DA LOJA {nome_loja}:")
    print(f"   📁 Arquivos processados: {resultado_loja['arquivos_processados']}")
    print(f"   📋 Total de registros: {resultado_loja['total_registros']}")
    print(f"   ❌ Arquivos com erro: {len(resultado_loja['arquivos_com_erro'])}")
    
    if resultado_loja['registros_por_estrutura']:
        print(f"   📈 Registros por estrutura:")
        for estrutura, registros in resultado_loja['registros_por_estrutura'].items():
            print(f"      • {estrutura}: {len(registros)}")
    
    return resultado_loja

def main():
    """Função principal - processar loja por loja"""
    print("🚀 EXTRAÇÃO SEQUENCIAL POR LOJA")
    print("=" * 60)
    
    # Definir lojas
    lojas_caminhos = [
        ("MAUA", "D:/OneDrive - Óticas Taty Mello/LOJAS/MAUA/CAIXA"),
        ("PERUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/PERUS/CAIXA"),
        ("RIO_PEQUENO", "D:/OneDrive - Óticas Taty Mello/LOJAS/RIO_PEQUENO/CAIXA"),
        ("SAO_MATEUS", "D:/OneDrive - Óticas Taty Mello/LOJAS/SAO_MATEUS/CAIXA"),
        ("SUZANO", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO/CAIXA"),
        ("SUZANO2", "D:/OneDrive - Óticas Taty Mello/LOJAS/SUZANO2/CAIXA")
    ]
    
    resultados_todas_lojas = {
        'data_processamento': datetime.now().isoformat(),
        'lojas_processadas': {},
        'resumo_geral': {
            'total_lojas': 0,
            'total_arquivos': 0,
            'total_registros': 0,
            'estruturas_encontradas': set()
        }
    }
    
    # Processar cada loja individualmente
    for nome_loja, caminho_loja in lojas_caminhos:
        resultado_loja = processar_loja_completa(nome_loja, caminho_loja)
        
        if resultado_loja:
            resultados_todas_lojas['lojas_processadas'][nome_loja] = resultado_loja
            resultados_todas_lojas['resumo_geral']['total_lojas'] += 1
            resultados_todas_lojas['resumo_geral']['total_arquivos'] += resultado_loja['arquivos_processados']
            resultados_todas_lojas['resumo_geral']['total_registros'] += resultado_loja['total_registros']
            
            # Coletar estruturas encontradas
            for estrutura in resultado_loja['registros_por_estrutura'].keys():
                resultados_todas_lojas['resumo_geral']['estruturas_encontradas'].add(estrutura)
    
    # Converter set para lista para JSON
    resultados_todas_lojas['resumo_geral']['estruturas_encontradas'] = list(resultados_todas_lojas['resumo_geral']['estruturas_encontradas'])
    
    # Salvar resumo geral
    caminho_resumo = 'data/originais/cxs/resumo_extracao_por_lojas.json'
    with open(caminho_resumo, 'w', encoding='utf-8') as f:
        json.dump(resultados_todas_lojas, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resumo geral salvo em: {caminho_resumo}")
    
    # Mostrar resumo final
    print(f"\n🎯 RESUMO FINAL:")
    print(f"   🏪 Lojas processadas: {resultados_todas_lojas['resumo_geral']['total_lojas']}")
    print(f"   📁 Total de arquivos: {resultados_todas_lojas['resumo_geral']['total_arquivos']}")
    print(f"   📋 Total de registros: {resultados_todas_lojas['resumo_geral']['total_registros']}")
    print(f"   📊 Estruturas encontradas: {', '.join(resultados_todas_lojas['resumo_geral']['estruturas_encontradas'])}")
    
    print("\n✅ Processamento por lojas concluído!")

if __name__ == "__main__":
    main()