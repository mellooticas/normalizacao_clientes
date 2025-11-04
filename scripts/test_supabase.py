#!/usr/bin/env python3
"""
Teste de Conexão Supabase - Carnê Fácil
Script limpo para validar credenciais e estrutura do banco
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Testa conexão com Supabase"""
    
    # Caregar URL do banco do .env
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL não encontrada no .env")
        return False
    
    logger.info("🔍 Testando conexão Supabase...")
    logger.info(f"URL: {DATABASE_URL[:50]}...")
    
    try:
        # Conectar
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("✅ Conexão estabelecida!")
        
        # Teste básico
        cursor.execute("SELECT version() as versao")
        versao = cursor.fetchone()
        logger.info(f"📊 PostgreSQL: {versao['versao'][:50]}...")
        
        # Verificar schemas existentes
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('core', 'vendas', 'marketing', 'staging', 'auditoria')
            ORDER BY schema_name
        """)
        schemas = cursor.fetchall()
        
        if schemas:
            logger.info("📁 Schemas encontrados:")
            for schema in schemas:
                logger.info(f"  ✓ {schema['schema_name']}")
        else:
            logger.warning("⚠️ Nenhum schema personalizado encontrado")
        
        # Contar tabelas principais
        tabelas = [
            'core.lojas',
            'core.clientes', 
            'core.telefones',
            'vendas.vendas',
            'marketing.cliente_info'
        ]
        
        logger.info("📊 Contagem de registros:")
        for tabela in tabelas:
            try:
                cursor.execute(f"SELECT COUNT(*) as total FROM {tabela}")
                result = cursor.fetchone()
                count = result['total']
                status = "✅" if count > 0 else "⚠️ "
                logger.info(f"  {status} {tabela}: {count:,} registros")
            except Exception as e:
                logger.info(f"  ❌ {tabela}: {str(e)[:50]}...")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Teste de conexão concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {e}")
        
        # Sugestões baseadas no erro
        error_str = str(e).lower()
        if "tenant or user not found" in error_str:
            logger.error("💡 Possível solução: Credenciais Supabase desatualizadas")
            logger.error("   1. Acesse https://app.supabase.com")
            logger.error("   2. Vá em Settings > Database > Connection string")
            logger.error("   3. Atualize SUPABASE_DATABASE_URL no .env")
        elif "connection refused" in error_str:
            logger.error("💡 Possível solução: Problema de rede ou firewall")
        elif "authentication failed" in error_str:
            logger.error("💡 Possível solução: Senha incorreta")
        
        return False

def main():
    """Função principal"""
    logger.info("="*60)
    logger.info("TESTE DE CONEXÃO SUPABASE - CARNÊ FÁCIL")
    logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("="*60)
    
    if test_supabase_connection():
        logger.info("\n🚀 SUPABASE OK - Pronto para importação!")
    else:
        logger.error("\n🔧 AÇÃO NECESSÁRIA: Corrigir conexão Supabase")
        logger.error("Verifique credenciais no .env antes de continuar")

if __name__ == "__main__":
    main()