#!/usr/bin/env python3
"""
Script para consolidar todos os arquivos conf_dav (produtos) em um único CSV
Primeira fase: consolidação de todos os arquivos
Segunda fase: normalização dos números DAV
"""

import pandas as pd
import glob
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def consolidar_conf_dav():
    """
    Consolida todos os arquivos conf_dav em um único arquivo
    """
    print("🎯 === CONSOLIDAÇÃO CONF_DAV (PRODUTOS) === 🎯")
    
    # Diretório dos arquivos
    diretorio = 'data/originais/controles_gerais/conf_dav'
    
    # Buscar todos os arquivos CSV
    padrao = os.path.join(diretorio, '*.csv')
    arquivos = glob.glob(padrao)
    
    print(f"📋 Diretório: {diretorio}")
    print(f"📄 Arquivos encontrados: {len(arquivos)}")
    
    if not arquivos:
        print("❌ Nenhum arquivo CSV encontrado!")
        return False
    
    # Lista para armazenar dados
    dados_consolidados = []
    resumo_arquivos = []
    
    print(f"\n🔄 === PROCESSANDO ARQUIVOS === 🔄")
    
    for i, arquivo in enumerate(sorted(arquivos), 1):
        nome_arquivo = os.path.basename(arquivo)
        print(f"\n📄 {i:2d}/{len(arquivos)} - {nome_arquivo}")
        
        try:
            # Carregar arquivo
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Verificar se tem dados
            if len(df) == 0:
                print(f"   ⚠️  Arquivo vazio")
                continue
            
            # Adicionar coluna de origem
            df['arquivo_origem'] = nome_arquivo
            
            # Adicionar período baseado no nome do arquivo
            periodo = extrair_periodo_nome(nome_arquivo)
            df['periodo'] = periodo
            
            print(f"   ✅ {len(df):,} registros | Colunas: {df.shape[1]} | Período: {periodo}")
            
            # Verificar estrutura
            if 'Nro.DAV' in df.columns:
                dav_count = df['Nro.DAV'].notna().sum()
                dav_unique = df['Nro.DAV'].nunique()
                print(f"   📊 DAVs: {dav_count:,} registros, {dav_unique:,} únicos")
                
                # Analisar prefixos dos DAVs
                dav_sample = df['Nro.DAV'].dropna().astype(str).head(5).tolist()
                print(f"   🔍 Amostra DAVs: {', '.join(dav_sample)}")
            
            # Resumo para relatório
            resumo_arquivos.append({
                'arquivo': nome_arquivo,
                'registros': len(df),
                'colunas': df.shape[1],
                'periodo': periodo,
                'dav_count': dav_count if 'Nro.DAV' in df.columns else 0,
                'dav_unique': dav_unique if 'Nro.DAV' in df.columns else 0
            })
            
            # Adicionar aos dados consolidados
            dados_consolidados.append(df)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue
    
    if not dados_consolidados:
        print("❌ Nenhum arquivo processado com sucesso!")
        return False
    
    print(f"\n🔄 === CONSOLIDANDO DADOS === 🔄")
    
    # Consolidar todos os dados
    df_consolidado = pd.concat(dados_consolidados, ignore_index=True, sort=False)
    
    print(f"📊 Total de registros: {len(df_consolidado):,}")
    print(f"📋 Total de colunas: {df_consolidado.shape[1]}")
    print(f"📄 Arquivos processados: {len(dados_consolidados)}")
    
    # Análise geral
    print(f"\n📊 === ANÁLISE CONSOLIDADA === 📊")
    
    if 'Nro.DAV' in df_consolidado.columns:
        total_dav = df_consolidado['Nro.DAV'].notna().sum()
        unique_dav = df_consolidado['Nro.DAV'].nunique()
        print(f"📋 DAVs totais: {total_dav:,}")
        print(f"📋 DAVs únicos: {unique_dav:,}")
        
        # Análise de empresas
        if 'Emp.' in df_consolidado.columns:
            empresas = df_consolidado['Emp.'].value_counts()
            print(f"🏢 Empresas: {len(empresas)} diferentes")
            for emp, count in empresas.head(10).items():
                print(f"   Emp {emp}: {count:,} registros")
        
        # Análise de prefixos DAV
        print(f"\n🔍 === ANÁLISE PREFIXOS DAV === 🔍")
        df_consolidado['dav_str'] = df_consolidado['Nro.DAV'].astype(str)
        df_consolidado['prefixo_dav'] = df_consolidado['dav_str'].str[:2]
        
        prefixos = df_consolidado['prefixo_dav'].value_counts()
        print(f"📋 Prefixos encontrados: {len(prefixos)}")
        for prefixo, count in prefixos.head(10).items():
            print(f"   Prefixo {prefixo}: {count:,} registros")
    
    # Criar diretório de saída se não existir
    os.makedirs('data/originais/controles_gerais/conf_dav/csv', exist_ok=True)
    
    # Salvar arquivo consolidado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_consolidado = f'data/originais/controles_gerais/conf_dav/csv/conf_dav_consolidado_{timestamp}.csv'
    
    df_consolidado.to_csv(arquivo_consolidado, index=False)
    
    print(f"\n💾 === ARQUIVO CONSOLIDADO === 💾")
    print(f"📄 Arquivo: {arquivo_consolidado}")
    print(f"📊 Registros: {len(df_consolidado):,}")
    print(f"📋 Colunas: {df_consolidado.shape[1]}")
    
    # Salvar resumo dos arquivos
    df_resumo = pd.DataFrame(resumo_arquivos)
    arquivo_resumo = f'data/originais/controles_gerais/conf_dav/csv/resumo_arquivos_{timestamp}.csv'
    df_resumo.to_csv(arquivo_resumo, index=False)
    
    print(f"📋 Resumo: {arquivo_resumo}")
    
    return arquivo_consolidado

def extrair_periodo_nome(nome_arquivo):
    """
    Extrai período do nome do arquivo
    """
    nome = nome_arquivo.upper().replace('.CSV', '')
    
    # Mapeamento de meses
    meses = {
        'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
        'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
        'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
    }
    
    # Tentar extrair mês e ano
    for mes, num in meses.items():
        if mes in nome:
            # Procurar ano
            for ano in ['20', '21', '22', '23', '24', '25']:
                if ano in nome:
                    return f"20{ano}-{num}"
    
    # Se não conseguir, usar nome original
    return nome

def normalizar_dav_produtos():
    """
    Normaliza números DAV removendo prefixos (segunda fase)
    """
    print(f"\n🎯 === NORMALIZAÇÃO NÚMEROS DAV (PRODUTOS) === 🎯")
    
    # Buscar arquivo consolidado mais recente
    padrao = 'data/originais/controles_gerais/conf_dav/csv/conf_dav_consolidado_*.csv'
    arquivos = glob.glob(padrao)
    
    if not arquivos:
        print("❌ Arquivo consolidado não encontrado!")
        return False
    
    arquivo_consolidado = sorted(arquivos)[-1]  # Mais recente
    print(f"📄 Arquivo base: {os.path.basename(arquivo_consolidado)}")
    
    try:
        df = pd.read_csv(arquivo_consolidado)
        print(f"📊 Registros carregados: {len(df):,}")
        
        if 'Nro.DAV' not in df.columns:
            print("❌ Coluna 'Nro.DAV' não encontrada!")
            return False
        
        print(f"\n🔄 === ANÁLISE PREFIXOS === 🔄")
        
        # Converter para string e analisar
        df['dav_original'] = df['Nro.DAV'].astype(str)
        df['dav_limpo'] = df['dav_original'].copy()
        
        # Estatísticas antes
        antes_unique = df['Nro.DAV'].nunique()
        print(f"📊 DAVs únicos antes: {antes_unique:,}")
        
        # Identificar e remover prefixos
        prefixos_removidos = 0
        
        # Prefixos conhecidos (baseado na análise anterior)
        prefixos = ['42', '48', '11', '90', '10', '9']
        
        for prefixo in prefixos:
            # Encontrar DAVs com este prefixo
            mask = df['dav_original'].str.startswith(prefixo) & (df['dav_original'].str.len() > len(prefixo))
            count = mask.sum()
            
            if count > 0:
                print(f"🔍 Prefixo {prefixo}: {count:,} registros")
                
                # Remover prefixo mantendo o resto
                df.loc[mask, 'dav_limpo'] = df.loc[mask, 'dav_original'].str[len(prefixo):]
                prefixos_removidos += count
        
        # Converter para numérico quando possível
        df['dav_numerico'] = pd.to_numeric(df['dav_limpo'], errors='coerce')
        
        # Estatísticas depois
        depois_unique = df['dav_numerico'].nunique()
        numericos_validos = df['dav_numerico'].notna().sum()
        
        print(f"\n📊 === RESULTADOS NORMALIZAÇÃO === 📊")
        print(f"🔧 Prefixos removidos: {prefixos_removidos:,} registros")
        print(f"📊 DAVs únicos depois: {depois_unique:,}")
        print(f"📊 DAVs numéricos válidos: {numericos_validos:,}")
        print(f"📈 Redução de duplicação: {((antes_unique - depois_unique) / antes_unique * 100):.1f}%")
        
        # Análise de faixas
        if numericos_validos > 0:
            min_dav = df['dav_numerico'].min()
            max_dav = df['dav_numerico'].max()
            print(f"📊 Faixa DAV: {min_dav:,.0f} até {max_dav:,.0f}")
        
        # Salvar arquivo normalizado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_normalizado = f'data/originais/controles_gerais/conf_dav/csv/conf_dav_normalizado_{timestamp}.csv'
        
        # Adicionar colunas de controle
        df['dav_normalizado'] = df['dav_numerico']
        df['prefixo_removido'] = df['dav_original'] != df['dav_limpo']
        
        df.to_csv(arquivo_normalizado, index=False)
        
        print(f"\n💾 === ARQUIVO NORMALIZADO === 💾")
        print(f"📄 Arquivo: {arquivo_normalizado}")
        print(f"📊 Registros: {len(df):,}")
        print(f"✅ DAVs normalizados prontos para uso")
        
        return arquivo_normalizado
        
    except Exception as e:
        print(f"❌ Erro na normalização: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 === PROCESSAMENTO COMPLETO CONF_DAV === 🎯")
    print("📋 Fase 1: Consolidação de arquivos")
    print("📋 Fase 2: Normalização de números DAV")
    
    # Fase 1: Consolidar arquivos
    arquivo_consolidado = consolidar_conf_dav()
    
    if not arquivo_consolidado:
        print("❌ Falha na consolidação!")
        return
    
    print(f"\n{'='*50}")
    
    # Fase 2: Normalizar DAVs
    arquivo_normalizado = normalizar_dav_produtos()
    
    if arquivo_normalizado:
        print(f"\n🎉 === PROCESSAMENTO CONCLUÍDO === 🎉")
        print(f"✅ Arquivo final: {arquivo_normalizado}")
        print(f"📋 Status: Dados de produtos consolidados e normalizados")
        print(f"🚀 Próximo: Dados prontos para análise e integração")
    else:
        print(f"\n⚠️ Consolidação ok, mas normalização falhou")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()