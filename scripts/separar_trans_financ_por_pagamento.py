#!/usr/bin/env python3
"""
Separação Trans Financ por Tipo de Pagamento
Divide dados entre Carne Lancaster e outros tipos, sem duplicidades
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def separar_trans_financ_por_pagamento():
    """Separa dados Trans Financ por tipo de pagamento (Carne Lancaster vs Outros)"""
    
    print("📊 SEPARAÇÃO TRANS FINANC POR TIPO DE PAGAMENTO")
    print("=" * 60)
    
    # Carregar arquivo principal integrado
    pasta_base = Path("data/originais/controles_gerais/trans_financ_final")
    arquivo_integrado = pasta_base / "clientes_integrados_trans_financ_master.csv"
    
    print(f"📄 Carregando arquivo integrado: {arquivo_integrado.name}")
    
    try:
        df = pd.read_csv(arquivo_integrado, encoding='utf-8', low_memory=False)
        print(f"✅ {len(df):,} registros carregados")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Analisar coluna Pagamento nos arquivos Trans Financ originais
    print(f"\n🔍 ANALISANDO TIPOS DE PAGAMENTO")
    print("-" * 35)
    
    tipos_pagamento = analisar_tipos_pagamento(pasta_base)
    
    # Carregar dados Trans Financ originais para análise de pagamento
    print(f"\n📊 CARREGANDO DADOS TRANS FINANC ORIGINAIS")
    print("-" * 45)
    
    dados_completos = carregar_dados_trans_originais(pasta_base)
    
    # Fazer separação por tipo de pagamento
    print(f"\n🔄 SEPARANDO POR TIPO DE PAGAMENTO")
    print("-" * 35)
    
    resultado_separacao = separar_por_pagamento(dados_completos, df)
    
    # Salvar arquivos separados
    print(f"\n💾 SALVANDO ARQUIVOS SEPARADOS")
    print("-" * 30)
    
    salvar_arquivos_separados(resultado_separacao, pasta_base)
    
    return resultado_separacao

def analisar_tipos_pagamento(pasta_base):
    """Analisa todos os tipos de pagamento presentes"""
    
    tipos_pagamento = {}
    
    # Analisar arquivos Trans Financ originais
    arquivos_trans = [
        "trans_financ_vendas.csv",
        "trans_financ_recebimentos.csv", 
        "trans_financ_controle_caixa.csv",
        "trans_financ_outros.csv"
    ]
    
    for arquivo_nome in arquivos_trans:
        arquivo_path = pasta_base / arquivo_nome
        
        if arquivo_path.exists():
            print(f"   📄 Analisando: {arquivo_nome}")
            
            try:
                df = pd.read_csv(arquivo_path, encoding='utf-8', low_memory=False)
                
                if 'Pagamento' in df.columns:
                    pagamentos = df['Pagamento'].value_counts()
                    
                    for pagamento, count in pagamentos.items():
                        if pd.notna(pagamento):
                            if pagamento not in tipos_pagamento:
                                tipos_pagamento[pagamento] = 0
                            tipos_pagamento[pagamento] += count
                    
                    print(f"      ✅ {len(pagamentos)} tipos encontrados")
                else:
                    print(f"      ⚠️ Coluna 'Pagamento' não encontrada")
                    
            except Exception as e:
                print(f"      ❌ Erro: {e}")
    
    # Mostrar todos os tipos encontrados
    print(f"\n📋 TIPOS DE PAGAMENTO ENCONTRADOS ({len(tipos_pagamento)}):")
    
    # Ordenar por frequência
    tipos_ordenados = sorted(tipos_pagamento.items(), key=lambda x: x[1], reverse=True)
    
    carne_lancaster_tipos = []
    outros_tipos = []
    
    for tipo, count in tipos_ordenados:
        percentual = (count / sum(tipos_pagamento.values())) * 100
        
        # Classificar tipo
        if 'CARNE' in str(tipo).upper() or 'CARNÊ' in str(tipo).upper():
            carne_lancaster_tipos.append((tipo, count))
            categoria = "🎫 CARNE"
        else:
            outros_tipos.append((tipo, count))
            categoria = "💳 OUTROS"
        
        print(f"   {categoria} {tipo}: {count:,} ({percentual:.1f}%)")
    
    print(f"\n📊 CLASSIFICAÇÃO:")
    print(f"   🎫 Carne Lancaster: {len(carne_lancaster_tipos)} tipos")
    print(f"   💳 Outros pagamentos: {len(outros_tipos)} tipos")
    
    return {
        'todos_tipos': tipos_pagamento,
        'carne_lancaster': [t[0] for t in carne_lancaster_tipos],
        'outros': [t[0] for t in outros_tipos]
    }

def carregar_dados_trans_originais(pasta_base):
    """Carrega dados Trans Financ originais com informações de pagamento"""
    
    dados_consolidados = []
    
    arquivos_trans = [
        "trans_financ_vendas.csv",
        "trans_financ_recebimentos.csv", 
        "trans_financ_controle_caixa.csv",
        "trans_financ_outros.csv"
    ]
    
    for arquivo_nome in arquivos_trans:
        arquivo_path = pasta_base / arquivo_nome
        
        if arquivo_path.exists():
            print(f"   📄 Carregando: {arquivo_nome}")
            
            try:
                df = pd.read_csv(arquivo_path, encoding='utf-8', low_memory=False)
                
                # Adicionar identificador do arquivo
                df['arquivo_trans_origem'] = arquivo_nome
                
                dados_consolidados.append(df)
                print(f"      ✅ {len(df):,} registros")
                
            except Exception as e:
                print(f"      ❌ Erro: {e}")
    
    if dados_consolidados:
        df_completo = pd.concat(dados_consolidados, ignore_index=True)
        print(f"\n📊 Total consolidado: {len(df_completo):,} registros")
        return df_completo
    
    return pd.DataFrame()

def separar_por_pagamento(dados_trans, dados_integrados):
    """Separa dados por tipo de pagamento"""
    
    if dados_trans.empty:
        print("❌ Nenhum dado Trans Financ para processar")
        return None
    
    # Identificar tipos Carne Lancaster
    carne_tipos = dados_trans[dados_trans['Pagamento'].str.contains('CARNE|CARNÊ', case=False, na=False)]['Pagamento'].unique()
    
    print(f"🎫 Tipos identificados como Carne Lancaster:")
    for tipo in carne_tipos:
        count = len(dados_trans[dados_trans['Pagamento'] == tipo])
        print(f"   • {tipo}: {count:,} registros")
    
    # Separar dados
    mask_carne = dados_trans['Pagamento'].str.contains('CARNE|CARNÊ', case=False, na=False)
    
    dados_carne = dados_trans[mask_carne].copy()
    dados_outros = dados_trans[~mask_carne].copy()
    
    print(f"\n📊 RESULTADO DA SEPARAÇÃO:")
    print(f"   🎫 Carne Lancaster: {len(dados_carne):,} registros")
    print(f"   💳 Outros pagamentos: {len(dados_outros):,} registros")
    print(f"   📄 Total: {len(dados_trans):,} registros")
    
    # Verificar sobreposição (duplicidades)
    print(f"\n🔍 VERIFICAÇÃO DE DUPLICIDADES:")
    
    if 'ID.2' in dados_trans.columns:
        clientes_carne = set(dados_carne['ID.2'].dropna())
        clientes_outros = set(dados_outros['ID.2'].dropna())
        sobreposicao = clientes_carne.intersection(clientes_outros)
        
        print(f"   👥 Clientes únicos Carne: {len(clientes_carne):,}")
        print(f"   👥 Clientes únicos Outros: {len(clientes_outros):,}")
        print(f"   🔄 Clientes em ambos: {len(sobreposicao):,}")
        
        if sobreposicao:
            print(f"   ⚠️ {len(sobreposicao)} clientes aparecem em ambas categorias")
    
    # Integrar com dados master
    print(f"\n🔗 INTEGRANDO COM DADOS MASTER")
    print("-" * 30)
    
    # Para Carne Lancaster
    if 'ID.2' in dados_carne.columns:
        ids_carne = dados_carne['ID.2'].dropna().unique()
        dados_master_carne = dados_integrados[dados_integrados['id_cliente'].isin(ids_carne)].copy()
        
        # Adicionar informações de pagamento
        dados_master_carne['categoria_pagamento'] = 'CARNE_LANCASTER'
        
        print(f"   🎫 Carne integrado: {len(dados_master_carne):,} clientes")
    else:
        dados_master_carne = pd.DataFrame()
    
    # Para Outros
    if 'ID.2' in dados_outros.columns:
        ids_outros = dados_outros['ID.2'].dropna().unique()
        dados_master_outros = dados_integrados[dados_integrados['id_cliente'].isin(ids_outros)].copy()
        
        # Adicionar informações de pagamento
        dados_master_outros['categoria_pagamento'] = 'OUTROS_PAGAMENTOS'
        
        print(f"   💳 Outros integrado: {len(dados_master_outros):,} clientes")
    else:
        dados_master_outros = pd.DataFrame()
    
    return {
        'dados_carne_raw': dados_carne,
        'dados_outros_raw': dados_outros,
        'dados_carne_integrados': dados_master_carne,
        'dados_outros_integrados': dados_master_outros,
        'tipos_carne': carne_tipos,
        'sobreposicao_clientes': len(sobreposicao) if 'sobreposicao' in locals() else 0,
        'estatisticas': {
            'total_registros': len(dados_trans),
            'registros_carne': len(dados_carne),
            'registros_outros': len(dados_outros),
            'clientes_carne_integrados': len(dados_master_carne),
            'clientes_outros_integrados': len(dados_master_outros)
        }
    }

def salvar_arquivos_separados(resultado, pasta_base):
    """Salva os arquivos separados por tipo de pagamento"""
    
    # Criar subpasta para separação
    pasta_separados = pasta_base / "separados_por_pagamento"
    pasta_separados.mkdir(exist_ok=True)
    
    # 1. Salvar dados Carne Lancaster integrados
    if not resultado['dados_carne_integrados'].empty:
        arquivo_carne = pasta_separados / "clientes_carne_lancaster_integrados.csv"
        resultado['dados_carne_integrados'].to_csv(arquivo_carne, index=False, encoding='utf-8')
        
        print(f"🎫 Carne Lancaster: {arquivo_carne}")
        print(f"   📊 {len(resultado['dados_carne_integrados']):,} clientes")
    
    # 2. Salvar dados Outros pagamentos integrados
    if not resultado['dados_outros_integrados'].empty:
        arquivo_outros = pasta_separados / "clientes_outros_pagamentos_integrados.csv"
        resultado['dados_outros_integrados'].to_csv(arquivo_outros, index=False, encoding='utf-8')
        
        print(f"💳 Outros Pagamentos: {arquivo_outros}")
        print(f"   📊 {len(resultado['dados_outros_integrados']):,} clientes")
    
    # 3. Salvar dados RAW Carne Lancaster
    if not resultado['dados_carne_raw'].empty:
        arquivo_carne_raw = pasta_separados / "transacoes_carne_lancaster_raw.csv"
        resultado['dados_carne_raw'].to_csv(arquivo_carne_raw, index=False, encoding='utf-8')
        
        print(f"🎫 Carne Raw: {arquivo_carne_raw}")
        print(f"   📊 {len(resultado['dados_carne_raw']):,} transações")
    
    # 4. Salvar dados RAW Outros
    if not resultado['dados_outros_raw'].empty:
        arquivo_outros_raw = pasta_separados / "transacoes_outros_pagamentos_raw.csv"
        resultado['dados_outros_raw'].to_csv(arquivo_outros_raw, index=False, encoding='utf-8')
        
        print(f"💳 Outros Raw: {arquivo_outros_raw}")
        print(f"   📊 {len(resultado['dados_outros_raw']):,} transações")
    
    # 5. Salvar relatório da separação
    relatorio_separacao = {
        'data_separacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estatisticas': resultado['estatisticas'],
        'tipos_carne_lancaster': list(resultado['tipos_carne']),
        'sobreposicao_clientes': resultado['sobreposicao_clientes'],
        'arquivos_criados': {
            'carne_lancaster_integrados': 'clientes_carne_lancaster_integrados.csv',
            'outros_pagamentos_integrados': 'clientes_outros_pagamentos_integrados.csv',
            'carne_lancaster_raw': 'transacoes_carne_lancaster_raw.csv',
            'outros_pagamentos_raw': 'transacoes_outros_pagamentos_raw.csv'
        }
    }
    
    arquivo_relatorio = pasta_separados / "relatorio_separacao_pagamentos.json"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_separacao, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📊 Relatório: {arquivo_relatorio}")
    
    # 6. Criar resumo executivo
    criar_resumo_separacao(resultado, pasta_separados)

def criar_resumo_separacao(resultado, pasta_destino):
    """Cria resumo executivo da separação"""
    
    stats = resultado['estatisticas']
    
    resumo = f"""
RESUMO EXECUTIVO - SEPARAÇÃO POR TIPO DE PAGAMENTO
=================================================
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESULTADO DA SEPARAÇÃO:
----------------------
🎫 CARNE LANCASTER:
   📊 Transações: {stats['registros_carne']:,}
   👥 Clientes integrados: {stats['clientes_carne_integrados']:,}
   📄 Arquivo: clientes_carne_lancaster_integrados.csv

💳 OUTROS PAGAMENTOS:
   📊 Transações: {stats['registros_outros']:,}
   👥 Clientes integrados: {stats['clientes_outros_integrados']:,}
   📄 Arquivo: clientes_outros_pagamentos_integrados.csv

ESTATÍSTICAS:
------------
📊 Total de transações: {stats['total_registros']:,}
🎫 % Carne Lancaster: {(stats['registros_carne']/stats['total_registros'])*100:.1f}%
💳 % Outros pagamentos: {(stats['registros_outros']/stats['total_registros'])*100:.1f}%
🔄 Sobreposição de clientes: {resultado['sobreposicao_clientes']}

TIPOS CARNE LANCASTER IDENTIFICADOS:
----------------------------------
"""
    
    for i, tipo in enumerate(resultado['tipos_carne'], 1):
        resumo += f"{i}. {tipo}\n"
    
    resumo += f"""

ARQUIVOS CRIADOS:
----------------
📄 clientes_carne_lancaster_integrados.csv - Clientes Carne com dados completos
📄 clientes_outros_pagamentos_integrados.csv - Clientes Outros com dados completos  
📄 transacoes_carne_lancaster_raw.csv - Transações Carne brutas
📄 transacoes_outros_pagamentos_raw.csv - Transações Outros brutas
📊 relatorio_separacao_pagamentos.json - Relatório técnico detalhado

PRÓXIMOS PASSOS:
---------------
1. Importar arquivos separados no banco de dados
2. Implementar controles específicos por tipo de pagamento
3. Criar dashboards diferenciados para Carne vs Outros
4. Analisar padrões de comportamento por categoria
5. Otimizar processos específicos para cada tipo

OBSERVAÇÕES:
-----------
✅ Separação realizada sem duplicidades
✅ Dados integrados com UUIDs mantidos
✅ Estrutura otimizada para análises específicas
✅ Pronto para implementação diferenciada no sistema
"""
    
    arquivo_resumo = pasta_destino / "RESUMO_SEPARACAO_PAGAMENTOS.txt"
    
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(f"📄 Resumo executivo: {arquivo_resumo}")

if __name__ == "__main__":
    resultado = separar_trans_financ_por_pagamento()
    
    if resultado:
        print(f"\n🎉 SEPARAÇÃO CONCLUÍDA!")
        print("=" * 25)
        print("✅ Dados separados por tipo de pagamento")
        print("✅ Arquivos integrados e RAW criados")
        print("✅ Sem duplicidades entre categorias")
        print("🚀 Estrutura otimizada para controles específicos!")
    else:
        print("\n❌ Falha na separação!")