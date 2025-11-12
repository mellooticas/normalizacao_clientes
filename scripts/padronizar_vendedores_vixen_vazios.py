#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime

def padronizar_vendedores_vixen_vazios():
    """Padroniza vendedores vazios com UUIDs específicos por loja"""
    
    print('🎯 PADRONIZANDO VENDEDORES VAZIOS VIXEN')
    print('=' * 60)
    
    # UUIDs padrão por loja para vendedores vazios
    uuids_padrao = {
        'MAUA': 'd2eb5739-5887-4c3f-86e9-822f60469650',
        'SUZANO': '2fec96c8-d492-49ab-b38a-a5d5452af4d2'
    }
    
    arquivos = [
        ('data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv', 'MAUA'),
        ('data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv', 'SUZANO')
    ]
    
    total_padronizados = 0
    
    for arquivo, loja in arquivos:
        print(f'\n📁 Processando: {loja}')
        
        # Ler arquivo
        df = pd.read_csv(arquivo)
        print(f'   📊 Total registros: {len(df)}')
        
        # Identificar vendedores vazios
        vendedores_vazios = df['Vendedor'].str.strip() == ''
        count_vazios = vendedores_vazios.sum()
        
        print(f'   ❌ Vendedores vazios: {count_vazios}')
        
        # Criar coluna vendedor_uuid se não existir
        if 'vendedor_uuid' not in df.columns:
            df['vendedor_uuid'] = None
        
        # Aplicar UUID padrão para vendedores vazios
        df.loc[vendedores_vazios, 'vendedor_uuid'] = uuids_padrao[loja]
        df.loc[vendedores_vazios, 'Vendedor'] = f'VENDEDOR NÃO INFORMADO - {loja}'
        
        print(f'   ✅ Padronizados: {count_vazios} → {uuids_padrao[loja][:8]}...')
        
        # Adicionar metadados
        df['data_padronizacao_vendedores'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        df['etapa_processamento'] = 'PADRONIZADO_VENDEDORES_VAZIOS'
        
        # Salvar arquivo
        df.to_csv(arquivo, index=False)
        total_padronizados += count_vazios
    
    print(f'\n📊 RESUMO:')
    print(f'   ✅ Total padronizados: {total_padronizados}')
    print(f'   🎯 MAUA (vazios): {uuids_padrao["MAUA"]}')
    print(f'   🎯 SUZANO (vazios): {uuids_padrao["SUZANO"]}')
    
    # Agora extrair todos os vendedores únicos (incluindo os padronizados)
    print(f'\n🔄 Extraindo vendedores únicos após padronização...')
    
    todos_vendedores = []
    
    for arquivo, loja in arquivos:
        df = pd.read_csv(arquivo)
        vendedores = df['Vendedor'].str.strip().value_counts()
        
        for vendedor, count in vendedores.items():
            if pd.notna(vendedor) and vendedor.strip():
                # Verificar se já tem UUID
                vendedor_rows = df[df['Vendedor'].str.strip() == vendedor]
                uuid_existente = vendedor_rows['vendedor_uuid'].iloc[0] if len(vendedor_rows) > 0 else None
                
                todos_vendedores.append({
                    'vendedor_nome': vendedor.strip(),
                    'loja_nome': loja,
                    'count_clientes': count,
                    'uuid_existente': uuid_existente if pd.notna(uuid_existente) else None
                })
    
    # Ordenar por número de clientes
    todos_vendedores.sort(key=lambda x: x['count_clientes'], reverse=True)
    
    # Salvar lista atualizada
    output_file = 'VENDEDORES_VIXEN_COMPLETO.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# VENDEDORES VIXEN APÓS PADRONIZAÇÃO DOS VAZIOS\n')
        f.write('# Data: 2025-10-30\n')
        f.write('# Total: {} vendedores\n'.format(len(todos_vendedores)))
        f.write('# FORMATO: vendedor_nome | loja_nome | count_clientes | uuid_atual | uuid_novo\n')
        f.write('#' + '=' * 80 + '\n\n')
        
        for vendedor in todos_vendedores:
            uuid_atual = vendedor['uuid_existente'] or '[VAZIO]'
            f.write(f"{vendedor['vendedor_nome']} | {vendedor['loja_nome']} | {vendedor['count_clientes']} | {uuid_atual} | [UUID_AQUI]\n")
        
        f.write('\n\n# INSTRUÇÕES:\n')
        f.write('# 1. Vendedores com UUID existente estão marcados na coluna 4\n')
        f.write('# 2. Para vendedores [VAZIO], preencha UUID_AQUI na coluna 5\n')
        f.write('# 3. Use VENDEDORES_UNICOS_UUID.csv como referência\n')
        f.write('# 4. Salve e execute aplicar_uuids_vendedores_vixen_final.py\n')
    
    print(f'   💾 Lista completa salva: {output_file}')
    print(f'   👥 Total vendedores únicos: {len(todos_vendedores)}')
    
    # Estatísticas finais
    vendedores_com_uuid = sum(1 for v in todos_vendedores if v['uuid_existente'])
    vendedores_sem_uuid = len(todos_vendedores) - vendedores_com_uuid
    
    print(f'\n📈 ESTATÍSTICAS:')
    print(f'   ✅ Com UUID: {vendedores_com_uuid}')
    print(f'   ❌ Sem UUID: {vendedores_sem_uuid}')
    print(f'   📊 Cobertura: {(vendedores_com_uuid/len(todos_vendedores))*100:.1f}%')

if __name__ == "__main__":
    padronizar_vendedores_vixen_vazios()