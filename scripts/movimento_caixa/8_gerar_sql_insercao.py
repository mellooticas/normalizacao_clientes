#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerar script SQL para inserção manual no Supabase
"""

import pandas as pd
from pathlib import Path

def converter_para_sql_insert(csv_path, table_name, schema='pagamentos'):
    """Converter CSV para comandos INSERT SQL"""
    df = pd.read_csv(csv_path)
    
    # Preparar colunas
    colunas = ', '.join(df.columns)
    
    inserts = []
    
    # Processar em lotes de 50 para evitar statements muito longos
    lote_size = 50
    for i in range(0, len(df), lote_size):
        lote_df = df.iloc[i:i+lote_size]
        
        # Preparar valores para este lote
        valores_lote = []
        
        for _, row in lote_df.iterrows():
            valores = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val) or val == '':
                    valores.append('NULL')
                elif isinstance(val, str):
                    # Escapar aspas simples
                    val_escaped = val.replace("'", "''")
                    valores.append(f"'{val_escaped}'")
                else:
                    valores.append(str(val))
            
            valores_lote.append(f"({', '.join(valores)})")
        
        # Criar INSERT para este lote
        valores_str = ',\n    '.join(valores_lote)
        insert_sql = f"""INSERT INTO {schema}.{table_name} ({colunas}) VALUES 
    {valores_str};"""
        
        inserts.append(insert_sql)
    
    return inserts

def main():
    """Função principal"""
    base_path = Path(__file__).parent.parent.parent / "data" / "processados" / "schema_pagamentos"
    
    # Buscar arquivos mais recentes
    movimentos_files = list(base_path.glob("movimentos_caixa_migrado_*.csv"))
    parcelas_files = list(base_path.glob("parcelas_carne_migrado_*.csv"))
    
    if not movimentos_files or not parcelas_files:
        print("❌ Arquivos CSV não encontrados")
        return
    
    movimentos_file = max(movimentos_files, key=lambda x: x.stat().st_ctime)
    parcelas_file = max(parcelas_files, key=lambda x: x.stat().st_ctime)
    
    print(f"📁 Processando: {movimentos_file.name}")
    print(f"📁 Processando: {parcelas_file.name}")
    
    # Converter movimentos
    print("🔄 Convertendo movimentos de caixa...")
    movimentos_inserts = converter_para_sql_insert(movimentos_file, 'movimentos_caixa')
    
    # Converter parcelas
    print("🔄 Convertendo parcelas de carnê...")
    parcelas_inserts = converter_para_sql_insert(parcelas_file, 'parcelas_carne')
    
    # Gerar arquivo SQL
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_file = base_path / f"inserir_dados_pagamentos_{timestamp}.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- ========================================\n")
        f.write("-- INSERÇÃO DE DADOS SCHEMA PAGAMENTOS\n")
        f.write(f"-- Gerado em: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("-- ========================================\n\n")
        
        f.write("-- 1. INSERIR MOVIMENTOS DE CAIXA\n")
        f.write("-- ========================================\n\n")
        
        for i, insert in enumerate(movimentos_inserts, 1):
            f.write(f"-- Lote {i} de movimentos\n")
            f.write(insert)
            f.write("\n\n")
        
        f.write("-- 2. INSERIR PARCELAS DE CARNÊ\n")
        f.write("-- ========================================\n\n")
        
        for i, insert in enumerate(parcelas_inserts, 1):
            f.write(f"-- Lote {i} de parcelas\n")
            f.write(insert)
            f.write("\n\n")
        
        f.write("-- 3. VERIFICAÇÃO PÓS-INSERÇÃO\n")
        f.write("-- ========================================\n\n")
        f.write("""SELECT 
    'MOVIMENTOS CAIXA' as tabela,
    COUNT(*) as registros_inseridos,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_movimento) as valor_total
FROM pagamentos.movimentos_caixa

UNION ALL

SELECT 
    'PARCELAS CARNÊ' as tabela,
    COUNT(*) as registros_inseridos,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_parcela) as valor_total
FROM pagamentos.parcelas_carne;

-- Popular resumos (automático via triggers)
SELECT 'INSERÇÃO CONCLUÍDA' as status;""")
    
    print(f"✅ Script SQL gerado: {output_file}")
    print(f"📊 Movimentos: {len(movimentos_inserts)} lotes")
    print(f"📊 Parcelas: {len(parcelas_inserts)} lotes")
    print("🔗 Execute este arquivo no SQL Editor do Supabase")

if __name__ == "__main__":
    main()