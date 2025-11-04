#!/usr/bin/env python3
"""
Consultar IDs das Lojas no Supabase
===================================

Executa consultas para verificar os IDs das lojas na tabela core.lojas
e criar mapeamento correto para a importação dos dados normalizados.
"""

import os
import logging
from pathlib import Path
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def conectar_supabase():
    """Conecta ao Supabase PostgreSQL"""
    load_dotenv()
    
    try:
        # Usar a URL completa do Supabase
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if database_url:
            # Extrair componentes da URL
            # Formato: postgresql://user:password@host:port/database
            import re
            pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
            match = re.match(pattern, database_url)
            
            if match:
                user, password, host, port, database = match.groups()
                
                conn = psycopg2.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password,
                    port=int(port),
                    sslmode='require'
                )
            else:
                # Fallback: tentar conectar diretamente com a URL
                conn = psycopg2.connect(database_url, sslmode='require')
        else:
            # Configuração manual alternativa
            conn = psycopg2.connect(
                host='aws-0-sa-east-1.pooler.supabase.com',
                database='postgres',
                user='postgres.gzrjqlbnhkqybvqzjvms',
                password='HpKuJXrVBGkONTQN',
                port=6543,
                sslmode='require'
            )
        
        logger.info("✅ Conectado ao Supabase")
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar Supabase: {e}")
        return None

def executar_consulta(conn, consulta, titulo):
    """Executa uma consulta e exibe o resultado"""
    try:
        logger.info(f"\n📊 {titulo}")
        logger.info("=" * 50)
        
        df = pd.read_sql_query(consulta, conn)
        
        if df.empty:
            logger.warning("⚠️ Nenhum resultado encontrado")
            return df
        
        # Exibir resultado formatado
        for index, row in df.iterrows():
            logger.info(f"   {index + 1}. " + " | ".join([f"{col}: {val}" for col, val in row.items()]))
        
        logger.info(f"📈 Total: {len(df)} registro(s)")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar consulta: {e}")
        return None

def main():
    logger.info("🔍 CONSULTANDO IDS DAS LOJAS NO SUPABASE")
    logger.info("=" * 60)
    
    # Conectar ao Supabase
    conn = conectar_supabase()
    if not conn:
        return
    
    try:
        # 1. Consulta básica - todas as lojas
        consulta1 = """
        SELECT 
            id,
            nome,
            codigo,
            ativo
        FROM core.lojas
        ORDER BY nome;
        """
        
        df_lojas = executar_consulta(conn, consulta1, "TODAS AS LOJAS")
        
        # 2. Mapeamento das lojas
        consulta2 = """
        SELECT 
            id,
            nome,
            codigo,
            CASE 
                WHEN UPPER(nome) LIKE '%MAUA%' OR UPPER(nome) LIKE '%MAUÁ%' THEN 'MAUA'
                WHEN UPPER(nome) LIKE '%SUZANO%' AND (UPPER(nome) LIKE '%2%' OR UPPER(nome) LIKE '%II%') THEN 'SUZANO2'
                WHEN UPPER(nome) LIKE '%SUZANO%' THEN 'SUZANO'
                WHEN UPPER(nome) LIKE '%PERUS%' THEN 'PERUS'
                WHEN UPPER(nome) LIKE '%RIO%PEQUENO%' OR UPPER(nome) LIKE '%RIO PEQUENO%' THEN 'RIO_PEQUENO'
                WHEN UPPER(nome) LIKE '%SAO%MATEUS%' OR UPPER(nome) LIKE '%SÃO%MATEUS%' THEN 'SAO_MATEUS'
                ELSE 'OUTROS'
            END AS loja_mapeada
        FROM core.lojas
        WHERE ativo = true
        ORDER BY nome;
        """
        
        df_mapeamento = executar_consulta(conn, consulta2, "MAPEAMENTO DAS LOJAS")
        
        # 3. Contar por tipo
        consulta3 = """
        SELECT 
            CASE 
                WHEN UPPER(nome) LIKE '%MAUA%' OR UPPER(nome) LIKE '%MAUÁ%' THEN 'MAUA'
                WHEN UPPER(nome) LIKE '%SUZANO%' AND (UPPER(nome) LIKE '%2%' OR UPPER(nome) LIKE '%II%') THEN 'SUZANO2'
                WHEN UPPER(nome) LIKE '%SUZANO%' THEN 'SUZANO'
                WHEN UPPER(nome) LIKE '%PERUS%' THEN 'PERUS'
                WHEN UPPER(nome) LIKE '%RIO%PEQUENO%' OR UPPER(nome) LIKE '%RIO PEQUENO%' THEN 'RIO_PEQUENO'
                WHEN UPPER(nome) LIKE '%SAO%MATEUS%' OR UPPER(nome) LIKE '%SÃO%MATEUS%' THEN 'SAO_MATEUS'
                ELSE 'OUTROS'
            END AS loja_tipo,
            COUNT(*) as quantidade,
            STRING_AGG(nome, ', ') as nomes_encontrados
        FROM core.lojas
        WHERE ativo = true
        GROUP BY loja_tipo
        ORDER BY quantidade DESC;
        """
        
        df_contagem = executar_consulta(conn, consulta3, "CONTAGEM POR TIPO")
        
        # Gerar mapeamento Python
        if df_mapeamento is not None and not df_mapeamento.empty:
            logger.info(f"\n🐍 MAPEAMENTO PYTHON PARA IMPORTAÇÃO:")
            logger.info("=" * 50)
            logger.info("# Dicionário para mapear lojas dos arquivos para IDs do Supabase")
            logger.info("MAPEAMENTO_LOJAS = {")
            
            for _, row in df_mapeamento.iterrows():
                if row['loja_mapeada'] != 'OUTROS':
                    logger.info(f"    '{row['loja_mapeada']}': {row['id']},  # {row['nome']}")
            
            logger.info("}")
            
            # Verificar se temos todas as lojas necessárias
            lojas_necessarias = {'MAUA', 'SUZANO', 'SUZANO2', 'PERUS', 'RIO_PEQUENO', 'SAO_MATEUS'}
            lojas_encontradas = set(df_mapeamento[df_mapeamento['loja_mapeada'] != 'OUTROS']['loja_mapeada'])
            
            logger.info(f"\n✅ VERIFICAÇÃO DE COBERTURA:")
            logger.info(f"   Lojas necessárias: {lojas_necessarias}")
            logger.info(f"   Lojas encontradas: {lojas_encontradas}")
            
            lojas_faltando = lojas_necessarias - lojas_encontradas
            if lojas_faltando:
                logger.warning(f"   ⚠️ Lojas faltando: {lojas_faltando}")
            else:
                logger.info(f"   🎉 Todas as lojas encontradas!")
        
    finally:
        conn.close()
        logger.info("\n🔌 Conexão fechada")

if __name__ == "__main__":
    main()