#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import re
from datetime import datetime

def aplicar_uuids_canais_vixen_manuais():
    """Aplica os UUIDs manuais definidos pelo usuário nos arquivos VIXEN"""
    
    print('🎯 APLICANDO UUIDS MANUAIS DOS CANAIS VIXEN')
    print('=' * 60)
    
    # Ler mapeamento manual do arquivo
    mapeamento_manual = {}
    with open('CANAIS_VIXEN_SEM_UUID.txt', 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                # Formato: canal_nome | count_clientes | uuid_manual
                partes = linha.split(' | ')
                if len(partes) >= 3:
                    canal_nome = partes[0].strip()
                    uuid_part = partes[2].strip()
                    
                    # Extrair UUID (remover [UUID_AQUI] se existir)
                    uuid_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', uuid_part)
                    if uuid_match:
                        uuid_final = uuid_match.group()
                        mapeamento_manual[canal_nome] = uuid_final
                        print(f"✅ '{canal_nome}' → {uuid_final}")
                    else:
                        print(f"⚠️ '{canal_nome}' → SEM UUID VÁLIDO")
    
    print(f'\n📊 Mapeamento manual: {len(mapeamento_manual)} canais')
    
    # Carregar mapeamento automático existente
    with open('data/originais/vixen/mapeamento_canais_vixen_limpo.json', 'r', encoding='utf-8') as f:
        mapeamento_auto = json.load(f)
    
    # Combinar mapeamentos
    mapeamento_completo = {}
    
    # Adicionar mapeamentos automáticos
    for canal, dados in mapeamento_auto['mapeamento_limpo'].items():
        mapeamento_completo[canal] = dados['canal_uuid']
    
    # Adicionar mapeamentos manuais (sobrescreve se necessário)
    for canal, uuid in mapeamento_manual.items():
        mapeamento_completo[canal] = uuid
        print(f"🔄 Manual: '{canal}' → {uuid}")
    
    print(f'\n📊 Mapeamento completo: {len(mapeamento_completo)} canais')
    
    # Aplicar nos arquivos VIXEN
    arquivos_vixen = [
        'data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv',
        'data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv'
    ]
    
    total_atualizados = 0
    canais_nao_encontrados = set()
    
    for arquivo in arquivos_vixen:
        print(f'\n🔄 Processando: {arquivo.split("/")[-1]}')
        
        # Ler arquivo
        df = pd.read_csv(arquivo)
        print(f'   📊 Registros: {len(df)}')
        
        # Criar coluna canal_uuid
        df['canal_uuid'] = None
        
        # Aplicar mapeamento
        atualizados_arquivo = 0
        for idx, row in df.iterrows():
            canal = str(row['Como nos conheceu']).strip()
            
            if canal in mapeamento_completo:
                df.at[idx, 'canal_uuid'] = mapeamento_completo[canal]
                atualizados_arquivo += 1
            else:
                canais_nao_encontrados.add(canal)
        
        # Adicionar metadados
        df['data_normalizacao_canais'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        df['etapa_processamento'] = 'NORMALIZADO_UUIDS_CANAIS'
        
        # Salvar arquivo atualizado
        df.to_csv(arquivo, index=False)
        print(f'   ✅ Atualizados: {atualizados_arquivo} registros')
        total_atualizados += atualizados_arquivo
    
    # Relatório final
    print(f'\n📊 RELATÓRIO FINAL:')
    print(f'   ✅ Total atualizados: {total_atualizados}')
    print(f'   📋 Canais mapeados: {len(mapeamento_completo)}')
    
    if canais_nao_encontrados:
        print(f'   ⚠️ Canais não encontrados: {len(canais_nao_encontrados)}')
        for canal in sorted(canais_nao_encontrados):
            if canal and canal != 'nan':
                print(f'      - "{canal}"')
    
    # Salvar mapeamento final
    mapeamento_final = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'tipo': 'COMPLETO_COM_MANUAIS',
        'canais_automaticos': len(mapeamento_auto['mapeamento_limpo']),
        'canais_manuais': len(mapeamento_manual),
        'total_canais': len(mapeamento_completo),
        'mapeamento_completo': mapeamento_completo
    }
    
    with open('data/originais/vixen/mapeamento_canais_vixen_final.json', 'w', encoding='utf-8') as f:
        json.dump(mapeamento_final, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Mapeamento final salvo: mapeamento_canais_vixen_final.json')
    print('\n🎯 PRÓXIMO PASSO: Normalizar vendedores VIXEN!')

if __name__ == "__main__":
    aplicar_uuids_canais_vixen_manuais()