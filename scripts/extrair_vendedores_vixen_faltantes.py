#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from collections import Counter

def extrair_vendedores_vixen_faltantes():
    """Extrai vendedores VIXEN que precisam de UUID"""
    
    print('👥 EXTRAINDO VENDEDORES VIXEN PARA NORMALIZAÇÃO')
    print('=' * 60)
    
    # Carregar dados VIXEN
    arquivos_vixen = [
        'data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv',
        'data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv'
    ]
    
    todos_vendedores = []
    
    for arquivo in arquivos_vixen:
        try:
            df = pd.read_csv(arquivo)
            loja_nome = 'MAUA' if 'maua' in arquivo else 'SUZANO'
            
            # Extrair vendedores únicos
            vendedores = df['Vendedor'].str.strip().value_counts()
            
            for vendedor, count in vendedores.items():
                if pd.notna(vendedor) and vendedor.strip():
                    todos_vendedores.append({
                        'vendedor_nome': vendedor.strip(),
                        'loja_nome': loja_nome,
                        'count_clientes': count
                    })
            
            print(f'📁 {arquivo.split("/")[-1]}: {len(vendedores)} vendedores únicos')
            
        except Exception as e:
            print(f'❌ Erro ao ler {arquivo}: {e}')
    
    # Consolidar vendedores
    vendedores_consolidados = {}
    for v in todos_vendedores:
        key = f"{v['vendedor_nome']}_{v['loja_nome']}"
        if key in vendedores_consolidados:
            vendedores_consolidados[key]['count_clientes'] += v['count_clientes']
        else:
            vendedores_consolidados[key] = v
    
    # Ordenar por número de clientes
    vendedores_lista = list(vendedores_consolidados.values())
    vendedores_lista.sort(key=lambda x: x['count_clientes'], reverse=True)
    
    print(f'\n👥 VENDEDORES VIXEN ÚNICOS: {len(vendedores_lista)}')
    print('-' * 60)
    
    for i, vendedor in enumerate(vendedores_lista[:20], 1):  # Top 20
        print(f"{i:2d}. '{vendedor['vendedor_nome']}' ({vendedor['loja_nome']}) - {vendedor['count_clientes']} clientes")
    
    if len(vendedores_lista) > 20:
        print(f"... e mais {len(vendedores_lista) - 20} vendedores")
    
    # Salvar lista para mapeamento manual
    output_file = 'VENDEDORES_VIXEN_SEM_UUID.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# VENDEDORES VIXEN PARA NORMALIZAÇÃO DE UUID\n')
        f.write('# Data: 2025-10-30\n')
        f.write('# Total: {} vendedores\n'.format(len(vendedores_lista)))
        f.write('# FORMATO: vendedor_nome | loja_nome | count_clientes | uuid_manual\n')
        f.write('#' + '=' * 80 + '\n\n')
        
        for vendedor in vendedores_lista:
            f.write(f"{vendedor['vendedor_nome']} | {vendedor['loja_nome']} | {vendedor['count_clientes']} | [UUID_AQUI]\n")
        
        f.write('\n\n# INSTRUÇÕES:\n')
        f.write('# 1. Para cada vendedor, procure na tabela vendas.vendedores ou use VENDEDORES_UNICOS_UUID.csv\n')
        f.write('# 2. Se encontrar correspondência, substitua [UUID_AQUI] pelo UUID correto\n')
        f.write('# 3. Se não existir, deixe [UUID_AQUI] para criar novo\n')
        f.write('# 4. Salve o arquivo e execute aplicar_uuids_vendedores_vixen.py\n')
    
    print(f'\n💾 Lista salva em: {output_file}')
    print('\n📝 PRÓXIMOS PASSOS:')
    print('1️⃣ Abra o arquivo e preencha os UUIDs dos vendedores')
    print('2️⃣ Use o arquivo VENDEDORES_UNICOS_UUID.csv como referência')
    print('3️⃣ Para vendedores não encontrados, deixe [UUID_AQUI]')
    print('4️⃣ Execute o script de aplicação após preenchimento')
    
    # Estatísticas
    total_clientes = sum(v['count_clientes'] for v in vendedores_lista)
    print(f'\n📊 ESTATÍSTICAS:')
    print(f'   👥 Vendedores únicos: {len(vendedores_lista)}')
    print(f'   👤 Total de clientes: {total_clientes}')
    print(f'   📈 Média clientes/vendedor: {total_clientes/len(vendedores_lista):.1f}')
    
    # Top 5 vendedores
    print(f'\n🏆 TOP 5 VENDEDORES:')
    for i, v in enumerate(vendedores_lista[:5], 1):
        print(f'   {i}. {v["vendedor_nome"]} ({v["loja_nome"]}) - {v["count_clientes"]} clientes')

if __name__ == "__main__":
    extrair_vendedores_vixen_faltantes()