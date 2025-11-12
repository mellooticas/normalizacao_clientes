#!/usr/bin/env python3
"""
Análise completa de TODOS os dados disponíveis
"""

import pandas as pd
import os
from pathlib import Path

def analisar_vendas_extraidos():
    """Analisa vendas em extraidos_corrigidos"""
    print("📊 ANÁLISE VENDAS - EXTRAÍDOS CORRIGIDOS")
    print("=" * 50)
    
    base_path = Path("data/originais/cxs/extraidos_corrigidos/vendas")
    
    total_vendas = 0
    total_valor = 0
    
    for arquivo in base_path.glob("*.csv"):
        if "com_uuids_enriquecido_completo" in arquivo.name:
            print(f"\n🔍 Analisando: {arquivo.name}")
            try:
                df = pd.read_csv(arquivo)
                print(f"   Registros: {len(df):,}")
                print(f"   Colunas: {list(df.columns)}")
                
                # Verificar se tem cliente_uuid
                if 'cliente_uuid' in df.columns:
                    uuids_validos = df['cliente_uuid'].notna().sum()
                    print(f"   ✅ Cliente UUIDs válidos: {uuids_validos:,}")
                
                # Verificar valores
                colunas_valor = ['valor_venda', 'valor', 'total']
                for col in colunas_valor:
                    if col in df.columns:
                        valor_col = pd.to_numeric(df[col], errors='coerce').sum()
                        print(f"   💰 {col}: R$ {valor_col:,.2f}")
                        total_valor += valor_col
                        break
                
                total_vendas += len(df)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    print(f"\n📋 RESUMO VENDAS EXTRAÍDOS:")
    print(f"   Total de vendas: {total_vendas:,}")
    print(f"   Valor total: R$ {total_valor:,.2f}")

def analisar_oss_normalizadas():
    """Analisa OSs normalizadas com UUIDs"""
    print("\n\n📊 ANÁLISE OSs - NORMALIZADAS COM UUID")
    print("=" * 50)
    
    base_path = Path("data/originais/oss/normalizadas_com_vendedor_uuid")
    
    if not base_path.exists():
        print("❌ Diretório não encontrado")
        return
    
    total_oss = 0
    total_valor = 0
    
    for arquivo in base_path.glob("*.csv"):
        print(f"\n🔍 Analisando: {arquivo.name}")
        try:
            df = pd.read_csv(arquivo)
            print(f"   Registros: {len(df):,}")
            print(f"   Colunas: {list(df.columns)}")
            
            # Verificar UUIDs
            if 'vendedor_uuid' in df.columns:
                uuids_validos = df['vendedor_uuid'].notna().sum()
                print(f"   ✅ Vendedor UUIDs válidos: {uuids_validos:,}")
            
            if 'cliente_uuid' in df.columns:
                uuids_validos = df['cliente_uuid'].notna().sum()
                print(f"   ✅ Cliente UUIDs válidos: {uuids_validos:,}")
            
            # Verificar valores
            colunas_valor = ['TOTAL', 'valor_total', 'total']
            for col in colunas_valor:
                if col in df.columns:
                    valor_col = pd.to_numeric(df[col], errors='coerce').sum()
                    print(f"   💰 {col}: R$ {valor_col:,.2f}")
                    total_valor += valor_col
                    break
            
            total_oss += len(df)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n📋 RESUMO OSs NORMALIZADAS:")
    print(f"   Total de OSs: {total_oss:,}")
    print(f"   Valor total: R$ {total_valor:,.2f}")

def analisar_finais_postgresql():
    """Analisa dados finais prontos para PostgreSQL"""
    print("\n\n📊 ANÁLISE DADOS FINAIS POSTGRESQL")
    print("=" * 50)
    
    # Vendas finais
    vendas_path = Path("data/originais/cxs/finais_postgresql_prontos")
    print(f"\n🔍 VENDAS FINAIS:")
    total_vendas = 0
    for arquivo in vendas_path.glob("*.csv"):
        df = pd.read_csv(arquivo)
        print(f"   {arquivo.name}: {len(df):,} registros")
        total_vendas += len(df)
    print(f"   Total vendas finais: {total_vendas:,}")
    
    # OSs finais
    oss_path = Path("data/originais/oss/finais_postgresql_prontos")
    print(f"\n🔍 OSs FINAIS:")
    total_oss = 0
    for arquivo in oss_path.glob("*.csv"):
        df = pd.read_csv(arquivo)
        print(f"   {arquivo.name}: {len(df):,} registros")
        total_oss += len(df)
    print(f"   Total OSs finais: {total_oss:,}")

def analisar_dados_importacao():
    """Analisa dados preparados para importação"""
    print("\n\n📊 ANÁLISE DADOS PARA IMPORTAÇÃO")
    print("=" * 50)
    
    dirs_importacao = [
        "data/importacao_clientes",
        "data/vendas_para_importar",
        "data/clientes_uuid",
        "data/finais_banco_completo"
    ]
    
    for dir_path in dirs_importacao:
        path = Path(dir_path)
        if path.exists():
            print(f"\n🔍 {dir_path}:")
            for arquivo in path.glob("*.csv"):
                try:
                    df = pd.read_csv(arquivo)
                    print(f"   {arquivo.name}: {len(df):,} registros")
                except:
                    print(f"   {arquivo.name}: ❌ Erro ao ler")

def main():
    print("🚀 ANÁLISE COMPLETA DE TODOS OS DADOS DISPONÍVEIS")
    print("=" * 60)
    
    analisar_vendas_extraidos()
    analisar_oss_normalizadas()
    analisar_finais_postgresql()
    analisar_dados_importacao()
    
    print("\n\n🎯 RECOMENDAÇÕES:")
    print("1. Usar arquivos '*_com_uuids_enriquecido_completo.csv' para vendas")
    print("2. Usar arquivos 'normalizadas_com_vendedor_uuid' para OSs")
    print("3. Verificar dados em 'finais_banco_completo' se existir")
    print("4. Priorizar dados que já têm UUIDs mapeados")

if __name__ == "__main__":
    main()