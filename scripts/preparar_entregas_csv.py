#!/usr/bin/env python3
"""
Script para preparar entregas para importação manual no Supabase
Gera CSV compatível com a tabela entregas_os
"""

import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import warnings
warnings.filterwarnings('ignore')

def gerar_uuid():
    """Gera UUID único"""
    return str(uuid.uuid4())

def preparar_entregas_csv():
    """
    Prepara entregas para importação manual
    """
    print("📄 === PREPARANDO CSV PARA SUPABASE === 📄")
    
    # 1. Carregar dados das entregas mapeadas
    print("\n📊 === CARREGANDO ENTREGAS MAPEADAS === 📊")
    
    arquivo = 'data/originais/controles_gerais/entregas_mapeadas_20251105_001403.csv'
    df = pd.read_csv(arquivo)
    print(f"✅ Entregas carregadas: {len(df):,} registros")
    
    # 2. Filtrar apenas entregas com qualidade
    print("\n🔍 === FILTRANDO ENTREGAS DE QUALIDADE === 🔍")
    
    # Dados obrigatórios
    df = df.dropna(subset=['cliente_id_venda', 'data_entrega'])
    print(f"📊 Com cliente_id e data_entrega: {len(df):,}")
    
    # Converter datas
    df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
    df['data_venda_dt'] = pd.to_datetime(df['data_venda'], errors='coerce')
    
    # Filtrar datas válidas
    df = df.dropna(subset=['data_entrega_dt'])
    print(f"📊 Com datas válidas: {len(df):,}")
    
    # Filtrar lógica de datas (entrega após venda, até 1 ano)
    df['dias_diferenca'] = (df['data_entrega_dt'] - df['data_venda_dt']).dt.days
    df_valido = df[(df['dias_diferenca'] >= 0) & (df['dias_diferenca'] <= 365)]
    print(f"📊 Com datas lógicas (0-365 dias): {len(df_valido):,}")
    
    # 3. Remover duplicatas por cliente+data
    print("\n🔄 === REMOVENDO DUPLICATAS === 🔄")
    
    antes = len(df_valido)
    df_valido = df_valido.drop_duplicates(subset=['cliente_id_venda', 'data_entrega_dt'])
    depois = len(df_valido)
    print(f"📊 Antes: {antes:,} | Depois: {depois:,} | Removidas: {antes-depois:,}")
    
    # 4. Preparar dados para Supabase
    print("\n🔧 === PREPARANDO ESTRUTURA SUPABASE === 🔧")
    
    entregas_supabase = []
    
    # Mapeamento de lojas
    loja_map = {
        'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
        'MAUA': '38e51e7f-a09e-4316-b2ab-a8b7ec4b8c43'
    }
    
    for _, row in df_valido.iterrows():
        try:
            # Determinar loja_id
            loja_id = loja_map.get(row['loja_dav'], row.get('loja_id_venda', ''))
            
            # Preparar observações detalhadas
            obs_parts = []
            if pd.notna(row.get('descricao_dav')):
                obs_parts.append(f"Descrição: {row['descricao_dav']}")
            if pd.notna(row.get('origem_dav')):
                obs_parts.append(f"Origem: {row['origem_dav']}")
            if pd.notna(row.get('arquivo_origem')):
                obs_parts.append(f"Arquivo: {row['arquivo_origem']}")
            if pd.notna(row.get('os_numero')):
                obs_parts.append(f"OS DAV: {int(float(row['os_numero']))}")
            
            observacoes = " | ".join(obs_parts) if obs_parts else "Importado da DAV"
            
            # Preparar registro para Supabase
            entrega = {
                'id': gerar_uuid(),  # UUID único
                'cliente_id': row['cliente_id_venda'],
                'loja_id': loja_id,
                'vendedor_id': row.get('vendedor_id_venda', ''),
                'numero_os': str(int(float(row['os_numero']))) if pd.notna(row['os_numero']) else '',
                'data_entrega': row['data_entrega_dt'].strftime('%Y-%m-%d'),
                'valor_entrega': float(row['valor_dav']) if pd.notna(row['valor_dav']) and row['valor_dav'] != '' else None,
                'status_entrega': 'FINALIZADO',
                'observacoes': observacoes,
                'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'criado_por': 'importacao_dav_historico'
            }
            
            # Limpar campos vazios
            for k, v in entrega.items():
                if v == '' or (isinstance(v, str) and v.strip() == ''):
                    entrega[k] = None
            
            entregas_supabase.append(entrega)
            
        except Exception as e:
            print(f"⚠️ Erro processando linha: {e}")
            continue
    
    # 5. Criar DataFrame final
    df_final = pd.DataFrame(entregas_supabase)
    print(f"📦 Entregas preparadas: {len(df_final):,}")
    
    # 6. Análise dos dados preparados
    print(f"\n📊 === ANÁLISE DOS DADOS PREPARADOS === 📊")
    
    # Por loja
    print(f"🏪 Por loja:")
    loja_dist = df_final['loja_id'].value_counts()
    for loja_id, qtd in loja_dist.items():
        loja_nome = 'SUZANO' if loja_id == '52f92716-d2ba-441a-ac3c-94bdfabd9722' else 'MAUÁ' if loja_id == '38e51e7f-a09e-4316-b2ab-a8b7ec4b8c43' else 'OUTRAS'
        print(f"   {loja_nome}: {qtd:,} entregas")
    
    # Período
    df_final['data_entrega_dt'] = pd.to_datetime(df_final['data_entrega'])
    periodo = f"{df_final['data_entrega_dt'].min().strftime('%Y-%m-%d')} → {df_final['data_entrega_dt'].max().strftime('%Y-%m-%d')}"
    print(f"📅 Período: {periodo}")
    
    # Valores
    valores_validos = df_final['valor_entrega'].dropna()
    if len(valores_validos) > 0:
        print(f"💰 Valores: R$ {valores_validos.min():.2f} → R$ {valores_validos.max():.2f} (média: R$ {valores_validos.mean():.2f})")
        print(f"💰 Total: R$ {valores_validos.sum():,.2f}")
    
    # Clientes únicos
    print(f"👥 Clientes únicos: {df_final['cliente_id'].nunique():,}")
    
    # 7. Salvar arquivo CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_csv = f"data/entregas_para_supabase_{timestamp}.csv"
    
    df_final.to_csv(arquivo_csv, index=False)
    
    print(f"\n💾 === ARQUIVO SALVO === 💾")
    print(f"📄 Arquivo: {arquivo_csv}")
    print(f"📊 Registros: {len(df_final):,}")
    print(f"📋 Colunas: {', '.join(df_final.columns)}")
    
    # 8. Instruções de importação
    print(f"\n📋 === INSTRUÇÕES PARA IMPORTAÇÃO === 📋")
    print(f"1. Acesse o Supabase: https://zlcgursmvxqcalimvjxl.supabase.co")
    print(f"2. Vá para Table Editor → entregas_os")
    print(f"3. Clique em 'Insert' → 'Import data from CSV'")
    print(f"4. Selecione o arquivo: {arquivo_csv}")
    print(f"5. Mapeie as colunas conforme necessário")
    print(f"6. Execute a importação")
    
    return arquivo_csv

def main():
    """Função principal"""
    print("🎯 === PREPARAÇÃO ENTREGAS PARA SUPABASE === 🎯")
    
    arquivo = preparar_entregas_csv()
    
    if arquivo:
        print(f"\n🎉 === PREPARAÇÃO CONCLUÍDA === 🎉")
        print(f"✅ Arquivo CSV pronto para importação")
        print(f"📄 {arquivo}")
        print(f"🚚 {1104} entregas históricas prontas para o sistema!")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === ERRO NA PREPARAÇÃO === ❌")

if __name__ == "__main__":
    main()