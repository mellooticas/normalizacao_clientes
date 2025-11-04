#!/usr/bin/env python3
"""
GERADOR DE ARQUIVOS FINAIS COMPLETOS - TODAS AS 5 TABELAS
================================================================
Gera arquivos finais limpos das 5 tabelas para controle completo
no banco de dados, removendo apenas versões intermediárias.
================================================================
"""

import pandas as pd
import os
from datetime import datetime

def gerar_arquivos_finais_completos():
    """Gera arquivos finais de todas as 5 tabelas"""
    
    print("🎯 GERANDO ARQUIVOS FINAIS - TODAS AS 5 TABELAS")
    print("=" * 60)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    output_dir = "data/finais_banco_completo"
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # 5 tabelas essenciais
    tabelas = [
        'vendas',                # Dados de vendas
        'restante_entrada',      # Financeiros/entradas  
        'recebimento_carne',     # Recebimentos
        'os_entregues_dia',      # Controle de entregas
        'entrega_carne'          # Entregas de carnê
    ]
    
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    # Colunas essenciais por tabela
    colunas_por_tabela = {
        'vendas': [
            'os_numero', 'cliente', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'valor_venda', 'data_movimento', 'loja_nome', 'loja_id', 
            'canal_captacao_uuid', 'canal_captacao_nome', 'arquivo_origem'
        ],
        'restante_entrada': [
            'os_numero', 'cliente', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'valor_parcela', 'data_movimento', 'loja_nome', 'loja_id',
            'canal_captacao_uuid', 'canal_captacao_nome', 'arquivo_origem'
        ],
        'recebimento_carne': [
            'os_numero', 'cliente', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'valor_parcela', 'data_movimento', 'loja_nome', 'loja_id',
            'canal_captacao_uuid', 'canal_captacao_nome', 'arquivo_origem'
        ],
        'os_entregues_dia': [
            'os_numero', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'data_movimento', 'loja_nome', 'loja_id', 'carne',
            'canal_captacao_uuid', 'canal_captacao_nome', 'arquivo_origem'
        ],
        'entrega_carne': [
            'os_numero', 'cliente', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'valor_parcela', 'data_movimento', 'loja_nome', 'loja_id',
            'canal_captacao_uuid', 'canal_captacao_nome', 'arquivo_origem'
        ]
    }
    
    resumo_geral = {}
    total_registros_todas_tabelas = 0
    
    for tabela in tabelas:
        print(f"\n📋 PROCESSANDO TABELA: {tabela.upper()}")
        print("-" * 50)
        
        total_registros_tabela = 0
        lojas_processadas = 0
        
        for loja in lojas:
            # Buscar arquivo base (sem UUIDs ainda)
            arquivo_origem = f"{base_dir}/{tabela}/{tabela}_{loja}.csv"
            
            if os.path.exists(arquivo_origem):
                try:
                    df = pd.read_csv(arquivo_origem)
                    print(f"🏪 {loja}: {len(df):,} registros (arquivo base)")
                    
                    # Filtrar apenas registros válidos
                    if tabela == 'os_entregues_dia':
                        df_validos = df[
                            (df['os'].notna()) & 
                            (df['os'] != '') &
                            (df['vendedor'].notna()) & 
                            (df['vendedor'] != '')
                        ].copy()
                        # Normalizar coluna os para os_numero
                        df_validos['os_numero'] = df_validos['os']
                    else:
                        # Para outras tabelas, verificar estrutura
                        colunas_disponiveis = df.columns.tolist()
                        print(f"     Colunas: {colunas_disponiveis[:5]}...")
                        
                        # Tentar identificar colunas principais
                        if 'cliente' in colunas_disponiveis:
                            df_validos = df[
                                (df['cliente'].notna()) & 
                                (df['cliente'] != '')
                            ].copy()
                        else:
                            df_validos = df.copy()
                    
                    # Salvar arquivo final por loja (base sem UUIDs por enquanto)
                    arquivo_final = f"{output_dir}/{tabela}_{loja}_BASE_BANCO.csv"
                    df_validos.to_csv(arquivo_final, index=False)
                    
                    total_registros_tabela += len(df_validos)
                    lojas_processadas += 1
                    
                    print(f"   💾 Salvos: {len(df_validos):,} registros válidos")
                    
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
            else:
                print(f"   ⚠️ {loja}: Arquivo não encontrado")
        
        # Gerar arquivo consolidado por tabela
        arquivos_tabela = []
        for loja in lojas:
            arquivo = f"{output_dir}/{tabela}_{loja}_BASE_BANCO.csv"
            if os.path.exists(arquivo):
                df_loja = pd.read_csv(arquivo)
                arquivos_tabela.append(df_loja)
        
        if arquivos_tabela:
            df_consolidado = pd.concat(arquivos_tabela, ignore_index=True)
            arquivo_consolidado = f"{output_dir}/{tabela.upper()}_TODAS_LOJAS_BASE_BANCO.csv"
            df_consolidado.to_csv(arquivo_consolidado, index=False)
            
            print(f"📊 Total {tabela}: {len(df_consolidado):,} registros consolidados")
            
            resumo_geral[tabela] = {
                'registros': len(df_consolidado),
                'lojas': lojas_processadas,
                'tem_uuids': 'vendedor_uuid' in df_consolidado.columns
            }
            
            total_registros_todas_tabelas += len(df_consolidado)
    
    # Relatório final
    print(f"\n📋 RELATÓRIO FINAL - TODAS AS TABELAS")
    print("=" * 60)
    print(f"📊 Total geral: {total_registros_todas_tabelas:,} registros")
    
    for tabela, dados in resumo_geral.items():
        print(f"\n📋 {tabela.upper()}:")
        print(f"   📊 Registros: {dados['registros']:,}")
        print(f"   🏪 Lojas: {dados['lojas']}")
        print(f"   🎯 UUIDs: {'✅ Já tem' if dados['tem_uuids'] else '⚠️ Precisa aplicar'}")
    
    print(f"\n✅ ARQUIVOS FINAIS COMPLETOS GERADOS!")
    print(f"📁 Localização: {output_dir}/")
    print(f"🎯 5 tabelas prontas para controle completo no Supabase")
    
    return resumo_geral

if __name__ == "__main__":
    resumo = gerar_arquivos_finais_completos()
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print(f"1. Upload das 5 tabelas no Supabase")
    print(f"2. Cruzamento via os_numero entre tabelas")
    print(f"3. Controle completo: vendas + financeiro + entregas")