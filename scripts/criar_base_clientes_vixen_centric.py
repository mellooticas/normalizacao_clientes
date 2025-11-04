#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
from datetime import datetime

def criar_base_clientes_vixen_centric():
    """Cria base de clientes usando VIXEN como master (tem ID) e mapeando OSS"""
    
    print('🎯 CRIANDO BASE CLIENTES VIXEN-CENTRIC')
    print('=' * 60)
    print('📋 ESTRATÉGIA:')
    print('   1️⃣ VIXEN = Master database (ID próprio)')
    print('   2️⃣ OSS = Mapped to VIXEN when possible')
    print('   3️⃣ OSS unmatched = Next phase (new IDs)')
    print('=' * 60)
    
    def normalizar_email(email):
        if pd.isna(email) or email == '':
            return None
        return str(email).lower().strip()
    
    def normalizar_telefone(fone):
        if pd.isna(fone) or fone == '':
            return None
        numeros = re.sub(r'[^0-9]', '', str(fone))
        if len(numeros) >= 8:
            return numeros[-9:] if len(numeros) >= 11 else numeros[-8:]
        return None
    
    def normalizar_nome(nome):
        if pd.isna(nome) or nome == '':
            return None
        nome_limpo = str(nome).upper().strip()
        nome_limpo = re.sub(r'[^A-Z\s]', '', nome_limpo)
        nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
        return nome_limpo
    
    def processar_loja(loja_nome):
        print(f'\n🏪 PROCESSANDO: {loja_nome}')
        print('-' * 40)
        
        # Carregar dados
        vixen_file = f'data/originais/cruzamento_vixen_oss/clientes_vixen_{loja_nome.lower()}_original.csv'
        oss_file = f'data/originais/cruzamento_vixen_oss/oss_{loja_nome.lower()}_original.csv'
        
        vixen = pd.read_csv(vixen_file)
        oss = pd.read_csv(oss_file)
        
        print(f'📊 VIXEN: {len(vixen)} clientes')
        print(f'📊 OSS: {len(oss)} OS')
        
        # Preparar dados para cruzamento
        vixen_prep = vixen.copy()
        vixen_prep['email_norm'] = vixen_prep['E-mail'].apply(normalizar_email)
        vixen_prep['telefone_norm'] = vixen_prep['Fone'].apply(normalizar_telefone)
        vixen_prep['nome_norm'] = vixen_prep['Nome Completo'].apply(normalizar_nome)
        
        oss_prep = oss.copy()
        oss_prep['email_norm'] = oss_prep['EMAIL:'].apply(normalizar_email)
        oss_prep['telefone_norm'] = oss_prep['CELULAR:'].apply(normalizar_telefone)
        oss_prep['nome_norm'] = oss_prep['NOME:'].apply(normalizar_nome)
        
        # Executar cruzamentos
        matches = []
        oss_matched = set()
        
        print(f'\n🔍 EXECUTANDO CRUZAMENTOS:')
        
        # 1. Email (alta precisão)
        email_matches = 0
        for idx, vixen_row in vixen_prep.iterrows():
            if vixen_row['email_norm']:
                oss_match = oss_prep[
                    (oss_prep['email_norm'] == vixen_row['email_norm']) & 
                    (~oss_prep.index.isin(oss_matched))
                ]
                if not oss_match.empty:
                    for _, oss_row in oss_match.iterrows():
                        matches.append({
                            'cliente_id': vixen_row['ID'],
                            'vixen_nome': vixen_row['Nome Completo'],
                            'oss_index': oss_row.name,
                            'oss_nome': oss_row['NOME:'],
                            'oss_numero': oss_row.get('OS N°', 'N/A'),
                            'data_compra': oss_row.get('data_compra', 'N/A'),
                            'total_os': oss_row.get('TOTAL', 0),
                            'match_method': 'EMAIL',
                            'confidence': 'HIGH'
                        })
                        oss_matched.add(oss_row.name)
                        email_matches += 1
        
        print(f'   📧 Email: {email_matches} matches')
        
        # 2. Telefone (média precisão)
        telefone_matches = 0
        for idx, vixen_row in vixen_prep.iterrows():
            if vixen_row['telefone_norm']:
                oss_match = oss_prep[
                    (oss_prep['telefone_norm'] == vixen_row['telefone_norm']) & 
                    (~oss_prep.index.isin(oss_matched))
                ]
                if not oss_match.empty:
                    for _, oss_row in oss_match.iterrows():
                        matches.append({
                            'cliente_id': vixen_row['ID'],
                            'vixen_nome': vixen_row['Nome Completo'],
                            'oss_index': oss_row.name,
                            'oss_nome': oss_row['NOME:'],
                            'oss_numero': oss_row.get('OS N°', 'N/A'),
                            'data_compra': oss_row.get('data_compra', 'N/A'),
                            'total_os': oss_row.get('TOTAL', 0),
                            'match_method': 'PHONE',
                            'confidence': 'MEDIUM'
                        })
                        oss_matched.add(oss_row.name)
                        telefone_matches += 1
        
        print(f'   📞 Telefone: {telefone_matches} matches')
        
        # 3. Nome (baixa precisão)
        nome_matches = 0
        for idx, vixen_row in vixen_prep.iterrows():
            if vixen_row['nome_norm']:
                oss_match = oss_prep[
                    (oss_prep['nome_norm'] == vixen_row['nome_norm']) & 
                    (~oss_prep.index.isin(oss_matched))
                ]
                if not oss_match.empty:
                    for _, oss_row in oss_match.iterrows():
                        matches.append({
                            'cliente_id': vixen_row['ID'],
                            'vixen_nome': vixen_row['Nome Completo'],
                            'oss_index': oss_row.name,
                            'oss_nome': oss_row['NOME:'],
                            'oss_numero': oss_row.get('OS N°', 'N/A'),
                            'data_compra': oss_row.get('data_compra', 'N/A'),
                            'total_os': oss_row.get('TOTAL', 0),
                            'match_method': 'NAME',
                            'confidence': 'LOW'
                        })
                        oss_matched.add(oss_row.name)
                        nome_matches += 1
        
        print(f'   👤 Nome: {nome_matches} matches')
        
        # Criar DataFrames de resultado
        matches_df = pd.DataFrame(matches)
        
        # Estatísticas
        total_matches = len(matches_df)
        clientes_com_compra = matches_df['cliente_id'].nunique()
        os_sem_cliente = len(oss) - len(oss_matched)
        
        print(f'\n📊 RESULTADOS {loja_nome}:')
        print(f'   🔗 Total relationships: {total_matches}')
        print(f'   ✅ VIXEN clients with purchase: {clientes_com_compra}')
        print(f'   ❌ VIXEN clients no purchase: {len(vixen) - clientes_com_compra}')
        print(f'   ❓ OS without VIXEN client: {os_sem_cliente}')
        print(f'   📈 Conversion rate: {(clientes_com_compra/len(vixen))*100:.1f}%')
        
        # Enriquecer base VIXEN
        vixen_enriquecido = vixen.copy()
        
        # Adicionar flags e contadores
        vixen_enriquecido['tem_compra'] = vixen_enriquecido['ID'].isin(matches_df['cliente_id'])
        vixen_enriquecido['total_compras'] = vixen_enriquecido['ID'].map(
            matches_df['cliente_id'].value_counts()
        ).fillna(0).astype(int)
        
        # Adicionar informações da primeira compra
        primeira_compra = matches_df.groupby('cliente_id').agg({
            'data_compra': 'first',
            'total_os': 'first',
            'match_method': 'first',
            'confidence': 'first'
        }).reset_index()
        
        vixen_enriquecido = vixen_enriquecido.merge(
            primeira_compra,
            left_on='ID',
            right_on='cliente_id',
            how='left'
        )
        
        # Adicionar metadados
        vixen_enriquecido['data_enriquecimento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        vixen_enriquecido['fonte_enriquecimento'] = 'CRUZAMENTO_OSS'
        
        # Salvar arquivos
        matches_df.to_csv(f'data/originais/cruzamento_vixen_oss/relacionamentos_{loja_nome.lower()}.csv', index=False)
        vixen_enriquecido.to_csv(f'data/originais/cruzamento_vixen_oss/clientes_master_{loja_nome.lower()}.csv', index=False)
        
        # OS sem match (para próxima fase)
        oss_sem_match = oss_prep[~oss_prep.index.isin(oss_matched)].copy()
        oss_sem_match.to_csv(f'data/originais/cruzamento_vixen_oss/oss_sem_cliente_{loja_nome.lower()}.csv', index=False)
        
        return {
            'loja': loja_nome,
            'vixen_total': len(vixen),
            'oss_total': len(oss),
            'matches': total_matches,
            'clientes_com_compra': clientes_com_compra,
            'os_sem_cliente': os_sem_cliente,
            'conversao': (clientes_com_compra/len(vixen))*100
        }
    
    # Processar ambas as lojas
    maua_stats = processar_loja('MAUA')
    suzano_stats = processar_loja('SUZANO')
    
    # Relatório consolidado
    print(f'\n🎯 RELATÓRIO CONSOLIDADO:')
    print('=' * 60)
    
    total_vixen = maua_stats['vixen_total'] + suzano_stats['vixen_total']
    total_oss = maua_stats['oss_total'] + suzano_stats['oss_total']
    total_matches = maua_stats['matches'] + suzano_stats['matches']
    total_com_compra = maua_stats['clientes_com_compra'] + suzano_stats['clientes_com_compra']
    total_os_sem_cliente = maua_stats['os_sem_cliente'] + suzano_stats['os_sem_cliente']
    
    print(f'📊 NÚMEROS FINAIS:')
    print(f'   👥 Total clientes VIXEN: {total_vixen}')
    print(f'   📋 Total OS: {total_oss}')
    print(f'   🔗 Total relacionamentos: {total_matches}')
    print(f'   ✅ Clientes que compraram: {total_com_compra}')
    print(f'   ❌ Clientes sem compra: {total_vixen - total_com_compra}')
    print(f'   ❓ OS sem cliente VIXEN: {total_os_sem_cliente}')
    print(f'   📈 Taxa conversão geral: {(total_com_compra/total_vixen)*100:.1f}%')
    
    print(f'\n💾 ARQUIVOS GERADOS:')
    print(f'   📋 relacionamentos_maua.csv')
    print(f'   📋 relacionamentos_suzano.csv') 
    print(f'   👥 clientes_master_maua.csv (VIXEN enriquecido)')
    print(f'   👥 clientes_master_suzano.csv (VIXEN enriquecido)')
    print(f'   ❓ oss_sem_cliente_maua.csv (próxima fase)')
    print(f'   ❓ oss_sem_cliente_suzano.csv (próxima fase)')
    
    print(f'\n🚀 PRÓXIMA FASE:')
    print(f'   🆔 Criar IDs para {total_os_sem_cliente} OS sem cliente')
    print(f'   🔗 Consolidar base única de clientes')
    print(f'   📊 Dashboard de conversão e retenção')

if __name__ == "__main__":
    criar_base_clientes_vixen_centric()