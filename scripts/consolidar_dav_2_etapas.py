#!/usr/bin/env python3
"""
Script em 2 etapas para consolidar lista_dav
Etapa 1: Juntar todos os arquivos
Etapa 2: Criar coluna OS numérica sem prefixos
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def etapa1_consolidar_todos_arquivos():
    """
    Etapa 1: Consolida todos os arquivos CSV em um único DataFrame
    """
    print("📋 === ETAPA 1: CONSOLIDAÇÃO BRUTA === 📋")
    
    pasta_dav = "data/originais/controles_gerais/lista_dav"
    arquivos = glob.glob(os.path.join(pasta_dav, "*.csv"))
    
    print(f"📂 Encontrados {len(arquivos)} arquivos")
    
    todos_dados = []
    arquivos_processados = 0
    total_registros = 0
    
    for arquivo in sorted(arquivos):
        nome_arquivo = os.path.basename(arquivo)
        print(f"📄 Processando: {nome_arquivo}...")
        
        try:
            # Tentar carregar com utf-8
            df = pd.read_csv(arquivo, encoding='utf-8')
            if df.empty:
                df = pd.read_csv(arquivo, encoding='latin-1')
        except:
            try:
                df = pd.read_csv(arquivo, encoding='latin-1')
            except Exception as e:
                print(f"❌ Erro em {nome_arquivo}: {e}")
                continue
        
        # Adicionar coluna de origem
        df['arquivo_origem'] = nome_arquivo
        
        # Adicionar ao consolidado
        todos_dados.append(df)
        arquivos_processados += 1
        total_registros += len(df)
        
        print(f"✅ {nome_arquivo}: {len(df)} registros")
    
    # Consolidar tudo
    if todos_dados:
        print(f"\n🔗 Consolidando {arquivos_processados} arquivos...")
        df_consolidado = pd.concat(todos_dados, ignore_index=True, sort=False)
        
        print(f"✅ Consolidação concluída:")
        print(f"   📁 Arquivos: {arquivos_processados}")
        print(f"   📋 Registros: {total_registros:,}")
        print(f"   📊 Colunas únicas: {len(df_consolidado.columns)}")
        
        # Salvar consolidado bruto
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_bruto = f"data/originais/controles_gerais/lista_dav_bruto_{timestamp}.csv"
        df_consolidado.to_csv(arquivo_bruto, index=False)
        
        print(f"💾 Arquivo bruto salvo: {arquivo_bruto}")
        return df_consolidado, arquivo_bruto
    
    else:
        print("❌ Nenhum arquivo processado")
        return None, None

def etapa2_criar_coluna_os_numerica(df_consolidado):
    """
    Etapa 2: Criar coluna OS numérica sem prefixos
    """
    print(f"\n🔢 === ETAPA 2: CRIAÇÃO COLUNA OS === 🔢")
    
    # Identificar colunas que podem ter números de OS
    colunas_os = []
    for col in df_consolidado.columns:
        if any(termo in col for termo in ['Nro.DAV', 'Nro.O.S.', 'ID DAV', 'ID O.S.']):
            colunas_os.append(col)
    
    print(f"📊 Colunas de OS encontradas: {colunas_os}")
    
    # Criar coluna OS consolidada
    df_consolidado['os_raw'] = None
    
    # Prioridade: Nro.DAV ou Nro.O.S. primeiro
    for col in ['Nro.DAV', 'Nro.O.S.']:
        if col in df_consolidado.columns:
            mask = df_consolidado['os_raw'].isna() & df_consolidado[col].notna()
            df_consolidado.loc[mask, 'os_raw'] = df_consolidado.loc[mask, col]
            print(f"✅ Preenchido com {col}: {mask.sum():,} registros")
    
    # Se ainda tem vazios, tentar outras colunas
    for col in ['ID DAV', 'ID O.S.']:
        if col in df_consolidado.columns:
            mask = df_consolidado['os_raw'].isna() & df_consolidado[col].notna()
            df_consolidado.loc[mask, 'os_raw'] = df_consolidado.loc[mask, col]
            print(f"✅ Preenchido com {col}: {mask.sum():,} registros")
    
    # Processar os_raw para criar OS numérica
    def processar_os(valor):
        """Converte OS para numérico removendo prefixos"""
        if pd.isna(valor):
            return None
        
        # Converter para string e limpar
        valor_str = str(valor).strip()
        
        # Remove .0 se existir
        if valor_str.endswith('.0'):
            valor_str = valor_str[:-2]
        
        # Remove prefixos 4200 e 4800
        if valor_str.startswith('4200'):
            valor_str = valor_str[4:]  # Remove 4200
        elif valor_str.startswith('4800'):
            valor_str = valor_str[4:]  # Remove 4800
        
        # Tentar converter para int (isso remove zeros à esquerda automaticamente)
        try:
            return int(valor_str)
        except:
            return None
    
    print(f"\n🔄 Processando números de OS...")
    df_consolidado['OS'] = df_consolidado['os_raw'].apply(processar_os)
    
    # Estatísticas
    os_preenchidas = df_consolidado['OS'].notna().sum()
    os_unicas = df_consolidado['OS'].nunique()
    
    print(f"✅ OS processadas: {os_preenchidas:,} de {len(df_consolidado):,} registros")
    print(f"🎯 OS únicas: {os_unicas:,}")
    
    if os_preenchidas > 0:
        print(f"📊 Range OS: {df_consolidado['OS'].min()} → {df_consolidado['OS'].max()}")
        print(f"📋 Exemplos: {df_consolidado['OS'].dropna().head(10).tolist()}")
    
    # Filtrar apenas registros com OS válidas
    df_final = df_consolidado[df_consolidado['OS'].notna()].copy()
    
    print(f"\n📋 Dataset final: {len(df_final):,} registros com OS válidas")
    
    return df_final

def processar_lista_dav_completa():
    """
    Processo completo em 2 etapas
    """
    print("🚀 === PROCESSAMENTO COMPLETO LISTA_DAV === 🚀")
    
    # Etapa 1: Consolidar arquivos
    df_bruto, arquivo_bruto = etapa1_consolidar_todos_arquivos()
    
    if df_bruto is None:
        print("❌ Falha na etapa 1")
        return
    
    # Etapa 2: Criar coluna OS
    df_final = etapa2_criar_coluna_os_numerica(df_bruto)
    
    # Salvar arquivo final
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_final = f"data/originais/controles_gerais/lista_dav_final_{timestamp}.csv"
    
    df_final.to_csv(arquivo_final, index=False)
    
    # Análises finais
    print(f"\n📊 === ANÁLISES FINAIS === 📊")
    
    # Por arquivo origem
    print(f"📋 Registros por arquivo:")
    origem_stats = df_final.groupby('arquivo_origem').agg({
        'OS': ['count', 'nunique']
    }).round(0)
    origem_stats.columns = ['registros', 'os_unicas']
    print(origem_stats.head(10))
    
    # Identificar lojas por ID emp. se existir
    if 'ID emp.' in df_final.columns:
        print(f"\n🏪 Por ID empresa:")
        loja_stats = df_final.groupby('ID emp.')['OS'].count()
        for loja_id, count in loja_stats.items():
            loja_nome = 'SUZANO' if str(loja_id) == '42' else 'MAUA' if str(loja_id) == '48' else f'LOJA_{loja_id}'
            print(f"   {loja_nome} (ID {loja_id}): {count:,} OS")
    
    # Período
    if 'Dh.DAV' in df_final.columns or 'Dh.O.S.' in df_final.columns:
        col_data = 'Dh.DAV' if 'Dh.DAV' in df_final.columns else 'Dh.O.S.'
        df_final['data_os'] = pd.to_datetime(df_final[col_data], errors='coerce')
        data_min = df_final['data_os'].min()
        data_max = df_final['data_os'].max()
        print(f"\n📅 Período: {data_min.strftime('%Y-%m-%d')} → {data_max.strftime('%Y-%m-%d')}")
    
    # Valores
    if 'Vl.líquido' in df_final.columns:
        df_final['valor_num'] = pd.to_numeric(df_final['Vl.líquido'], errors='coerce')
        valor_total = df_final['valor_num'].sum()
        valor_medio = df_final['valor_num'].mean()
        print(f"\n💰 Valores:")
        print(f"   Total: R$ {valor_total:,.2f}")
        print(f"   Médio: R$ {valor_medio:.2f}")
    
    print(f"\n💾 === ARQUIVOS GERADOS === 💾")
    print(f"📁 Bruto: {arquivo_bruto}")
    print(f"🎯 Final: {arquivo_final}")
    print(f"📊 Registros finais: {len(df_final):,}")
    print(f"🔢 OS únicas: {df_final['OS'].nunique():,}")
    
    # Preparar para cruzamento
    arquivo_cruzamento = f"data/originais/controles_gerais/lista_dav_cruzamento_{timestamp}.csv"
    df_cruzamento = df_final[['arquivo_origem', 'OS'] + [col for col in df_final.columns if col in ['Cliente', 'Vendedor', 'Vl.líquido', 'Status', 'ID emp.']]].copy()
    df_cruzamento.to_csv(arquivo_cruzamento, index=False)
    print(f"🔗 Cruzamento: {arquivo_cruzamento}")
    
    print(f"\n🎯 Pronto para cruzamento com vendas usando coluna 'OS'!")
    
    return arquivo_final

if __name__ == "__main__":
    arquivo_final = processar_lista_dav_completa()
    print(f"\n✅ Processamento concluído!")
    print(f"📅 Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")