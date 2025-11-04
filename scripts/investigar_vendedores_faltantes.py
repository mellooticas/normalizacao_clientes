#!/usr/bin/env python3
"""
INVESTIGADOR DE VENDEDORES FALTANTES - RUMO AOS 100%
================================================================
Identifica EXATAMENTE quais vendedores ainda não têm UUID
em TODAS as tabelas para completar os 100%.
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def investigar_vendedores_faltantes():
    """Investiga todos os vendedores que ainda não possuem UUID"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    
    # Todas as tabelas e lojas
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    vendedores_faltantes = defaultdict(lambda: defaultdict(list))
    estatisticas_completas = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'sem_uuid': 0, 'vendedores_unicos': set()}))
    
    print("🔍 INVESTIGANDO VENDEDORES FALTANTES EM TODAS AS TABELAS")
    print("=" * 70)
    
    total_registros_sem_uuid = 0
    total_vendedores_unicos_faltantes = set()
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    
                    # Verifica se tem colunas necessárias
                    if 'vendedor' in df.columns:
                        total_registros = len(df)
                        
                        if 'vendedor_uuid' in df.columns:
                            # Registros sem UUID
                            sem_uuid = df[df['vendedor_uuid'].isna() | (df['vendedor_uuid'] == '') | (df['vendedor_uuid'] == 'N/A')]
                            
                            # Vendedores únicos sem UUID
                            if not sem_uuid.empty:
                                vendedores_unicos = sem_uuid['vendedor'].dropna().unique()
                                vendedores_unicos = [v for v in vendedores_unicos if str(v).strip() != '' and str(v) != 'nan']
                                
                                if vendedores_unicos:
                                    for vendedor in vendedores_unicos:
                                        vendedor_limpo = str(vendedor).strip()
                                        count = len(sem_uuid[sem_uuid['vendedor'] == vendedor])
                                        vendedores_faltantes[tabela][loja].append({
                                            'vendedor': vendedor_limpo,
                                            'registros': count
                                        })
                                        total_vendedores_unicos_faltantes.add(f"{tabela}_{loja}_{vendedor_limpo}")
                                    
                                    print(f"🏪 {loja}: {len(vendedores_unicos)} vendedores únicos sem UUID ({len(sem_uuid)}/{total_registros} registros)")
                                    total_registros_sem_uuid += len(sem_uuid)
                                else:
                                    print(f"✅ {loja}: Todos vendedores têm UUID ({total_registros} registros)")
                            else:
                                print(f"✅ {loja}: Todos vendedores têm UUID ({total_registros} registros)")
                        else:
                            # Não tem coluna vendedor_uuid - todos sem UUID
                            vendedores_unicos = df['vendedor'].dropna().unique()
                            vendedores_unicos = [v for v in vendedores_unicos if str(v).strip() != '' and str(v) != 'nan']
                            
                            if vendedores_unicos:
                                for vendedor in vendedores_unicos:
                                    vendedor_limpo = str(vendedor).strip()
                                    count = len(df[df['vendedor'] == vendedor])
                                    vendedores_faltantes[tabela][loja].append({
                                        'vendedor': vendedor_limpo,
                                        'registros': count
                                    })
                                    total_vendedores_unicos_faltantes.add(f"{tabela}_{loja}_{vendedor_limpo}")
                                
                                print(f"❌ {loja}: {len(vendedores_unicos)} vendedores sem coluna UUID ({total_registros} registros)")
                                total_registros_sem_uuid += total_registros
                            else:
                                print(f"⚠️ {loja}: Sem vendedores válidos ({total_registros} registros)")
                    else:
                        print(f"⚠️ {loja}: Sem coluna 'vendedor'")
                        
                except Exception as e:
                    print(f"❌ {loja}: Erro - {e}")
            else:
                print(f"⚠️ {loja}: Arquivo não encontrado")
    
    return vendedores_faltantes, total_registros_sem_uuid, len(total_vendedores_unicos_faltantes)

def gerar_lista_completa_faltantes(vendedores_faltantes):
    """Gera lista organizada de todos os vendedores faltantes"""
    
    print(f"\n🎯 GERANDO LISTA COMPLETA DE VENDEDORES FALTANTES")
    print("=" * 60)
    
    # Agrupa todos os vendedores únicos por tabela
    vendedores_globais = defaultdict(set)
    
    for tabela, lojas_data in vendedores_faltantes.items():
        for loja, vendedores_lista in lojas_data.items():
            for vendedor_info in vendedores_lista:
                vendedores_globais[tabela].add(vendedor_info['vendedor'])
    
    # Cria arquivo de mapeamento completo
    with open('vendedores_faltantes_completo.txt', 'w', encoding='utf-8') as f:
        f.write("# VENDEDORES FALTANTES PARA 100% DE COBERTURA\n")
        f.write("# =============================================\n")
        f.write("# INSTRUÇÕES:\n")
        f.write("# 1. Complete os UUIDs para TODOS os vendedores abaixo\n")
        f.write("# 2. Formato: NOME_VENDEDOR = uuid_aqui\n")
        f.write("# 3. Se não deve ter UUID: NOME_VENDEDOR = IGNORAR\n\n")
        
        total_global = 0
        
        for tabela in ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']:
            if tabela in vendedores_globais and vendedores_globais[tabela]:
                f.write(f"# {'='*50}\n")
                f.write(f"# 📋 TABELA: {tabela.upper()}\n")
                f.write(f"# {'='*50}\n")
                f.write(f"# Vendedores únicos: {len(vendedores_globais[tabela])}\n\n")
                
                # Lista detalhada por loja
                for loja in ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']:
                    if loja in vendedores_faltantes[tabela] and vendedores_faltantes[tabela][loja]:
                        f.write(f"# 🏪 LOJA: {loja.upper()}\n")
                        f.write(f"# {'-'*30}\n")
                        
                        for vendedor_info in sorted(vendedores_faltantes[tabela][loja], key=lambda x: x['vendedor']):
                            vendedor = vendedor_info['vendedor']
                            registros = vendedor_info['registros']
                            f.write(f"# {vendedor} ({registros} registros)\n")
                            f.write(f"{vendedor} = \n\n")
                            total_global += 1
                        
                        f.write("\n")
                
                f.write("\n")
        
        f.write(f"# TOTAL DE MAPEAMENTOS NECESSÁRIOS: {total_global}\n")
    
    print(f"📝 Arquivo criado: vendedores_faltantes_completo.txt")
    print(f"📊 Total de mapeamentos necessários: {total_global}")
    
    return total_global

def main():
    print("🚀 INICIANDO INVESTIGAÇÃO COMPLETA - RUMO AOS 100%")
    print("=" * 60)
    
    # Investiga vendedores faltantes
    vendedores_faltantes, total_sem_uuid, vendedores_unicos = investigar_vendedores_faltantes()
    
    print(f"\n📊 RESUMO DA INVESTIGAÇÃO")
    print("=" * 40)
    print(f"📋 Total de registros sem UUID: {total_sem_uuid:,}")
    print(f"👥 Combinações únicas (tabela_loja_vendedor): {vendedores_unicos}")
    
    if vendedores_faltantes:
        # Gera lista completa
        total_mapeamentos = gerar_lista_completa_faltantes(vendedores_faltantes)
        
        print(f"\n🎯 PARA ATINGIR 100%:")
        print(f"1. Abra: vendedores_faltantes_completo.txt")
        print(f"2. Complete {total_mapeamentos} mapeamentos de UUID")
        print(f"3. Execute aplicação final")
        print(f"\n✅ INVESTIGAÇÃO CONCLUÍDA!")
    else:
        print(f"\n🎉 INCRÍVEL! JÁ TEMOS 100% DE COBERTURA!")

if __name__ == "__main__":
    main()