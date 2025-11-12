#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados migrados para o schema pagamentos no Supabase
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_database_connection():
    """Conectar ao banco Supabase"""
    DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não encontrada no .env")
    
    return psycopg2.connect(DATABASE_URL)

def importar_movimentos_caixa(conn, csv_path):
    """Importar movimentos de caixa para o Supabase"""
    logging.info(f"Carregando movimentos de caixa de: {csv_path}")
    
    # Carregar CSV
    df = pd.read_csv(csv_path)
    logging.info(f"Movimentos carregados: {len(df)} registros")
    
    # Preparar dados para inserção
    registros = []
    for _, row in df.iterrows():
        registro = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val) or val == '':
                registro.append(None)
            else:
                registro.append(val)
        registros.append(tuple(registro))
    
    # Preparar query de inserção
    colunas = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    query = f"INSERT INTO pagamentos.movimentos_caixa ({colunas}) VALUES ({placeholders})"
    
    # Processar em lotes
    cursor = conn.cursor()
    lote_size = 100
    sucesso = 0
    
    try:
        for i in range(0, len(registros), lote_size):
            lote = registros[i:i+lote_size]
            lote_num = (i // lote_size) + 1
            total_lotes = (len(registros) + lote_size - 1) // lote_size
            
            try:
                execute_values(cursor, query, lote, page_size=lote_size)
                conn.commit()
                sucesso += len(lote)
                logging.info(f"Lote {lote_num}/{total_lotes}: {len(lote)} movimentos inseridos")
                
            except Exception as e:
                logging.error(f"Erro no lote {lote_num}: {str(e)}")
                conn.rollback()
                continue
        
        logging.info(f"Movimentos importados com sucesso: {sucesso}/{len(registros)}")
        return sucesso
        
    finally:
        cursor.close()

def importar_parcelas_carne(conn, csv_path):
    """Importar parcelas de carnê para o Supabase"""
    logging.info(f"Carregando parcelas de carnê de: {csv_path}")
    
    # Carregar CSV
    df = pd.read_csv(csv_path)
    logging.info(f"Parcelas carregadas: {len(df)} registros")
    
    # Preparar dados para inserção
    registros = []
    for _, row in df.iterrows():
        registro = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val) or val == '':
                registro.append(None)
            else:
                registro.append(val)
        registros.append(tuple(registro))
    
    # Preparar query de inserção
    colunas = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    query = f"INSERT INTO pagamentos.parcelas_carne ({colunas}) VALUES ({placeholders})"
    
    # Processar em lotes
    cursor = conn.cursor()
    lote_size = 100
    sucesso = 0
    
    try:
        for i in range(0, len(registros), lote_size):
            lote = registros[i:i+lote_size]
            lote_num = (i // lote_size) + 1
            total_lotes = (len(registros) + lote_size - 1) // lote_size
            
            try:
                execute_values(cursor, query, lote, page_size=lote_size)
                conn.commit()
                sucesso += len(lote)
                logging.info(f"Lote {lote_num}/{total_lotes}: {len(lote)} parcelas inseridas")
                
            except Exception as e:
                logging.error(f"Erro no lote {lote_num}: {str(e)}")
                conn.rollback()
                continue
        
        logging.info(f"Parcelas importadas com sucesso: {sucesso}/{len(registros)}")
        return sucesso
        
    finally:
        cursor.close()

def verificar_importacao(conn):
    """Verificar se a importação foi bem-sucedida"""
    logging.info("=== VERIFICANDO IMPORTAÇÃO ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verificar movimentos de caixa
        cursor.execute("SELECT COUNT(*) as total FROM pagamentos.movimentos_caixa")
        mov_count = cursor.fetchone()['total']
        
        # Verificar parcelas de carnê
        cursor.execute("SELECT COUNT(*) as total FROM pagamentos.parcelas_carne")
        parcelas_count = cursor.fetchone()['total']
        
        logging.info(f"Movimentos de caixa importados: {mov_count}")
        logging.info(f"Parcelas de carnê importadas: {parcelas_count}")
        
        # Testar uma query básica
        cursor.execute("""
            SELECT id, valor_movimento, data_movimento 
            FROM pagamentos.movimentos_caixa 
            LIMIT 5
        """)
        
        resultados = cursor.fetchall()
        
        if resultados:
            logging.info("✅ Teste de consulta bem-sucedido")
            for item in resultados[:3]:
                logging.info(f"   - ID: {str(item['id'])[:8]}... Valor: R$ {item['valor_movimento']}")
        else:
            logging.warning("⚠️ Nenhum dado encontrado na consulta de teste")
            
    except Exception as e:
        logging.error(f"Erro na verificação: {str(e)}")
    finally:
        cursor.close()

def main():
    """Função principal"""
    logging.info("=== INICIANDO IMPORTAÇÃO PARA SUPABASE ===")
    
    # Conectar ao banco
    try:
        conn = get_database_connection()
        logging.info("✅ Conexão com Supabase estabelecida")
    except Exception as e:
        logging.error(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        return
    
    # Caminhos dos arquivos
    base_path = Path(__file__).parent.parent.parent / "data" / "processados" / "schema_pagamentos"
    
    # Buscar arquivos mais recentes
    movimentos_files = list(base_path.glob("movimentos_caixa_migrado_*.csv"))
    parcelas_files = list(base_path.glob("parcelas_carne_migrado_*.csv"))
    
    if not movimentos_files:
        logging.error("❌ Arquivo de movimentos de caixa não encontrado")
        conn.close()
        return
    
    if not parcelas_files:
        logging.error("❌ Arquivo de parcelas de carnê não encontrado")
        conn.close()
        return
    
    # Usar o arquivo mais recente
    movimentos_file = max(movimentos_files, key=os.path.getctime)
    parcelas_file = max(parcelas_files, key=os.path.getctime)
    
    logging.info(f"📁 Arquivo de movimentos: {movimentos_file.name}")
    logging.info(f"📁 Arquivo de parcelas: {parcelas_file.name}")
    
    # Importar dados
    try:
        # 1. Importar movimentos de caixa
        sucesso_mov = importar_movimentos_caixa(conn, movimentos_file)
        
        # 2. Importar parcelas de carnê
        sucesso_parcelas = importar_parcelas_carne(conn, parcelas_file)
        
        # 3. Verificar importação
        verificar_importacao(conn)
        
        print(f"\n✅ IMPORTAÇÃO CONCLUÍDA!")
        print(f"📊 Movimentos importados: {sucesso_mov}")
        print(f"📊 Parcelas importadas: {sucesso_parcelas}")
        print(f"🗄️ Schema: pagamentos")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        logging.error(f"❌ Erro durante a importação: {str(e)}")
        return
    finally:
        conn.close()
        logging.info("🔌 Conexão fechada")

if __name__ == "__main__":
    main()