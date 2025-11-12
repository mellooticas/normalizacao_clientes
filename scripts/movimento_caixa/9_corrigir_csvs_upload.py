#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir CSVs para upload direto no Supabase
Problema: movimento_caixa_id está vazio nas parcelas
"""

import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def corrigir_csvs_para_upload():
    """Corrigir os CSVs para que possam ser uploadados direto no Supabase"""
    
    base_path = Path(__file__).parent.parent.parent / "data" / "processados" / "schema_pagamentos"
    
    # Arquivos de entrada
    movimentos_file = base_path / "movimentos_caixa_migrado_20251106_012836.csv"
    parcelas_file = base_path / "parcelas_carne_migrado_20251106_012836.csv"
    
    logging.info("=== CORRIGINDO CSVS PARA UPLOAD ===")
    
    # 1. Carregar dados
    logging.info("📁 Carregando movimentos de caixa...")
    df_movimentos = pd.read_csv(movimentos_file)
    logging.info(f"   Movimentos carregados: {len(df_movimentos)}")
    
    logging.info("📁 Carregando parcelas de carnê...")
    df_parcelas = pd.read_csv(parcelas_file)
    logging.info(f"   Parcelas carregadas: {len(df_parcelas)}")
    
    # 2. Problema: parcelas sem movimento_caixa_id
    parcelas_sem_movimento = df_parcelas['movimento_caixa_id'].isna().sum()
    logging.info(f"⚠️ Parcelas sem movimento_caixa_id: {parcelas_sem_movimento}")
    
    if parcelas_sem_movimento > 0:
        logging.info("🔧 Estratégia: Remover constraint obrigatória ou criar movimentos fictícios")
        
        # Opção 1: Filtrar apenas parcelas que têm movimento_caixa_id
        parcelas_validas = df_parcelas.dropna(subset=['movimento_caixa_id'])
        logging.info(f"   Parcelas válidas após filtro: {len(parcelas_validas)}")
        
        # Opção 2: Criar versão sem constraint para upload inicial
        parcelas_upload = df_parcelas.copy()
        # Remover constraint temporariamente preenchendo com NULL
        parcelas_upload['movimento_caixa_id'] = parcelas_upload['movimento_caixa_id'].fillna('')
        
        # Salvar versão corrigida
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar parcelas corrigidas (com movimento_caixa_id como string vazia se NULL)
        parcelas_upload_file = base_path / f"parcelas_carne_upload_{timestamp}.csv"
        parcelas_upload.to_csv(parcelas_upload_file, index=False)
        logging.info(f"✅ Parcelas para upload salvas: {parcelas_upload_file}")
        
        # Salvar apenas parcelas válidas (com movimento_caixa_id preenchido)
        if len(parcelas_validas) > 0:
            parcelas_validas_file = base_path / f"parcelas_carne_validas_{timestamp}.csv"
            parcelas_validas.to_csv(parcelas_validas_file, index=False)
            logging.info(f"✅ Parcelas válidas salvas: {parcelas_validas_file}")
    
    # 3. Verificar movimentos (provavelmente estão OK)
    movimentos_sem_id = df_movimentos['id'].isna().sum()
    logging.info(f"✅ Movimentos sem ID: {movimentos_sem_id}")
    
    # 4. Preparar arquivos finais para upload
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    
    # Movimentos (copiar como está)
    movimentos_upload_file = base_path / f"movimentos_caixa_upload_{timestamp}.csv"
    df_movimentos.to_csv(movimentos_upload_file, index=False)
    logging.info(f"✅ Movimentos para upload: {movimentos_upload_file}")
    
    # 5. Estatísticas finais
    logging.info("=== ARQUIVOS PRONTOS PARA UPLOAD ===")
    logging.info(f"📊 Movimentos: {len(df_movimentos)} registros")
    logging.info(f"📊 Parcelas: {len(df_parcelas)} registros")
    logging.info(f"⚠️ Parcelas sem FK: {parcelas_sem_movimento}")
    
    # 6. Instruções de upload
    print(f"""
✅ ARQUIVOS PRONTOS PARA UPLOAD NO SUPABASE

📁 Movimentos de Caixa:
   Arquivo: {movimentos_upload_file.name}
   Registros: {len(df_movimentos)}
   Tabela: pagamentos.movimentos_caixa
   Status: ✅ Pronto para upload

📁 Parcelas de Carnê:
   Arquivo: {parcelas_upload_file.name if 'parcelas_upload_file' in locals() else 'N/A'}
   Registros: {len(df_parcelas)}
   Tabela: pagamentos.parcelas_carne
   Status: ⚠️ Requer ajuste na constraint

🔧 PRÓXIMOS PASSOS:
1. Upload movimentos_caixa primeiro (sem dependências)
2. Ajustar constraint FK em parcelas_carne ou criar relacionamentos
3. Upload parcelas_carne

📋 COMANDOS SQL PARA AJUSTAR CONSTRAINTS:
-- Tornar movimento_caixa_id opcional temporariamente
ALTER TABLE pagamentos.parcelas_carne 
ALTER COLUMN movimento_caixa_id DROP NOT NULL;

-- Após upload, recriar relacionamentos se necessário
""")

if __name__ == "__main__":
    corrigir_csvs_para_upload()