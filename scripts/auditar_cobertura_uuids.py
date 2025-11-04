#!/usr/bin/env python3
"""
Auditoria Completa de UUIDs em todos os arquivos enriquecidos
Verificar cobertura de: loja_id, forma_pagamento_uuid, vendedor_uuid
"""

import pandas as pd
import glob
from pathlib import Path

def auditar_cobertura_uuids():
    """Audita cobertura de UUIDs em todos os arquivos enriquecidos"""
    print("🔍 AUDITORIA COMPLETA DE UUIDs")
    print("="*60)
    
    # Tabelas para verificar
    tabelas = [
        'vendas',
        'restante_entrada', 
        'recebimento_carne',
        'os_entregues_dia',
        'entrega_carne'
    ]
    
    resultados_geral = {}
    campos_faltantes_geral = {}
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        # Buscar arquivos enriquecidos
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        
        # Filtrar apenas lojas individuais
        arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
        
        resultados_tabela = {}
        campos_faltantes_tabela = {}
        
        for arquivo in arquivos_lojas:
            nome_arquivo = Path(arquivo).stem
            loja = nome_arquivo.split('_')[1] if '_' in nome_arquivo else 'DESCONHECIDA'
            
            print(f"\n📁 {nome_arquivo}")
            
            try:
                df = pd.read_csv(arquivo)
                total_registros = len(df)
                
                # Verificar campos UUID
                campos_uuid = {
                    'loja_id': 'Loja UUID',
                    'forma_pagamento_uuid': 'Forma Pagamento UUID',
                    'vendedor_uuid': 'Vendedor UUID'
                }
                
                estatisticas = {}
                campos_faltantes = []
                
                for campo, descricao in campos_uuid.items():
                    if campo in df.columns:
                        com_uuid = df[campo].notna().sum()
                        sem_uuid = df[campo].isna().sum()
                        taxa = (com_uuid / total_registros * 100) if total_registros > 0 else 0
                        
                        status = "✅" if taxa == 100 else "⚠️" if taxa >= 90 else "❌"
                        print(f"   {status} {descricao}: {com_uuid}/{total_registros} ({taxa:.1f}%)")
                        
                        estatisticas[campo] = {
                            'com_uuid': com_uuid,
                            'sem_uuid': sem_uuid,
                            'total': total_registros,
                            'taxa': taxa
                        }
                        
                        # Identificar campos com cobertura < 100%
                        if taxa < 100:
                            campos_faltantes.append({
                                'campo': campo,
                                'descricao': descricao,
                                'faltando': sem_uuid,
                                'taxa': taxa
                            })
                    else:
                        print(f"   ❌ {descricao}: Campo não existe")
                        campos_faltantes.append({
                            'campo': campo,
                            'descricao': descricao,
                            'faltando': total_registros,
                            'taxa': 0
                        })
                
                resultados_tabela[loja] = {
                    'arquivo': nome_arquivo,
                    'total_registros': total_registros,
                    'estatisticas': estatisticas
                }
                
                if campos_faltantes:
                    campos_faltantes_tabela[loja] = campos_faltantes
                
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
        
        resultados_geral[tabela] = resultados_tabela
        if campos_faltantes_tabela:
            campos_faltantes_geral[tabela] = campos_faltantes_tabela
    
    return resultados_geral, campos_faltantes_geral

def gerar_relatorio_faltantes(campos_faltantes_geral):
    """Gera relatório detalhado do que está faltando"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE UUIDs FALTANTES")
    print("="*60)
    
    if not campos_faltantes_geral:
        print("🎉 PARABÉNS! TODOS OS ARQUIVOS TÊM 100% DE UUIDs!")
        return
    
    total_problemas = 0
    
    for tabela, lojas in campos_faltantes_geral.items():
        print(f"\n📋 {tabela.upper()}:")
        
        for loja, campos in lojas.items():
            print(f"\n🏪 {loja}:")
            
            for campo_info in campos:
                campo = campo_info['campo']
                descricao = campo_info['descricao']
                faltando = campo_info['faltando']
                taxa = campo_info['taxa']
                
                if taxa == 0:
                    status = "❌ AUSENTE"
                elif taxa < 50:
                    status = "🔴 CRÍTICO"
                elif taxa < 90:
                    status = "🟡 MÉDIO"
                else:
                    status = "🟠 QUASE"
                
                print(f"   {status} {descricao}: {faltando} registros sem UUID ({taxa:.1f}% cobertura)")
                total_problemas += 1
    
    print(f"\n🎯 RESUMO:")
    print(f"   ⚠️  Total de problemas encontrados: {total_problemas}")

def identificar_valores_unicos_faltantes(campos_faltantes_geral):
    """Identifica valores únicos que precisam de UUID"""
    print("\n" + "="*60)
    print("🔍 VALORES ÚNICOS QUE PRECISAM DE UUID")
    print("="*60)
    
    if not campos_faltantes_geral:
        return
    
    # Focar principalmente em vendedores, que é o mais comum estar faltando
    for tabela, lojas in campos_faltantes_geral.items():
        print(f"\n📋 {tabela.upper()}:")
        
        for loja, campos in lojas.items():
            for campo_info in campos:
                campo = campo_info['campo']
                
                if campo == 'vendedor_uuid':
                    print(f"\n🏪 {loja} - VENDEDORES SEM UUID:")
                    
                    # Carregar arquivo para analisar vendedores únicos
                    caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*{loja.lower()}*_enriquecido_completo.csv"
                    arquivos = glob.glob(caminho)
                    
                    if arquivos:
                        try:
                            df = pd.read_csv(arquivos[0])
                            
                            # Vendedores sem UUID
                            sem_uuid = df[df['vendedor_uuid'].isna()]
                            
                            if 'vendedor' in df.columns:
                                vendedores_unicos = sem_uuid['vendedor'].dropna().unique()
                            elif 'vendedor_nome_normalizado' in df.columns:
                                vendedores_unicos = sem_uuid['vendedor_nome_normalizado'].dropna().unique()
                            else:
                                vendedores_unicos = []
                            
                            if len(vendedores_unicos) > 0:
                                print(f"   📊 {len(vendedores_unicos)} vendedores únicos sem UUID:")
                                for vendedor in sorted(vendedores_unicos)[:10]:  # Mostrar primeiros 10
                                    print(f"      - {vendedor}")
                                if len(vendedores_unicos) > 10:
                                    print(f"      ... e mais {len(vendedores_unicos) - 10}")
                        
                        except Exception as e:
                            print(f"   ❌ Erro ao analisar: {e}")

def gerar_resumo_executivo(resultados_geral):
    """Gera resumo executivo da auditoria"""
    print("\n" + "="*60)
    print("📊 RESUMO EXECUTIVO DA AUDITORIA")
    print("="*60)
    
    total_arquivos = 0
    total_registros = 0
    
    # Estatísticas por campo UUID
    stats_campos = {
        'loja_id': {'com_uuid': 0, 'total': 0},
        'forma_pagamento_uuid': {'com_uuid': 0, 'total': 0},
        'vendedor_uuid': {'com_uuid': 0, 'total': 0}
    }
    
    for tabela, lojas in resultados_geral.items():
        for loja, dados in lojas.items():
            total_arquivos += 1
            total_registros += dados['total_registros']
            
            for campo, stats in dados['estatisticas'].items():
                if campo in stats_campos:
                    stats_campos[campo]['com_uuid'] += stats['com_uuid']
                    stats_campos[campo]['total'] += stats['total']
    
    print(f"📁 Total de arquivos analisados: {total_arquivos}")
    print(f"📊 Total de registros: {total_registros:,}")
    print()
    
    print("🎯 COBERTURA GERAL DE UUIDs:")
    for campo, stats in stats_campos.items():
        if stats['total'] > 0:
            taxa = (stats['com_uuid'] / stats['total'] * 100)
            status = "✅" if taxa == 100 else "⚠️" if taxa >= 90 else "❌"
            
            nome_campo = {
                'loja_id': 'Loja UUID',
                'forma_pagamento_uuid': 'Forma Pagamento UUID', 
                'vendedor_uuid': 'Vendedor UUID'
            }.get(campo, campo)
            
            print(f"   {status} {nome_campo}: {stats['com_uuid']:,}/{stats['total']:,} ({taxa:.1f}%)")

def executar_auditoria_completa():
    """Executa auditoria completa de UUIDs"""
    print("🚀 INICIANDO AUDITORIA COMPLETA DE UUIDs")
    print("="*60)
    
    # Executar auditoria
    resultados, campos_faltantes = auditar_cobertura_uuids()
    
    # Gerar relatórios
    gerar_relatorio_faltantes(campos_faltantes)
    identificar_valores_unicos_faltantes(campos_faltantes)
    gerar_resumo_executivo(resultados)
    
    print("\n✅ AUDITORIA CONCLUÍDA!")
    
    return resultados, campos_faltantes

if __name__ == "__main__":
    resultados, faltantes = executar_auditoria_completa()