#!/usr/bin/env python3
"""
Consolidador Trans Financ - Versão Simplificada
Cria apenas 4 arquivos principais por origem para controle no banco
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def consolidar_trans_financ_simplificado():
    """Consolida e divide em apenas 4 arquivos principais por origem"""
    
    print("📊 CONSOLIDAÇÃO TRANS FINANC - VERSÃO SIMPLIFICADA")
    print("=" * 60)
    
    # Carregar arquivo consolidado
    pasta_base = Path("data/originais/controles_gerais/trans_financ/trans_financ_consolidado")
    arquivo_consolidado = pasta_base / "trans_financ_consolidado_completo.csv"
    
    print(f"📄 Carregando: {arquivo_consolidado}")
    
    try:
        df = pd.read_csv(arquivo_consolidado, encoding='utf-8', low_memory=False)
        print(f"✅ {len(df):,} registros carregados")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Criar pasta final simplificada
    pasta_final = Path("data/originais/controles_gerais/trans_financ_final")
    pasta_final.mkdir(exist_ok=True)
    
    print(f"📁 Pasta final: {pasta_final}")
    
    # Analisar origens
    print(f"\n🔍 ANÁLISE DAS ORIGENS:")
    print("-" * 30)
    
    if 'Origem' not in df.columns:
        print("❌ Coluna 'Origem' não encontrada")
        return
    
    # Limpar e analisar origens
    df['Origem_Limpa'] = df['Origem'].str.strip()
    origens_stats = df['Origem_Limpa'].value_counts()
    
    print(f"🎯 {len(origens_stats)} origens encontradas:")
    for origem, count in origens_stats.items():
        percentual = (count / len(df)) * 100
        print(f"   • {origem}: {count:,} ({percentual:.1f}%)")
    
    # Definir as 4 origens principais para arquivos separados
    origens_principais = {
        'VENDAS': ['ORDEM DE SERVIÇO PDV'],
        'RECEBIMENTOS': ['REC. CORRENTISTA'],
        'CONTROLE_CAIXA': ['SANGRIA'],
        'OUTROS': ['FUNDO DE CAIXA', 'VENDA']  # Agrupa os menores
    }
    
    print(f"\n📂 CRIANDO 4 ARQUIVOS PRINCIPAIS:")
    print("-" * 40)
    
    arquivos_criados = []
    estatisticas_finais = {}
    
    # Criar cada arquivo principal
    for categoria, lista_origens in origens_principais.items():
        # Filtrar dados desta categoria
        filtro = df['Origem_Limpa'].isin(lista_origens)
        df_categoria = df[filtro].copy()
        
        if len(df_categoria) > 0:
            # Nome do arquivo
            nome_arquivo = f"trans_financ_{categoria.lower()}.csv"
            arquivo_final = pasta_final / nome_arquivo
            
            # Salvar arquivo
            df_categoria.to_csv(arquivo_final, index=False, encoding='utf-8')
            
            # Estatísticas
            valor_total = df_categoria['Vl.líquido'].sum() if 'Vl.líquido' in df_categoria.columns else 0
            periodo_inicio = df_categoria['mes_origem'].min() if 'mes_origem' in df_categoria.columns else 'N/A'
            periodo_fim = df_categoria['mes_origem'].max() if 'mes_origem' in df_categoria.columns else 'N/A'
            
            estatisticas_finais[categoria] = {
                'arquivo': nome_arquivo,
                'registros': len(df_categoria),
                'percentual': (len(df_categoria) / len(df)) * 100,
                'valor_total': float(valor_total),
                'periodo': f"{periodo_inicio} a {periodo_fim}",
                'origens_incluidas': lista_origens
            }
            
            arquivos_criados.append(arquivo_final)
            
            # Ícone por categoria
            if categoria == 'VENDAS':
                icone = "🛒"
            elif categoria == 'RECEBIMENTOS':
                icone = "💰"
            elif categoria == 'CONTROLE_CAIXA':
                icone = "🏦"
            else:
                icone = "📄"
            
            print(f"   {icone} {nome_arquivo}")
            print(f"      📊 {len(df_categoria):,} registros ({(len(df_categoria)/len(df))*100:.1f}%)")
            print(f"      💵 R$ {valor_total:,.2f}")
            print(f"      📅 {periodo_inicio} a {periodo_fim}")
            print(f"      🎯 Origens: {', '.join(lista_origens)}")
            print()
    
    # Criar arquivo de metadados
    criar_metadados_finais(df, estatisticas_finais, pasta_final)
    
    # Criar arquivo de resumo executivo
    criar_resumo_executivo(estatisticas_finais, pasta_final)
    
    print(f"✅ CONSOLIDAÇÃO SIMPLIFICADA CONCLUÍDA!")
    print(f"📁 {len(arquivos_criados)} arquivos criados em: {pasta_final}")
    print(f"🎯 Pronto para importação no banco de dados")
    
    return arquivos_criados, estatisticas_finais

def criar_metadados_finais(df, estatisticas, pasta_destino):
    """Cria arquivo de metadados para controle"""
    
    metadados = {
        'info_consolidacao': {
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_registros_originais': len(df),
            'periodo_completo': f"{df['mes_origem'].min()} a {df['mes_origem'].max()}",
            'valor_total_geral': float(df['Vl.líquido'].sum()) if 'Vl.líquido' in df.columns else 0,
            'arquivos_origem_processados': df['arquivo_origem'].nunique() if 'arquivo_origem' in df.columns else 0
        },
        'arquivos_finais': estatisticas,
        'estrutura_original': {
            'colunas_totais': len(df.columns),
            'principais_colunas': list(df.columns[:20])  # Primeiras 20 colunas
        },
        'qualidade_dados': {
            'registros_com_origem': len(df[df['Origem'].notna()]),
            'registros_sem_cliente': len(df[df['Cliente'].isna()]) if 'Cliente' in df.columns else 0,
            'registros_sem_valor': len(df[df['Vl.líquido'].isna()]) if 'Vl.líquido' in df.columns else 0
        }
    }
    
    arquivo_metadados = pasta_destino / "metadados_trans_financ.json"
    
    with open(arquivo_metadados, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Metadados salvos: {arquivo_metadados}")

def criar_resumo_executivo(estatisticas, pasta_destino):
    """Cria resumo executivo em texto simples"""
    
    resumo_texto = f"""
RESUMO EXECUTIVO - TRANS FINANC CONSOLIDADO
==========================================
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

ESTRUTURA FINAL CRIADA:
----------------------
4 arquivos principais para importação no banco:

"""
    
    total_registros = sum(stats['registros'] for stats in estatisticas.values())
    total_valor = sum(stats['valor_total'] for stats in estatisticas.values())
    
    for categoria, stats in estatisticas.items():
        if categoria == 'VENDAS':
            icone = "🛒"
        elif categoria == 'RECEBIMENTOS':
            icone = "💰"
        elif categoria == 'CONTROLE_CAIXA':
            icone = "🏦"
        else:
            icone = "📄"
        
        resumo_texto += f"{icone} {stats['arquivo']}\n"
        resumo_texto += f"   Registros: {stats['registros']:,} ({stats['percentual']:.1f}%)\n"
        resumo_texto += f"   Valor: R$ {stats['valor_total']:,.2f}\n"
        resumo_texto += f"   Período: {stats['periodo']}\n"
        resumo_texto += f"   Origens: {', '.join(stats['origens_incluidas'])}\n\n"
    
    resumo_texto += f"""
TOTAIS CONSOLIDADOS:
------------------
📊 Total de registros: {total_registros:,}
💵 Valor total: R$ {total_valor:,.2f}
📁 Arquivos para banco: 4

PRÓXIMOS PASSOS:
---------------
1. Importar os 4 arquivos CSV no banco de dados
2. Criar tabelas específicas por categoria
3. Implementar controles e relatórios no sistema
4. Manter apenas estes 4 arquivos para gestão

OBSERVAÇÕES:
-----------
✅ Dados consolidados e organizados por categoria
✅ Estrutura otimizada para controle no banco
✅ Metadados disponíveis para referência
✅ Pronto para implementação no sistema
"""
    
    arquivo_resumo = pasta_destino / "RESUMO_EXECUTIVO.txt"
    
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo_texto)
    
    print(f"📄 Resumo executivo: {arquivo_resumo}")

if __name__ == "__main__":
    arquivos, stats = consolidar_trans_financ_simplificado()
    
    if arquivos:
        print(f"\n🎯 RESULTADO FINAL:")
        print("=" * 20)
        print("✅ 4 arquivos criados para controle no banco")
        print("✅ Estrutura otimizada e organizada")
        print("✅ Metadados e documentação inclusos")
        print("🚀 Pronto para próxima fase!")
    else:
        print("\n❌ Falha na consolidação!")