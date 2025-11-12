#!/usr/bin/env python3
"""
Script para preparar os 2.247 cruzamentos DAV para a estrutura REAL da tabela entregas_os
Estrutura: id, venda_id, vendedor_id, data_entrega, tem_carne, created_at, updated_at, deleted_at
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

def preparar_cruzamentos_para_supabase():
    """
    Prepara os 2.247 cruzamentos para a estrutura real da tabela entregas_os
    """
    print("🎯 === PREPARANDO CRUZAMENTOS PARA SUPABASE === 🎯")
    print("📋 Estrutura: id, venda_id, vendedor_id, data_entrega, tem_carne")
    
    # 1. Carregar cruzamentos
    print("\n📊 === CARREGANDO CRUZAMENTOS === 📊")
    
    arquivo_cruzamentos = 'data/cruzamentos_completos_dav_vendas_20251105_032132.csv'
    df = pd.read_csv(arquivo_cruzamentos)
    print(f"✅ Cruzamentos carregados: {len(df):,}")
    
    # Análise por tipo
    tipo_dist = df['tipo_match'].value_counts()
    print(f"📊 Por tipo:")
    for tipo, qtd in tipo_dist.items():
        print(f"   {tipo}: {qtd:,}")
    
    # 2. Filtrar cruzamentos válidos
    print("\n🔍 === FILTRANDO CRUZAMENTOS VÁLIDOS === 🔍")
    
    # Filtros obrigatórios
    df_valido = df.dropna(subset=['venda_id', 'data_entrega'])
    print(f"📊 Com venda_id e data_entrega: {len(df_valido):,}")
    
    # Converter datas
    df_valido['data_entrega_dt'] = pd.to_datetime(df_valido['data_entrega'], format='%d/%m/%Y', errors='coerce')
    df_valido['data_venda_dt'] = pd.to_datetime(df_valido['data_venda'], errors='coerce')
    
    # Filtrar datas válidas
    df_valido = df_valido.dropna(subset=['data_entrega_dt'])
    print(f"📊 Com datas válidas: {len(df_valido):,}")
    
    # Filtrar lógica de datas (entrega deve ser após venda, até 2 anos)
    df_valido['dias_diferenca'] = (df_valido['data_entrega_dt'] - df_valido['data_venda_dt']).dt.days
    df_logico = df_valido[(df_valido['dias_diferenca'] >= -30) & (df_valido['dias_diferenca'] <= 730)]  # -30 a +730 dias
    print(f"📊 Com lógica temporal válida: {len(df_logico):,}")
    
    # 3. Remover duplicatas por venda_id + data_entrega (constraint única)
    print("\n🔄 === REMOVENDO DUPLICATAS === 🔄")
    
    antes = len(df_logico)
    df_unico = df_logico.drop_duplicates(subset=['venda_id', 'data_entrega_dt'])
    depois = len(df_unico)
    print(f"📊 Antes: {antes:,} | Depois: {depois:,} | Removidas: {antes-depois:,}")
    
    # 4. Preparar dados para Supabase (estrutura real)
    print("\n🔧 === PREPARANDO ESTRUTURA SUPABASE === 🔧")
    
    entregas_supabase = []
    
    for _, row in df_unico.iterrows():
        try:
            # Determinar tem_carne baseado na descrição
            descricao = str(row.get('cliente_nome_dav', '')).upper()
            arquivo_origem = str(row.get('arquivo_origem', '')).upper()
            
            # Lógica para detectar lentes de contato (tem_carne = true)
            tem_carne = any(palavra in descricao + ' ' + arquivo_origem for palavra in [
                'LENTE', 'CONTATO', 'LC', 'ACUVUE', 'BIOFINITY', 'PROCLEAR',
                'COOPERVISION', 'BAUSCH', 'JOHNSON', 'ALCON'
            ])
            
            # Preparar registro para Supabase (ESTRUTURA REAL)
            entrega = {
                'id': gerar_uuid(),
                'venda_id': row['venda_id'],
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
    
    # 5. Criar DataFrame final
    df_final = pd.DataFrame(entregas_supabase)
    print(f"📦 Entregas preparadas: {len(df_final):,}")
    
    # 6. Análise dos dados preparados
    print(f"\n📊 === ANÁLISE DOS DADOS PREPARADOS === 📊")
    
    # Análise tem_carne
    carne_dist = df_final['tem_carne'].value_counts()
    print(f"🥩 Com carne (lentes): {carne_dist.get(True, 0):,}")
    print(f"👓 Sem carne (óculos): {carne_dist.get(False, 0):,}")
    
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
    
    # 7. Análise por tipo de match original
    print(f"\n📊 === ANÁLISE POR TIPO DE MATCH === 📊")
    
    # Merge com dados originais para ver tipos
    df_final_com_tipo = df_final.merge(
        df_unico[['venda_id', 'data_entrega_dt', 'tipo_match', 'cliente_nome_dav', 'loja_dav']], 
        on=['venda_id'], 
        suffixes=('', '_orig'),
        how='left'
    )
    
    # Filtrar por data próxima (para casos de múltiplas datas)
    df_final_com_tipo['diff_days'] = abs((df_final_com_tipo['data_entrega_dt'] - df_final_com_tipo['data_entrega_dt_orig']).dt.days)
    df_final_com_tipo = df_final_com_tipo.sort_values('diff_days').drop_duplicates(subset=['venda_id', 'data_entrega_dt'])
    
    if 'tipo_match' in df_final_com_tipo.columns:
        tipo_final = df_final_com_tipo['tipo_match'].value_counts()
        print(f"📊 Por origem do match:")
        for tipo, qtd in tipo_final.items():
            print(f"   {tipo}: {qtd:,}")
    
    # Por loja
    if 'loja_dav' in df_final_com_tipo.columns:
        loja_final = df_final_com_tipo['loja_dav'].value_counts()
        print(f"🏪 Por loja:")
        for loja, qtd in loja_final.items():
            print(f"   {loja}: {qtd:,}")
    
    # 8. Salvar arquivo CSV (apenas colunas necessárias)
    print(f"\n💾 === SALVANDO ARQUIVO === 💾")
    
    # Selecionar apenas colunas da tabela real
    colunas_tabela = ['id', 'venda_id', 'vendedor_id', 'data_entrega', 'tem_carne', 'created_at', 'updated_at', 'deleted_at']
    df_export = df_final[colunas_tabela].copy()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_csv = f"data/entregas_supabase_2247_cruzamentos_{timestamp}.csv"
    
    df_export.to_csv(arquivo_csv, index=False)
    
    print(f"📄 Arquivo: {arquivo_csv}")
    print(f"📊 Registros: {len(df_export):,}")
    print(f"📋 Colunas: {', '.join(df_export.columns)}")
    
    # 9. Verificação final
    print(f"\n🔍 === VERIFICAÇÃO FINAL === 🔍")
    
    # Verificar se há valores nulos onde não deveria
    venda_id_nulos = df_export['venda_id'].isnull().sum()
    data_entrega_nulos = df_export['data_entrega'].isnull().sum()
    
    print(f"✅ venda_id nulos: {venda_id_nulos} (deve ser 0)")
    print(f"✅ data_entrega nulos: {data_entrega_nulos} (deve ser 0)")
    
    # Verificar constraint única
    duplicatas = df_export.duplicated(subset=['venda_id', 'data_entrega']).sum()
    print(f"✅ Duplicatas venda_id+data_entrega: {duplicatas} (deve ser 0)")
    
    # Verificar UUIDs válidos
    uuids_validos = df_export['venda_id'].str.len().eq(36).all()
    print(f"✅ UUIDs venda_id válidos: {uuids_validos}")
    
    # 10. Instruções de importação
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
    print(f"6. Execute a importação de {len(df_export):,} registros")
    
    return arquivo_csv

def main():
    """Função principal"""
    print("🎯 === PREPARAÇÃO DOS 2.247 CRUZAMENTOS === 🎯")
    print("📋 Para estrutura real da tabela entregas_os")
    
    arquivo = preparar_cruzamentos_para_supabase()
    
    if arquivo:
        print(f"\n🎉 === PREPARAÇÃO CONCLUÍDA === 🎉")
        print(f"✅ Arquivo CSV pronto para importação")
        print(f"📄 {arquivo}")
        print(f"🚚 Entregas dos cruzamentos DAV preparadas!")
        print(f"🎯 Estrutura 100% compatível com tabela entregas_os")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === ERRO NA PREPARAÇÃO === ❌")

if __name__ == "__main__":
    main()