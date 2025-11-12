#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def investigar_vendedores_vixen():
    """Investiga discrepância entre total de clientes e vendedores"""
    
    print('🔍 INVESTIGANDO DISCREPÂNCIA VENDEDORES VIXEN')
    print('=' * 60)
    
    arquivos = [
        'data/originais/vixen/finais_postgresql_prontos/clientes_maua_final.csv',
        'data/originais/vixen/finais_postgresql_prontos/clientes_suzano_final.csv'
    ]
    
    total_registros = 0
    total_com_vendedor = 0
    total_sem_vendedor = 0
    
    for arquivo in arquivos:
        df = pd.read_csv(arquivo)
        loja = 'MAUA' if 'maua' in arquivo else 'SUZANO'
        
        # Contar registros
        total = len(df)
        
        # Verificar diferentes tipos de "sem vendedor"
        vendedor_notna = df['Vendedor'].notna()
        vendedor_nao_vazio = df['Vendedor'].str.strip() != ''
        
        com_vendedor = (vendedor_notna & vendedor_nao_vazio).sum()
        sem_vendedor_na = df['Vendedor'].isna().sum()
        sem_vendedor_vazio = (df['Vendedor'].str.strip() == '').sum()
        sem_vendedor_total = total - com_vendedor
        
        print(f'📁 {loja}:')
        print(f'   📊 Total registros: {total}')
        print(f'   ✅ Com vendedor: {com_vendedor}')
        print(f'   ❌ Sem vendedor (NA): {sem_vendedor_na}')
        print(f'   ❌ Sem vendedor (vazio): {sem_vendedor_vazio}')
        print(f'   ❌ Total sem vendedor: {sem_vendedor_total}')
        print(f'   📈 % com vendedor: {(com_vendedor/total)*100:.1f}%')
        
        # Mostrar exemplos de registros sem vendedor
        sem_vendedor_df = df[~(vendedor_notna & vendedor_nao_vazio)]
        if len(sem_vendedor_df) > 0:
            print(f'   👀 Primeiros 3 registros sem vendedor:')
            for i, row in sem_vendedor_df.head(3).iterrows():
                vendedor_val = row['Vendedor'] if pd.notna(row['Vendedor']) else '[NA]'
                print(f'      - Cliente: {row["Nome Completo"][:30]}... | Vendedor: "{vendedor_val}"')
        print()
        
        total_registros += total
        total_com_vendedor += com_vendedor
        total_sem_vendedor += sem_vendedor_total
    
    print(f'📊 RESUMO GERAL:')
    print(f'   📋 Total registros VIXEN: {total_registros}')
    print(f'   ✅ Com vendedor: {total_com_vendedor}')
    print(f'   ❌ Sem vendedor: {total_sem_vendedor}')
    print(f'   📈 % cobertura vendedores: {(total_com_vendedor/total_registros)*100:.1f}%')
    
    print(f'\n💡 CONCLUSÃO:')
    print(f'   🔸 Dos {total_registros} clientes VIXEN')
    print(f'   🔸 Apenas {total_com_vendedor} têm vendedor definido')
    print(f'   🔸 {total_sem_vendedor} registros sem vendedor ({(total_sem_vendedor/total_registros)*100:.1f}%)')

if __name__ == "__main__":
    investigar_vendedores_vixen()