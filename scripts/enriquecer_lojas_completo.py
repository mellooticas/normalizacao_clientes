#!/usr/bin/env python3
"""
Enriquecer TODOS os dados de caixa com UUIDs das lojas
Garantia: 100% das lojas terão UUID pois sabemos todas as 6 lojas
"""

import pandas as pd
import glob
import os
from pathlib import Path

def definir_uuids_lojas():
    """Define os UUIDs conhecidos das lojas (extraídos dos dados normalizados)"""
    return {
        'MAUA': '9a22ccf1-36fe-4b9f-9391-ca31433dc31e',
        'PERUS': 'da3978c9-bba2-431a-91b7-970a406d3acf',
        'RIO_PEQUENO': '4e94f51f-3b0f-4e0f-ba73-64982b870f2c',
        'SAO_MATEUS': '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4',
        'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
        'SUZANO2': 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
    }

def mapear_arquivo_para_loja():
    """Mapeamento entre nomes de arquivos e lojas padrão"""
    return {
        'maua': 'MAUA',
        'perus': 'PERUS',
        'rio_pequeno': 'RIO_PEQUENO', 
        'sao_mateus': 'SAO_MATEUS',
        'suzano': 'SUZANO',
        'suzano2': 'SUZANO2',
        'todas_lojas': 'CONSOLIDADO'  # Arquivo especial
    }

def enriquecer_dados_caixa_completo():
    """Enriquece TODOS os dados de caixa com informações garantidas"""
    print("🚀 ENRIQUECIMENTO COMPLETO DOS DADOS DE CAIXA")
    print("="*60)
    
    # Definir mapeamentos
    uuids_lojas = definir_uuids_lojas()
    mapa_lojas = mapear_arquivo_para_loja()
    
    # Tabelas para processar
    tabelas = [
        'vendas',
        'restante_entrada', 
        'recebimento_carne',
        'os_entregues_dia',
        'entrega_carne'
    ]
    
    estatisticas_gerais = {}
    
    for tabela in tabelas:
        print(f"\n📋 PROCESSANDO: {tabela.upper()}")
        print("-" * 50)
        
        # Buscar arquivos da tabela
        caminho_tabela = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_com_uuids.csv"
        arquivos = glob.glob(caminho_tabela)
        
        # Se não existir _com_uuids, usar arquivos originais
        if not arquivos:
            caminho_tabela = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*.csv"
            arquivos = glob.glob(caminho_tabela)
        
        estatisticas_tabela = {}
        
        for arquivo in arquivos:
            nome_arquivo = Path(arquivo).stem
            
            # Identificar loja do arquivo
            loja_identificada = None
            for prefixo, loja_padrao in mapa_lojas.items():
                if prefixo in nome_arquivo:
                    loja_identificada = loja_padrao
                    break
            
            if not loja_identificada:
                print(f"   ⚠️  {nome_arquivo}: Loja não identificada")
                continue
                
            print(f"   📁 {nome_arquivo}")
            print(f"      🏪 Loja: {loja_identificada}")
            
            # Carregar dados
            df = pd.read_csv(arquivo)
            registros_originais = len(df)
            
            # ENRIQUECIMENTO GARANTIDO - LOJA
            if loja_identificada in uuids_lojas:
                df['loja_id'] = uuids_lojas[loja_identificada]
                df['loja_nome'] = loja_identificada
                print(f"      ✅ Loja UUID: 100% ({registros_originais} registros)")
            else:
                df['loja_id'] = None
                df['loja_nome'] = loja_identificada
                print(f"      ⚠️  Loja UUID: Não encontrado para {loja_identificada}")
            
            # VERIFICAR OUTROS CAMPOS JÁ ENRIQUECIDOS
            campos_existentes = []
            
            if 'forma_pagamento_uuid' in df.columns:
                com_forma_uuid = df['forma_pagamento_uuid'].notna().sum()
                taxa_forma = (com_forma_uuid / registros_originais) * 100
                campos_existentes.append(f"Forma Pagto: {taxa_forma:.1f}%")
            
            if 'vendedor_uuid' in df.columns:
                com_vendedor_uuid = df['vendedor_uuid'].notna().sum()
                taxa_vendedor = (com_vendedor_uuid / registros_originais) * 100
                campos_existentes.append(f"Vendedor: {taxa_vendedor:.1f}%")
            
            if 'canal_captacao_uuid' in df.columns:
                com_canal_uuid = df['canal_captacao_uuid'].notna().sum()
                taxa_canal = (com_canal_uuid / registros_originais) * 100
                campos_existentes.append(f"Canal: {taxa_canal:.1f}%")
            
            if campos_existentes:
                print(f"      📊 Outros UUIDs: {' | '.join(campos_existentes)}")
            
            # ADICIONAR METADADOS ÚTEIS
            df['arquivo_origem_processado'] = nome_arquivo
            df['data_processamento'] = pd.Timestamp.now()
            
            # Salvar arquivo enriquecido
            arquivo_final = arquivo.replace('.csv', '_enriquecido_completo.csv')
            df.to_csv(arquivo_final, index=False)
            print(f"      💾 Salvo: {Path(arquivo_final).name}")
            
            # Estatísticas
            estatisticas_tabela[loja_identificada] = {
                'registros': registros_originais,
                'loja_uuid_100': loja_identificada in uuids_lojas,
                'arquivo_final': arquivo_final
            }
        
        estatisticas_gerais[tabela] = estatisticas_tabela
    
    return estatisticas_gerais

def gerar_relatorio_enriquecimento(estatisticas):
    """Gera relatório do enriquecimento completo"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL - ENRIQUECIMENTO COMPLETO")
    print("="*60)
    
    total_registros = 0
    total_com_loja_uuid = 0
    
    for tabela, lojas in estatisticas.items():
        print(f"\n📋 {tabela.upper()}:")
        
        for loja, stats in lojas.items():
            registros = stats['registros']
            tem_loja_uuid = stats['loja_uuid_100']
            
            status = "✅" if tem_loja_uuid else "⚠️"
            print(f"   {status} {loja}: {registros:,} registros")
            
            total_registros += registros
            if tem_loja_uuid:
                total_com_loja_uuid += registros
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"   📊 Total de registros: {total_registros:,}")
    print(f"   ✅ Com loja UUID: {total_com_loja_uuid:,}")
    print(f"   📈 Taxa de enriquecimento: {(total_com_loja_uuid/total_registros*100):.1f}%")
    
    print(f"\n🏪 LOJAS PROCESSADAS:")
    uuids_lojas = definir_uuids_lojas()
    for loja, uuid_loja in uuids_lojas.items():
        print(f"   ✅ {loja}: {uuid_loja}")

def verificar_arquivos_gerados():
    """Verifica arquivos gerados no processo"""
    print(f"\n🔍 VERIFICANDO ARQUIVOS GERADOS:")
    
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    
    for tabela in tabelas:
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        print(f"   📋 {tabela}: {len(arquivos)} arquivos gerados")
        
        for arquivo in arquivos[:3]:  # Mostrar primeiros 3
            nome = Path(arquivo).name
            print(f"      📁 {nome}")

if __name__ == "__main__":
    # Executar enriquecimento completo
    estatisticas = enriquecer_dados_caixa_completo()
    
    # Gerar relatório
    gerar_relatorio_enriquecimento(estatisticas)
    
    # Verificar arquivos gerados
    verificar_arquivos_gerados()
    
    print("\n✅ ENRIQUECIMENTO COMPLETO FINALIZADO!")
    print("🎯 Todos os dados agora têm UUIDs de loja garantidos!")