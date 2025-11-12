#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexão Supabase - Sistema Óticas Carnê Fácil
Valida todas as credenciais e estrutura do banco
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def test_env_variables():
    """Testa se as variáveis de ambiente estão configuradas"""
    logger.info("\n📋 1. Verificando Variáveis de Ambiente")
    logger.info("-" * 60)
    
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
    }
    
    all_ok = True
    for var_name, var_value in required_vars.items():
        if var_value and '[SENHA_DO_BANCO]' not in var_value:
            # Mascarar valores sensíveis
            if 'KEY' in var_name:
                display_value = var_value[:20] + "..." + var_value[-10:]
            elif 'URL' in var_name and '@' in var_value:
                # Mascarar senha na URL
                parts = var_value.split('@')
                before_at = parts[0].rsplit(':', 1)[0]
                display_value = before_at + ":****@" + parts[1]
            else:
                display_value = var_value
            logger.info(f"✅ {var_name}: {display_value}")
        else:
            logger.error(f"❌ {var_name}: NÃO CONFIGURADO")
            if '[SENHA_DO_BANCO]' in str(var_value):
                logger.warning("   ⚠️  Substitua [SENHA_DO_BANCO] pela senha real!")
            all_ok = False
    
    return all_ok

def test_supabase_connection():
    """Testa conexão com Supabase PostgreSQL"""
    logger.info("\n🔌 2. Testando Conexão com Banco de Dados")
    logger.info("-" * 60)
    
    DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL não encontrada no .env")
        return False
    
    if '[SENHA_DO_BANCO]' in DATABASE_URL:
        logger.error("❌ DATABASE_URL contém placeholder [SENHA_DO_BANCO]")
        logger.info("   ℹ️  Edite .env e substitua pela senha real")
        logger.info("   📍 Senha disponível em: Supabase Dashboard > Settings > Database")
        return False
    
    try:
        logger.info("🔄 Conectando ao Supabase...")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        
        logger.info("✅ Conexão estabelecida com sucesso!")
        
        # Testar query simples
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"✅ PostgreSQL: {version[:60]}...")
        
        # Verificar schemas
        logger.info("\n📁 Verificando schemas...")
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast', 'pgbouncer')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        
        if schemas:
            logger.info(f"✅ Schemas encontrados ({len(schemas)}):")
            for schema in schemas:
                logger.info(f"   - {schema[0]}")
        else:
            logger.warning("⚠️  Nenhum schema customizado encontrado")
            logger.info("   Execute os scripts SQL de criação primeiro:")
            logger.info("   - database/02_schema_core_supabase.sql")
            logger.info("   - database/03_schema_vendas_supabase.sql")
        
        # Verificar tabelas no schema core
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'core';
        """)
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'core'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            logger.info(f"\n✅ Tabelas no schema 'core' ({len(tables)}):")
            for table in tables[:10]:
                logger.info(f"   - core.{table[0]}")
            if len(tables) > 10:
                logger.info(f"   ... e mais {len(tables) - 10} tabelas")
        else:
            logger.warning("\n⚠️  Schema 'core' não encontrado ou vazio")
            logger.info("   Execute: database/02_schema_core_supabase.sql")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Erro de conexão: {e}")
        logger.info("\n💡 Possíveis soluções:")
        logger.info("   1. Verifique se a senha no .env está correta")
        logger.info("   2. Confirme que o projeto Supabase está ativo")
        logger.info("   3. Teste sua conexão com internet")
        logger.info("   4. Acesse: https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs")
        return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def test_supabase_client():
    """Testa conexão usando supabase-py (opcional)"""
    logger.info("\n🐍 3. Testando Supabase Python Client (Opcional)")
    logger.info("-" * 60)
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            logger.warning("⚠️  SUPABASE_URL ou SERVICE_ROLE_KEY não configurados")
            return None
        
        logger.info("🔄 Criando cliente Supabase...")
        supabase: Client = create_client(url, key)
        
        logger.info("✅ Cliente Supabase criado com sucesso!")
        logger.info(f"📍 URL: {url}")
        
        return True
        
    except ImportError:
        logger.warning("⚠️  Biblioteca 'supabase' não instalada (opcional)")
        logger.info("   Instale com: pip install supabase")
        return None  # Não é erro crítico
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🔧 TESTE DE CONFIGURAÇÃO SUPABASE")
    print("Sistema Óticas Carnê Fácil")
    from datetime import datetime
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70)
    
    # Verificar arquivo .env
    env_path = Path('.env')
    if not env_path.exists():
        logger.error("\n❌ Arquivo .env não encontrado!")
        logger.info("   📋 Copie .env.example para .env e configure as credenciais")
        logger.info("   📍 Credenciais disponíveis em: https://supabase.com/dashboard")
        return 1
    
    # Executar testes
    results = []
    
    results.append(('Variáveis de Ambiente', test_env_variables()))
    results.append(('Conexão PostgreSQL', test_supabase_connection()))
    
    client_test = test_supabase_client()
    if client_test is not None:
        results.append(('Supabase Client', client_test))
    
    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        if passed:
            print(f"✅ {test_name:.<55} PASSOU")
        else:
            print(f"❌ {test_name:.<55} FALHOU")
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 TUDO CONFIGURADO CORRETAMENTE!")
        print("✅ Sistema pronto para importação de dados")
        print("\n📋 Próximos passos:")
        print("   1. Execute os scripts SQL no Supabase (em ordem)")
        print("   2. Execute: python scripts/import_dados_completos.py")
        print("\n📚 Documentação:")
        print("   - GUIA_CONFIGURACAO_SUPABASE.md")
        print("   - database/README.md")
    else:
        print("\n⚠️  CONFIGURAÇÃO INCOMPLETA")
        print("\n📋 Ações necessárias:")
        print("   1. Configure todas as variáveis no arquivo .env")
        print("   2. Obtenha a senha do banco no dashboard Supabase:")
        print("      https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs")
        print("   3. Execute este teste novamente: python test_conexao_supabase.py")
        print("\n📚 Consulte: GUIA_CONFIGURACAO_SUPABASE.md")
    
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
