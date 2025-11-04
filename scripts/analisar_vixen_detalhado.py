#!/usr/bin/env python3
"""
Análise Detalhada VIXEN
=======================

Análise profunda dos dados de clientes VIXEN.
"""

import pandas as pd
from pathlib import Path
import numpy as np

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_dir = base_dir / "data" / "originais" / "vixen"
    arquivo_csv = vixen_dir / "vixen_planilha1.csv"
    
    print("🔍 ANÁLISE DETALHADA VIXEN")
    print("=" * 50)
    
    # Carregar dados
    df = pd.read_csv(arquivo_csv)
    print(f"📊 Total de registros: {len(df):,}")
    print(f"📊 Total de colunas: {len(df.columns)}")
    
    print(f"\n📋 ESTRUTURA DAS COLUNAS:")
    for i, col in enumerate(df.columns, 1):
        nulos = df[col].isnull().sum()
        nao_nulos = len(df) - nulos
        percentual_preenchido = (nao_nulos / len(df)) * 100
        print(f"   {i:2d}. {col:<20} | {nao_nulos:>5,} preenchidos ({percentual_preenchido:5.1f}%)")
    
    print(f"\n🏪 ANÁLISE POR EMPRESA/LOJA:")
    if 'Emp.origem' in df.columns:
        empresas = df['Emp.origem'].value_counts()
        print(f"   Total de empresas: {len(empresas)}")
        for empresa, count in empresas.items():
            print(f"   🔹 {empresa}: {count:,} clientes")
    
    print(f"\n👥 ANÁLISE DE VENDEDORES:")
    if 'Vendedor' in df.columns:
        vendedores = df['Vendedor'].value_counts()
        print(f"   Total de vendedores: {len(vendedores)}")
        print(f"   Top 10 vendedores:")
        for vendedor, count in vendedores.head(10).items():
            print(f"   🔹 {vendedor}: {count:,} clientes")
    
    print(f"\n📍 ANÁLISE GEOGRÁFICA:")
    if 'Cidade' in df.columns:
        cidades = df['Cidade'].value_counts()
        print(f"   Total de cidades: {len(cidades)}")
        print(f"   Top 10 cidades:")
        for cidade, count in cidades.head(10).items():
            print(f"   🔹 {cidade}: {count:,} clientes")
    
    if 'UF' in df.columns:
        ufs = df['UF'].value_counts()
        print(f"\n   Estados (UF):")
        for uf, count in ufs.items():
            print(f"   🔹 {uf}: {count:,} clientes")
    
    print(f"\n📞 CANAIS DE CAPTAÇÃO:")
    if 'Como nos conheceu' in df.columns:
        canais = df['Como nos conheceu'].value_counts()
        print(f"   Total de canais: {len(canais)}")
        for canal, count in canais.head(10).items():
            if pd.notna(canal):
                print(f"   🔹 {canal}: {count:,} clientes")
    
    print(f"\n👤 ANÁLISE DEMOGRÁFICA:")
    if 'Sexo' in df.columns:
        sexos = df['Sexo'].value_counts()
        for sexo, count in sexos.items():
            if pd.notna(sexo):
                percentual = (count / len(df)) * 100
                print(f"   🔹 {sexo}: {count:,} clientes ({percentual:.1f}%)")
    
    print(f"\n📅 ANÁLISE TEMPORAL:")
    if 'Dh.inclusão' in df.columns:
        df_temp = df.copy()
        df_temp['Dh.inclusão'] = pd.to_datetime(df_temp['Dh.inclusão'], errors='coerce')
        
        # Extrair anos
        anos = df_temp['Dh.inclusão'].dt.year.value_counts().sort_index()
        print(f"   Cadastros por ano:")
        for ano, count in anos.items():
            if pd.notna(ano):
                print(f"   🔹 {int(ano)}: {count:,} cadastros")
    
    print(f"\n📧 QUALIDADE DOS DADOS:")
    
    # Verificar duplicações
    duplicados_cliente = df['Cliente'].duplicated().sum()
    duplicados_nome = df['Nome Completo'].duplicated().sum()
    duplicados_id = df['ID'].duplicated().sum()
    
    print(f"   📊 Duplicações:")
    print(f"   🔹 IDs duplicados: {duplicados_id:,}")
    print(f"   🔹 Clientes duplicados: {duplicados_cliente:,}")
    print(f"   🔹 Nomes duplicados: {duplicados_nome:,}")
    
    # Verificar dados essenciais
    sem_nome = df['Nome Completo'].isnull().sum()
    sem_empresa = df['Emp.origem'].isnull().sum() if 'Emp.origem' in df.columns else 0
    sem_vendedor = df['Vendedor'].isnull().sum() if 'Vendedor' in df.columns else 0
    
    print(f"\n   📊 Dados essenciais faltantes:")
    print(f"   🔹 Sem nome completo: {sem_nome:,}")
    print(f"   🔹 Sem empresa origem: {sem_empresa:,}")
    print(f"   🔹 Sem vendedor: {sem_vendedor:,}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
    print(f"   🔹 Integrar com dados de vendas (CXS/OSS)")
    print(f"   🔹 Normalizar nomes de vendedores")
    print(f"   🔹 Mapear empresas com lojas")
    print(f"   🔹 Analisar duplicações de clientes")
    print(f"   🔹 Padronizar canais de captação")

if __name__ == "__main__":
    main()