#!/usr/bin/env python3
"""
Análise Completa dos Dados de Entregas - Sistema Carne Fácil
===========================================================

Analisa todos os arquivos os_entregues_dia_*_final.csv para entender:
1. Estrutura dos dados de entregas reais
2. Volume por loja
3. Período coberto
4. Cruzamento com vendas existentes
5. Dados disponíveis vs necessários

Objetivo: Preparar estratégia para entregas_os baseada em dados reais
"""

import pandas as pd
import glob
from datetime import datetime
from pathlib import Path

def analisar_arquivo_entregas(arquivo):
    """Analisa um arquivo individual de entregas"""
    
    loja_nome = arquivo.split('_')[-2]  # Extrai nome da loja
    
    try:
        df = pd.read_csv(arquivo)
        
        # Informações básicas
        info = {
            'loja': loja_nome.upper(),
            'arquivo': arquivo.split('/')[-1],
            'total_registros': len(df),
            'colunas': list(df.columns),
            'periodo_inicio': None,
            'periodo_fim': None,
            'os_unicas': 0,
            'entregas_carne': 0,
            'entregas_nao_carne': 0
        }
        
        # Analisa datas
        if 'data_movimento' in df.columns:
            df['data_movimento'] = pd.to_datetime(df['data_movimento'], errors='coerce')
            datas_validas = df['data_movimento'].dropna()
            
            if len(datas_validas) > 0:
                info['periodo_inicio'] = datas_validas.min().strftime('%Y-%m-%d')
                info['periodo_fim'] = datas_validas.max().strftime('%Y-%m-%d')
        
        # Analisa OS únicas
        if 'os_numero' in df.columns:
            info['os_unicas'] = df['os_numero'].nunique()
        
        # Analisa tipo de entrega
        if 'carne' in df.columns:
            info['entregas_carne'] = len(df[df['carne'] == 'Sim'])
            info['entregas_nao_carne'] = len(df[df['carne'] == 'Não'])
        
        # Amostra dos dados
        info['amostra'] = df.head(3).to_dict('records')
        
        return info
        
    except Exception as e:
        return {
            'loja': loja_nome.upper(),
            'arquivo': arquivo.split('/')[-1],
            'erro': str(e),
            'total_registros': 0
        }

def main():
    """Análise completa dos dados de entregas"""
    
    print("🚚 === ANÁLISE COMPLETA DOS DADOS DE ENTREGAS === 🚚")
    print("📊 Analisando arquivos os_entregues_dia_*_final.csv...")
    
    # Localiza todos os arquivos de entregas
    pattern = 'data/originais/cxs/finais_postgresql_prontos/os_entregues_dia_*_final.csv'
    arquivos = glob.glob(pattern)
    
    if not arquivos:
        print("❌ Nenhum arquivo encontrado!")
        return
    
    print(f"✅ Encontrados {len(arquivos)} arquivos:")
    
    # Analisa cada arquivo
    resultados = []
    total_registros = 0
    total_os_unicas = 0
    
    for arquivo in sorted(arquivos):
        print(f"   📂 Analisando: {arquivo.split('/')[-1]}")
        resultado = analisar_arquivo_entregas(arquivo)
        resultados.append(resultado)
        
        if 'erro' not in resultado:
            total_registros += resultado['total_registros']
            total_os_unicas += resultado['os_unicas']
    
    print(f"\n📊 === RESUMO GERAL === 📊")
    print(f"🏪 Total de lojas: {len([r for r in resultados if 'erro' not in r])}")
    print(f"📋 Total de registros: {total_registros:,}")
    print(f"🎯 Total de OS únicas: {total_os_unicas:,}")
    
    # Detalhes por loja
    print(f"\n🏪 === DETALHES POR LOJA === 🏪")
    
    for resultado in resultados:
        if 'erro' in resultado:
            print(f"❌ {resultado['loja']}: ERRO - {resultado['erro']}")
            continue
            
        print(f"\n🔵 {resultado['loja']}:")
        print(f"   📄 Arquivo: {resultado['arquivo']}")
        print(f"   📊 Registros: {resultado['total_registros']:,}")
        print(f"   🎯 OS únicas: {resultado['os_unicas']:,}")
        
        if resultado['periodo_inicio']:
            print(f"   📅 Período: {resultado['periodo_inicio']} → {resultado['periodo_fim']}")
        
        if resultado.get('entregas_carne', 0) > 0 or resultado.get('entregas_nao_carne', 0) > 0:
            print(f"   🚚 Carnê: {resultado['entregas_carne']:,} | Outros: {resultado['entregas_nao_carne']:,}")
        
        print(f"   📋 Colunas ({len(resultado['colunas'])}): {', '.join(resultado['colunas'])}")
    
    # Análise de estrutura
    print(f"\n🔍 === ANÁLISE DE ESTRUTURA === 🔍")
    
    colunas_comuns = None
    for resultado in resultados:
        if 'erro' in resultado:
            continue
            
        if colunas_comuns is None:
            colunas_comuns = set(resultado['colunas'])
        else:
            colunas_comuns = colunas_comuns.intersection(set(resultado['colunas']))
    
    if colunas_comuns:
        print(f"✅ Colunas comuns a todos os arquivos ({len(colunas_comuns)}):")
        for coluna in sorted(colunas_comuns):
            print(f"   • {coluna}")
    
    # Análise para cruzamento com vendas
    print(f"\n🔗 === ANÁLISE PARA CRUZAMENTO === 🔗")
    
    print("✅ Campos disponíveis para cruzamento:")
    print("   • os_numero - Número da OS (chave principal)")
    print("   • data_movimento - Data da entrega")
    print("   • loja_id - UUID da loja") 
    print("   • vendedor_uuid - UUID do vendedor")
    print("   • carne - Tipo de entrega (Sim/Não)")
    
    # Verificação com vendas existentes
    print(f"\n📊 === CRUZAMENTO COM VENDAS === 📊")
    
    try:
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"✅ Vendas carregadas: {len(vendas_df):,} registros")
        
        # Coleta todas as OS de entregas
        todas_os_entregas = set()
        for arquivo in arquivos:
            try:
                df = pd.read_csv(arquivo)
                if 'os_numero' in df.columns:
                    todas_os_entregas.update(df['os_numero'].dropna().astype(str))
            except:
                continue
        
        print(f"🎯 OS únicas nas entregas: {len(todas_os_entregas):,}")
        
        # Verifica cruzamento
        if 'numero_venda' in vendas_df.columns:
            vendas_os = set(vendas_df['numero_venda'].dropna().astype(str))
            print(f"🎯 OS únicas nas vendas: {len(vendas_os):,}")
            
            # Cruzamento
            os_comuns = todas_os_entregas.intersection(vendas_os)
            os_so_entregas = todas_os_entregas - vendas_os
            os_so_vendas = vendas_os - todas_os_entregas
            
            print(f"\n🔄 CRUZAMENTO:")
            print(f"   ✅ OS em ambos: {len(os_comuns):,}")
            print(f"   📦 Só nas entregas: {len(os_so_entregas):,}")
            print(f"   💰 Só nas vendas: {len(os_so_vendas):,}")
            
            cobertura = (len(os_comuns) / len(vendas_os)) * 100 if vendas_os else 0
            print(f"   📊 Cobertura: {cobertura:.1f}% das vendas têm entrega")
            
    except Exception as e:
        print(f"⚠️ Erro ao carregar vendas: {e}")
    
    # Recomendações
    print(f"\n💡 === RECOMENDAÇÕES === 💡")
    print("🎯 ESTRATÉGIA PARA ENTREGAS_OS:")
    print("   1. Usar dados reais dos arquivos os_entregues_dia_*")
    print("   2. Cruzar por os_numero com vendas existentes")
    print("   3. Complementar com dados mock para vendas sem entrega")
    print("   4. Manter estrutura: os_numero, data_entrega, status, loja_id")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    print("   1. Consolidar todos os arquivos os_entregues_dia_*")
    print("   2. Normalizar datas de entrega")
    print("   3. Fazer cruzamento com vendas por os_numero")
    print("   4. Gerar tabela entregas_os completa")
    
    # Salva análise detalhada
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'ANALISE_ENTREGAS_COMPLETA_{timestamp}.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Análise Completa dos Dados de Entregas\n\n")
        f.write(f"**Data da Análise:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Resumo Geral\n\n")
        f.write(f"- **Total de lojas:** {len([r for r in resultados if 'erro' not in r])}\n")
        f.write(f"- **Total de registros:** {total_registros:,}\n")
        f.write(f"- **Total de OS únicas:** {total_os_unicas:,}\n\n")
        
        f.write("## Detalhes por Loja\n\n")
        for resultado in resultados:
            if 'erro' in resultado:
                continue
            f.write(f"### {resultado['loja']}\n\n")
            f.write(f"- **Registros:** {resultado['total_registros']:,}\n")
            f.write(f"- **OS únicas:** {resultado['os_unicas']:,}\n")
            if resultado['periodo_inicio']:
                f.write(f"- **Período:** {resultado['periodo_inicio']} → {resultado['periodo_fim']}\n")
            f.write(f"- **Colunas:** {', '.join(resultado['colunas'])}\n\n")
    
    print(f"\n💾 Análise detalhada salva em: {output_file}")
    print("🚀 Pronto para implementar entregas_os com dados reais!")

if __name__ == "__main__":
    main()