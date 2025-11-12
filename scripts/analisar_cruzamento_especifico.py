#!/usr/bin/env python3
"""
Análise Específica para Cruzamento VIXEN x OSS
==============================================

Analisa vendedores e clientes entre VIXEN e OSS para identificar correspondências.
"""

import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome) or nome == "":
        return ""
    return str(nome).strip().upper()

def similaridade_nomes(nome1, nome2):
    """Calcula similaridade entre dois nomes"""
    nome1_norm = normalizar_nome(nome1)
    nome2_norm = normalizar_nome(nome2)
    
    if not nome1_norm or not nome2_norm:
        return 0.0
    
    return SequenceMatcher(None, nome1_norm, nome2_norm).ratio()

def analisar_vendedores(df_vixen, df_oss, loja):
    print(f"\n👥 ANÁLISE DE VENDEDORES - {loja}:")
    
    # Vendedores VIXEN
    vendedores_vixen = df_vixen['Vendedor'].value_counts()
    print(f"   📊 VIXEN: {len(vendedores_vixen)} vendedores únicos")
    
    # Mostrar top vendedores VIXEN
    print(f"   🔹 Top 5 VIXEN:")
    for vendedor, count in vendedores_vixen.head(5).items():
        vendedor_display = vendedor if vendedor.strip() else "[VAZIO]"
        print(f"      • {vendedor_display}: {count} clientes")
    
    # Vendedores OSS
    if 'CONSULTOR' in df_oss.columns:
        vendedores_oss = df_oss['CONSULTOR'].value_counts()
        print(f"   📊 OSS: {len(vendedores_oss)} consultores únicos")
        
        print(f"   🔹 Top 5 OSS:")
        for vendedor, count in vendedores_oss.head(5).items():
            print(f"      • {vendedor}: {count} OS")
    
    elif 'vendedor_nome_normalizado' in df_oss.columns:
        vendedores_oss = df_oss['vendedor_nome_normalizado'].value_counts()
        print(f"   📊 OSS: {len(vendedores_oss)} vendedores únicos")
        
        print(f"   🔹 Top 5 OSS:")
        for vendedor, count in vendedores_oss.head(5).items():
            print(f"      • {vendedor}: {count} OS")

def analisar_clientes(df_vixen, df_oss, loja):
    print(f"\n👤 ANÁLISE DE CLIENTES - {loja}:")
    
    # Clientes VIXEN
    clientes_vixen = len(df_vixen['Nome Completo'].unique())
    print(f"   📊 VIXEN: {clientes_vixen:,} clientes únicos")
    
    # Clientes OSS  
    if 'NOME:' in df_oss.columns:
        clientes_oss = len(df_oss['NOME:'].unique())
        print(f"   📊 OSS: {clientes_oss:,} clientes únicos")
        
        # Tentar encontrar correspondências
        print(f"   🔍 Verificando correspondências...")
        
        # Amostra para teste
        amostra_vixen = df_vixen['Nome Completo'].head(10).tolist()
        amostra_oss = df_oss['NOME:'].dropna().head(10).tolist()
        
        correspondencias = 0
        for nome_vixen in amostra_vixen:
            for nome_oss in amostra_oss:
                if similaridade_nomes(nome_vixen, nome_oss) > 0.8:
                    correspondencias += 1
                    print(f"      ✅ {nome_vixen} ≈ {nome_oss}")
                    break
        
        print(f"   📊 Correspondências na amostra: {correspondencias}/10")

def analisar_periodos(df_vixen, df_oss, loja):
    print(f"\n📅 ANÁLISE TEMPORAL - {loja}:")
    
    # VIXEN - usando data de inclusão se disponível
    if 'Dh.inclusão' in df_vixen.columns:
        try:
            df_vixen_temp = df_vixen.copy()
            df_vixen_temp['data_inclusao'] = pd.to_datetime(df_vixen_temp['Dh.inclusão'], errors='coerce')
            
            anos_vixen = df_vixen_temp['data_inclusao'].dt.year.value_counts().sort_index()
            print(f"   📊 VIXEN - Cadastros por ano:")
            for ano, count in anos_vixen.tail(5).items():
                if pd.notna(ano):
                    print(f"      🔹 {int(ano)}: {count:,} cadastros")
        except:
            print(f"   ⚠️  VIXEN: Dados temporais não disponíveis")
    
    # OSS - usando data de compra
    if 'data_compra' in df_oss.columns:
        try:
            df_oss_temp = df_oss.copy()
            df_oss_temp['data_compra'] = pd.to_datetime(df_oss_temp['data_compra'], errors='coerce')
            
            anos_oss = df_oss_temp['data_compra'].dt.year.value_counts().sort_index()
            print(f"   📊 OSS - Vendas por ano:")
            for ano, count in anos_oss.tail(5).items():
                if pd.notna(ano):
                    print(f"      🔹 {int(ano)}: {count:,} OS")
        except:
            print(f"   ⚠️  OSS: Dados temporais com problemas")

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    cruzamento_dir = base_dir / "data" / "originais" / "cruzamento_vixen_oss"
    
    print("🔍 ANÁLISE ESPECÍFICA VIXEN x OSS")
    print("=" * 60)
    
    # Analisar MAUA
    print(f"\n🏪 LOJA: MAUA")
    print("=" * 30)
    
    vixen_maua = pd.read_csv(cruzamento_dir / "clientes_vixen_maua_original.csv")
    oss_maua = pd.read_csv(cruzamento_dir / "oss_maua_original.csv")
    
    analisar_vendedores(vixen_maua, oss_maua, "MAUA")
    analisar_clientes(vixen_maua, oss_maua, "MAUA")
    analisar_periodos(vixen_maua, oss_maua, "MAUA")
    
    # Analisar SUZANO
    print(f"\n🏪 LOJA: SUZANO")
    print("=" * 30)
    
    vixen_suzano = pd.read_csv(cruzamento_dir / "clientes_vixen_suzano_original.csv")
    oss_suzano = pd.read_csv(cruzamento_dir / "oss_suzano_original.csv")
    
    analisar_vendedores(vixen_suzano, oss_suzano, "SUZANO")
    analisar_clientes(vixen_suzano, oss_suzano, "SUZANO")
    analisar_periodos(vixen_suzano, oss_suzano, "SUZANO")
    
    print(f"\n🎯 CONCLUSÕES E RECOMENDAÇÕES:")
    print(f"   🔹 Cruzamento principal: Por loja (MAUA/SUZANO)")
    print(f"   🔹 Análise de vendedores: Mapear nomes similares")
    print(f"   🔹 Análise de clientes: Busca por similaridade de nomes")
    print(f"   🔹 Relatórios consolidados: Combinar dados por loja")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   1️⃣ Criar mapeamento de vendedores por similaridade")
    print(f"   2️⃣ Implementar busca fuzzy para clientes")
    print(f"   3️⃣ Gerar dashboard consolidado por loja")
    print(f"   4️⃣ Criar relatório de cobertura cliente x OS")

if __name__ == "__main__":
    main()