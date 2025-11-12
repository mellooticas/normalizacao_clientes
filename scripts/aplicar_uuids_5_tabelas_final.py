#!/usr/bin/env python3
"""
APLICAR UUIDs TODAS AS 5 TABELAS - FINAL
================================================================
Aplica os UUIDs mapeados em todas as 5 tabelas essenciais
do sistema usando os mapeamentos já criados.
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def carregar_mapeamento_vendedores():
    """Carrega o mapeamento de vendedores por loja"""
    
    mapeamento = {}
    
    try:
        with open('mapeamento_vendedores_por_loja.txt', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        loja_atual = None
        
        for linha in conteudo.split('\n'):
            linha = linha.strip()
            
            if '🏪 LOJA:' in linha:
                loja_atual = linha.split('🏪 LOJA:')[1].strip().lower()
                continue
            
            if linha.startswith('#') or not linha or '=' not in linha:
                continue
            
            partes = linha.split('=', 1)
            if len(partes) == 2 and loja_atual:
                vendedor = partes[0].strip()
                uuid = partes[1].strip()
                
                if uuid and uuid != 'IGNORAR':
                    chave = f"{loja_atual}_{vendedor}"
                    mapeamento[chave] = uuid
        
        print(f"✅ Carregados {len(mapeamento)} mapeamentos de vendedores")
        return mapeamento
        
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento: {e}")
        return {}

def aplicar_uuids_todas_tabelas():
    """Aplica UUIDs em todas as 5 tabelas"""
    
    print("🚀 APLICANDO UUIDs EM TODAS AS 5 TABELAS")
    print("=" * 60)
    
    # Carregar mapeamento
    mapeamento = carregar_mapeamento_vendedores()
    if not mapeamento:
        print("❌ Nenhum mapeamento encontrado!")
        return
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    total_geral = 0
    resumo_por_tabela = {}
    
    for tabela in tabelas:
        print(f"\n📋 PROCESSANDO TABELA: {tabela.upper()}")
        print("-" * 50)
        
        total_tabela = 0
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    aplicados_loja = 0
                    
                    # Aplicar UUIDs de vendedores
                    if 'vendedor' in df.columns:
                        for idx, row in df.iterrows():
                            vendedor = str(row.get('vendedor', '')).strip()
                            uuid_atual = row.get('vendedor_uuid', '')
                            
                            # Se não tem UUID ou está vazio
                            if pd.isna(uuid_atual) or uuid_atual == '' or uuid_atual == 'N/A':
                                chave = f"{loja}_{vendedor}"
                                
                                if chave in mapeamento:
                                    df.at[idx, 'vendedor_uuid'] = mapeamento[chave]
                                    aplicados_loja += 1
                    
                    # Aplicar UUIDs de loja (pegar do OS_ENTREGUES_DIA como referência)
                    arquivo_ref = f"{base_dir}/os_entregues_dia/os_entregues_dia_{loja}_com_uuids_enriquecido_completo.csv"
                    if os.path.exists(arquivo_ref):
                        df_ref = pd.read_csv(arquivo_ref)
                        if not df_ref.empty and 'loja_id' in df_ref.columns:
                            loja_id = df_ref['loja_id'].iloc[0]
                            loja_nome = df_ref['loja_nome'].iloc[0]
                            
                            df['loja_id'] = loja_id
                            df['loja_nome'] = loja_nome
                    
                    # Salvar arquivo atualizado
                    df.to_csv(arquivo, index=False)
                    
                    print(f"🏪 {loja}: {aplicados_loja} UUIDs aplicados (total: {len(df)})")
                    total_tabela += aplicados_loja
                    
                except Exception as e:
                    print(f"❌ {loja}: Erro - {e}")
            else:
                print(f"⚠️ {loja}: Arquivo não encontrado")
        
        resumo_por_tabela[tabela] = total_tabela
        total_geral += total_tabela
        print(f"📊 Total {tabela}: {total_tabela} UUIDs aplicados")
    
    # Relatório final
    print(f"\n📋 RELATÓRIO FINAL - TODAS AS TABELAS")
    print("=" * 60)
    print(f"🎯 Total geral: {total_geral} UUIDs aplicados")
    
    for tabela, total in resumo_por_tabela.items():
        print(f"   📋 {tabela}: {total} UUIDs")
    
    return total_geral

if __name__ == "__main__":
    total = aplicar_uuids_todas_tabelas()
    
    if total > 0:
        print(f"\n✅ SUCESSO!")
        print(f"🚀 {total} UUIDs aplicados em todas as 5 tabelas!")
        print(f"🎯 Sistema pronto para upload no Supabase")
    else:
        print(f"\n⚠️ Nenhum UUID foi aplicado")
        print(f"🔍 Verifique os mapeamentos e arquivos")