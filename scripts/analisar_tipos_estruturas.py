#!/usr/bin/env python3
"""
Script para análise dos tipos de estruturas de caixa
Sistema Carne Fácil - Análise por tipos de movimentação
"""

import pandas as pd
import json
from datetime import datetime
import os
import re

def analisar_tipos_estruturas():
    """
    Analisa todos os tipos de estruturas extraídas das lojas
    """
    print("🔍 ANÁLISE DOS TIPOS DE ESTRUTURAS DE CAIXA")
    print("=" * 60)
    
    # Carregar dados de todas as lojas
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    resultado_analise = {
        'data_analise': datetime.now().isoformat(),
        'estruturas_analisadas': {},
        'resumo_por_tipo': {},
        'padroes_identificados': {},
        'problemas_encontrados': []
    }
    
    todos_registros = []
    
    # Carregar dados de cada loja
    for loja in lojas:
        caminho_csv = f'data/originais/cxs/dados_loja_{loja}.csv'
        
        if os.path.exists(caminho_csv):
            print(f"📊 Carregando dados da loja: {loja.upper()}")
            try:
                df = pd.read_csv(caminho_csv)
                print(f"   ✅ {len(df)} registros carregados")
                todos_registros.extend(df.to_dict('records'))
            except Exception as e:
                print(f"   ❌ Erro ao carregar {loja}: {str(e)}")
        else:
            print(f"   ⚠️  Arquivo não encontrado: {caminho_csv}")
    
    if not todos_registros:
        print("❌ Nenhum registro encontrado!")
        return
    
    print(f"\n📋 Total de registros carregados: {len(todos_registros)}")
    
    # Analisar cada tipo de estrutura
    tipos_estrutura = {}
    
    for registro in todos_registros:
        tipo = registro.get('tipo_estrutura', 'INDEFINIDO')
        
        if tipo not in tipos_estrutura:
            tipos_estrutura[tipo] = {
                'total_registros': 0,
                'lojas_encontradas': set(),
                'campos_utilizados': set(),
                'amostra_registros': [],
                'valores_exemplo': {},
                'problemas_identificados': []
            }
        
        tipos_estrutura[tipo]['total_registros'] += 1
        
        # Tratar valores NaN para loja
        loja_valor = registro.get('loja', '')
        if pd.isna(loja_valor) or loja_valor == '' or str(loja_valor).lower() == 'nan':
            loja_valor = 'INDEFINIDA'
        
        tipos_estrutura[tipo]['lojas_encontradas'].add(str(loja_valor))
        
        # Coletar campos utilizados
        for campo, valor in registro.items():
            if campo not in ['data_movimento', 'loja', 'arquivo_origem', 'aba', 'tipo_estrutura', 'linha_arquivo']:
                # Verificar se valor não é NaN ou vazio
                if not pd.isna(valor) and valor and str(valor).strip() and str(valor).lower() != 'nan':
                    tipos_estrutura[tipo]['campos_utilizados'].add(campo)
                    
                    # Guardar exemplos de valores
                    if campo not in tipos_estrutura[tipo]['valores_exemplo']:
                        tipos_estrutura[tipo]['valores_exemplo'][campo] = []
                    
                    if len(tipos_estrutura[tipo]['valores_exemplo'][campo]) < 5:
                        tipos_estrutura[tipo]['valores_exemplo'][campo].append(str(valor))
        
        # Guardar amostra de registros
        if len(tipos_estrutura[tipo]['amostra_registros']) < 3:
            tipos_estrutura[tipo]['amostra_registros'].append(registro)
    
    # Processar resultados
    for tipo, dados in tipos_estrutura.items():
        # Converter sets para listas
        dados['lojas_encontradas'] = sorted(list(dados['lojas_encontradas']))
        dados['campos_utilizados'] = sorted(list(dados['campos_utilizados']))
        
        # Analisar padrões específicos
        resultado_analise['estruturas_analisadas'][tipo] = dados
        
        print(f"\n📊 ESTRUTURA: {tipo}")
        print(f"   📈 Total de registros: {dados['total_registros']}")
        print(f"   🏪 Lojas: {', '.join(dados['lojas_encontradas'])}")
        print(f"   📋 Campos utilizados: {', '.join(dados['campos_utilizados'])}")
        
        # Mostrar amostra
        if dados['amostra_registros']:
            print(f"   🔍 Amostra de dados:")
            for i, amostra in enumerate(dados['amostra_registros'][:2], 1):
                principais = []
                
                if amostra.get('nn_venda') and not pd.isna(amostra['nn_venda']):
                    principais.append(f"Venda: {amostra['nn_venda']}")
                    
                if amostra.get('os') and not pd.isna(amostra['os']):
                    principais.append(f"OS: {amostra['os']}")
                    
                if amostra.get('cliente') and not pd.isna(amostra['cliente']):
                    cliente_str = str(amostra['cliente'])
                    principais.append(f"Cliente: {cliente_str[:30]}...")
                    
                if amostra.get('valor_venda') and not pd.isna(amostra['valor_venda']):
                    principais.append(f"Valor: {amostra['valor_venda']}")
                    
                if amostra.get('valor_parcela') and not pd.isna(amostra['valor_parcela']):
                    principais.append(f"Parcela: {amostra['valor_parcela']}")
                
                if principais:
                    print(f"      {i}. {' | '.join(principais)}")
                else:
                    print(f"      {i}. (dados não disponíveis)")
    
    # Identificar padrões gerais
    print(f"\n🎯 PADRÕES IDENTIFICADOS:")
    
    # 1. Estruturas financeiras (com valores)
    estruturas_financeiras = []
    for tipo, dados in tipos_estrutura.items():
        campos = dados['campos_utilizados']
        if any(campo in campos for campo in ['valor_venda', 'valor_parcela', 'valor_total', 'entrada']):
            estruturas_financeiras.append(tipo)
    
    print(f"   💰 Estruturas financeiras: {', '.join(estruturas_financeiras)}")
    
    # 2. Estruturas operacionais (sem valores financeiros)
    estruturas_operacionais = []
    for tipo, dados in tipos_estrutura.items():
        if tipo not in estruturas_financeiras:
            estruturas_operacionais.append(tipo)
    
    print(f"   🔧 Estruturas operacionais: {', '.join(estruturas_operacionais)}")
    
    # 3. Campos mais utilizados
    todos_campos = {}
    for tipo, dados in tipos_estrutura.items():
        for campo in dados['campos_utilizados']:
            if campo not in todos_campos:
                todos_campos[campo] = 0
            todos_campos[campo] += dados['total_registros']
    
    campos_principais = sorted(todos_campos.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"   📊 Campos mais utilizados:")
    for campo, uso in campos_principais:
        print(f"      • {campo}: usado em {uso} registros")
    
    # Salvar análise completa
    # Converter sets para listas para JSON
    resultado_json = {}
    for tipo, dados in resultado_analise['estruturas_analisadas'].items():
        resultado_json[tipo] = {
            'total_registros': dados['total_registros'],
            'lojas_encontradas': dados['lojas_encontradas'],
            'campos_utilizados': dados['campos_utilizados'],
            'valores_exemplo': dados['valores_exemplo'],
            'amostra_registros': dados['amostra_registros'][:2]  # Limitar amostra
        }
    
    resultado_analise['estruturas_analisadas'] = resultado_json
    resultado_analise['resumo_por_tipo'] = {
        'estruturas_financeiras': estruturas_financeiras,
        'estruturas_operacionais': estruturas_operacionais,
        'campos_principais': dict(campos_principais)
    }
    
    caminho_analise = 'data/originais/cxs/analise_tipos_estruturas.json'
    with open(caminho_analise, 'w', encoding='utf-8') as f:
        json.dump(resultado_analise, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise de tipos salva em: {caminho_analise}")
    
    # Criar resumo para normalização
    print(f"\n📋 PRÓXIMOS PASSOS PARA NORMALIZAÇÃO:")
    print(f"   1. 💰 Estruturas VENDAS + RESTANTE_ENTRADA → Tabela de vendas/entradas")
    print(f"   2. 📦 Estrutura RECEBIMENTO_CARNE → Tabela de recebimentos de parcelas")
    print(f"   3. 🚚 Estrutura OS_ENTREGUES_DIA → Tabela de entregas")
    print(f"   4. 📋 Estrutura ENTREGA_CARNE → Tabela de controle de carnês")
    
    return resultado_analise

def criar_mapeamento_normalizacao():
    """
    Cria mapeamento para normalização das estruturas
    """
    print(f"\n🔄 CRIANDO MAPEAMENTO PARA NORMALIZAÇÃO...")
    
    mapeamento = {
        'tabelas_destino': {
            'movimentacoes_financeiras': {
                'estruturas_origem': ['VENDAS', 'RESTANTE_ENTRADA'],
                'campos_principais': ['nn_venda', 'cliente', 'forma_de_pgto', 'valor_venda', 'entrada'],
                'tipo_movimento': 'ENTRADA'
            },
            'recebimentos_parcelas': {
                'estruturas_origem': ['RECEBIMENTO_CARNE'],
                'campos_principais': ['os', 'cliente', 'forma_de_pgto', 'valor_parcela', 'nn_parcela'],
                'tipo_movimento': 'RECEBIMENTO'
            },
            'entregas_os': {
                'estruturas_origem': ['OS_ENTREGUES_DIA'],
                'campos_principais': ['os', 'vendedor', 'carn'],
                'tipo_movimento': 'ENTREGA'
            },
            'controle_carnes': {
                'estruturas_origem': ['ENTREGA_CARNE'],
                'campos_principais': ['os', 'parcelas', 'valor_total'],
                'tipo_movimento': 'CONTROLE'
            }
        },
        'campos_comuns': {
            'data_movimento': 'data do movimento extraída de B1',
            'loja': 'loja normalizada extraída de L1',
            'arquivo_origem': 'arquivo Excel de origem',
            'aba': 'aba do dia (01-31)',
            'linha_arquivo': 'linha no arquivo Excel'
        }
    }
    
    caminho_mapeamento = 'data/originais/cxs/mapeamento_normalizacao.json'
    with open(caminho_mapeamento, 'w', encoding='utf-8') as f:
        json.dump(mapeamento, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Mapeamento salvo em: {caminho_mapeamento}")
    
    return mapeamento

def main():
    """Função principal"""
    resultado = analisar_tipos_estruturas()
    mapeamento = criar_mapeamento_normalizacao()
    
    print(f"\n✅ Análise por tipos concluída!")
    print(f"📋 Próximo passo: Executar normalização baseada no mapeamento criado")

if __name__ == "__main__":
    main()