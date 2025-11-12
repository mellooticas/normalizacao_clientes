#!/usr/bin/env python3
"""
Script para preparar entregas para a estrutura REAL da tabela entregas_os
Estrutura correta: venda_id, vendedor_id, data_entrega, tem_carne
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

def preparar_entregas_estrutura_real():
    """
    Prepara entregas para a estrutura REAL da tabela entregas_os
    """
    print("🔧 === PREPARANDO PARA ESTRUTURA REAL === 🔧")
    print("📋 Tabela: vendas.entregas_os")
    print("📋 Colunas: id, venda_id, vendedor_id, data_entrega, tem_carne")
    
    # 1. Carregar dados das entregas mapeadas
    print("\n📊 === CARREGANDO ENTREGAS MAPEADAS === 📊")
    
    arquivo = 'data/originais/controles_gerais/entregas_mapeadas_20251105_001403.csv'
    df = pd.read_csv(arquivo)
    print(f"✅ Entregas carregadas: {len(df):,} registros")
    
    # 2. Filtrar apenas entregas com qualidade
    print("\n🔍 === FILTRANDO ENTREGAS DE QUALIDADE === 🔍")
    
    # Dados obrigatórios: venda_numero e data_entrega
    df = df.dropna(subset=['venda_numero', 'data_entrega'])
    print(f"📊 Com venda_numero e data_entrega: {len(df):,}")
    
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
    
    # 3. Carregar vendas para mapear numero → venda_id
    print("\n🔗 === MAPEANDO VENDAS === 🔗")
    
    vendas = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
    print(f"✅ Vendas carregadas: {len(vendas):,}")
    
    # Criar mapeamento numero_venda → id
    # Limpar valores vazios e converter para float
    vendas = vendas.dropna(subset=['numero_venda'])
    vendas = vendas[vendas['numero_venda'].astype(str).str.strip() != '']
    vendas['numero_venda'] = pd.to_numeric(vendas['numero_venda'], errors='coerce')
    vendas = vendas.dropna(subset=['numero_venda'])
    
    mapa_vendas = vendas.set_index('numero_venda')['id'].to_dict()
    print(f"📋 Mapeamento criado: {len(mapa_vendas):,} vendas")
    
    # 4. Mapear venda_id nas entregas
    df_valido['venda_numero_float'] = pd.to_numeric(df_valido['venda_numero'], errors='coerce')
    df_valido = df_valido.dropna(subset=['venda_numero_float'])
    df_valido['venda_id_mapeado'] = df_valido['venda_numero_float'].map(mapa_vendas)
    
    # Filtrar apenas entregas com venda_id válido
    df_com_venda = df_valido.dropna(subset=['venda_id_mapeado'])
    print(f"📊 Entregas com venda_id válido: {len(df_com_venda):,}")
    
    # 5. Remover duplicatas por venda_id + data_entrega (constraint única)
    print("\n🔄 === REMOVENDO DUPLICATAS === 🔄")
    
    antes = len(df_com_venda)
    df_com_venda = df_com_venda.drop_duplicates(subset=['venda_id_mapeado', 'data_entrega_dt'])
    depois = len(df_com_venda)
    print(f"📊 Antes: {antes:,} | Depois: {depois:,} | Removidas: {antes-depois:,}")
    
    # 6. Preparar dados para Supabase (estrutura real)
    print("\n🔧 === PREPARANDO ESTRUTURA REAL === 🔧")
    
    entregas_supabase = []
    
    for _, row in df_com_venda.iterrows():
        try:
            # Determinar tem_carne baseado na descrição
            descricao = str(row.get('descricao_dav', '')).upper()
            tem_carne = any(palavra in descricao for palavra in ['CARNE', 'PROTEÇÃO', 'MULTIFOCAL', 'PROGRESSIV'])
            
            # Preparar registro para Supabase (ESTRUTURA REAL)
            entrega = {
                'id': gerar_uuid(),
                'venda_id': row['venda_id_mapeado'],
                'vendedor_id': row.get('vendedor_id_venda') if pd.notna(row.get('vendedor_id_venda')) else None,
                'data_entrega': row['data_entrega_dt'].strftime('%Y-%m-%d'),
                'tem_carne': tem_carne,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'deleted_at': None
            }
            
            entregas_supabase.append(entrega)
            
        except Exception as e:
            print(f"⚠️ Erro processando linha: {e}")
            continue
    
    # 7. Criar DataFrame final
    df_final = pd.DataFrame(entregas_supabase)
    print(f"📦 Entregas preparadas: {len(df_final):,}")
    
    # 8. Análise dos dados preparados
    print(f"\n📊 === ANÁLISE DOS DADOS PREPARADOS === 📊")
    
    # Análise tem_carne
    carne_dist = df_final['tem_carne'].value_counts()
    print(f"🥩 Com carne: {carne_dist.get(True, 0):,}")
    print(f"👓 Sem carne: {carne_dist.get(False, 0):,}")
    
    # Período
    df_final['data_entrega_dt'] = pd.to_datetime(df_final['data_entrega'])
    periodo = f"{df_final['data_entrega_dt'].min().strftime('%Y-%m-%d')} → {df_final['data_entrega_dt'].max().strftime('%Y-%m-%d')}"
    print(f"📅 Período: {periodo}")
    
    # Vendedores
    vendedores_validos = df_final['vendedor_id'].dropna()
    print(f"👤 Vendedores válidos: {len(vendedores_validos):,} de {len(df_final):,} ({len(vendedores_validos)/len(df_final)*100:.1f}%)")
    print(f"👤 Vendedores únicos: {vendedores_validos.nunique():,}")
    
    # Vendas únicas
    print(f"🛒 Vendas únicas: {df_final['venda_id'].nunique():,}")
    
    # 9. Salvar arquivo CSV (apenas colunas necessárias)
    print(f"\n💾 === SALVANDO ARQUIVO === 💾")
    
    # Selecionar apenas colunas da tabela real
    colunas_tabela = ['id', 'venda_id', 'vendedor_id', 'data_entrega', 'tem_carne', 'created_at', 'updated_at', 'deleted_at']
    df_export = df_final[colunas_tabela].copy()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_csv = f"data/entregas_estrutura_real_{timestamp}.csv"
    
    df_export.to_csv(arquivo_csv, index=False)
    
    print(f"📄 Arquivo: {arquivo_csv}")
    print(f"📊 Registros: {len(df_export):,}")
    print(f"📋 Colunas: {', '.join(df_export.columns)}")
    
    # 10. Verificação final
    print(f"\n🔍 === VERIFICAÇÃO FINAL === 🔍")
    
    # Verificar se há valores nulos onde não deveria
    venda_id_nulos = df_export['venda_id'].isnull().sum()
    data_entrega_nulos = df_export['data_entrega'].isnull().sum()
    
    print(f"✅ venda_id nulos: {venda_id_nulos} (deve ser 0)")
    print(f"✅ data_entrega nulos: {data_entrega_nulos} (deve ser 0)")
    
    # Verificar constraint única
    duplicatas = df_export.duplicated(subset=['venda_id', 'data_entrega']).sum()
    print(f"✅ Duplicatas venda_id+data_entrega: {duplicatas} (deve ser 0)")
    
    # 11. Instruções de importação
    print(f"\n📋 === INSTRUÇÕES PARA IMPORTAÇÃO === 📋")
    print(f"1. Acesse o Supabase: https://zlcgursmvxqcalimvjxl.supabase.co")
    print(f"2. Vá para Table Editor → entregas_os")
    print(f"3. Clique em 'Insert' → 'Import data from CSV'")
    print(f"4. Selecione o arquivo: {arquivo_csv}")
    print(f"5. Mapeie as colunas:")
    print(f"   - id → id (UUID)")
    print(f"   - venda_id → venda_id (UUID)")
    print(f"   - vendedor_id → vendedor_id (UUID)")
    print(f"   - data_entrega → data_entrega (DATE)")
    print(f"   - tem_carne → tem_carne (BOOLEAN)")
    print(f"   - created_at → created_at (TIMESTAMP)")
    print(f"   - updated_at → updated_at (TIMESTAMP)")
    print(f"   - deleted_at → deleted_at (TIMESTAMP)")
    print(f"6. Execute a importação")
    
    return arquivo_csv

def main():
    """Função principal"""
    print("🎯 === ENTREGAS PARA ESTRUTURA REAL === 🎯")
    
    arquivo = preparar_entregas_estrutura_real()
    
    if arquivo:
        print(f"\n🎉 === PREPARAÇÃO CONCLUÍDA === 🎉")
        print(f"✅ Arquivo CSV pronto para importação")
        print(f"📄 {arquivo}")
        print(f"🚚 Entregas preparadas para estrutura REAL da tabela!")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === ERRO NA PREPARAÇÃO === ❌")

if __name__ == "__main__":
    main()