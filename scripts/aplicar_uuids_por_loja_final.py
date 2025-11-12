#!/usr/bin/env python3
"""
APLICADOR DE UUIDs POR LOJA - FINAL 100%
================================================================
Aplica os UUIDs mapeados por loja para atingir 100% de cobertura
nos dados operacionais (OS_ENTREGUES_DIA).
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def carregar_mapeamento_por_loja():
    """Carrega o mapeamento de vendedores por loja"""
    
    mapeamento = {}
    
    print("📋 CARREGANDO MAPEAMENTO POR LOJA")
    print("-" * 50)
    
    try:
        with open('mapeamento_vendedores_por_loja.txt', 'r', encoding='utf-8') as f:
            loja_atual = None
            
            for linha in f:
                linha = linha.strip()
                
                # Identifica loja atual
                if '🏪 LOJA:' in linha:
                    loja_atual = linha.split('🏪 LOJA:')[1].strip().lower()
                    continue
                
                # Ignora comentários e linhas vazias
                if linha.startswith('#') or not linha or '=' not in linha:
                    continue
                
                # Extrai nome e UUID
                partes = linha.split('=', 1)
                if len(partes) == 2 and loja_atual:
                    vendedor = partes[0].strip()
                    uuid = partes[1].strip()
                    
                    if uuid and uuid != 'IGNORAR':
                        # Chave única: loja_vendedor
                        chave = f"{loja_atual}_{vendedor}"
                        mapeamento[chave] = uuid
                        print(f"   ✅ {loja_atual}: {vendedor} → {uuid[:8]}...")
        
        print(f"\n📊 Total de mapeamentos carregados: {len(mapeamento)}")
        return mapeamento
        
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento: {e}")
        return {}

def aplicar_uuids_por_loja(mapeamento):
    """Aplica UUIDs nos arquivos por loja"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    total_aplicados = 0
    estatisticas = {}
    
    print(f"\n📋 APLICANDO UUIDs POR LOJA")
    print("=" * 50)
    
    for loja in lojas:
        arquivo = f"{base_dir}/os_entregues_dia/os_entregues_dia_{loja}_com_uuids_enriquecido_completo.csv"
        
        print(f"\n🏪 PROCESSANDO: {loja.upper()}")
        print("-" * 30)
        
        if os.path.exists(arquivo):
            try:
                df = pd.read_csv(arquivo)
                
                if 'vendedor_uuid' in df.columns and 'vendedor' in df.columns:
                    aplicados_loja = 0
                    detalhes_aplicacao = defaultdict(int)
                    
                    # Processa cada linha
                    for idx, row in df.iterrows():
                        vendedor = str(row['vendedor']).strip()
                        uuid_atual = row['vendedor_uuid']
                        
                        # Se não tem UUID
                        if pd.isna(uuid_atual) or uuid_atual == '' or uuid_atual == 'N/A':
                            chave = f"{loja}_{vendedor}"
                            
                            if chave in mapeamento:
                                df.at[idx, 'vendedor_uuid'] = mapeamento[chave]
                                aplicados_loja += 1
                                detalhes_aplicacao[vendedor] += 1
                    
                    # Salva arquivo atualizado
                    if aplicados_loja > 0:
                        df.to_csv(arquivo, index=False)
                        total_aplicados += aplicados_loja
                        
                        print(f"   ✅ {aplicados_loja} UUIDs aplicados")
                        for vendedor, count in sorted(detalhes_aplicacao.items()):
                            uuid_vendedor = mapeamento.get(f"{loja}_{vendedor}", "")[:8]
                            print(f"      • Código {vendedor}: {count} registros → {uuid_vendedor}...")
                    else:
                        print(f"   ✅ Nenhum UUID necessário")
                    
                    estatisticas[loja] = aplicados_loja
                    
                else:
                    print(f"   ⚠️ Colunas necessárias não encontradas")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
        else:
            print(f"   ⚠️ Arquivo não encontrado")
    
    return total_aplicados, estatisticas

def main():
    print("🚀 INICIANDO APLICAÇÃO FINAL DE UUIDs POR LOJA")
    print("=" * 60)
    
    # Carrega mapeamento
    mapeamento = carregar_mapeamento_por_loja()
    
    if not mapeamento:
        print("❌ Nenhum mapeamento encontrado!")
        return
    
    # Aplica UUIDs
    total_aplicados, estatisticas = aplicar_uuids_por_loja(mapeamento)
    
    # Relatório final
    print(f"\n🎯 RELATÓRIO FINAL DE APLICAÇÃO")
    print("=" * 50)
    
    for loja, count in estatisticas.items():
        if count > 0:
            print(f"🏪 {loja.upper()}: {count} UUIDs aplicados")
    
    print(f"\n🎉 TOTAL GERAL: {total_aplicados} UUIDs aplicados!")
    
    if total_aplicados > 0:
        print(f"\n✅ APLICAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"🎯 Execute a auditoria para verificar 100% de cobertura em OS_ENTREGUES_DIA")
    else:
        print(f"\n⚠️ Nenhum UUID foi aplicado - verifique o mapeamento")

if __name__ == "__main__":
    main()