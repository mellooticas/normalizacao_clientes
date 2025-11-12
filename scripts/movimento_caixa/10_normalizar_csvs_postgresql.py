#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalizar CSVs para compatibilidade total com PostgreSQL/Supabase
Corrigir: booleanos, timestamps, NULLs, formatos de data
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalizar_para_postgres(df, tabela_nome):
    """Normalizar DataFrame para compatibilidade com PostgreSQL"""
    df_norm = df.copy()
    
    logging.info(f"🔧 Normalizando {tabela_nome}...")
    
    # 1. Converter booleanos Python para PostgreSQL
    colunas_bool = [col for col in df_norm.columns if df_norm[col].dtype == 'bool' or 
                   (df_norm[col].dtype == 'object' and 
                    df_norm[col].dropna().isin(['True', 'False', True, False]).all())]
    
    for col in colunas_bool:
        logging.info(f"   📝 Convertendo booleano: {col}")
        # Converter para lowercase string
        df_norm[col] = df_norm[col].astype(str).str.lower()
        # Converter 'nan' para NULL
        df_norm[col] = df_norm[col].replace('nan', '')
    
    # 2. Normalizar timestamps
    colunas_timestamp = [col for col in df_norm.columns if 'timestamp' in col.lower() or 
                        col in ['created_at', 'updated_at']]
    
    for col in colunas_timestamp:
        if col in df_norm.columns:
            logging.info(f"   📅 Normalizando timestamp: {col}")
            # Converter para formato ISO sem microssegundos
            df_norm[col] = pd.to_datetime(df_norm[col], errors='coerce')
            df_norm[col] = df_norm[col].dt.strftime('%Y-%m-%d %H:%M:%S%z')
            # Substituir NaT por string vazia
            df_norm[col] = df_norm[col].fillna('')
    
    # 3. Normalizar datas
    colunas_data = [col for col in df_norm.columns if 'data_' in col or col.endswith('_data')]
    
    for col in colunas_data:
        if col in df_norm.columns:
            logging.info(f"   📅 Normalizando data: {col}")
            # Converter para formato YYYY-MM-DD
            df_norm[col] = pd.to_datetime(df_norm[col], errors='coerce')
            df_norm[col] = df_norm[col].dt.strftime('%Y-%m-%d')
            # Substituir NaT por string vazia
            df_norm[col] = df_norm[col].fillna('')
    
    # 4. Normalizar colunas TIME
    if 'hora_movimento' in df_norm.columns:
        logging.info(f"   🕐 Normalizando hora_movimento")
        # Manter formato HH:MM:SS
        df_norm['hora_movimento'] = df_norm['hora_movimento'].fillna('')
    
    # 5. Tratar campos numéricos
    colunas_numericas = df_norm.select_dtypes(include=[np.number]).columns
    for col in colunas_numericas:
        # Manter NaN como vazio para campos opcionais
        if col in ['numero_documento', 'codigo_funcionario', 'codigo_caixa']:
            df_norm[col] = df_norm[col].fillna('')
    
    # 6. Limpar campos de texto
    colunas_texto = df_norm.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        if col not in colunas_bool:  # Não mexer nos booleanos já convertidos
            # Substituir NaN por string vazia
            df_norm[col] = df_norm[col].fillna('')
            # Limpar aspas extras que podem quebrar o CSV
            if df_norm[col].dtype == 'object':
                df_norm[col] = df_norm[col].astype(str)
                df_norm[col] = df_norm[col].str.replace('"', '""')  # Escapar aspas duplas
    
    # 7. Verificar UUIDs
    colunas_uuid = [col for col in df_norm.columns if 'uuid' in col.lower() or col == 'id']
    for col in colunas_uuid:
        if col in df_norm.columns:
            # Manter UUIDs como estão, apenas substituir NaN por vazio
            df_norm[col] = df_norm[col].fillna('')
    
    logging.info(f"✅ {tabela_nome} normalizado: {len(df_norm)} registros")
    return df_norm

def processar_csvs():
    """Processar e normalizar todos os CSVs"""
    base_path = Path(__file__).parent.parent.parent / "data" / "processados" / "schema_pagamentos"
    
    # Arquivos de entrada
    movimentos_file = base_path / "movimentos_caixa_upload_20251106_100717.csv"
    parcelas_file = base_path / "parcelas_carne_upload_20251106_100717.csv"
    
    if not movimentos_file.exists() or not parcelas_file.exists():
        logging.error("❌ Arquivos de upload não encontrados!")
        return
    
    logging.info("=== NORMALIZANDO CSVS PARA POSTGRESQL ===")
    
    # 1. Processar movimentos de caixa
    logging.info("📁 Carregando movimentos de caixa...")
    df_movimentos = pd.read_csv(movimentos_file)
    logging.info(f"   Registros carregados: {len(df_movimentos)}")
    
    df_movimentos_norm = normalizar_para_postgres(df_movimentos, "movimentos_caixa")
    
    # 2. Processar parcelas de carnê
    logging.info("📁 Carregando parcelas de carnê...")
    df_parcelas = pd.read_csv(parcelas_file)
    logging.info(f"   Registros carregados: {len(df_parcelas)}")
    
    df_parcelas_norm = normalizar_para_postgres(df_parcelas, "parcelas_carne")
    
    # 3. Salvar arquivos normalizados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salvar movimentos normalizados
    movimentos_norm_file = base_path / f"movimentos_caixa_postgresql_{timestamp}.csv"
    df_movimentos_norm.to_csv(movimentos_norm_file, index=False, quoting=1)  # QUOTE_ALL
    logging.info(f"✅ Movimentos normalizados salvos: {movimentos_norm_file.name}")
    
    # Salvar parcelas normalizadas
    parcelas_norm_file = base_path / f"parcelas_carne_postgresql_{timestamp}.csv"
    df_parcelas_norm.to_csv(parcelas_norm_file, index=False, quoting=1)  # QUOTE_ALL
    logging.info(f"✅ Parcelas normalizadas salvas: {parcelas_norm_file.name}")
    
    # 4. Relatório de normalização
    logging.info("=== RELATÓRIO DE NORMALIZAÇÃO ===")
    
    # Verificar amostra de dados normalizados
    print("\n🔍 AMOSTRA MOVIMENTOS NORMALIZADOS:")
    print("Colunas booleanas:")
    bool_cols = ['is_pagamento_carne', 'is_operacao_caixa', 'is_entrada_venda', 'is_processado']
    for col in bool_cols:
        if col in df_movimentos_norm.columns:
            valores_unicos = df_movimentos_norm[col].unique()[:5]
            print(f"  {col}: {valores_unicos}")
    
    print("\nColunas de data/timestamp:")
    date_cols = ['data_movimento', 'timestamp_movimento', 'created_at']
    for col in date_cols:
        if col in df_movimentos_norm.columns:
            amostra = df_movimentos_norm[col].dropna().iloc[:3].tolist()
            print(f"  {col}: {amostra}")
    
    print("\n🔍 AMOSTRA PARCELAS NORMALIZADAS:")
    print("Colunas de data:")
    date_cols_parcelas = ['data_vencimento', 'data_pagamento', 'created_at']
    for col in date_cols_parcelas:
        if col in df_parcelas_norm.columns:
            amostra = df_parcelas_norm[col].dropna().iloc[:3].tolist()
            print(f"  {col}: {amostra}")
    
    # 5. Instruções finais
    print(f"""
✅ CSVS NORMALIZADOS PARA POSTGRESQL!

📁 ARQUIVOS PRONTOS PARA UPLOAD:
1. {movimentos_norm_file.name}
   - Registros: {len(df_movimentos_norm)}
   - Tabela: pagamentos.movimentos_caixa
   
2. {parcelas_norm_file.name}
   - Registros: {len(df_parcelas_norm)}
   - Tabela: pagamentos.parcelas_carne

🔧 MELHORIAS APLICADAS:
✅ Booleanos: True/False → true/false
✅ Timestamps: Formato ISO normalizado
✅ Datas: Formato YYYY-MM-DD
✅ NULLs: Campos vazios para valores opcionais
✅ Aspas: Escapadas corretamente
✅ UUIDs: Mantidos intactos

📋 PRÓXIMOS PASSOS:
1. Execute o SQL: CRIAR_SCHEMA_PAGAMENTOS_SUPABASE.sql
2. Upload via Table Editor: Use os arquivos *_postgresql_*.csv
3. Verificação: Execute queries de validação
""")

if __name__ == "__main__":
    processar_csvs()