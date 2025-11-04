#!/usr/bin/env python3
"""
Resumo Final - Integração Trans Financ com Clientes Master
"""

import pandas as pd
import json
from pathlib import Path

def criar_resumo_final_integracao():
    """Cria resumo visual da integração realizada"""
    
    print("📊 RESUMO FINAL - INTEGRAÇÃO TRANS FINANC ↔ CLIENTES MASTER")
    print("=" * 70)
    
    # Carregar relatório
    pasta = Path("data/originais/controles_gerais/trans_financ_final")
    arquivo_relatorio = pasta / "relatorio_cruzamento_trans_financ_master.json"
    
    with open(arquivo_relatorio, 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    
    # Carregar arquivo principal integrado
    arquivo_integrado = pasta / "clientes_integrados_trans_financ_master.csv"
    df_integrado = pd.read_csv(arquivo_integrado, encoding='utf-8')
    
    print("🎯 RESULTADO DA INTEGRAÇÃO:")
    print("-" * 30)
    
    # Estatísticas principais
    stats = relatorio['estatisticas_detalhadas']
    taxas = relatorio['taxas_cobertura']
    
    print(f"👥 CLIENTES TRANS FINANC: {stats['total_trans_financ']:,}")
    print(f"📋 CLIENTES MASTER VIXEN/OSS: {stats['total_master']:,}")
    print(f"✅ MATCHES ENCONTRADOS: {stats['matches_diretos']:,}")
    print()
    
    print(f"📈 TAXAS DE SUCESSO:")
    print(f"   🎯 Taxa de Match Trans Financ: {taxas['match_rate_trans_financ']:.1f}%")
    print(f"   📊 Cobertura do Master: {taxas['cobertura_master']:.1f}%")
    print()
    
    print(f"🔍 ANÁLISE DOS MATCHES:")
    print("-" * 25)
    
    # Análise por loja
    print(f"📍 DISTRIBUIÇÃO POR LOJA:")
    loja_stats = df_integrado['loja_nome'].value_counts()
    for loja, count in loja_stats.items():
        percentual = (count / len(df_integrado)) * 100
        print(f"   🏪 {loja}: {count:,} clientes ({percentual:.1f}%)")
    
    print()
    
    # Análise financeira
    print(f"💰 ANÁLISE FINANCEIRA:")
    valor_total = df_integrado['valor_total_financ'].sum()
    transacoes_total = df_integrado['total_transacoes_financ'].sum()
    ticket_medio = valor_total / len(df_integrado) if len(df_integrado) > 0 else 0
    
    print(f"   💵 Valor total: R$ {valor_total:,.2f}")
    print(f"   📊 Total transações: {transacoes_total:,}")
    print(f"   🎯 Ticket médio: R$ {ticket_medio:,.2f}")
    print()
    
    # Top clientes
    print(f"🏆 TOP 5 CLIENTES POR VALOR:")
    top_clientes = df_integrado.nlargest(5, 'valor_total_financ')
    
    for i, (_, cliente) in enumerate(top_clientes.iterrows(), 1):
        nome = cliente['nome_completo'][:30]
        valor = cliente['valor_total_financ']
        loja = cliente['loja_nome']
        transacoes = cliente['total_transacoes_financ']
        
        print(f"   {i}. {nome} - {loja}")
        print(f"      💰 R$ {valor:,.2f} ({transacoes} transações)")
    
    print()
    
    # Análise de qualidade
    print(f"🔍 QUALIDADE DOS DADOS INTEGRADOS:")
    print("-" * 35)
    
    # Clientes com OSS
    com_oss = df_integrado['tem_compra_oss'].sum()
    print(f"   📋 Clientes com OSS: {com_oss:,} ({(com_oss/len(df_integrado))*100:.1f}%)")
    
    # Distribuição por canal
    print(f"   📡 Canais de aquisição mapeados: {df_integrado['canal_uuid'].notna().sum():,}")
    
    # Vendedores mapeados
    print(f"   👤 Vendedores mapeados: {df_integrado['vendedor_uuid'].notna().sum():,}")
    
    print()
    
    # Estrutura criada
    print(f"📁 ESTRUTURA CRIADA:")
    print("-" * 20)
    
    arquivos_criados = [
        ("clientes_integrados_trans_financ_master.csv", f"{len(df_integrado):,} clientes integrados"),
        ("clientes_trans_financ_orphaos.csv", f"{stats['trans_orphaos']:,} órfãos Trans Financ"),
        ("clientes_master_sem_transacoes_financ.csv", f"{stats['master_sem_trans']:,} master sem transações"),
        ("relatorio_cruzamento_trans_financ_master.json", "Relatório detalhado")
    ]
    
    for arquivo, descricao in arquivos_criados:
        print(f"   📄 {arquivo}")
        print(f"      {descricao}")
    
    print()
    
    # Próximos passos
    print(f"🚀 PRÓXIMOS PASSOS:")
    print("-" * 18)
    print("1. 📊 Importar clientes_integrados_trans_financ_master.csv no banco")
    print("2. 🔗 Usar UUIDs para integração com outras tabelas")
    print("3. 📈 Implementar dashboards financeiros por loja/vendedor")
    print("4. 🎯 Analisar clientes órfãos para possível correção")
    print("5. 💰 Criar relatórios de performance financeira")
    
    print()
    
    # Conclusão
    print(f"✅ CONCLUSÃO:")
    print("-" * 12)
    print(f"🎉 Integração bem-sucedida com {taxas['match_rate_trans_financ']:.1f}% de taxa de match!")
    print(f"🔗 Base unificada criada com dados financeiros + cadastrais + UUIDs")
    print(f"📊 Pronta para implementação no sistema de controle bancário")
    print(f"🚀 Estrutura otimizada para análises e relatórios!")

if __name__ == "__main__":
    criar_resumo_final_integracao()