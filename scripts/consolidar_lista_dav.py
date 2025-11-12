#!/usr/bin/env python3
"""
Script para consolidar e normalizar todos os arquivos da lista_dav
Gerando um arquivo único e estruturado para trabalho
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def normalizar_numero_os(numero_str):
    """
    Normaliza números de OS removendo prefixos 4200/4800
    """
    if pd.isna(numero_str):
        return None
    
    numero_str = str(numero_str).strip()
    
    # Remove .0 se existir
    if numero_str.endswith('.0'):
        numero_str = numero_str[:-2]
    
    # Remove prefixos conhecidos
    if numero_str.startswith('4200'):
        return numero_str[4:]  # Remove prefixo 4200
    elif numero_str.startswith('4800'):
        return numero_str[4:]  # Remove prefixo 4800
    
    return numero_str

def identificar_loja_por_prefixo(numero_str, id_empresa=None):
    """
    Identifica loja pelo prefixo do número da OS
    """
    if pd.isna(numero_str):
        return None
    
    numero_str = str(numero_str).strip()
    
    if numero_str.startswith('4200'):
        return 'SUZANO'
    elif numero_str.startswith('4800'):
        return 'MAUA'
    elif id_empresa:
        if str(id_empresa) == '42':
            return 'SUZANO'
        elif str(id_empresa) == '48':
            return 'MAUA'
    
    return f'LOJA_{str(id_empresa) if id_empresa else "DESCONHECIDA"}'

def processar_arquivo_dav(caminho_arquivo):
    """
    Processa um arquivo individual da lista_dav
    """
    try:
        # Carregar arquivo
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        
        # Se falhar com utf-8, tentar latin-1
        if df.empty:
            df = pd.read_csv(caminho_arquivo, encoding='latin-1')
            
    except Exception as e:
        try:
            df = pd.read_csv(caminho_arquivo, encoding='latin-1')
        except Exception as e2:
            print(f"❌ Erro ao processar {caminho_arquivo}: {e2}")
            return None
    
    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"📄 Processando: {nome_arquivo} ({len(df)} registros)")
    
    # Identificar colunas principais
    colunas_mapeamento = {
        # Número da OS/DAV
        'Nro.DAV': 'nro_os',
        'Nro.O.S.': 'nro_os',
        'ID DAV': 'id_os',
        'ID O.S.': 'id_os',
        
        # Cliente
        'Cliente': 'cliente_nome',
        'ID': 'cliente_id',
        'ID.1': 'cliente_id_alt',
        
        # Vendedor
        'Vendedor': 'vendedor_nome',
        'ID.2': 'vendedor_id',
        
        # Datas
        'Dh.DAV': 'data_os',
        'Dh.O.S.': 'data_os',
        'Dt.entrega': 'data_entrega',
        'Dt.prev.entrega': 'data_prev_entrega',
        
        # Valores
        'Vl.bruto': 'valor_bruto',
        'Vl.líquido': 'valor_liquido',
        'Vl.desconto': 'valor_desconto',
        'Vl.acréscimo': 'valor_acrescimo',
        
        # Outros
        'Status': 'status',
        'Origem': 'origem',
        'Descrição': 'descricao',
        'Meios de Contato': 'meios_contato',
        'ID emp.': 'id_empresa',
        'Operador': 'operador'
    }
    
    # Renomear colunas disponíveis
    df_normalizado = pd.DataFrame()
    df_normalizado['arquivo_origem'] = nome_arquivo
    
    for col_original, col_nova in colunas_mapeamento.items():
        if col_original in df.columns:
            df_normalizado[col_nova] = df[col_original]
        else:
            df_normalizado[col_nova] = None
    
    # Processar número da OS
    # Verificar se encontramos alguma coluna de OS
    col_os_encontrada = None
    if 'nro_os' in df_normalizado.columns and df_normalizado['nro_os'].notna().any():
        col_os_encontrada = 'nro_os'
    
    if col_os_encontrada:
        df_normalizado['nro_os_original'] = df_normalizado[col_os_encontrada]
        df_normalizado['nro_os_normalizado'] = df_normalizado[col_os_encontrada].apply(normalizar_numero_os)
        
        # Identificar loja
        df_normalizado['loja_identificada'] = df_normalizado.apply(
            lambda row: identificar_loja_por_prefixo(row[col_os_encontrada], row['id_empresa']), axis=1
        )
        
        # Limpar registros sem OS
        df_normalizado = df_normalizado[df_normalizado['nro_os_normalizado'].notna()]
        
        if len(df_normalizado) == 0:
            print(f"⚠️ {nome_arquivo}: Nenhum registro válido após limpeza")
            return None
            
        print(f"✅ {nome_arquivo}: {len(df_normalizado)} registros processados")
        return df_normalizado
    else:
        print(f"⚠️ {nome_arquivo}: Coluna de número OS não encontrada ou vazia")
        print(f"   Colunas disponíveis: {list(df.columns)}")
        return None

def consolidar_lista_dav():
    """
    Consolida todos os arquivos da lista_dav em um arquivo único
    """
    
    print("📋 === CONSOLIDAÇÃO COMPLETA LISTA_DAV === 📋")
    
    # 1. Localizar todos os arquivos
    pasta_dav = "data/originais/controles_gerais/lista_dav"
    arquivos = glob.glob(os.path.join(pasta_dav, "*.csv"))
    
    print(f"\n📂 Encontrados {len(arquivos)} arquivos CSV")
    
    # 2. Processar cada arquivo
    print(f"\n🔄 === PROCESSANDO ARQUIVOS === 🔄")
    
    todos_dados = []
    arquivos_processados = 0
    arquivos_com_erro = 0
    total_registros = 0
    
    for arquivo in sorted(arquivos):
        df_processado = processar_arquivo_dav(arquivo)
        
        if df_processado is not None:
            todos_dados.append(df_processado)
            arquivos_processados += 1
            total_registros += len(df_processado)
        else:
            arquivos_com_erro += 1
    
    # 3. Consolidar todos os dados
    print(f"\n📊 === CONSOLIDANDO DADOS === 📊")
    
    if todos_dados:
        df_consolidado = pd.concat(todos_dados, ignore_index=True)
        
        print(f"✅ Consolidação concluída:")
        print(f"   📁 Arquivos processados: {arquivos_processados}")
        print(f"   ❌ Arquivos com erro: {arquivos_com_erro}")
        print(f"   📋 Total de registros: {total_registros:,}")
        print(f"   🎯 OS únicas: {df_consolidado['nro_os_normalizado'].nunique():,}")
        
        # 4. Análises do consolidado
        print(f"\n📊 === ANÁLISES DO CONSOLIDADO === 📊")
        
        print(f"🏪 Distribuição por loja:")
        loja_dist = df_consolidado['loja_identificada'].value_counts()
        for loja, qtd in loja_dist.items():
            print(f"   {loja}: {qtd:,} OS ({qtd/len(df_consolidado)*100:.1f}%)")
        
        print(f"\n📅 Período dos dados:")
        df_consolidado['data_os_dt'] = pd.to_datetime(df_consolidado['data_os'], errors='coerce')
        data_min = df_consolidado['data_os_dt'].min()
        data_max = df_consolidado['data_os_dt'].max()
        print(f"   {data_min.strftime('%Y-%m-%d')} → {data_max.strftime('%Y-%m-%d')}")
        
        print(f"\n💰 Valores:")
        df_consolidado['valor_liquido_num'] = pd.to_numeric(df_consolidado['valor_liquido'], errors='coerce')
        valor_total = df_consolidado['valor_liquido_num'].sum()
        valor_medio = df_consolidado['valor_liquido_num'].mean()
        print(f"   Total: R$ {valor_total:,.2f}")
        print(f"   Médio: R$ {valor_medio:.2f}")
        
        print(f"\n📊 Status das OS:")
        status_dist = df_consolidado['status'].value_counts()
        for status, qtd in status_dist.head(5).items():
            print(f"   {status}: {qtd:,} OS ({qtd/len(df_consolidado)*100:.1f}%)")
        
        # 5. Salvar arquivo consolidado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_consolidado = f"data/originais/controles_gerais/lista_dav_consolidada_{timestamp}.csv"
        
        df_consolidado.to_csv(arquivo_consolidado, index=False, encoding='utf-8')
        
        print(f"\n💾 === ARQUIVO CONSOLIDADO SALVO === 💾")
        print(f"📁 Arquivo: {arquivo_consolidado}")
        print(f"📊 Registros: {len(df_consolidado):,}")
        print(f"📋 Colunas: {len(df_consolidado.columns)}")
        print(f"🎯 OS únicas: {df_consolidado['nro_os_normalizado'].nunique():,}")
        
        # 6. Gerar arquivo de estatísticas
        arquivo_stats = f"data/originais/controles_gerais/lista_dav_estatisticas_{timestamp}.csv"
        
        stats_dados = []
        for arquivo in sorted(arquivos):
            nome = os.path.basename(arquivo)
            df_temp = df_consolidado[df_consolidado['arquivo_origem'] == nome]
            if len(df_temp) > 0:
                stats_dados.append({
                    'arquivo': nome,
                    'registros': len(df_temp),
                    'os_unicas': df_temp['nro_os_normalizado'].nunique(),
                    'loja_principal': df_temp['loja_identificada'].mode().iloc[0] if len(df_temp) > 0 else None,
                    'periodo_inicio': df_temp['data_os_dt'].min(),
                    'periodo_fim': df_temp['data_os_dt'].max(),
                    'valor_total': df_temp['valor_liquido_num'].sum()
                })
        
        df_stats = pd.DataFrame(stats_dados)
        df_stats.to_csv(arquivo_stats, index=False)
        print(f"📊 Estatísticas salvas: {arquivo_stats}")
        
        # 7. Preparar para cruzamento
        print(f"\n🔗 === PREPARAÇÃO PARA CRUZAMENTO === 🔗")
        
        # Criar versão para cruzamento (OS simples)
        df_cruzamento = df_consolidado.copy()
        df_cruzamento['os_para_cruzamento'] = df_cruzamento['nro_os_normalizado'].apply(
            lambda x: str(x).lstrip('0') if x else None
        )
        
        arquivo_cruzamento = f"data/originais/controles_gerais/lista_dav_para_cruzamento_{timestamp}.csv"
        df_cruzamento.to_csv(arquivo_cruzamento, index=False)
        print(f"🎯 Arquivo para cruzamento: {arquivo_cruzamento}")
        print(f"📊 OS únicas para cruzamento: {df_cruzamento['os_para_cruzamento'].nunique():,}")
        
        return arquivo_consolidado, arquivo_cruzamento
        
    else:
        print("❌ Nenhum arquivo foi processado com sucesso")
        return None, None

if __name__ == "__main__":
    arquivo_principal, arquivo_cruzamento = consolidar_lista_dav()
    
    if arquivo_principal:
        print(f"\n🎯 === CONSOLIDAÇÃO CONCLUÍDA === 🎯")
        print(f"✅ Arquivo principal: {arquivo_principal}")
        print(f"🔗 Arquivo para cruzamento: {arquivo_cruzamento}")
        print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ === FALHA NA CONSOLIDAÇÃO === ❌")