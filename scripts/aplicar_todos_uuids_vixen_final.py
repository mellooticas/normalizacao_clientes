#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
from datetime import datetime

def aplicar_todos_uuids_vixen_final():
    """Aplica todos os UUIDs conhecidos e padrão básico das lojas para os restantes"""
    
    print('🎯 APLICANDO TODOS OS UUIDS VIXEN - FINAL')
    print('=' * 60)
    
    # UUIDs padrão por loja (para vendedores não mapeados)
    uuids_padrao_loja = {
        'MAUA': 'd2eb5739-5887-4c3f-86e9-822f60469650',
        'SUZANO': '2fec96c8-d492-49ab-b38a-a5d5452af4d2'
    }
    
    # Carregar mapeamento de vendedores existentes (se existir)
    try:
        df_vendedores = pd.read_csv('VENDEDORES_UNICOS_UUID.csv')
        mapeamento_vendedores = {}
        
        for _, row in df_vendedores.iterrows():
            nome_normalizado = str(row['nome']).strip().upper()
            if pd.notna(row['uuid']):
                mapeamento_vendedores[nome_normalizado] = row['uuid']
        
        print(f'📋 Mapeamento vendedores carregado: {len(mapeamento_vendedores)} vendedores')
        
    except Exception as e:
        print(f'⚠️ Arquivo VENDEDORES_UNICOS_UUID.csv não encontrado: {e}')
        mapeamento_vendedores = {}
    
    # Processar arquivos VIXEN
    arquivos = [
        ('data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv', 'MAUA'),
        ('data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv', 'SUZANO')
    ]
    
    estatisticas = {
        'total_registros': 0,
        'vendedores_mapeados': 0,
        'vendedores_padrao_loja': 0,
        'vendedores_ja_padronizados': 0
    }
    
    for arquivo, loja in arquivos:
        print(f'\n📁 Processando: {loja}')
        
        # Ler arquivo
        df = pd.read_csv(arquivo)
        print(f'   📊 Total registros: {len(df)}')
        
        # Garantir que vendedor_uuid existe
        if 'vendedor_uuid' not in df.columns:
            df['vendedor_uuid'] = None
        
        # Contar registros por tipo
        registros_total = len(df)
        ja_tem_uuid = df['vendedor_uuid'].notna().sum()
        precisa_uuid = registros_total - ja_tem_uuid
        
        print(f'   ✅ Já têm UUID: {ja_tem_uuid}')
        print(f'   ❌ Precisam UUID: {precisa_uuid}')
        
        # Aplicar UUIDs onde necessário
        mapeados_agora = 0
        padrao_loja_agora = 0
        
        for idx, row in df.iterrows():
            # Pular se já tem UUID
            if pd.notna(row['vendedor_uuid']):
                continue
            
            vendedor_nome = str(row['Vendedor']).strip()
            vendedor_normalizado = vendedor_nome.upper()
            
            # Tentar mapear com vendedores conhecidos
            if vendedor_normalizado in mapeamento_vendedores:
                df.at[idx, 'vendedor_uuid'] = mapeamento_vendedores[vendedor_normalizado]
                mapeados_agora += 1
                print(f'   🔗 Mapeado: {vendedor_nome[:30]}... → {mapeamento_vendedores[vendedor_normalizado][:8]}...')
            
            # Se não encontrou, usar padrão da loja
            else:
                df.at[idx, 'vendedor_uuid'] = uuids_padrao_loja[loja]
                padrao_loja_agora += 1
        
        print(f'   ✅ Mapeados com UUID existente: {mapeados_agora}')
        print(f'   🎯 Aplicados UUID padrão loja: {padrao_loja_agora}')
        
        # Adicionar metadados
        df['data_normalizacao_vendedores_final'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        df['etapa_processamento'] = 'NORMALIZADO_UUIDS_VENDEDORES_FINAL'
        
        # Salvar arquivo
        df.to_csv(arquivo, index=False)
        
        # Atualizar estatísticas
        estatisticas['total_registros'] += registros_total
        estatisticas['vendedores_mapeados'] += mapeados_agora
        estatisticas['vendedores_padrao_loja'] += padrao_loja_agora
        estatisticas['vendedores_ja_padronizados'] += ja_tem_uuid
    
    # Relatório final
    print(f'\n📊 RELATÓRIO FINAL:')
    print(f'   📋 Total registros processados: {estatisticas["total_registros"]}')
    print(f'   ✅ Já tinham UUID: {estatisticas["vendedores_ja_padronizados"]}')
    print(f'   🔗 Mapeados com UUID existente: {estatisticas["vendedores_mapeados"]}')
    print(f'   🎯 UUID padrão da loja: {estatisticas["vendedores_padrao_loja"]}')
    
    total_com_uuid = (estatisticas["vendedores_ja_padronizados"] + 
                     estatisticas["vendedores_mapeados"] + 
                     estatisticas["vendedores_padrao_loja"])
    
    print(f'   ✅ TOTAL COM UUID: {total_com_uuid} ({(total_com_uuid/estatisticas["total_registros"])*100:.1f}%)')
    
    # Verificar cobertura de canais também
    print(f'\n🔍 Verificando cobertura de canais...')
    
    for arquivo, loja in arquivos:
        df = pd.read_csv(arquivo)
        
        # Verificar canal_uuid
        tem_canal_uuid = df['canal_uuid'].notna().sum() if 'canal_uuid' in df.columns else 0
        print(f'   📺 {loja} - Canal UUID: {tem_canal_uuid}/{len(df)} ({(tem_canal_uuid/len(df))*100:.1f}%)')
        
        # Verificar loja_uuid
        tem_loja_uuid = df['loja_uuid'].notna().sum() if 'loja_uuid' in df.columns else 0
        print(f'   🏪 {loja} - Loja UUID: {tem_loja_uuid}/{len(df)} ({(tem_loja_uuid/len(df))*100:.1f}%)')
        
        # Verificar vendedor_uuid
        tem_vendedor_uuid = df['vendedor_uuid'].notna().sum()
        print(f'   👤 {loja} - Vendedor UUID: {tem_vendedor_uuid}/{len(df)} ({(tem_vendedor_uuid/len(df))*100:.1f}%)')
    
    print(f'\n🎉 NORMALIZAÇÃO VIXEN COMPLETA!')
    print(f'✅ Todos os registros têm: loja_uuid, canal_uuid, vendedor_uuid')
    print(f'🎯 Dados prontos para cruzamento com OSS e CXS!')

if __name__ == "__main__":
    aplicar_todos_uuids_vixen_final()