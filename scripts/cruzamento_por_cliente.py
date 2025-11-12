#!/usr/bin/env python3
"""
Script para cruzamento inteligente por ID de cliente
Mapeando OS → Vendas → Entregas através dos clientes
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def cruzamento_por_cliente():
    """
    Cruzamento inteligente usando ID de cliente como chave
    """
    print("🔗 === CRUZAMENTO INTELIGENTE POR CLIENTE === 🔗")
    
    # 1. Carregar dados DAV completo
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_final_20251104_234859.csv')
    print(f"✅ DAV carregado: {len(dav):,} registros")
    
    # 2. Analisar estrutura de IDs de cliente
    print("\n🔍 === ANÁLISE IDs DE CLIENTE === 🔍")
    
    # ID do cliente na DAV
    if 'ID' in dav.columns:
        dav['cliente_id_dav'] = pd.to_numeric(dav['ID'], errors='coerce')
        clientes_dav = dav['cliente_id_dav'].dropna().nunique()
        print(f"📊 Clientes únicos DAV (ID): {clientes_dav:,}")
        print(f"📋 Exemplos IDs DAV: {dav['cliente_id_dav'].dropna().head(10).tolist()}")
    
    # 3. Carregar dados de vendas do sistema
    vendas_sistema = pd.read_csv('data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv')
    print(f"✅ Vendas sistema: {len(vendas_sistema):,} registros")
    print(f"📊 Clientes únicos sistema: {vendas_sistema['cliente_id'].nunique():,}")
    
    # 4. Carregar vendas com OS (dados antigos)
    vendas_os = pd.read_csv('data_backup/vendas_os_completo.csv')
    vendas_os_clean = vendas_os[vendas_os['os_n'].notna() & (vendas_os['os_n'] != '')]
    print(f"✅ Vendas com OS: {len(vendas_os_clean):,} registros")
    
    # 5. Analisar entregas na DAV
    print("\n🚚 === ANÁLISE ENTREGAS DAV === 🚚")
    
    # Processar datas de entrega
    dav['data_entrega_dt'] = pd.to_datetime(dav['Dt.entrega'], errors='coerce')
    dav['data_os_dt'] = pd.to_datetime(dav['Dh.DAV'], errors='coerce')
    if 'Dh.O.S.' in dav.columns:
        dav['data_os_dt'] = dav['data_os_dt'].fillna(pd.to_datetime(dav['Dh.O.S.'], errors='coerce'))
    
    entregas_realizadas = dav['data_entrega_dt'].notna().sum()
    print(f"📊 Entregas realizadas: {entregas_realizadas:,} de {len(dav):,} ({entregas_realizadas/len(dav)*100:.1f}%)")
    
    if entregas_realizadas > 0:
        periodo_entregas = f"{dav['data_entrega_dt'].min().strftime('%Y-%m-%d')} → {dav['data_entrega_dt'].max().strftime('%Y-%m-%d')}"
        print(f"📅 Período entregas: {periodo_entregas}")
        
        # Status das entregas
        print(f"\n📋 Status das OS com entrega:")
        status_entrega = dav[dav['data_entrega_dt'].notna()]['Status'].value_counts()
        for status, qtd in status_entrega.head(5).items():
            print(f"   {status}: {qtd:,} entregas")
    
    # 6. Tentar cruzamento por cliente com vendas antigas (que têm OS)
    print("\n🔗 === CRUZAMENTO POR CLIENTE (VENDAS COM OS) === 🔗")
    
    # Extrair IDs de cliente das vendas antigas se possível
    if 'ID' in vendas_os_clean.columns:
        vendas_os_clean['cliente_id_vendas'] = pd.to_numeric(vendas_os_clean['ID'], errors='coerce')
        clientes_vendas_os = vendas_os_clean['cliente_id_vendas'].dropna().nunique()
        print(f"📊 Clientes únicos vendas OS: {clientes_vendas_os:,}")
        
        # Cruzamento por cliente
        clientes_dav_set = set(dav['cliente_id_dav'].dropna())
        clientes_vendas_set = set(vendas_os_clean['cliente_id_vendas'].dropna())
        clientes_comuns = clientes_dav_set & clientes_vendas_set
        
        print(f"👥 Clientes em comum: {len(clientes_comuns):,}")
        
        if len(clientes_comuns) > 0:
            print(f"✅ CRUZAMENTO POR CLIENTE ENCONTRADO!")
            
            # Criar mapeamento cliente → OS → entregas
            cruzamentos_cliente = []
            
            for cliente_id in list(clientes_comuns)[:1000]:  # Primeiros 1000 para teste
                dav_cliente = dav[dav['cliente_id_dav'] == cliente_id]
                vendas_cliente = vendas_os_clean[vendas_os_clean['cliente_id_vendas'] == cliente_id]
                
                for _, dav_row in dav_cliente.iterrows():
                    for _, venda_row in vendas_cliente.iterrows():
                        
                        # Mapear loja
                        id_empresa = dav_row.get('ID emp.', '')
                        loja_dav = 'SUZANO' if str(id_empresa) == '42' else 'MAUA' if str(id_empresa) == '48' else f'LOJA_{id_empresa}'
                        
                        cruzamento = {
                            # === CHAVE ===
                            'cliente_id': int(cliente_id),
                            'os_numero': dav_row.get('OS', ''),
                            'os_numero_venda': pd.to_numeric(venda_row.get('os_n', ''), errors='coerce'),
                            
                            # === CLIENTE ===
                            'cliente_nome_dav': dav_row.get('Cliente', ''),
                            'cliente_nome_venda': venda_row.get('nome', ''),
                            
                            # === DATAS ===
                            'data_os': dav_row.get('Dh.DAV', dav_row.get('Dh.O.S.', '')),
                            'data_entrega_dav': dav_row.get('Dt.entrega', ''),
                            'data_prev_entrega_dav': dav_row.get('Dt.prev.entrega', ''),
                            'data_venda': venda_row.get('data_de_compra', ''),
                            'data_prev_entrega_venda': venda_row.get('prev_de_entr', ''),
                            
                            # === LOJA ===
                            'loja_dav': loja_dav,
                            'loja_venda': venda_row.get('loja', ''),
                            
                            # === VALORES ===
                            'valor_dav': dav_row.get('Vl.líquido', ''),
                            'valor_venda': venda_row.get('total', ''),
                            
                            # === STATUS ===
                            'status_dav': dav_row.get('Status', ''),
                            'origem_dav': dav_row.get('Origem', ''),
                            
                            # === VENDEDOR ===
                            'vendedor_dav': dav_row.get('Vendedor', ''),
                            'consultor_venda': venda_row.get('consultor', ''),
                            
                            # === CONTATO ===
                            'telefone_venda': venda_row.get('telefone', ''),
                            'celular_venda': venda_row.get('celular', ''),
                            'email_venda': venda_row.get('email', ''),
                            
                            # === ORIGEM ===
                            'arquivo_dav': dav_row.get('arquivo_origem', ''),
                            'como_conheceu': venda_row.get('como_conheceu', ''),
                            
                            # === ENTREGA ===
                            'tem_entrega_dav': 1 if pd.notna(dav_row.get('Dt.entrega', '')) else 0,
                            'descricao_dav': dav_row.get('Descrição', '')
                        }
                        
                        cruzamentos_cliente.append(cruzamento)
            
            # Salvar cruzamento por cliente
            if cruzamentos_cliente:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo_cliente = f"data/originais/controles_gerais/cruzamento_por_cliente_{timestamp}.csv"
                
                df_cliente = pd.DataFrame(cruzamentos_cliente)
                df_cliente.to_csv(arquivo_cliente, index=False)
                
                print(f"💾 Cruzamento por cliente salvo: {arquivo_cliente}")
                print(f"📊 Registros: {len(df_cliente):,}")
                print(f"👥 Clientes únicos: {df_cliente['cliente_id'].nunique():,}")
                
                # Análise das entregas
                entregas_encontradas = df_cliente['tem_entrega_dav'].sum()
                print(f"🚚 Entregas encontradas: {entregas_encontradas:,} de {len(df_cliente):,}")
                
                if entregas_encontradas > 0:
                    # Analisar qualidade das entregas
                    df_entregas = df_cliente[df_cliente['tem_entrega_dav'] == 1].copy()
                    
                    print(f"\n📊 === ANÁLISE DAS ENTREGAS === 📊")
                    print(f"📋 Total entregas: {len(df_entregas):,}")
                    
                    # Por loja
                    print(f"🏪 Entregas por loja:")
                    loja_entregas = df_entregas['loja_dav'].value_counts()
                    for loja, qtd in loja_entregas.items():
                        print(f"   {loja}: {qtd:,} entregas")
                    
                    # Por status
                    print(f"📊 Entregas por status:")
                    status_entregas = df_entregas['status_dav'].value_counts()
                    for status, qtd in status_entregas.head(5).items():
                        print(f"   {status}: {qtd:,} entregas")
                    
                    # Salvar apenas entregas
                    arquivo_entregas = f"data/originais/controles_gerais/entregas_por_cliente_{timestamp}.csv"
                    df_entregas.to_csv(arquivo_entregas, index=False)
                    print(f"🚚 Arquivo de entregas: {arquivo_entregas}")
                    
                    return arquivo_cliente, arquivo_entregas
                
                return arquivo_cliente, None
    
    # 7. Se não encontrou por cliente, tentar outros métodos
    print("\n🔍 === ANÁLISE ALTERNATIVA === 🔍")
    print("Analisando outras possibilidades de cruzamento...")
    
    # Verificar se há padrões nos nomes
    if 'Cliente' in dav.columns:
        print(f"📊 Nomes únicos DAV: {dav['Cliente'].nunique():,}")
        print(f"📋 Exemplos nomes: {dav['Cliente'].dropna().head(5).tolist()}")
    
    return None, None

def main():
    """Função principal"""
    print("🚀 === CRUZAMENTO INTELIGENTE POR CLIENTE === 🚀")
    
    arquivo_cliente, arquivo_entregas = cruzamento_por_cliente()
    
    if arquivo_cliente:
        print(f"\n🎯 === SUCESSO === 🎯")
        print(f"✅ Cruzamento por cliente: {arquivo_cliente}")
        if arquivo_entregas:
            print(f"🚚 Entregas mapeadas: {arquivo_entregas}")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n⚠️ === NECESSÁRIO ANÁLISE ADICIONAL === ⚠️")
        print("Não foi possível fazer cruzamento direto por cliente.")
        print("Considere análise manual dos padrões de dados.")

if __name__ == "__main__":
    main()