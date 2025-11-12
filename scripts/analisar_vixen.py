#!/usr/bin/env python3
"""
Analisar e Converter Arquivo VIXEN
==================================

Analisa o arquivo clientes_completos_vixen.XLSX e converte para CSV.
"""

import pandas as pd
from pathlib import Path
import openpyxl

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_dir = base_dir / "data" / "originais" / "vixen"
    arquivo_xlsx = vixen_dir / "clientes_completos_vixen.XLSX"
    
    print("🔍 ANALISANDO ARQUIVO VIXEN")
    print("=" * 50)
    
    if not arquivo_xlsx.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_xlsx}")
        return
    
    # Verificar tamanho do arquivo
    tamanho_mb = arquivo_xlsx.stat().st_size / (1024 * 1024)
    print(f"📊 Arquivo: {arquivo_xlsx.name}")
    print(f"📏 Tamanho: {tamanho_mb:.2f} MB")
    
    try:
        # Carregar workbook para verificar abas
        print(f"\n📋 Verificando abas...")
        wb = openpyxl.load_workbook(arquivo_xlsx, read_only=True)
        abas = wb.sheetnames
        print(f"   🔹 Total de abas: {len(abas)}")
        
        for i, aba in enumerate(abas, 1):
            print(f"   📄 Aba {i}: {aba}")
        
        wb.close()
        
        # Analisar cada aba
        print(f"\n📊 ANALISANDO CONTEÚDO DAS ABAS:")
        
        for aba in abas:
            print(f"\n🔍 Processando aba: {aba}")
            try:
                # Carregar apenas algumas linhas para análise
                df_sample = pd.read_excel(arquivo_xlsx, sheet_name=aba, nrows=5)
                
                print(f"   📊 Colunas ({len(df_sample.columns)}):")
                for col in df_sample.columns:
                    print(f"      🔹 {col}")
                
                # Carregar dados completos
                df_full = pd.read_excel(arquivo_xlsx, sheet_name=aba)
                print(f"   📈 Total de registros: {len(df_full):,}")
                
                # Verificar dados não nulos
                if len(df_full) > 0:
                    print(f"   📋 Amostra dos dados:")
                    for col in df_full.columns[:3]:  # Primeiras 3 colunas
                        valores_unicos = df_full[col].nunique()
                        print(f"      🔸 {col}: {valores_unicos:,} valores únicos")
                
                # Salvar CSV da aba
                nome_csv = f"vixen_{aba.lower().replace(' ', '_')}.csv"
                arquivo_csv = vixen_dir / nome_csv
                df_full.to_csv(arquivo_csv, index=False)
                print(f"   ✅ Salvo: {nome_csv}")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar aba {aba}: {e}")
        
        print(f"\n🎯 ANÁLISE VIXEN CONCLUÍDA")
        
        # Listar arquivos gerados
        print(f"\n📁 ARQUIVOS GERADOS:")
        csvs_gerados = list(vixen_dir.glob("*.csv"))
        total_registros = 0
        
        for csv_file in sorted(csvs_gerados):
            try:
                df_check = pd.read_csv(csv_file)
                registros = len(df_check)
                total_registros += registros
                print(f"   ✅ {csv_file.name}: {registros:,} registros")
            except:
                print(f"   ❌ {csv_file.name}: Erro ao verificar")
        
        print(f"\n📊 RESUMO TOTAL:")
        print(f"   📄 Arquivos CSV: {len(csvs_gerados)}")
        print(f"   📈 Total registros: {total_registros:,}")
        print(f"   📂 Localização: {vixen_dir}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()