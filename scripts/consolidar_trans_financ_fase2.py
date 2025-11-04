#!/usr/bin/env python3
"""
Consolidador Trans Financ - Fase 2
Divide o arquivo consolidado em documentos menores organizados
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def dividir_trans_financ():
    """Divide o arquivo consolidado em documentos menores organizados"""
    
    print("📂 DIVISÃO TRANS FINANC - FASE 2")
    print("=" * 50)
    
    # Carregar arquivo consolidado
    pasta_base = Path("data/originais/controles_gerais/trans_financ/trans_financ_consolidado")
    arquivo_consolidado = pasta_base / "trans_financ_consolidado_completo.csv"
    
    print(f"📊 Carregando: {arquivo_consolidado}")
    
    try:
        df = pd.read_csv(arquivo_consolidado, encoding='utf-8')
        print(f"✅ {len(df):,} registros carregados")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Criar estrutura de subpastas
    subpastas = {
        'por_origem': pasta_base / "por_origem",
        'por_ano': pasta_base / "por_ano", 
        'por_trimestre': pasta_base / "por_trimestre",
        'por_tipo_operacao': pasta_base / "por_tipo_operacao",
        'amostras': pasta_base / "amostras"
    }
    
    # Criar todas as subpastas
    for nome, pasta in subpastas.items():
        pasta.mkdir(exist_ok=True)
        print(f"📁 Criada: {nome}")
    
    print(f"\n🔄 INICIANDO DIVISÕES:")
    print("-" * 30)
    
    # 1. Divisão por Origem
    dividir_por_origem(df, subpastas['por_origem'])
    
    # 2. Divisão por Ano
    dividir_por_ano(df, subpastas['por_ano'])
    
    # 3. Divisão por Trimestre
    dividir_por_trimestre(df, subpastas['por_trimestre'])
    
    # 4. Divisão por Tipo de Operação
    dividir_por_tipo_operacao(df, subpastas['por_tipo_operacao'])
    
    # 5. Criar Amostras Específicas
    criar_amostras(df, subpastas['amostras'])
    
    # 6. Criar Índice Geral
    criar_indice_geral(df, pasta_base, subpastas)
    
    print(f"\n🎉 DIVISÃO CONCLUÍDA!")
    print(f"📊 Estrutura organizada em: {pasta_base}")

def dividir_por_origem(df, pasta_destino):
    """Divide por origem das transações"""
    
    print(f"\n1️⃣ DIVISÃO POR ORIGEM:")
    
    if 'Origem' not in df.columns:
        print("   ❌ Coluna 'Origem' não encontrada")
        return
    
    # Limpar e normalizar origens
    df['Origem_Limpa'] = df['Origem'].str.strip()
    origens_unicas = df['Origem_Limpa'].value_counts()
    
    print(f"   🎯 {len(origens_unicas)} origens encontradas")
    
    for origem, count in origens_unicas.items():
        if pd.isna(origem) or origem == '':
            nome_arquivo = "origem_vazia.csv"
        else:
            # Limpar nome para arquivo
            nome_limpo = origem.replace('/', '_').replace('\\', '_').replace(':', '_')
            nome_limpo = ''.join(c for c in nome_limpo if c.isalnum() or c in '._- ')
            nome_arquivo = f"{nome_limpo.strip()}.csv"
        
        # Filtrar dados desta origem
        df_origem = df[df['Origem_Limpa'] == origem].copy()
        
        # Salvar arquivo
        arquivo_origem = pasta_destino / nome_arquivo
        df_origem.to_csv(arquivo_origem, index=False, encoding='utf-8')
        
        print(f"   📄 {nome_arquivo}: {count:,} registros")
    
    print(f"   ✅ {len(origens_unicas)} arquivos criados em: {pasta_destino}")

def dividir_por_ano(df, pasta_destino):
    """Divide por ano"""
    
    print(f"\n2️⃣ DIVISÃO POR ANO:")
    
    if 'mes_origem' not in df.columns:
        print("   ❌ Coluna 'mes_origem' não encontrada")
        return
    
    # Extrair ano
    df['ano'] = df['mes_origem'].str[:4]
    anos_unicos = df['ano'].value_counts().sort_index()
    
    print(f"   📅 {len(anos_unicos)} anos encontrados")
    
    for ano, count in anos_unicos.items():
        if pd.isna(ano):
            continue
            
        # Filtrar dados do ano
        df_ano = df[df['ano'] == ano].copy()
        
        # Salvar arquivo
        arquivo_ano = pasta_destino / f"trans_financ_{ano}.csv"
        df_ano.to_csv(arquivo_ano, index=False, encoding='utf-8')
        
        print(f"   📄 {ano}: {count:,} registros")
    
    print(f"   ✅ {len(anos_unicos)} arquivos criados em: {pasta_destino}")

def dividir_por_trimestre(df, pasta_destino):
    """Divide por trimestre"""
    
    print(f"\n3️⃣ DIVISÃO POR TRIMESTRE:")
    
    if 'mes_origem' not in df.columns:
        print("   ❌ Coluna 'mes_origem' não encontrada")
        return
    
    # Criar coluna trimestre
    def calcular_trimestre(mes_origem):
        if pd.isna(mes_origem):
            return "INDEFINIDO"
        
        try:
            ano = mes_origem[:4]
            mes = int(mes_origem[5:7])
            
            if mes in [1, 2, 3]:
                return f"{ano}_Q1"
            elif mes in [4, 5, 6]:
                return f"{ano}_Q2"
            elif mes in [7, 8, 9]:
                return f"{ano}_Q3"
            else:
                return f"{ano}_Q4"
        except:
            return "INDEFINIDO"
    
    df['trimestre'] = df['mes_origem'].apply(calcular_trimestre)
    trimestres_unicos = df['trimestre'].value_counts().sort_index()
    
    print(f"   📊 {len(trimestres_unicos)} trimestres encontrados")
    
    for trimestre, count in trimestres_unicos.items():
        if trimestre == "INDEFINIDO":
            continue
            
        # Filtrar dados do trimestre
        df_trimestre = df[df['trimestre'] == trimestre].copy()
        
        # Salvar arquivo
        arquivo_trimestre = pasta_destino / f"trans_financ_{trimestre}.csv"
        df_trimestre.to_csv(arquivo_trimestre, index=False, encoding='utf-8')
        
        print(f"   📄 {trimestre}: {count:,} registros")
    
    print(f"   ✅ {len(trimestres_unicos)-1} arquivos criados em: {pasta_destino}")

def dividir_por_tipo_operacao(df, pasta_destino):
    """Divide por tipo de operação baseado na origem"""
    
    print(f"\n4️⃣ DIVISÃO POR TIPO OPERAÇÃO:")
    
    # Categorizar operações
    def categorizar_operacao(origem):
        if pd.isna(origem):
            return "INDEFINIDO"
        
        origem_upper = str(origem).upper()
        
        if 'ORDEM' in origem_upper or 'PDV' in origem_upper:
            return "VENDAS"
        elif 'SANGRIA' in origem_upper:
            return "CONTROLE_CAIXA"
        elif 'CORRENTISTA' in origem_upper:
            return "RECEBIMENTOS"
        elif 'FUNDO' in origem_upper:
            return "FUNDOS"
        elif 'VENDA' in origem_upper:
            return "VENDAS_DIRETAS"
        else:
            return "OUTROS"
    
    df['tipo_operacao'] = df['Origem'].apply(categorizar_operacao)
    tipos_unicos = df['tipo_operacao'].value_counts()
    
    print(f"   🏷️ {len(tipos_unicos)} tipos encontrados")
    
    for tipo, count in tipos_unicos.items():
        # Filtrar dados do tipo
        df_tipo = df[df['tipo_operacao'] == tipo].copy()
        
        # Salvar arquivo
        arquivo_tipo = pasta_destino / f"tipo_{tipo.lower()}.csv"
        df_tipo.to_csv(arquivo_tipo, index=False, encoding='utf-8')
        
        print(f"   📄 {tipo}: {count:,} registros")
    
    print(f"   ✅ {len(tipos_unicos)} arquivos criados em: {pasta_destino}")

def criar_amostras(df, pasta_destino):
    """Cria amostras específicas para análise"""
    
    print(f"\n5️⃣ CRIANDO AMOSTRAS:")
    
    amostras = {
        'amostra_1000_registros': df.sample(min(1000, len(df))),
        'amostra_vendas_recentes': df[df['Origem'].str.contains('ORDEM', na=False)].tail(500),
        'amostra_valores_altos': df.nlargest(100, 'Vl.líquido') if 'Vl.líquido' in df.columns else df.head(100),
        'amostra_por_mes': df.groupby('mes_origem').apply(lambda x: x.sample(min(10, len(x)))).reset_index(drop=True)
    }
    
    for nome, amostra_df in amostras.items():
        if len(amostra_df) > 0:
            arquivo_amostra = pasta_destino / f"{nome}.csv"
            amostra_df.to_csv(arquivo_amostra, index=False, encoding='utf-8')
            print(f"   📄 {nome}: {len(amostra_df)} registros")
    
    print(f"   ✅ {len(amostras)} amostras criadas em: {pasta_destino}")

def criar_indice_geral(df, pasta_base, subpastas):
    """Cria índice geral de todos os arquivos criados"""
    
    print(f"\n6️⃣ CRIANDO ÍNDICE GERAL:")
    
    indice = {
        'resumo_geral': {
            'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_registros_originais': len(df),
            'periodo_abrangido': f"{df['mes_origem'].min()} a {df['mes_origem'].max()}",
            'colunas_totais': len(df.columns)
        },
        'estrutura_criada': {},
        'estatisticas_resumidas': {
            'origens_unicas': df['Origem'].nunique() if 'Origem' in df.columns else 0,
            'anos_abrangidos': df['mes_origem'].str[:4].nunique() if 'mes_origem' in df.columns else 0,
            'valor_total': float(df['Vl.líquido'].sum()) if 'Vl.líquido' in df.columns else 0
        }
    }
    
    # Mapear arquivos criados
    for nome_pasta, pasta in subpastas.items():
        arquivos = list(pasta.glob("*.csv"))
        indice['estrutura_criada'][nome_pasta] = {
            'total_arquivos': len(arquivos),
            'arquivos': [arquivo.name for arquivo in arquivos]
        }
        print(f"   📁 {nome_pasta}: {len(arquivos)} arquivos")
    
    # Salvar índice
    arquivo_indice = pasta_base / "indice_geral_trans_financ.json"
    
    with open(arquivo_indice, 'w', encoding='utf-8') as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)
    
    print(f"   📊 Índice salvo: {arquivo_indice}")

if __name__ == "__main__":
    dividir_trans_financ()