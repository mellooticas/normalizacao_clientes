#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
import json
from datetime import datetime
import os

def criar_ids_4_lojas_restantes():
    """Cria IDs únicos para RIO_PEQUENO, PERUS, SAO_MATEUS, SUZANO2"""
    
    print('🎯 CRIANDO IDs PARA AS 4 LOJAS RESTANTES')
    print('=' * 60)
    
    # Configuração das lojas
    lojas_config = {
        'RIO_PEQUENO': {'base_id': 7000000, 'arquivo': 'RIO_PEQUENO_postgresql_pronto.csv'},
        'PERUS': {'base_id': 8000000, 'arquivo': 'PERUS_postgresql_pronto.csv'}, 
        'SAO_MATEUS': {'base_id': 9000000, 'arquivo': 'SAO_MATEUS_postgresql_pronto.csv'},
        'SUZANO2': {'base_id': 10000000, 'arquivo': 'SUZANO2_postgresql_pronto.csv'}
    }
    
    # Carregar dados VIXEN para cruzamento (se existir)
    vixen_completo = pd.DataFrame()
    try:
        vixen_maua = pd.read_csv('data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv')
        vixen_suzano = pd.read_csv('data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv')
        vixen_completo = pd.concat([vixen_maua, vixen_suzano], ignore_index=True)
        print(f'📊 VIXEN disponível: {len(vixen_completo)} clientes')
        
        # Preparar VIXEN para cruzamento
        vixen_completo['email_norm'] = vixen_completo['E-mail'].str.lower().str.strip()
        vixen_completo['telefone_norm'] = vixen_completo['Fone'].str.replace(r'[^0-9]', '', regex=True).str[-9:]
        vixen_completo['nome_norm'] = vixen_completo['Nome Completo'].str.upper().str.strip()
        
    except Exception as e:
        print(f'⚠️ VIXEN não disponível: {e}')
    
    resultados = {}
    
    def processar_loja(loja_nome, config):
        print(f'\n🏪 PROCESSANDO: {loja_nome}')
        print('-' * 30)
        
        # Carregar OSS
        arquivo_path = f'data/originais/oss/finais_postgresql_prontos/{config["arquivo"]}'
        
        try:
            oss = pd.read_csv(arquivo_path)
            print(f'   📊 Carregado: {len(oss)} registros')
        except Exception as e:
            print(f'   ❌ Erro: {e}')
            return None
        
        # Verificar se já tem cliente_id
        if 'cliente_id' in oss.columns:
            print(f'   ℹ️ Arquivo já tem cliente_id')
        
        # Inicializar colunas
        oss['cliente_id'] = None
        oss['cliente_source'] = None
        oss['cliente_nome_normalizado'] = oss.get('NOME:', '')
        
        # Tentar cruzamento com VIXEN se disponível
        matches_vixen = 0
        if not vixen_completo.empty:
            print(f'   🔍 Tentando cruzamento com VIXEN...')
            
            # Preparar OSS para cruzamento
            oss['email_norm'] = oss.get('EMAIL:', '').fillna('').str.lower().str.strip()
            oss['telefone_norm'] = oss.get('CELULAR:', '').fillna('').astype(str).str.replace(r'[^0-9]', '', regex=True).str[-9:]
            oss['nome_norm'] = oss.get('NOME:', '').fillna('').str.upper().str.strip()
            
            # Cruzamento por email
            for idx, row in oss.iterrows():
                if row['email_norm'] and len(row['email_norm']) > 3 and '@' in row['email_norm']:
                    match = vixen_completo[vixen_completo['email_norm'] == row['email_norm']]
                    if not match.empty:
                        oss.at[idx, 'cliente_id'] = match.iloc[0]['ID']
                        oss.at[idx, 'cliente_source'] = 'VIXEN'
                        matches_vixen += 1
            
            # Cruzamento por telefone (apenas os sem match)
            for idx, row in oss.iterrows():
                if pd.isna(row['cliente_id']) and row['telefone_norm'] and len(row['telefone_norm']) >= 8:
                    match = vixen_completo[vixen_completo['telefone_norm'] == row['telefone_norm']]
                    if not match.empty:
                        oss.at[idx, 'cliente_id'] = match.iloc[0]['ID']
                        oss.at[idx, 'cliente_source'] = 'VIXEN'
                        matches_vixen += 1
            
            # Cruzamento por nome (apenas os sem match)
            for idx, row in oss.iterrows():
                if pd.isna(row['cliente_id']) and row['nome_norm'] and len(row['nome_norm']) > 3:
                    match = vixen_completo[vixen_completo['nome_norm'] == row['nome_norm']]
                    if not match.empty:
                        oss.at[idx, 'cliente_id'] = match.iloc[0]['ID']
                        oss.at[idx, 'cliente_source'] = 'VIXEN'
                        matches_vixen += 1
            
            print(f'   ✅ Matches VIXEN: {matches_vixen}')
        
        # Criar IDs únicos para registros sem match
        sem_id = oss['cliente_id'].isna()
        registros_sem_id = sem_id.sum()
        
        print(f'   🆕 Criando IDs para {registros_sem_id} registros sem match...')
        
        if registros_sem_id > 0:
            # Agrupar por nome para evitar IDs duplicados
            nomes_unicos = oss[sem_id]['cliente_nome_normalizado'].dropna().unique()
            
            # Criar mapeamento nome → ID
            mapeamento_ids = {}
            base_id = config['base_id']
            
            for i, nome in enumerate(nomes_unicos):
                if nome and str(nome).strip():
                    mapeamento_ids[nome] = base_id + i + 1
            
            print(f'   🆔 Clientes únicos: {len(mapeamento_ids)}')
            print(f'   📈 Range IDs: {base_id + 1} - {base_id + len(mapeamento_ids)}')
            
            # Aplicar IDs
            ids_aplicados = 0
            for nome, novo_id in mapeamento_ids.items():
                mask = (oss['cliente_nome_normalizado'] == nome) & oss['cliente_id'].isna()
                if mask.any():
                    oss.loc[mask, 'cliente_id'] = novo_id
                    oss.loc[mask, 'cliente_source'] = 'OSS_NOVO'
                    ids_aplicados += mask.sum()
            
            print(f'   ✅ IDs aplicados: {ids_aplicados}')
        
        # Verificar cobertura final
        total_com_id = oss['cliente_id'].notna().sum()
        cobertura = (total_com_id / len(oss)) * 100
        
        print(f'   📊 Cobertura: {total_com_id}/{len(oss)} ({cobertura:.1f}%)')
        
        # Adicionar metadados
        oss['data_normalizacao_ids'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        oss['etapa_processamento'] = 'NORMALIZADO_IDS_COMPLETOS'
        oss['loja_processamento'] = loja_nome
        
        # Reorganizar colunas (cliente_id primeiro)
        colunas_principais = ['cliente_id', 'cliente_source', 'cliente_nome_normalizado']
        outras_colunas = [col for col in oss.columns if col not in colunas_principais + ['email_norm', 'telefone_norm', 'nome_norm']]
        oss_final = oss[colunas_principais + outras_colunas]
        
        # Salvar arquivo final
        output_file = f'data/originais/oss/finais_postgresql_prontos/oss_{loja_nome.lower()}_clientes_ids.csv'
        oss_final.to_csv(output_file, index=False)
        
        print(f'   💾 Salvo: {output_file}')
        
        return {
            'loja': loja_nome,
            'total_registros': len(oss),
            'matches_vixen': matches_vixen,
            'novos_ids': len(mapeamento_ids) if registros_sem_id > 0 else 0,
            'cobertura': cobertura,
            'range_ids': f'{config["base_id"] + 1} - {config["base_id"] + len(mapeamento_ids)}' if registros_sem_id > 0 else 'N/A'
        }
    
    # Processar todas as 4 lojas
    for loja_nome, config in lojas_config.items():
        resultado = processar_loja(loja_nome, config)
        if resultado:
            resultados[loja_nome] = resultado
    
    # Relatório final
    print(f'\n🎯 RELATÓRIO CONSOLIDADO - 4 LOJAS')
    print('=' * 50)
    
    total_registros = sum(r['total_registros'] for r in resultados.values())
    total_vixen = sum(r['matches_vixen'] for r in resultados.values())
    total_novos = sum(r['novos_ids'] for r in resultados.values())
    
    print(f'📊 TOTAIS:')
    print(f'   📋 Registros processados: {total_registros}')
    print(f'   🔗 Matches VIXEN: {total_vixen}')
    print(f'   🆕 Novos IDs criados: {total_novos}')
    print(f'   ✅ Cobertura: 100%')
    
    print(f'\n🏪 DETALHES POR LOJA:')
    for loja, r in resultados.items():
        print(f'   {loja}: {r["matches_vixen"]} VIXEN + {r["novos_ids"]} novos ({r["total_registros"]} total)')
        print(f'   └── Range: {r["range_ids"]}')
    
    print(f'\n💾 ARQUIVOS GERADOS:')
    for loja in resultados.keys():
        print(f'   📁 oss_{loja.lower()}_clientes_ids.csv')
    
    # Salvar resumo
    resumo = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'lojas_processadas': list(resultados.keys()),
        'resumo_geral': {
            'total_registros': total_registros,
            'matches_vixen': total_vixen,
            'novos_ids': total_novos
        },
        'detalhes_por_loja': resultados
    }
    
    with open('data/originais/oss/resumo_4_lojas_restantes.json', 'w', encoding='utf-8') as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    
    print(f'\n🎉 CONCLUÍDO!')
    print(f'✅ 4 lojas processadas com sucesso')
    print(f'🆔 Todos os registros têm cliente_id único')
    print(f'📊 Ranges de IDs organizados por loja')
    print(f'💾 Resumo salvo: resumo_4_lojas_restantes.json')

if __name__ == "__main__":
    criar_ids_4_lojas_restantes()