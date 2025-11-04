#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consultar vendedores no Supabase
Busca UUIDs dos vendedores/consultores para mapeamento nos dados normalizados
"""

import os
import psycopg2
import pandas as pd
from pathlib import Path

# Configuração do banco
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres.gzrjqlbnhkqybvqzjvms:A8HFydvpfOGe8V8B@aws-0-sa-east-1.pooler.supabase.com:6543/postgres')

def conectar_supabase():
    """Conecta ao Supabase"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def consultar_vendedores():
    """Consulta vendedores no Supabase"""
    
    conn = conectar_supabase()
    if not conn:
        return
    
    try:
        # Consulta básica
        print("=== VENDEDORES NO SUPABASE ===")
        query1 = """
        SELECT 
            id,
            nome,
            codigo,
            loja_id,
            ativo,
            created_at
        FROM core.vendedores
        ORDER BY nome;
        """
        
        df_vendedores = pd.read_sql(query1, conn)
        print(f"Total de vendedores encontrados: {len(df_vendedores)}")
        print("\nVendedores:")
        print(df_vendedores.to_string(index=False))
        
        # Consulta de mapeamento
        print("\n=== MAPEAMENTO PARA CONSULTORES DOS DADOS ===")
        query2 = """
        SELECT 
            id,
            nome,
            codigo,
            loja_id,
            ativo,
            CASE 
                WHEN UPPER(nome) LIKE '%BETH%' OR UPPER(nome) LIKE '%ELIZABETE%' OR UPPER(nome) LIKE '%BETHÂNIA%' THEN 'BETH'
                WHEN UPPER(nome) LIKE '%FELIPE%' THEN 'FELIPE' 
                WHEN UPPER(nome) LIKE '%LARISSA%' THEN 'LARISSA'
                WHEN UPPER(nome) LIKE '%TATY%' OR UPPER(nome) LIKE '%TATIANA%' OR UPPER(nome) LIKE '%TATIANE%' THEN 'TATY'
                WHEN UPPER(nome) LIKE '%WEVILLY%' OR UPPER(nome) LIKE '%WEVILY%' THEN 'WEVILLY'
                WHEN UPPER(nome) LIKE '%ERIKA%' OR UPPER(nome) LIKE '%ÉRIKA%' THEN 'ERIKA'
                WHEN UPPER(nome) LIKE '%ROGÉRIO%' OR UPPER(nome) LIKE '%ROGERIO%' THEN 'ROGÉRIO'
                ELSE 'OUTROS'
            END AS consultor_mapeado
        FROM core.vendedores
        WHERE ativo = true
        ORDER BY nome;
        """
        
        df_mapeamento = pd.read_sql(query2, conn)
        print("Mapeamento de vendedores:")
        print(df_mapeamento.to_string(index=False))
        
        # Agrupa por consultor
        print("\n=== AGRUPAMENTO POR CONSULTOR ===")
        query3 = """
        SELECT 
            CASE 
                WHEN UPPER(nome) LIKE '%BETH%' OR UPPER(nome) LIKE '%ELIZABETE%' OR UPPER(nome) LIKE '%BETHÂNIA%' THEN 'BETH'
                WHEN UPPER(nome) LIKE '%FELIPE%' THEN 'FELIPE' 
                WHEN UPPER(nome) LIKE '%LARISSA%' THEN 'LARISSA'
                WHEN UPPER(nome) LIKE '%TATY%' OR UPPER(nome) LIKE '%TATIANA%' OR UPPER(nome) LIKE '%TATIANE%' THEN 'TATY'
                WHEN UPPER(nome) LIKE '%WEVILLY%' OR UPPER(nome) LIKE '%WEVILY%' THEN 'WEVILLY'
                WHEN UPPER(nome) LIKE '%ERIKA%' OR UPPER(nome) LIKE '%ÉRIKA%' THEN 'ERIKA'
                WHEN UPPER(nome) LIKE '%ROGÉRIO%' OR UPPER(nome) LIKE '%ROGERIO%' THEN 'ROGÉRIO'
                ELSE 'OUTROS'
            END AS consultor_tipo,
            COUNT(*) as quantidade,
            STRING_AGG(nome, ', ') as nomes_encontrados,
            STRING_AGG(DISTINCT id::text, ', ') as uuids
        FROM core.vendedores
        WHERE ativo = true
        GROUP BY consultor_tipo
        ORDER BY quantidade DESC;
        """
        
        df_agrupado = pd.read_sql(query3, conn)
        print("Agrupamento por consultor:")
        print(df_agrupado.to_string(index=False))
        
        # Gera mapeamento para uso nos dados
        print("\n=== MAPEAMENTO PYTHON PARA USO ===")
        print("VENDEDOR_UUID_MAP = {")
        
        vendedores_encontrados = df_mapeamento[df_mapeamento['consultor_mapeado'] != 'OUTROS']
        for _, row in vendedores_encontrados.iterrows():
            consultor = row['consultor_mapeado']
            uuid = row['id']
            nome = row['nome']
            print(f"    '{consultor}': '{uuid}',  # {nome}")
        
        print("}")
        
        # Estatísticas dos dados
        print("\n=== ESTATÍSTICAS DOS DADOS NORMALIZADOS ===")
        consultores_dados = {
            'BETH': 641,
            'FELIPE': 208, 
            'LARISSA': 58,
            'TATY': 37,
            'WEVILLY': 17,
            'ERIKA': 9,
            'ROGÉRIO': 5
        }
        
        print("Consultores nos dados normalizados:")
        for consultor, qtd in consultores_dados.items():
            encontrado = consultor in df_mapeamento['consultor_mapeado'].values
            status = "✅ ENCONTRADO" if encontrado else "❌ NÃO ENCONTRADO"
            print(f"  {consultor}: {qtd} vendas - {status}")
        
    except Exception as e:
        print(f"Erro durante consulta: {e}")
    
    finally:
        conn.close()

def main():
    """Função principal"""
    print("=== CONSULTA VENDEDORES SUPABASE ===")
    consultar_vendedores()

if __name__ == "__main__":
    main()