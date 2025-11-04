#!/usr/bin/env python3
"""
INVESTIGADOR DE DISCREPÂNCIA - AUDITORIA vs EXTRATOR
================================================================
Identifica exatamente onde está a diferença entre os números
da auditoria (62.5%) e do extrator (100%).
================================================================
"""

import pandas as pd
import os

def investigar_discrepancia():
    """Investiga a discrepância entre auditoria e extrator"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    print("🔍 INVESTIGANDO DISCREPÂNCIA ENTRE AUDITORIA E EXTRATOR")
    print("=" * 70)
    
    total_registros = 0
    total_com_uuid = 0
    total_sem_uuid = 0
    problemas_encontrados = []
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    total_registros += len(df)
                    
                    print(f"\n🏪 {loja.upper()}:")
                    print(f"   📊 Total de registros: {len(df)}")
                    print(f"   📋 Colunas: {list(df.columns)}")
                    
                    if 'vendedor_uuid' in df.columns:
                        # Análise detalhada de UUIDs
                        
                        # 1. Valores nulos (pd.isna)
                        nulos = df['vendedor_uuid'].isna().sum()
                        
                        # 2. Strings vazias
                        vazios = (df['vendedor_uuid'] == '').sum()
                        
                        # 3. Valores 'N/A'
                        na_strings = (df['vendedor_uuid'] == 'N/A').sum()
                        
                        # 4. Valores válidos (tem algum conteúdo)
                        validos = df['vendedor_uuid'].notna().sum() - vazios - na_strings
                        
                        # 5. UUIDs que realmente parecem UUID (contém hífens)
                        uuids_reais = df[df['vendedor_uuid'].str.contains('-', na=False)]['vendedor_uuid'].count() if 'vendedor_uuid' in df.columns else 0
                        
                        sem_uuid_total = nulos + vazios + na_strings
                        com_uuid_total = len(df) - sem_uuid_total
                        
                        total_com_uuid += com_uuid_total
                        total_sem_uuid += sem_uuid_total
                        
                        print(f"   📊 ANÁLISE DETALHADA DE vendedor_uuid:")
                        print(f"      🔸 Valores nulos (isna): {nulos}")
                        print(f"      🔸 Strings vazias (''): {vazios}")
                        print(f"      🔸 Strings 'N/A': {na_strings}")
                        print(f"      🔸 Valores não vazios: {validos}")
                        print(f"      🔸 UUIDs reais (com -): {uuids_reais}")
                        print(f"      ✅ COM UUID: {com_uuid_total}")
                        print(f"      ❌ SEM UUID: {sem_uuid_total}")
                        
                        percentual = (com_uuid_total / len(df) * 100) if len(df) > 0 else 0
                        print(f"      📈 Percentual: {percentual:.1f}%")
                        
                        if sem_uuid_total > 0:
                            problemas_encontrados.append({
                                'tabela': tabela,
                                'loja': loja,
                                'sem_uuid': sem_uuid_total,
                                'total': len(df),
                                'percentual': percentual
                            })
                        
                        # Verifica se há vendedores (qualquer coluna de vendedor)
                        colunas_vendedor = [col for col in df.columns if 'vendedor' in col.lower() and col != 'vendedor_uuid']
                        if colunas_vendedor:
                            print(f"      👤 Colunas de vendedor: {colunas_vendedor}")
                            for col in colunas_vendedor:
                                vendedores_validos = df[col].dropna()
                                vendedores_validos = vendedores_validos[vendedores_validos != '']
                                print(f"         📊 {col}: {len(vendedores_validos)} registros válidos")
                        
                    else:
                        print(f"   ⚠️ COLUNA vendedor_uuid NÃO EXISTE")
                        total_sem_uuid += len(df)
                        problemas_encontrados.append({
                            'tabela': tabela,
                            'loja': loja,
                            'sem_uuid': len(df),
                            'total': len(df),
                            'percentual': 0
                        })
                        
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
            else:
                print(f"   ⚠️ Arquivo não encontrado")
    
    # Resumo final
    print(f"\n🎯 RESUMO DA INVESTIGAÇÃO")
    print("=" * 50)
    print(f"📊 Total de registros: {total_registros:,}")
    print(f"✅ Registros COM UUID: {total_com_uuid:,}")
    print(f"❌ Registros SEM UUID: {total_sem_uuid:,}")
    
    percentual_global = (total_com_uuid / total_registros * 100) if total_registros > 0 else 0
    print(f"📈 Percentual global: {percentual_global:.1f}%")
    
    if problemas_encontrados:
        print(f"\n🔍 PROBLEMAS ENCONTRADOS: {len(problemas_encontrados)}")
        for problema in problemas_encontrados:
            if problema['sem_uuid'] > 0:
                print(f"   📋 {problema['tabela']}/{problema['loja']}: {problema['sem_uuid']} sem UUID de {problema['total']} ({problema['percentual']:.1f}%)")
    
    print(f"\n🎯 EXPLICAÇÃO DA DISCREPÂNCIA:")
    if percentual_global < 100:
        print(f"   A auditoria estava CORRETA: {percentual_global:.1f}%")
        print(f"   O extrator falhou porque só verificou registros com vendedores válidos")
        print(f"   Existem {total_sem_uuid:,} registros que precisam de UUID")
    else:
        print(f"   TODOS os registros realmente têm UUID!")
    
    return problemas_encontrados

def main():
    print("🚀 INICIANDO INVESTIGAÇÃO DE DISCREPÂNCIA")
    print("=" * 60)
    
    problemas = investigar_discrepancia()
    
    print(f"\n✅ INVESTIGAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()