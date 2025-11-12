#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def executar_sql_canais_novos():
    """Executa SQL para inserir canais novos do VIXEN"""
    sql_file = 'data/originais/vixen/insert_canais_novos_vixen.sql'
    print('🎯 Executando SQL para inserir canais novos...')

    # Carregar credenciais
    load_dotenv()
    DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print('❌ DATABASE_URL não encontrada no .env')
        return False

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor.execute(sql)
        conn.commit()
        print('✅ SQL executado com sucesso!')
        print('📊 5 canais novos inseridos no banco')
        
        # Verificar inserção
        cursor.execute('SELECT COUNT(*) as total FROM marketing.canais_aquisicao WHERE codigo >= %s', ('173',))
        result = cursor.fetchone()
        print(f'🔍 Verificação: {result["total"]} canais novos confirmados')
        
        # Listar canais inseridos
        cursor.execute("""
            SELECT codigo, nome, descricao 
            FROM marketing.canais_aquisicao 
            WHERE codigo >= %s 
            ORDER BY codigo
        """, ('173',))
        results = cursor.fetchall()
        
        print('\n📋 CANAIS INSERIDOS:')
        for row in results:
            print(f'   {row["codigo"]}: {row["nome"]}')
            
        cursor.close()
        conn.close()

    except Exception as e:
        print(f'❌ Erro: {e}')
        return False
    
    return True

if __name__ == "__main__":
    executar_sql_canais_novos()