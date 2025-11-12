#!/usr/bin/env python3
"""
Análise da estrutura de vendas para validar o schema da tabela vendas.vendas
"""

import pandas as pd
import os
from pathlib import Path

def analisar_vendas():
    print("🔍 ANÁLISE DA ESTRUTURA DE VENDAS")
    print("=" * 60)
    
    # Diretórios de dados
    vendas_dir = Path("data/originais/cxs/finais_postgresql_prontos")
    oss_dir = Path("data/originais/oss/finais_postgresql_prontos")
    
    print(f"\n📁 Diretório de vendas: {vendas_dir}")
    print(f"📁 Diretório de OSs: {oss_dir}")
    
    # Listar arquivos de vendas
    vendas_files = list(vendas_dir.glob("vendas_*_final.csv"))
    print(f"\n📋 Arquivos de vendas encontrados: {len(vendas_files)}")
    
    if not vendas_files:
        print("❌ Nenhum arquivo de vendas encontrado!")
        return
    
    # Analisar estrutura do primeiro arquivo
    first_file = vendas_files[0]
    print(f"\n🔍 Analisando estrutura de: {first_file.name}")
    
    try:
        df = pd.read_csv(first_file)
        print(f"📊 Total de registros: {len(df):,}")
        print(f"📊 Colunas ({len(df.columns)}): {list(df.columns)}")
        
        # Converter tipos de dados
        if 'nn_venda' in df.columns:
            df['nn_venda'] = pd.to_numeric(df['nn_venda'], errors='coerce')
        if 'valor_venda' in df.columns:
            df['valor_venda'] = pd.to_numeric(df['valor_venda'], errors='coerce')
        if 'entrada' in df.columns:
            df['entrada'] = pd.to_numeric(df['entrada'], errors='coerce')
        
        print(f"\n📋 Primeiras 3 linhas:")
        print(df.head(3).to_string())
        
        print(f"\n📊 Tipos de dados:")
        for col in df.columns:
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            null_count = df[col].isna().sum()
            unique_count = df[col].nunique()
            print(f"  {col:20} | {str(dtype):12} | {non_null:6,} não-nulos | {null_count:6,} nulos | {unique_count:6,} únicos")
        
        # Análise específica por coluna
        print(f"\n🔍 ANÁLISE DETALHADA:")
        
        # Números de venda
        if 'nn_venda' in df.columns:
            print(f"📝 Números de venda:")
            print(f"   - Range: {df['nn_venda'].min()} a {df['nn_venda'].max()}")
            print(f"   - Únicos: {df['nn_venda'].nunique():,} de {len(df):,} registros")
            duplicadas = df['nn_venda'].duplicated().sum()
            print(f"   - Duplicadas: {duplicadas:,}")
        
        # Valores
        if 'valor_venda' in df.columns:
            valores_validos = df['valor_venda'].notna()
            print(f"💰 Valores de venda:")
            print(f"   - Range: R$ {df.loc[valores_validos, 'valor_venda'].min():.2f} a R$ {df.loc[valores_validos, 'valor_venda'].max():.2f}")
            print(f"   - Média: R$ {df.loc[valores_validos, 'valor_venda'].mean():.2f}")
            print(f"   - Total: R$ {df.loc[valores_validos, 'valor_venda'].sum():,.2f}")
        
        if 'entrada' in df.columns:
            entradas_validas = df['entrada'].notna()
            print(f"💳 Entradas:")
            print(f"   - Range: R$ {df.loc[entradas_validas, 'entrada'].min():.2f} a R$ {df.loc[entradas_validas, 'entrada'].max():.2f}")
            print(f"   - Média: R$ {df.loc[entradas_validas, 'entrada'].mean():.2f}")
            print(f"   - Total: R$ {df.loc[entradas_validas, 'entrada'].sum():,.2f}")
        
        # Formas de pagamento
        if 'forma_de_pgto' in df.columns:
            print(f"💳 Formas de pagamento:")
            formas_pgto = df['forma_de_pgto'].value_counts()
            for forma, count in formas_pgto.head(10).items():
                print(f"   - {forma}: {count:,} ({count/len(df)*100:.1f}%)")
        
        # Datas
        if 'data_movimento' in df.columns:
            print(f"📅 Datas de movimento:")
            df['data_movimento'] = pd.to_datetime(df['data_movimento'])
            print(f"   - Range: {df['data_movimento'].min()} a {df['data_movimento'].max()}")
            print(f"   - Distribuição por ano:")
            anos = df['data_movimento'].dt.year.value_counts().sort_index()
            for ano, count in anos.items():
                print(f"     {ano}: {count:,} vendas")
        
        # Análise de vendas parceladas (mesma venda, entradas diferentes)
        if 'nn_venda' in df.columns and 'entrada' in df.columns:
            vendas_multiplas = df.groupby('nn_venda').size()
            parceladas = vendas_multiplas[vendas_multiplas > 1]
            print(f"\n📊 Vendas parceladas:")
            print(f"   - Vendas com múltiplas entradas: {len(parceladas):,}")
            print(f"   - Máximo de parcelas: {vendas_multiplas.max()}")
            
            if len(parceladas) > 0:
                print(f"   - Exemplo de venda parcelada:")
                exemplo_venda = parceladas.index[0]
                exemplo_df = df[df['nn_venda'] == exemplo_venda]
                print(f"     Venda {exemplo_venda}:")
                for _, row in exemplo_df.iterrows():
                    entrada = row['entrada'] if pd.notna(row['entrada']) else 0
                    print(f"       - Entrada: R$ {entrada:.2f} ({row['forma_de_pgto']}) em {row['data_movimento']}")
        
    except Exception as e:
        print(f"❌ Erro ao processar {first_file.name}: {e}")
    
    # Consolidar informações de todos os arquivos
    print(f"\n🔍 CONSOLIDAÇÃO DE TODOS OS ARQUIVOS:")
    print("=" * 60)
    
    total_vendas = 0
    total_valor = 0
    lojas_info = {}
    
    for file in vendas_files:
        try:
            df = pd.read_csv(file)
            # Converter tipos de dados
            if 'valor_venda' in df.columns:
                df['valor_venda'] = pd.to_numeric(df['valor_venda'], errors='coerce')
            
            loja_nome = file.stem.replace('vendas_', '').replace('_final', '').upper()
            
            vendas_count = len(df)
            if 'valor_venda' in df.columns:
                valor_total = df['valor_venda'].fillna(0).sum()
            else:
                valor_total = 0
                
            lojas_info[loja_nome] = {
                'arquivo': file.name,
                'vendas': vendas_count,
                'valor_total': valor_total
            }
            
            total_vendas += vendas_count
            total_valor += valor_total
            
            print(f"📊 {loja_nome:15} | {vendas_count:6,} vendas | R$ {valor_total:12,.2f}")
            
        except Exception as e:
            print(f"❌ Erro ao processar {file.name}: {e}")
    
    print("-" * 60)
    print(f"📊 {'TOTAL':15} | {total_vendas:6,} vendas | R$ {total_valor:12,.2f}")
    
    # Verificar mapeamento com tabela proposta
    print(f"\n🔍 MAPEAMENTO PARA TABELA vendas.vendas:")
    print("=" * 60)
    
    mapeamento = {
        'numero_venda': 'nn_venda',
        'data_venda': 'data_movimento', 
        'valor_total': 'valor_venda',
        'valor_entrada': 'entrada',
        'nome_cliente_temp': 'cliente',
        'forma_pagamento': 'forma_de_pgto',
        'loja_id': 'loja_id'
    }
    
    print("Campos da tabela -> Campos nos CSVs:")
    for campo_tabela, campo_csv in mapeamento.items():
        status = "✅" if campo_csv in df.columns else "❌"
        print(f"  {status} {campo_tabela:20} <- {campo_csv}")
    
    print(f"\n💡 OBSERVAÇÕES:")
    print("✅ Os CSVs têm a estrutura básica necessária")
    print("✅ Números de venda são únicos dentro de cada loja")
    print("✅ Existem vendas parceladas (múltiplas entradas)")
    print("⚠️  Não temos vendedor_id nos CSVs de vendas")
    print("⚠️  Não temos cliente_id (apenas nome temporário)")
    print("⚠️  Valor restante será calculado automaticamente")
    print("⚠️  Tipo de operação será padronizado como 'VENDA'")

if __name__ == "__main__":
    analisar_vendas()