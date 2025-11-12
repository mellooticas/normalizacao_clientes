#!/usr/bin/env python3
"""
Script para inserir entregas mapeadas no Supabase
Conecta dados da DAV com o sistema de vendas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from supabase import create_client, Client
import warnings
warnings.filterwarnings('ignore')

def conectar_supabase():
    """Conecta ao Supabase"""
    try:
        url = "https://zlcgursmvxqcalimvjxl.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpsY2d1cnNtdnhxY2FsaW12anhsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODI0MDQ2MSwiZXhwIjoyMDQzODE2NDYxfQ.8cWM_xBOzNFkLwJJSa1-5U6dKBCsrXdgCZSNdw3vPBY"
        supabase: Client = create_client(url, key)
        print("✅ Conexão Supabase estabelecida")
        return supabase
    except Exception as e:
        print(f"❌ Erro conectando Supabase: {e}")
        return None

def processar_entregas():
    """
    Processa e insere entregas mapeadas
    """
    print("🚚 === INSERINDO ENTREGAS MAPEADAS === 🚚")
    
    # Conectar ao Supabase
    supabase = conectar_supabase()
    if not supabase:
        return False
    
    # 1. Carregar dados das entregas mapeadas
    print("\n📊 === CARREGANDO ENTREGAS MAPEADAS === 📊")
    
    arquivo = 'data/originais/controles_gerais/entregas_mapeadas_20251105_001403.csv'
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
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
    
    # 3. Preparar dados para inserção
    print("\n🔧 === PREPARANDO DADOS === 🔧")
    
    entregas_para_inserir = []
    
    for _, row in df_valido.iterrows():
        try:
            # Determinar loja_id baseado na loja_dav
            loja_map = {
                'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
                'MAUA': '38e51e7f-a09e-4316-b2ab-a8b7ec4b8c43'
            }
            loja_id = loja_map.get(row['loja_dav'], row.get('loja_id_venda', ''))
            
            # Preparar registro
            entrega = {
                'cliente_id': row['cliente_id_venda'],
                'loja_id': loja_id,
                'vendedor_id': row.get('vendedor_id_venda'),
                'numero_os': str(int(float(row['os_numero']))) if pd.notna(row['os_numero']) else None,
                'data_entrega': row['data_entrega_dt'].strftime('%Y-%m-%d'),
                'valor_entrega': float(row['valor_dav']) if pd.notna(row['valor_dav']) else None,
                'status_entrega': 'FINALIZADO',
                'observacoes': f"DAV: {row.get('descricao_dav', '')} | Origem: {row.get('origem_dav', '')} | Arquivo: {row.get('arquivo_origem', '')}",
                'data_criacao': datetime.now().isoformat(),
                'criado_por': 'script_importacao_dav'
            }
            
            # Remover campos nulos
            entrega = {k: v for k, v in entrega.items() if v is not None and v != ''}
            
            entregas_para_inserir.append(entrega)
            
        except Exception as e:
            print(f"⚠️ Erro processando linha: {e}")
            continue
    
    print(f"📦 Entregas preparadas: {len(entregas_para_inserir):,}")
    
    # 4. Verificar duplicatas no banco
    print("\n🔍 === VERIFICANDO DUPLICATAS === 🔍")
    
    try:
        # Buscar entregas existentes por cliente e data
        clientes_datas = [(e['cliente_id'], e['data_entrega']) for e in entregas_para_inserir]
        
        existing_count = 0
        entregas_novas = []
        
        for entrega in entregas_para_inserir:
            # Verificar se já existe
            result = supabase.table('entregas_os').select('id').eq('cliente_id', entrega['cliente_id']).eq('data_entrega', entrega['data_entrega']).execute()
            
            if not result.data:  # Não existe
                entregas_novas.append(entrega)
            else:
                existing_count += 1
        
        print(f"📊 Entregas já existentes: {existing_count:,}")
        print(f"🆕 Entregas novas: {len(entregas_novas):,}")
        
    except Exception as e:
        print(f"⚠️ Erro verificando duplicatas: {e}")
        entregas_novas = entregas_para_inserir  # Inserir todas se der erro
    
    # 5. Inserir em lotes
    if entregas_novas:
        print(f"\n📥 === INSERINDO {len(entregas_novas):,} ENTREGAS === 📥")
        
        BATCH_SIZE = 100
        total_batches = (len(entregas_novas) + BATCH_SIZE - 1) // BATCH_SIZE
        inseridas = 0
        erros = 0
        
        for i in range(0, len(entregas_novas), BATCH_SIZE):
            batch = entregas_novas[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            try:
                result = supabase.table('entregas_os').insert(batch).execute()
                
                if result.data:
                    inseridas += len(batch)
                    print(f"✅ Lote {batch_num}/{total_batches}: {len(batch)} entregas inseridas")
                else:
                    erros += len(batch)
                    print(f"❌ Lote {batch_num}/{total_batches}: Erro na inserção")
                    
            except Exception as e:
                erros += len(batch)
                print(f"❌ Lote {batch_num}/{total_batches}: {e}")
        
        print(f"\n📊 === RESULTADO FINAL === 📊")
        print(f"✅ Entregas inseridas: {inseridas:,}")
        print(f"❌ Entregas com erro: {erros:,}")
        print(f"📈 Taxa de sucesso: {inseridas/(inseridas+erros)*100:.1f}%")
        
        # 6. Análise final
        print(f"\n📊 === ANÁLISE DAS ENTREGAS INSERIDAS === 📊")
        
        if inseridas > 0:
            # Buscar estatísticas
            total_entregas = supabase.table('entregas_os').select('id', fetch_count=True).execute()
            print(f"🚚 Total de entregas no sistema: {len(total_entregas.data):,}")
            
            # Por loja
            suzano_entregas = supabase.table('entregas_os').select('id', fetch_count=True).eq('loja_id', '52f92716-d2ba-441a-ac3c-94bdfabd9722').execute()
            maua_entregas = supabase.table('entregas_os').select('id', fetch_count=True).eq('loja_id', '38e51e7f-a09e-4316-b2ab-a8b7ec4b8c43').execute()
            
            print(f"🏪 SUZANO: {len(suzano_entregas.data):,} entregas")
            print(f"🏪 MAUÁ: {len(maua_entregas.data):,} entregas")
        
        return inseridas > 0
    
    else:
        print("\n⚠️ === NENHUMA ENTREGA NOVA PARA INSERIR === ⚠️")
        print("Todas as entregas mapeadas já existem no banco")
        return True

def main():
    """Função principal"""
    print("🎯 === IMPORTAÇÃO DE ENTREGAS DAV === 🎯")
    
    sucesso = processar_entregas()
    
    if sucesso:
        print(f"\n🎉 === IMPORTAÇÃO CONCLUÍDA === 🎉")
        print(f"✅ Entregas da DAV agora estão no sistema!")
        print(f"🔗 Histórico de entregas conectado com vendas")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === FALHA NA IMPORTAÇÃO === ❌")
        print("Verifique os logs acima para detalhes")

if __name__ == "__main__":
    main()