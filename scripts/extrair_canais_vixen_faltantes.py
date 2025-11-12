#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from collections import Counter

def extrair_canais_vixen_faltantes():
    """Extrai canais VIXEN que não têm correspondência nos 171 existentes"""
    
    print('🔍 EXTRAINDO CANAIS VIXEN SEM CORRESPONDÊNCIA')
    print('=' * 60)
    
    # Carregar mapeamento limpo
    with open('data/originais/vixen/mapeamento_canais_vixen_limpo.json', 'r', encoding='utf-8') as f:
        mapeamento = json.load(f)
    
    # Carregar dados VIXEN para contar clientes por canal faltante
    vixen_files = [
        'data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv',
        'data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv'
    ]
    
    todos_dados = []
    for file in vixen_files:
        try:
            df = pd.read_csv(file)
            todos_dados.append(df)
            print(f'📁 {file.split("/")[-1]}: {len(df)} registros')
        except Exception as e:
            print(f'❌ Erro ao ler {file}: {e}')
    
    # Concatenar todos os dados
    df_completo = pd.concat(todos_dados, ignore_index=True)
    print(f'📊 Total de registros VIXEN: {len(df_completo)}')
    
    # Contar canais únicos nos dados VIXEN
    canais_vixen = df_completo['Como nos conheceu'].str.strip().value_counts()
    print(f'📊 Canais únicos VIXEN: {len(canais_vixen)}')
    
    # Identificar canais que NÃO estão mapeados
    canais_mapeados = set(mapeamento['mapeamento_limpo'].keys())
    canais_faltantes = []
    
    for canal, count in canais_vixen.items():
        if canal not in canais_mapeados:
            canais_faltantes.append({
                'canal_nome': canal,
                'count_clientes': count,
                'loja_origem': 'VIXEN'
            })
    
    # Ordenar por número de clientes (decrescente)
    canais_faltantes.sort(key=lambda x: x['count_clientes'], reverse=True)
    
    print(f'\n🆕 CANAIS VIXEN SEM CORRESPONDÊNCIA: {len(canais_faltantes)}')
    print('-' * 60)
    
    for i, canal in enumerate(canais_faltantes, 1):
        print(f"{i:2d}. '{canal['canal_nome']}' - {canal['count_clientes']} clientes")
    
    # Salvar lista para atualização manual
    output_file = 'CANAIS_VIXEN_SEM_UUID.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# CANAIS VIXEN SEM CORRESPONDÊNCIA NOS 171 EXISTENTES\n')
        f.write('# Data: 2025-10-30\n')
        f.write('# Total: {} canais\n'.format(len(canais_faltantes)))
        f.write('# FORMATO: canal_nome | count_clientes | uuid_manual\n')
        f.write('#' + '=' * 60 + '\n\n')
        
        for canal in canais_faltantes:
            f.write(f"{canal['canal_nome']} | {canal['count_clientes']} | [UUID_AQUI]\n")
        
        f.write('\n\n# INSTRUÇÕES:\n')
        f.write('# 1. Para cada canal, encontre o UUID correspondente na tabela marketing.canais_aquisicao\n')
        f.write('# 2. Se não existir, deixe [UUID_AQUI] para criar novo\n')
        f.write('# 3. Salve o arquivo e execute aplicar_uuids_canais_vixen_manuais.py\n')
    
    print(f'\n💾 Lista salva em: {output_file}')
    print('\n📝 PRÓXIMOS PASSOS:')
    print('1️⃣ Abra o arquivo e preencha os UUIDs corretos')
    print('2️⃣ Para canais sem correspondência, deixe [UUID_AQUI]')
    print('3️⃣ Execute o script de aplicação após preenchimento')
    
    # Resumo estatístico
    total_clientes_faltantes = sum(canal['count_clientes'] for canal in canais_faltantes)
    print(f'\n📊 RESUMO:')
    print(f'   🔸 Canais mapeados: {len(canais_mapeados)}')
    print(f'   🔸 Canais faltantes: {len(canais_faltantes)}')
    print(f'   🔸 Clientes em canais faltantes: {total_clientes_faltantes}')
    print(f'   🔸 % cobertura: {len(canais_mapeados)/(len(canais_mapeados)+len(canais_faltantes))*100:.1f}%')

if __name__ == "__main__":
    extrair_canais_vixen_faltantes()