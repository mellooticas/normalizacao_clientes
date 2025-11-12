#!/usr/bin/env python3
"""
Análise de Origens - Trans Financ
Extrai todas as origens únicas da coluna 'Origem' de todos os arquivos trans_financ
"""

import pandas as pd
import os
from pathlib import Path
from collections import defaultdict
import json

def analisar_origens_trans_financ():
    """Analisa todas as origens dos arquivos trans_financ"""
    
    print("📊 ANÁLISE ORIGENS - TRANS FINANC")
    print("=" * 50)
    
    # Pasta dos arquivos
    pasta_trans = Path("data/originais/controles_gerais/trans_financ")
    
    # Estruturas para coleta
    origens_globais = set()
    origens_por_arquivo = {}
    estatisticas_arquivos = {}
    arquivos_processados = 0
    arquivos_com_erro = []
    
    # Processar todos os arquivos CSV
    for arquivo in sorted(pasta_trans.glob("*.csv")):
        print(f"\n📄 Processando: {arquivo.name}")
        
        try:
            # Ler arquivo
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Verificar se tem coluna Origem
            if 'Origem' not in df.columns:
                print(f"   ⚠️ Arquivo sem coluna 'Origem': {arquivo.name}")
                continue
            
            # Limpar e extrair origens
            origens_arquivo = set()
            origem_counts = defaultdict(int)
            
            for origem in df['Origem'].dropna():
                origem_limpa = str(origem).strip()
                if origem_limpa:
                    origens_arquivo.add(origem_limpa)
                    origens_globais.add(origem_limpa)
                    origem_counts[origem_limpa] += 1
            
            # Estatísticas do arquivo
            estatisticas_arquivos[arquivo.name] = {
                'total_registros': len(df),
                'registros_com_origem': len(df[df['Origem'].notna()]),
                'origens_unicas': len(origens_arquivo),
                'origens_mais_frequentes': dict(sorted(origem_counts.items(), 
                                                     key=lambda x: x[1], reverse=True)[:5])
            }
            
            origens_por_arquivo[arquivo.name] = sorted(list(origens_arquivo))
            arquivos_processados += 1
            
            print(f"   ✅ {len(df):,} registros | {len(origens_arquivo)} origens únicas")
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {arquivo.name}: {e}")
            arquivos_com_erro.append(arquivo.name)
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS CONSOLIDADOS")
    print("=" * 50)
    
    print(f"\n📁 Arquivos processados: {arquivos_processados}")
    print(f"❌ Arquivos com erro: {len(arquivos_com_erro)}")
    print(f"🎯 Total de origens únicas: {len(origens_globais)}")
    
    # Listar todas as origens encontradas
    print(f"\n📋 TODAS AS ORIGENS ENCONTRADAS ({len(origens_globais)}):")
    print("-" * 30)
    for i, origem in enumerate(sorted(origens_globais), 1):
        print(f"{i:2d}. {origem}")
    
    # Análise de frequência global
    print(f"\n📈 ANÁLISE DE FREQUÊNCIA:")
    print("-" * 30)
    
    # Contar frequência global de cada origem
    frequencia_global = defaultdict(int)
    total_ocorrencias = 0
    
    for arquivo_stats in estatisticas_arquivos.values():
        for origem, count in arquivo_stats['origens_mais_frequentes'].items():
            frequencia_global[origem] += count
            total_ocorrencias += count
    
    # Top 10 origens mais frequentes
    top_origens = sorted(frequencia_global.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (origem, freq) in enumerate(top_origens, 1):
        percentual = (freq / total_ocorrencias) * 100 if total_ocorrencias > 0 else 0
        print(f"{i:2d}. {origem:<30} {freq:,} ({percentual:.1f}%)")
    
    # Criar CSV com relação de origens
    criar_csv_origens(origens_globais, frequencia_global)
    
    # Salvar análise detalhada
    salvar_analise_detalhada(origens_por_arquivo, estatisticas_arquivos, 
                           frequencia_global, arquivos_com_erro)
    
    print(f"\n✅ Análise concluída!")
    print(f"📄 CSV criado: data/originais/controles_gerais/relacao_origens_trans_financ.csv")
    print(f"📊 Análise detalhada: data/originais/controles_gerais/analise_origens_trans_financ.json")

def criar_csv_origens(origens_globais, frequencia_global):
    """Cria CSV com relação de todas as origens"""
    
    # Preparar dados para CSV
    dados_csv = []
    
    for origem in sorted(origens_globais):
        frequencia = frequencia_global.get(origem, 0)
        dados_csv.append({
            'origem': origem,
            'frequencia_total': frequencia,
            'tipo_estimado': estimar_tipo_origem(origem),
            'categoria': categorizar_origem(origem)
        })
    
    # Criar DataFrame e salvar
    df_origens = pd.DataFrame(dados_csv)
    
    arquivo_csv = Path("data/originais/controles_gerais/relacao_origens_trans_financ.csv")
    df_origens.to_csv(arquivo_csv, index=False, encoding='utf-8')
    
    print(f"\n📄 CSV de origens criado: {arquivo_csv}")
    print(f"   📊 {len(df_origens)} origens catalogadas")

def estimar_tipo_origem(origem):
    """Estima o tipo da origem baseado no nome"""
    origem_upper = origem.upper()
    
    if 'PDV' in origem_upper or 'ORDEM' in origem_upper:
        return 'ORDEM_SERVICO'
    elif 'SANGRIA' in origem_upper:
        return 'SANGRIA_CAIXA'
    elif 'SUPRIMENTO' in origem_upper:
        return 'SUPRIMENTO_CAIXA'
    elif 'ABERTURA' in origem_upper:
        return 'ABERTURA_CAIXA'
    elif 'FECHAMENTO' in origem_upper:
        return 'FECHAMENTO_CAIXA'
    elif 'RECEBIMENTO' in origem_upper:
        return 'RECEBIMENTO'
    elif 'PAGAMENTO' in origem_upper:
        return 'PAGAMENTO'
    elif 'TRANSFERENCIA' in origem_upper:
        return 'TRANSFERENCIA'
    else:
        return 'OUTRO'

def categorizar_origem(origem):
    """Categoriza a origem em grupos principais"""
    origem_upper = origem.upper()
    
    if any(palavra in origem_upper for palavra in ['PDV', 'ORDEM', 'OS']):
        return 'VENDAS'
    elif any(palavra in origem_upper for palavra in ['SANGRIA', 'SUPRIMENTO', 'ABERTURA', 'FECHAMENTO']):
        return 'CONTROLE_CAIXA'
    elif any(palavra in origem_upper for palavra in ['RECEBIMENTO', 'PAGAMENTO']):
        return 'FINANCEIRO'
    elif any(palavra in origem_upper for palavra in ['TRANSFERENCIA']):
        return 'MOVIMENTACAO'
    else:
        return 'OUTROS'

def salvar_analise_detalhada(origens_por_arquivo, estatisticas_arquivos, 
                           frequencia_global, arquivos_com_erro):
    """Salva análise detalhada em JSON"""
    
    analise_completa = {
        'resumo': {
            'arquivos_processados': len(estatisticas_arquivos),
            'arquivos_com_erro': len(arquivos_com_erro),
            'total_origens_unicas': len(frequencia_global),
            'total_ocorrencias': sum(frequencia_global.values())
        },
        'origens_por_arquivo': origens_por_arquivo,
        'estatisticas_arquivos': estatisticas_arquivos,
        'frequencia_global': dict(frequencia_global),
        'arquivos_com_erro': arquivos_com_erro,
        'top_10_origens': dict(sorted(frequencia_global.items(), 
                                    key=lambda x: x[1], reverse=True)[:10])
    }
    
    arquivo_json = Path("data/originais/controles_gerais/analise_origens_trans_financ.json")
    
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(analise_completa, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Análise detalhada salva: {arquivo_json}")

if __name__ == "__main__":
    analisar_origens_trans_financ()