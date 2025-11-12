#!/usr/bin/env python3
"""
Script para cruzamento por nome de cliente
Mapeando entregas da DAV para o sistema atual
"""

import pandas as pd
import numpy as np
from datetime import datetime
from fuzzywuzzy import fuzz
import warnings
warnings.filterwarnings('ignore')

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome):
        return ""
    return str(nome).upper().strip().replace("  ", " ")

def cruzamento_por_nome():
    """
    Cruzamento por nome de cliente
    """
    print("👥 === CRUZAMENTO POR NOME DE CLIENTE === 👥")
    
    # 1. Carregar dados
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_final_20251104_234859.csv')
    print(f"✅ DAV: {len(dav):,} registros")
    
    # Filtrar apenas OS com entrega realizada
    dav['data_entrega_dt'] = pd.to_datetime(dav['Dt.entrega'], errors='coerce')
    dav_com_entrega = dav[dav['data_entrega_dt'].notna()].copy()
    print(f"🚚 DAV com entregas: {len(dav_com_entrega):,} registros")
    
    # Vendas do sistema atual
    vendas = pd.read_csv('data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv')
    print(f"✅ Vendas sistema: {len(vendas):,} registros")
    
    # 2. Preparar nomes para cruzamento
    print("\n🔤 === PREPARANDO NOMES === 🔤")
    
    dav_com_entrega['nome_normalizado'] = dav_com_entrega['Cliente'].apply(normalizar_nome)
    vendas['nome_normalizado'] = vendas['nome_cliente_temp'].apply(normalizar_nome)
    
    # Remover nomes vazios
    dav_com_entrega = dav_com_entrega[dav_com_entrega['nome_normalizado'] != '']
    vendas = vendas[vendas['nome_normalizado'] != '']
    
    print(f"📊 DAV com nomes válidos: {len(dav_com_entrega):,}")
    print(f"📊 Vendas com nomes válidos: {len(vendas):,}")
    
    # 3. Cruzamento direto por nome
    print("\n🔗 === CRUZAMENTO DIRETO === 🔗")
    
    nomes_dav = set(dav_com_entrega['nome_normalizado'])
    nomes_vendas = set(vendas['nome_normalizado'])
    nomes_comuns = nomes_dav & nomes_vendas
    
    print(f"👥 Nomes em comum: {len(nomes_comuns):,}")
    
    if len(nomes_comuns) > 0:
        # Criar mapeamento direto
        mapeamentos_diretos = []
        
        for nome in list(nomes_comuns)[:500]:  # Primeiros 500 para teste
            dav_nome = dav_com_entrega[dav_com_entrega['nome_normalizado'] == nome]
            vendas_nome = vendas[vendas['nome_normalizado'] == nome]
            
            for _, dav_row in dav_nome.iterrows():
                for _, venda_row in vendas_nome.iterrows():
                    
                    # Mapear loja
                    id_empresa = dav_row.get('ID emp.', '')
                    loja_dav = 'SUZANO' if str(id_empresa) == '42' else 'MAUA' if str(id_empresa) == '48' else f'LOJA_{id_empresa}'
                    
                    mapeamento = {
                        # === IDENTIFICAÇÃO ===
                        'cliente_nome': nome,
                        'os_numero': dav_row.get('OS', ''),
                        'venda_numero': venda_row.get('numero_venda', ''),
                        'cliente_id_venda': venda_row.get('cliente_id', ''),
                        
                        # === ENTREGA (PRINCIPAL) ===
                        'data_entrega': dav_row.get('Dt.entrega', ''),
                        'data_prev_entrega_dav': dav_row.get('Dt.prev.entrega', ''),
                        'status_entrega': dav_row.get('Status', ''),
                        
                        # === DATAS ===
                        'data_os': dav_row.get('Dh.DAV', dav_row.get('Dh.O.S.', '')),
                        'data_venda': venda_row.get('data_venda', ''),
                        
                        # === LOJA ===
                        'loja_dav': loja_dav,
                        'loja_id_venda': venda_row.get('loja_id', ''),
                        
                        # === VALORES ===
                        'valor_dav': dav_row.get('Vl.líquido', ''),
                        'valor_venda': venda_row.get('valor_total', ''),
                        'valor_entrada_venda': venda_row.get('valor_entrada', ''),
                        
                        # === VENDEDOR ===
                        'vendedor_dav': dav_row.get('Vendedor', ''),
                        'vendedor_id_venda': venda_row.get('vendedor_id', ''),
                        
                        # === ORIGEM ===
                        'origem_dav': dav_row.get('Origem', ''),
                        'descricao_dav': dav_row.get('Descrição', ''),
                        'arquivo_origem': dav_row.get('arquivo_origem', ''),
                        
                        # === STATUS ===
                        'status_venda': venda_row.get('status', ''),
                        'cancelado_venda': venda_row.get('cancelado', ''),
                        
                        # === OBSERVAÇÕES ===
                        'observacoes_venda': venda_row.get('observacoes', '')
                    }
                    
                    mapeamentos_diretos.append(mapeamento)
        
        # Salvar mapeamento direto
        if mapeamentos_diretos:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_direto = f"data/originais/controles_gerais/entregas_mapeadas_{timestamp}.csv"
            
            df_direto = pd.DataFrame(mapeamentos_diretos)
            df_direto.to_csv(arquivo_direto, index=False)
            
            print(f"💾 Entregas mapeadas: {arquivo_direto}")
            print(f"📊 Registros: {len(df_direto):,}")
            print(f"👥 Clientes únicos: {df_direto['cliente_nome'].nunique():,}")
            print(f"🚚 Entregas únicas: {df_direto['data_entrega'].nunique():,}")
            
            # Análise das entregas mapeadas
            print(f"\n📊 === ANÁLISE DAS ENTREGAS MAPEADAS === 📊")
            
            # Por loja
            print(f"🏪 Por loja DAV:")
            loja_dist = df_direto['loja_dav'].value_counts()
            for loja, qtd in loja_dist.items():
                print(f"   {loja}: {qtd:,} entregas")
            
            # Por status
            print(f"📊 Por status:")
            status_dist = df_direto['status_entrega'].value_counts()
            for status, qtd in status_dist.head(5).items():
                print(f"   {status}: {qtd:,} entregas")
            
            # Período
            df_direto['data_entrega_dt'] = pd.to_datetime(df_direto['data_entrega'], errors='coerce')
            periodo = f"{df_direto['data_entrega_dt'].min().strftime('%Y-%m-%d')} → {df_direto['data_entrega_dt'].max().strftime('%Y-%m-%d')}"
            print(f"📅 Período entregas: {periodo}")
            
            # Análise de qualidade
            print(f"\n🔍 === QUALIDADE DO MAPEAMENTO === 🔍")
            
            # Valores similares
            df_direto['valor_dav_num'] = pd.to_numeric(df_direto['valor_dav'], errors='coerce')
            df_direto['valor_venda_num'] = pd.to_numeric(df_direto['valor_venda'], errors='coerce')
            df_direto['diferenca_valor'] = abs(df_direto['valor_dav_num'] - df_direto['valor_venda_num']) / df_direto['valor_venda_num'] * 100
            
            valores_ok = (df_direto['diferenca_valor'] <= 20).sum()  # ±20%
            print(f"💰 Valores similares (±20%): {valores_ok:,} de {len(df_direto):,} ({valores_ok/len(df_direto)*100:.1f}%)")
            
            # Datas próximas
            df_direto['data_venda_dt'] = pd.to_datetime(df_direto['data_venda'], errors='coerce')
            df_direto['diferenca_dias'] = (df_direto['data_entrega_dt'] - df_direto['data_venda_dt']).dt.days
            
            datas_ok = ((df_direto['diferenca_dias'] >= 0) & (df_direto['diferenca_dias'] <= 90)).sum()  # Entrega após venda, até 90 dias
            print(f"📅 Datas lógicas (entrega 0-90 dias após venda): {datas_ok:,} de {len(df_direto):,} ({datas_ok/len(df_direto)*100:.1f}%)")
            
            return arquivo_direto
    
    print("❌ Nenhum nome em comum encontrado para mapeamento direto")
    return None

def main():
    """Função principal"""
    print("🚀 === MAPEAMENTO DE ENTREGAS POR NOME === 🚀")
    
    arquivo = cruzamento_por_nome()
    
    if arquivo:
        print(f"\n🎯 === SUCESSO === 🎯")
        print(f"✅ Entregas mapeadas salvas: {arquivo}")
        print(f"🚚 Agora você tem entregas da DAV conectadas com vendas do sistema!")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n⚠️ === SEM MAPEAMENTO DIRETO === ⚠️")
        print("Considere análise fuzzy ou outros métodos de cruzamento.")

if __name__ == "__main__":
    main()