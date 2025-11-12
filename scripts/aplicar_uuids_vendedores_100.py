#!/usr/bin/env python3
"""
APLICADOR DE UUIDs COMPLETO - 100% COBERTURA
================================================================
Aplica TODOS os UUIDs mapeados pelo usuário para atingir
100% de cobertura de vendedores em todas as tabelas.
================================================================
"""

import pandas as pd
import os
import re
from collections import defaultdict

def carregar_mapeamento():
    """Carrega o mapeamento de vendedores do arquivo"""
    
    mapeamento = {}
    
    print("📋 CARREGANDO MAPEAMENTO DE VENDEDORES")
    print("-" * 50)
    
    try:
        with open('mapeamento_vendedores_100_completo.txt', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                
                # Ignora comentários e linhas vazias
                if linha.startswith('#') or not linha or '=' not in linha:
                    continue
                
                # Extrai nome e UUID
                partes = linha.split('=', 1)
                if len(partes) == 2:
                    nome = partes[0].strip()
                    uuid = partes[1].strip()
                    
                    if uuid and uuid != 'IGNORAR':
                        mapeamento[nome] = uuid
                        print(f"   ✅ {nome} → {uuid}")
                    elif uuid == 'IGNORAR':
                        print(f"   ⚠️ {nome} → IGNORADO")
        
        print(f"\n📊 Total de mapeamentos carregados: {len(mapeamento)}")
        return mapeamento
        
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento: {e}")
        return {}

def aplicar_uuids_tabela(base_dir, tabela, lojas, mapeamento):
    """Aplica UUIDs em uma tabela específica"""
    
    print(f"\n📋 PROCESSANDO TABELA: {tabela.upper()}")
    print("-" * 50)
    
    total_aplicados = 0
    estatisticas = {}
    
    for loja in lojas:
        arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
        
        if os.path.exists(arquivo):
            try:
                df = pd.read_csv(arquivo)
                
                if 'vendedor_uuid' in df.columns and 'vendedor' in df.columns:
                    aplicados_loja = 0
                    
                    # Processa cada linha
                    for idx, row in df.iterrows():
                        vendedor = str(row['vendedor']).strip()
                        uuid_atual = row['vendedor_uuid']
                        
                        # Se não tem UUID e está no mapeamento
                        if (pd.isna(uuid_atual) or uuid_atual == '' or uuid_atual == 'N/A') and vendedor in mapeamento:
                            df.at[idx, 'vendedor_uuid'] = mapeamento[vendedor]
                            aplicados_loja += 1
                    
                    # Salva arquivo atualizado
                    if aplicados_loja > 0:
                        df.to_csv(arquivo, index=False)
                        total_aplicados += aplicados_loja
                        print(f"🏪 {loja}: {aplicados_loja} UUIDs aplicados")
                    else:
                        print(f"✅ {loja}: Nenhum UUID necessário")
                    
                    estatisticas[loja] = aplicados_loja
                    
                else:
                    print(f"⚠️ {loja}: Colunas necessárias não encontradas")
                    
            except Exception as e:
                print(f"❌ {loja}: Erro ao processar - {e}")
        else:
            print(f"⚠️ {loja}: Arquivo não encontrado")
    
    return total_aplicados, estatisticas

def main():
    print("🚀 INICIANDO APLICAÇÃO COMPLETA DE UUIDs - 100% COBERTURA")
    print("=" * 70)
    
    # Carrega mapeamento
    mapeamento = carregar_mapeamento()
    
    if not mapeamento:
        print("❌ Nenhum mapeamento encontrado!")
        return
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    total_geral = 0
    resumo_tabelas = {}
    
    # Aplica UUIDs em todas as tabelas
    for tabela in tabelas:
        total_tabela, estatisticas = aplicar_uuids_tabela(base_dir, tabela, lojas, mapeamento)
        total_geral += total_tabela
        resumo_tabelas[tabela] = {'total': total_tabela, 'lojas': estatisticas}
    
    # Relatório final
    print(f"\n🎯 RELATÓRIO FINAL DE APLICAÇÃO")
    print("=" * 50)
    
    for tabela, dados in resumo_tabelas.items():
        if dados['total'] > 0:
            print(f"\n📋 {tabela.upper()}: {dados['total']} UUIDs aplicados")
            for loja, count in dados['lojas'].items():
                if count > 0:
                    print(f"   🏪 {loja}: {count}")
    
    print(f"\n🎉 TOTAL GERAL: {total_geral} UUIDs aplicados!")
    
    if total_geral > 0:
        print(f"\n✅ APLICAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"🎯 Execute a auditoria para verificar 100% de cobertura")
    else:
        print(f"\n⚠️ Nenhum UUID foi aplicado - verifique o mapeamento")

if __name__ == "__main__":
    main()