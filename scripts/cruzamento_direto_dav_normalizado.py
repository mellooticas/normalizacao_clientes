#!/usr/bin/env python3
"""
Script para cruzamento DIRETO entre DAV normalizado e sistema de vendas
Agora com números limpos fica muito mais fácil!
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def cruzamento_dav_vendas_direto():
    """
    Cruzamento direto com números DAV normalizados
    """
    print("🎯 === CRUZAMENTO DIRETO DAV ↔ VENDAS === 🎯")
    print("🚀 Com números normalizados fica muito mais fácil!")
    
    # 1. Carregar DAV normalizado
    print("\n📊 === CARREGANDO DADOS === 📊")
    
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv')
    print(f"✅ DAV carregado: {len(dav):,} registros")
    
    # Filtrar apenas entregas válidas
    dav_entregas = dav[dav['Dt.entrega'].notna()].copy()
    print(f"🚚 DAV com entregas: {len(dav_entregas):,} registros")
    
    # 2. Carregar vendas do sistema
    vendas = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
    print(f"✅ Vendas sistema: {len(vendas):,} registros")
    
    # 3. Preparar números para cruzamento
    print("\n🔢 === PREPARANDO NÚMEROS === 🔢")
    
    # DAV - usar coluna OS_numero (já normalizada)
    dav_entregas['os_numero'] = pd.to_numeric(dav_entregas['OS_numero'], errors='coerce')
    dav_limpo = dav_entregas.dropna(subset=['os_numero'])
    print(f"📊 DAV com OS válidos: {len(dav_limpo):,}")
    
    # Vendas - usar numero_venda
    vendas['numero_venda_num'] = pd.to_numeric(vendas['numero_venda'], errors='coerce')
    vendas_limpo = vendas.dropna(subset=['numero_venda_num'])
    print(f"📊 Vendas com números válidos: {len(vendas_limpo):,}")
    
    # 4. Análise dos ranges
    print(f"\n📊 === ANÁLISE DOS RANGES === 📊")
    
    dav_min = int(dav_limpo['os_numero'].min())
    dav_max = int(dav_limpo['os_numero'].max())
    print(f"🚚 DAV range: {dav_min:,} → {dav_max:,}")
    
    vendas_min = int(vendas_limpo['numero_venda_num'].min())
    vendas_max = int(vendas_limpo['numero_venda_num'].max())
    print(f"🛒 Vendas range: {vendas_min:,} → {vendas_max:,}")
    
    # Overlap
    overlap_min = max(dav_min, vendas_min)
    overlap_max = min(dav_max, vendas_max)
    print(f"🔗 Overlap: {overlap_min:,} → {overlap_max:,}")
    
    # 5. Cruzamento direto por número
    print(f"\n🔗 === CRUZAMENTO DIRETO === 🔗")
    
    # Criar sets para interseção rápida
    numeros_dav = set(dav_limpo['os_numero'].astype(int))
    numeros_vendas = set(vendas_limpo['numero_venda_num'].astype(int))
    
    numeros_comuns = numeros_dav & numeros_vendas
    print(f"🎯 Números em comum: {len(numeros_comuns):,}")
    
    if len(numeros_comuns) > 0:
        print(f"📈 Taxa de match: {len(numeros_comuns)/len(numeros_dav)*100:.1f}% das entregas DAV")
        print(f"📈 Taxa de match: {len(numeros_comuns)/len(numeros_vendas)*100:.1f}% das vendas")
        
        # Criar DataFrame de cruzamento
        cruzamentos = []
        
        print(f"\n🔄 === CRIANDO CRUZAMENTOS === 🔄")
        
        for numero in sorted(list(numeros_comuns)):
            # Buscar no DAV
            dav_rows = dav_limpo[dav_limpo['os_numero'] == numero]
            
            # Buscar nas vendas
            vendas_rows = vendas_limpo[vendas_limpo['numero_venda_num'] == numero]
            
            # Cruzar todas as combinações
            for _, dav_row in dav_rows.iterrows():
                for _, venda_row in vendas_rows.iterrows():
                    
                    # Determinar loja
                    id_empresa = dav_row.get('ID emp.', '')
                    loja_dav = 'SUZANO' if str(id_empresa) == '42' else 'MAUA' if str(id_empresa) == '48' else f'LOJA_{id_empresa}'
                    
                    cruzamento = {
                        # === IDENTIFICAÇÃO ===
                        'numero_os': int(numero),
                        'venda_id': venda_row.get('id', ''),
                        'cliente_id': venda_row.get('cliente_id', ''),
                        'cliente_nome': dav_row.get('Cliente', ''),
                        
                        # === ENTREGA ===
                        'data_entrega': dav_row.get('Dt.entrega', ''),
                        'data_prev_entrega': dav_row.get('Dt.prev.entrega', ''),
                        'status_entrega': dav_row.get('Status', ''),
                        
                        # === DATAS ===
                        'data_dav': dav_row.get('Dh.DAV', ''),
                        'data_venda': venda_row.get('data_venda', ''),
                        
                        # === LOJAS ===
                        'loja_dav': loja_dav,
                        'loja_id_venda': venda_row.get('loja_id', ''),
                        
                        # === VALORES ===
                        'valor_dav': dav_row.get('Vl.líquido', ''),
                        'valor_venda': venda_row.get('valor_total', ''),
                        'valor_entrada': venda_row.get('valor_entrada', ''),
                        
                        # === VENDEDORES ===
                        'vendedor_dav': dav_row.get('Vendedor', ''),
                        'vendedor_id_venda': venda_row.get('vendedor_id', ''),
                        
                        # === STATUS ===
                        'status_venda': venda_row.get('status', ''),
                        'cancelado': venda_row.get('cancelado', ''),
                        
                        # === ORIGEM ===
                        'origem_dav': dav_row.get('Origem', ''),
                        'descricao_dav': dav_row.get('Descrição', ''),
                        'arquivo_origem': dav_row.get('arquivo_origem', ''),
                        
                        # === OBSERVAÇÕES ===
                        'observacoes_venda': venda_row.get('observacoes', '')
                    }
                    
                    cruzamentos.append(cruzamento)
        
        # 6. Criar DataFrame de cruzamentos
        df_cruzamentos = pd.DataFrame(cruzamentos)
        print(f"✅ Cruzamentos criados: {len(df_cruzamentos):,}")
        
        # 7. Análise dos cruzamentos
        print(f"\n📊 === ANÁLISE DOS CRUZAMENTOS === 📊")
        
        # Por loja
        print(f"🏪 Por loja DAV:")
        loja_dist = df_cruzamentos['loja_dav'].value_counts()
        for loja, qtd in loja_dist.items():
            print(f"   {loja}: {qtd:,} entregas")
        
        # Por status
        print(f"📊 Por status entrega:")
        status_dist = df_cruzamentos['status_entrega'].value_counts()
        for status, qtd in status_dist.head(5).items():
            print(f"   {status}: {qtd:,} entregas")
        
        # Período
        df_cruzamentos['data_entrega_dt'] = pd.to_datetime(df_cruzamentos['data_entrega'], format='%d/%m/%Y', errors='coerce')
        entregas_com_data = df_cruzamentos['data_entrega_dt'].dropna()
        
        if len(entregas_com_data) > 0:
            inicio = entregas_com_data.min().strftime('%Y-%m-%d')
            fim = entregas_com_data.max().strftime('%Y-%m-%d')
            print(f"📅 Período entregas: {inicio} → {fim}")
        
        # Clientes únicos
        print(f"👥 Clientes únicos: {df_cruzamentos['cliente_id'].nunique():,}")
        print(f"👥 Nomes únicos: {df_cruzamentos['cliente_nome'].nunique():,}")
        
        # 8. Salvar arquivo de cruzamentos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_cruzamentos = f'data/cruzamentos_dav_vendas_direto_{timestamp}.csv'
        
        df_cruzamentos.to_csv(arquivo_cruzamentos, index=False)
        
        print(f"\n💾 === ARQUIVO SALVO === 💾")
        print(f"📄 Arquivo: {arquivo_cruzamentos}")
        print(f"📊 Registros: {len(df_cruzamentos):,}")
        print(f"🎯 Match rate: {len(numeros_comuns):,} de {len(numeros_dav):,} entregas ({len(numeros_comuns)/len(numeros_dav)*100:.1f}%)")
        
        # 9. Análise de qualidade
        print(f"\n🔍 === QUALIDADE DOS CRUZAMENTOS === 🔍")
        
        # Valores similares
        df_cruzamentos['valor_dav_num'] = pd.to_numeric(df_cruzamentos['valor_dav'], errors='coerce')
        df_cruzamentos['valor_venda_num'] = pd.to_numeric(df_cruzamentos['valor_venda'], errors='coerce')
        
        valores_validos = df_cruzamentos.dropna(subset=['valor_dav_num', 'valor_venda_num'])
        if len(valores_validos) > 0:
            valores_validos['diferenca_pct'] = abs(valores_validos['valor_dav_num'] - valores_validos['valor_venda_num']) / valores_validos['valor_venda_num'] * 100
            valores_ok = (valores_validos['diferenca_pct'] <= 20).sum()
            print(f"💰 Valores similares (±20%): {valores_ok:,} de {len(valores_validos):,} ({valores_ok/len(valores_validos)*100:.1f}%)")
        
        # Datas lógicas
        df_cruzamentos['data_venda_dt'] = pd.to_datetime(df_cruzamentos['data_venda'], errors='coerce')
        datas_validas = df_cruzamentos.dropna(subset=['data_entrega_dt', 'data_venda_dt'])
        
        if len(datas_validas) > 0:
            datas_validas['diferenca_dias'] = (datas_validas['data_entrega_dt'] - datas_validas['data_venda_dt']).dt.days
            datas_ok = ((datas_validas['diferenca_dias'] >= 0) & (datas_validas['diferenca_dias'] <= 90)).sum()
            print(f"📅 Datas lógicas (entrega 0-90 dias após venda): {datas_ok:,} de {len(datas_validas):,} ({datas_ok/len(datas_validas)*100:.1f}%)")
        
        return arquivo_cruzamentos
    
    else:
        print(f"❌ Nenhum número em comum encontrado!")
        return None

def main():
    """Função principal"""
    print("🚀 === CRUZAMENTO DIRETO COM DAV NORMALIZADO === 🚀")
    
    arquivo = cruzamento_dav_vendas_direto()
    
    if arquivo:
        print(f"\n🎉 === CRUZAMENTO CONCLUÍDO === 🎉")
        print(f"✅ Arquivo gerado: {arquivo}")
        print(f"🚀 Agora com números normalizados ficou muito mais fácil!")
        print(f"📊 Entregas do DAV conectadas com vendas do sistema")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === CRUZAMENTO SEM RESULTADOS === ❌")
        print("Verifique os ranges de números entre DAV e vendas")

if __name__ == "__main__":
    main()