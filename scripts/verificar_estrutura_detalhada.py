#!/usr/bin/env python3
"""
INVESTIGADOR DE COLUNAS E DADOS FALTANTES
================================================================
Verifica exatamente quais colunas existem e onde estão
os vendedores sem UUID para entender a discrepância.
================================================================
"""

import pandas as pd
import os

def verificar_estrutura_arquivos():
    """Verifica a estrutura de cada arquivo"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    print("🔍 VERIFICANDO ESTRUTURA DE TODOS OS ARQUIVOS")
    print("=" * 60)
    
    total_sem_uuid = 0
    detalhes_sem_uuid = []
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    
                    print(f"\n🏪 {loja.upper()}:")
                    print(f"   📊 Total de registros: {len(df)}")
                    print(f"   📋 Colunas: {list(df.columns)}")
                    
                    # Verifica coluna vendedor (pode ter nomes diferentes)
                    colunas_vendedor = [col for col in df.columns if 'vendedor' in col.lower()]
                    
                    if colunas_vendedor:
                        print(f"   👥 Colunas de vendedor encontradas: {colunas_vendedor}")
                        
                        for col_vendedor in colunas_vendedor:
                            if col_vendedor != 'vendedor_uuid':
                                # Usa esta coluna como vendedor
                                vendedores_validos = df[col_vendedor].dropna()
                                vendedores_validos = vendedores_validos[vendedores_validos != '']
                                
                                print(f"   📈 Vendedores válidos em '{col_vendedor}': {len(vendedores_validos)}")
                                print(f"   🔢 Vendedores únicos: {len(vendedores_validos.unique())}")
                                
                                if 'vendedor_uuid' in df.columns:
                                    # Verifica UUIDs
                                    sem_uuid = df[df['vendedor_uuid'].isna() | (df['vendedor_uuid'] == '') | (df['vendedor_uuid'] == 'N/A')]
                                    sem_uuid_com_vendedor = sem_uuid[sem_uuid[col_vendedor].notna() & (sem_uuid[col_vendedor] != '')]
                                    
                                    if len(sem_uuid_com_vendedor) > 0:
                                        print(f"   ❌ Registros sem UUID: {len(sem_uuid_com_vendedor)}")
                                        vendedores_sem_uuid = sem_uuid_com_vendedor[col_vendedor].unique()
                                        print(f"   👤 Vendedores únicos sem UUID: {len(vendedores_sem_uuid)}")
                                        print(f"   📝 Lista: {list(vendedores_sem_uuid)[:10]}...")  # Primeiros 10
                                        
                                        total_sem_uuid += len(sem_uuid_com_vendedor)
                                        detalhes_sem_uuid.append({
                                            'tabela': tabela,
                                            'loja': loja,
                                            'registros_sem_uuid': len(sem_uuid_com_vendedor),
                                            'vendedores_unicos': list(vendedores_sem_uuid),
                                            'coluna_vendedor': col_vendedor
                                        })
                                    else:
                                        print(f"   ✅ Todos os vendedores têm UUID")
                                else:
                                    print(f"   ❌ Coluna 'vendedor_uuid' NÃO ENCONTRADA")
                                    # Todos sem UUID
                                    vendedores_sem_uuid = vendedores_validos.unique()
                                    total_sem_uuid += len(vendedores_validos)
                                    detalhes_sem_uuid.append({
                                        'tabela': tabela,
                                        'loja': loja,
                                        'registros_sem_uuid': len(vendedores_validos),
                                        'vendedores_unicos': list(vendedores_sem_uuid),
                                        'coluna_vendedor': col_vendedor
                                    })
                    else:
                        print(f"   ⚠️ NENHUMA coluna de vendedor encontrada")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao processar: {e}")
            else:
                print(f"   ⚠️ Arquivo não encontrado")
    
    return total_sem_uuid, detalhes_sem_uuid

def main():
    print("🚀 INICIANDO VERIFICAÇÃO DETALHADA DE ESTRUTURA")
    print("=" * 60)
    
    total_sem_uuid, detalhes = verificar_estrutura_arquivos()
    
    print(f"\n📊 RESUMO FINAL")
    print("=" * 40)
    print(f"📋 Total de registros sem UUID: {total_sem_uuid:,}")
    print(f"📁 Arquivos com problemas: {len(detalhes)}")
    
    if detalhes:
        print(f"\n🎯 DETALHES DOS PROBLEMAS:")
        for item in detalhes:
            print(f"   📋 {item['tabela']} / {item['loja']}: {item['registros_sem_uuid']} registros sem UUID")
            print(f"       Coluna: {item['coluna_vendedor']}")
            print(f"       Vendedores únicos: {len(item['vendedores_unicos'])}")
    
    print(f"\n✅ VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()