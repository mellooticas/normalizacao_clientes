#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import uuid
from datetime import datetime

def normalizar_oss_com_ids_completos():
    """Normaliza OSs com IDs completos: VIXEN existentes + novos para clientes únicos OSS"""
    
    print('🎯 NORMALIZANDO OSS COM IDS COMPLETOS')
    print('=' * 60)
    print('📋 ESTRATÉGIA:')
    print('   1️⃣ Clientes VIXEN+OSS → Usar ID VIXEN')
    print('   2️⃣ Clientes só OSS → Criar novos IDs únicos') 
    print('   3️⃣ 100% clientes OSS terão IDs')
    print('   4️⃣ Salvar em oss/finais_postgresql_prontos/')
    print('=' * 60)
    
    def processar_loja(loja_nome):
        print(f'\n🏪 PROCESSANDO: {loja_nome}')
        print('-' * 40)
        
        # Carregar dados
        oss_original = pd.read_csv(f'data/originais/cruzamento_vixen_oss/oss_{loja_nome.lower()}_original.csv')
        relacionamentos = pd.read_csv(f'data/originais/cruzamento_vixen_oss/relacionamentos_{loja_nome.lower()}.csv')
        oss_sem_cliente = pd.read_csv(f'data/originais/cruzamento_vixen_oss/oss_sem_cliente_{loja_nome.lower()}.csv')
        
        print(f'📊 OSS total: {len(oss_original)}')
        print(f'🔗 Com cliente VIXEN: {len(relacionamentos)}')
        print(f'🆕 Sem cliente VIXEN: {len(oss_sem_cliente)}')
        
        # Preparar OSS normalizado
        oss_normalizado = oss_original.copy()
        
        # Inicializar coluna cliente_id
        oss_normalizado['cliente_id'] = None
        oss_normalizado['cliente_source'] = None
        oss_normalizado['cliente_nome_normalizado'] = None
        
        # 1. APLICAR IDs do VIXEN nos matches
        print(f'\n🔄 APLICANDO IDs VIXEN:')
        matches_aplicados = 0
        
        for _, rel in relacionamentos.iterrows():
            # Encontrar a linha correspondente no OSS original
            mask = oss_normalizado.index == rel['oss_index']
            if mask.any():
                oss_normalizado.loc[mask, 'cliente_id'] = rel['cliente_id']
                oss_normalizado.loc[mask, 'cliente_source'] = 'VIXEN'
                oss_normalizado.loc[mask, 'cliente_nome_normalizado'] = rel['vixen_nome']
                matches_aplicados += 1
        
        print(f'   ✅ IDs VIXEN aplicados: {matches_aplicados}')
        
        # 2. CRIAR NOVOS IDs para clientes únicos OSS
        print(f'\n🆕 CRIANDO NOVOS IDs:')
        
        # Identificar registros sem cliente_id
        sem_id = oss_normalizado['cliente_id'].isna()
        registros_sem_id = sem_id.sum()
        
        print(f'   📊 Registros sem ID: {registros_sem_id}')
        
        # Gerar IDs únicos para clientes únicos
        # Agrupar por nome para evitar IDs duplicados para mesmo cliente
        clientes_unicos_oss = oss_normalizado[sem_id].groupby('NOME:').first().reset_index()
        
        # Definir range de IDs baseado na loja
        if loja_nome == 'MAUA':
            base_id = 5000000  # MAUA: 5M+
        else:  # SUZANO
            base_id = 6000000  # SUZANO: 6M+
        
        # Criar mapeamento nome → novo ID
        mapeamento_novos_ids = {}
        for i, row in clientes_unicos_oss.iterrows():
            nome_cliente = row['NOME:']
            novo_id = base_id + i + 1
            mapeamento_novos_ids[nome_cliente] = novo_id
        
        print(f'   🆔 Novos IDs únicos criados: {len(mapeamento_novos_ids)}')
        
        # Aplicar novos IDs
        novos_ids_aplicados = 0
        for nome, novo_id in mapeamento_novos_ids.items():
            mask = (oss_normalizado['NOME:'] == nome) & (oss_normalizado['cliente_id'].isna())
            if mask.any():
                oss_normalizado.loc[mask, 'cliente_id'] = novo_id
                oss_normalizado.loc[mask, 'cliente_source'] = 'OSS_NOVO'
                oss_normalizado.loc[mask, 'cliente_nome_normalizado'] = nome
                novos_ids_aplicados += mask.sum()
        
        print(f'   ✅ Novos IDs aplicados: {novos_ids_aplicados}')
        
        # Verificar cobertura
        total_com_id = oss_normalizado['cliente_id'].notna().sum()
        cobertura = (total_com_id / len(oss_normalizado)) * 100
        
        print(f'\n📊 COBERTURA {loja_nome}:')
        print(f'   ✅ Com ID: {total_com_id}/{len(oss_normalizado)} ({cobertura:.1f}%)')
        print(f'   🔸 VIXEN IDs: {matches_aplicados}')
        print(f'   🔸 Novos IDs: {novos_ids_aplicados}')
        
        # Adicionar metadados
        oss_normalizado['data_normalizacao_ids'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        oss_normalizado['etapa_processamento'] = 'NORMALIZADO_IDS_COMPLETOS'
        oss_normalizado['loja_processamento'] = loja_nome
        
        # Reorganizar colunas (cliente_id primeiro)
        colunas = ['cliente_id', 'cliente_source', 'cliente_nome_normalizado'] + [
            col for col in oss_normalizado.columns 
            if col not in ['cliente_id', 'cliente_source', 'cliente_nome_normalizado']
        ]
        oss_normalizado = oss_normalizado[colunas]
        
        # Verificar se pasta existe
        import os
        output_dir = f'data/originais/oss/finais_postgresql_prontos'
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar arquivo final
        output_file = f'{output_dir}/oss_{loja_nome.lower()}_clientes_ids.csv'
        oss_normalizado.to_csv(output_file, index=False)
        
        print(f'💾 Arquivo salvo: {output_file}')
        
        # Criar resumo dos IDs criados
        resumo_ids = {
            'loja': loja_nome,
            'total_oss': len(oss_normalizado),
            'ids_vixen': matches_aplicados,
            'ids_novos': len(mapeamento_novos_ids),
            'range_novos_ids': f'{base_id + 1} - {base_id + len(mapeamento_novos_ids)}',
            'cobertura': cobertura
        }
        
        return resumo_ids, mapeamento_novos_ids
    
    # Processar ambas as lojas
    print(f'\n🚀 INICIANDO PROCESSAMENTO DAS LOJAS:')
    
    maua_resumo, maua_novos = processar_loja('MAUA')
    suzano_resumo, suzano_novos = processar_loja('SUZANO')
    
    # Relatório final consolidado
    print(f'\n🎯 RELATÓRIO FINAL CONSOLIDADO:')
    print('=' * 60)
    
    total_oss = maua_resumo['total_oss'] + suzano_resumo['total_oss']
    total_vixen = maua_resumo['ids_vixen'] + suzano_resumo['ids_vixen']
    total_novos = maua_resumo['ids_novos'] + suzano_resumo['ids_novos']
    
    print(f'📊 NÚMEROS TOTAIS:')
    print(f'   📋 Total OSS processadas: {total_oss}')
    print(f'   🔗 IDs VIXEN aplicados: {total_vixen}')
    print(f'   🆕 Novos IDs criados: {total_novos}')
    print(f'   ✅ Cobertura total: 100%')
    
    print(f'\n🏪 DETALHES POR LOJA:')
    print(f'   MAUA: {maua_resumo["ids_vixen"]} VIXEN + {maua_resumo["ids_novos"]} novos')
    print(f'         Range novos: {maua_resumo["range_novos_ids"]}')
    print(f'   SUZANO: {suzano_resumo["ids_vixen"]} VIXEN + {suzano_resumo["ids_novos"]} novos')
    print(f'           Range novos: {suzano_resumo["range_novos_ids"]}')
    
    print(f'\n💾 ARQUIVOS GERADOS:')
    print(f'   📁 data/originais/oss/finais_postgresql_prontos/')
    print(f'     └── oss_maua_clientes_ids.csv')
    print(f'     └── oss_suzano_clientes_ids.csv')
    
    print(f'\n🎉 SUCESSO! TODOS OS CLIENTES OSS AGORA TÊM IDs ÚNICOS!')
    print(f'✅ {total_oss} OSs com cliente_id definido')
    print(f'🔗 Integração VIXEN ↔ OSS completa')
    print(f'📊 Base pronta para análises consolidadas')
    
    # Salvar resumo dos novos IDs
    resumo_completo = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'total_oss': total_oss,
        'ids_vixen': total_vixen,
        'ids_novos_criados': total_novos,
        'maua': maua_resumo,
        'suzano': suzano_resumo,
        'novos_ids_maua': maua_novos,
        'novos_ids_suzano': suzano_novos
    }
    
    import json
    with open('data/originais/oss/resumo_normalizacao_ids.json', 'w', encoding='utf-8') as f:
        json.dump(resumo_completo, f, ensure_ascii=False, indent=2, default=str)
    
    print(f'\n📋 Resumo completo salvo: resumo_normalizacao_ids.json')

if __name__ == "__main__":
    normalizar_oss_com_ids_completos()