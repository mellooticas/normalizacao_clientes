#!/usr/bin/env python3
"""
Normalização Lista DAV - Sistema Carne Fácil
============================================

Normaliza dados da pasta originais/controles_gerais/lista_dav:

OBJETIVOS:
1. Processar todos os arquivos mensais (2020-2024)
2. Normalizar Nro.DAV/Nro.O.S. (4200xxx, 4800xxx) para números simples
3. Mapear ID clientes para cruzamento
4. Identificar lojas (42=Suzano, 48=Mauá)
5. Estruturar para cruzamento com vendas e entregas

CAMPOS IMPORTANTES:
- Nro.DAV/Nro.O.S.: OS números (420008332 → 8332)
- ID: Cliente ID para cruzamento
- ID emp.: Loja (42=Suzano, 48=Mauá)
- Dt.entrega: Data de entrega real
- Status: FINALIZADO, PENDENTE, etc.
"""

import pandas as pd
import glob
from datetime import datetime
import re
from pathlib import Path

def analisar_estrutura_arquivos():
    """Analisa estrutura dos arquivos lista_dav"""
    
    print("🔍 === ANÁLISE ESTRUTURA LISTA_DAV === 🔍")
    
    # Lista todos os arquivos
    pattern = 'data/originais/controles_gerais/lista_dav/*.csv'
    arquivos = glob.glob(pattern)
    
    print(f"📁 Encontrados {len(arquivos)} arquivos")
    
    # Analisa alguns arquivos para entender estrutura
    amostras = {
        'mais_antigo': None,
        'mais_recente': None,
        'maior_arquivo': None
    }
    
    tamanhos = []
    
    for arquivo in arquivos:
        nome = Path(arquivo).name
        try:
            df = pd.read_csv(arquivo)
            tamanho = len(df)
            tamanhos.append((arquivo, nome, tamanho, list(df.columns)))
            
            # Identifica extremos
            if 'JAN_24' in nome:
                amostras['mais_recente'] = (arquivo, nome, tamanho, df.columns)
            elif 'NOV_20' in nome:
                amostras['mais_antigo'] = (arquivo, nome, tamanho, df.columns)
                
        except Exception as e:
            print(f"   ❌ Erro em {nome}: {e}")
    
    # Ordena por tamanho
    tamanhos.sort(key=lambda x: x[2], reverse=True)
    amostras['maior_arquivo'] = tamanhos[0]
    
    print(f"\n📊 === ANÁLISE POR ARQUIVO === 📊")
    
    for key, dados in amostras.items():
        if dados:
            arquivo, nome, tamanho, colunas = dados
            print(f"\n🔵 {key.upper()} ({nome}):")
            print(f"   📋 Registros: {tamanho:,}")
            print(f"   📊 Colunas: {len(colunas)}")
            print(f"   📝 Principais: {', '.join(colunas[:8])}...")
    
    # Identifica padrões de colunas
    print(f"\n🔍 === PADRÕES DE COLUNAS === 🔍")
    
    colunas_comuns = None
    variações = {}
    
    for arquivo, nome, tamanho, colunas in tamanhos:
        colunas_set = set(colunas)
        
        if colunas_comuns is None:
            colunas_comuns = colunas_set
        else:
            colunas_comuns = colunas_comuns.intersection(colunas_set)
        
        # Registra variações
        chave_colunas = tuple(sorted(colunas))
        if chave_colunas not in variações:
            variações[chave_colunas] = []
        variações[chave_colunas].append(nome)
    
    print(f"✅ Colunas comuns ({len(colunas_comuns)}):")
    for col in sorted(colunas_comuns):
        print(f"   • {col}")
    
    print(f"\n📊 Variações de estrutura:")
    for i, (colunas, arquivos) in enumerate(variações.items(), 1):
        print(f"   Padrão {i}: {len(arquivos)} arquivos")
        print(f"      Arquivos: {', '.join(arquivos[:5])}{'...' if len(arquivos) > 5 else ''}")
    
    return tamanhos, colunas_comuns

def normalizar_numero_os(nro_os):
    """Normaliza número de OS removendo prefixos"""
    if pd.isna(nro_os):
        return None
    
    nro_str = str(nro_os)
    
    # Remove prefixos 420, 4200, 480, 4800
    # 420008332 → 8332
    # 480003045 → 3045
    
    # Padrão: Remove 420/480 do início
    if nro_str.startswith('420'):
        return nro_str[3:]  # Remove 420
    elif nro_str.startswith('480'):
        return nro_str[3:]  # Remove 480
    
    return nro_str

def identificar_loja(id_emp):
    """Identifica loja pelo ID empresa"""
    
    loja_map = {
        42: 'SUZANO',
        48: 'MAUA'
    }
    
    try:
        id_num = int(id_emp) if pd.notna(id_emp) else None
        return loja_map.get(id_num, f'LOJA_{id_num}')
    except:
        return 'DESCONHECIDA'

def normalizar_arquivo_dav(arquivo_path):
    """Normaliza um arquivo individual"""
    
    nome_arquivo = Path(arquivo_path).name
    
    try:
        # Carrega arquivo
        df = pd.read_csv(arquivo_path)
        
        # Identifica coluna de número OS (pode variar)
        col_nro_os = None
        for col in ['Nro.DAV', 'Nro.O.S.']:
            if col in df.columns:
                col_nro_os = col
                break
        
        if col_nro_os is None:
            print(f"   ❌ {nome_arquivo}: Coluna de número OS não encontrada")
            return None
        
        # Normaliza dados
        df_norm = pd.DataFrame({
            'arquivo_origem': nome_arquivo,
            'id_os_original': df.get('ID DAV', df.get('ID O.S.', None)),
            'nro_os_original': df[col_nro_os],
            'nro_os_normalizado': df[col_nro_os].apply(normalizar_numero_os),
            'cliente_id': df['ID'],
            'cliente_nome': df['Cliente'],
            'vendedor_id': df['ID.1'],
            'vendedor_nome': df['Vendedor'],
            'id_empresa': df['ID emp.'],
            'loja_nome': df['ID emp.'].apply(identificar_loja),
            'data_os': df.get('Dh.DAV', df.get('Dh.O.S.', None)),
            'data_prev_entrega': df['Dt.prev.entrega'],
            'data_entrega': df['Dt.entrega'],
            'status': df['Status'],
            'valor_bruto': df['Vl.bruto'],
            'valor_liquido': df['Vl.líquido'],
            'origem': df['Origem'],
            'meios_contato': df['Meios de Contato'],
            'descricao': df['Descrição']
        })
        
        # Remove registros sem OS
        antes = len(df_norm)
        df_norm = df_norm.dropna(subset=['nro_os_normalizado'])
        depois = len(df_norm)
        
        if antes != depois:
            print(f"   ⚠️ {nome_arquivo}: Removidos {antes - depois} registros sem OS")
        
        return df_norm
        
    except Exception as e:
        print(f"   ❌ {nome_arquivo}: Erro - {e}")
        return None

def processar_todos_arquivos():
    """Processa todos os arquivos da lista_dav"""
    
    print(f"\n🔄 === PROCESSAMENTO COMPLETO === 🔄")
    
    # Lista arquivos
    pattern = 'data/originais/controles_gerais/lista_dav/*.csv'
    arquivos = glob.glob(pattern)
    
    print(f"📂 Processando {len(arquivos)} arquivos...")
    
    # Processa cada arquivo
    todos_dados = []
    estatisticas = {}
    
    for arquivo in sorted(arquivos):
        nome = Path(arquivo).name
        print(f"   📄 Processando: {nome}")
        
        df_norm = normalizar_arquivo_dav(arquivo)
        
        if df_norm is not None:
            todos_dados.append(df_norm)
            
            # Estatísticas
            estatisticas[nome] = {
                'registros': len(df_norm),
                'os_unicas': df_norm['nro_os_normalizado'].nunique(),
                'lojas': df_norm['loja_nome'].value_counts().to_dict(),
                'periodo': f"{df_norm['data_os'].min()} → {df_norm['data_os'].max()}" if 'data_os' in df_norm.columns else 'N/A'
            }
            
            print(f"      ✅ {len(df_norm):,} registros, {df_norm['nro_os_normalizado'].nunique():,} OS únicas")
        
    # Consolida tudo
    if todos_dados:
        df_consolidado = pd.concat(todos_dados, ignore_index=True)
        print(f"\n✅ Consolidação concluída: {len(df_consolidado):,} registros")
        
        return df_consolidado, estatisticas
    else:
        print(f"\n❌ Nenhum dado processado")
        return None, {}

def analisar_dados_consolidados(df):
    """Analisa dados consolidados"""
    
    print(f"\n📊 === ANÁLISE DOS DADOS CONSOLIDADOS === 📊")
    
    print(f"📋 Total de registros: {len(df):,}")
    print(f"🎯 OS únicas: {df['nro_os_normalizado'].nunique():,}")
    print(f"👥 Clientes únicos: {df['cliente_id'].nunique():,}")
    
    # Por loja
    print(f"\n🏪 Distribuição por loja:")
    loja_stats = df['loja_nome'].value_counts()
    for loja, count in loja_stats.items():
        pct = (count / len(df)) * 100
        print(f"   {loja}: {count:,} ({pct:.1f}%)")
    
    # Por status
    print(f"\n📊 Status das OS:")
    status_stats = df['status'].value_counts()
    for status, count in status_stats.head().items():
        pct = (count / len(df)) * 100
        print(f"   {status}: {count:,} ({pct:.1f}%)")
    
    # Entregas realizadas
    entregas_realizadas = df['data_entrega'].notna().sum()
    pct_entregas = (entregas_realizadas / len(df)) * 100
    print(f"\n🚚 Entregas realizadas: {entregas_realizadas:,} ({pct_entregas:.1f}%)")
    
    # Período dos dados
    try:
        df['data_os'] = pd.to_datetime(df['data_os'], errors='coerce')
        datas_validas = df['data_os'].dropna()
        if len(datas_validas) > 0:
            print(f"📅 Período: {datas_validas.min().strftime('%Y-%m-%d')} → {datas_validas.max().strftime('%Y-%m-%d')}")
    except:
        print(f"📅 Período: Erro ao calcular")

def preparar_cruzamento_vendas(df):
    """Prepara dados para cruzamento com vendas"""
    
    print(f"\n🔗 === PREPARAÇÃO PARA CRUZAMENTO === 🔗")
    
    # Carrega vendas para teste de cruzamento
    try:
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"📂 Vendas carregadas: {len(vendas_df):,}")
        
        # Normaliza OS das vendas
        vendas_df['numero_venda_norm'] = vendas_df['numero_venda'].apply(normalizar_numero_os)
        
        # Testa cruzamento
        os_dav = set(df['nro_os_normalizado'].astype(str))
        os_vendas = set(vendas_df['numero_venda_norm'].astype(str))
        
        overlap = os_dav.intersection(os_vendas)
        
        print(f"🎯 Resultados do cruzamento:")
        print(f"   OS na DAV: {len(os_dav):,}")
        print(f"   OS nas vendas: {len(os_vendas):,}")
        print(f"   OS comuns: {len(overlap):,}")
        print(f"   Cobertura DAV: {len(overlap)/len(os_dav)*100:.1f}%")
        print(f"   Cobertura vendas: {len(overlap)/len(os_vendas)*100:.1f}%")
        
        return overlap
        
    except Exception as e:
        print(f"❌ Erro no teste de cruzamento: {e}")
        return set()

def main():
    """Processo completo de normalização"""
    
    print("🚀 === NORMALIZAÇÃO LISTA DAV === 🚀")
    
    # 1. Analisa estrutura
    tamanhos, colunas_comuns = analisar_estrutura_arquivos()
    
    # 2. Processa todos os arquivos
    df_consolidado, estatisticas = processar_todos_arquivos()
    
    if df_consolidado is None:
        return
    
    # 3. Analisa dados consolidados
    analisar_dados_consolidados(df_consolidado)
    
    # 4. Testa cruzamento com vendas
    overlap = preparar_cruzamento_vendas(df_consolidado)
    
    # 5. Salva resultado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'data/originais/controles_gerais/lista_dav_normalizada_{timestamp}.csv'
    
    df_consolidado.to_csv(output_path, index=False)
    
    print(f"\n💾 Arquivo salvo: {output_path}")
    print(f"📁 Tamanho: {len(df_consolidado):,} registros")
    
    print(f"\n🎯 === PRÓXIMOS PASSOS === 🎯")
    print("1. Revisar cruzamento com vendas")
    print("2. Mapear IDs de clientes")
    print("3. Integrar com entregas existentes")
    print("4. Expandir dados de entregas_os")

if __name__ == "__main__":
    main()