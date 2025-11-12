#!/usr/bin/env python3
"""
Script para verificar quantos clientes reais existem no banco
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: SUPABASE_URL ou SUPABASE_KEY não encontrados no .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Verificando dados de clientes...\n")

# 1. Contar total de clientes
try:
    response = supabase.table('core.clientes').select('id', count='exact').execute()
    total_clientes = response.count
    print(f"✅ Total de clientes na tabela core.clientes: {total_clientes:,}")
except Exception as e:
    print(f"❌ Erro ao contar clientes: {e}")

# 2. Verificar view vw_clientes
try:
    response = supabase.table('vw_clientes').select('*', count='exact').limit(0).execute()
    total_view = response.count
    print(f"✅ Total de clientes na view vw_clientes: {total_view:,}")
except Exception as e:
    print(f"❌ Erro ao acessar view: {e}")

# 3. Buscar amostra de 10 clientes
try:
    response = supabase.table('vw_clientes') \
        .select('id, nome, cpf, status, total_vendas, valor_total_vendas, telefone_principal') \
        .order('created_at', desc=True) \
        .limit(10) \
        .execute()
    
    print(f"\n📋 Amostra de 10 clientes mais recentes:\n")
    print(f"{'Nome':<35} {'CPF':<15} {'Status':<10} {'Vendas':<8} {'Valor Total':<15} {'Telefone':<15}")
    print("=" * 115)
    
    for cliente in response.data:
        nome = (cliente.get('nome', 'N/A') or 'N/A')[:34]
        cpf = (cliente.get('cpf', 'N/A') or 'N/A')[:14]
        status = (cliente.get('status', 'N/A') or 'N/A')[:9]
        total_vendas = cliente.get('total_vendas', 0) or 0
        valor_total = cliente.get('valor_total_vendas', 0) or 0
        telefone = (cliente.get('telefone_principal', 'N/A') or 'N/A')[:14]
        
        print(f"{nome:<35} {cpf:<15} {status:<10} {total_vendas:<8} R$ {valor_total:>11,.2f} {telefone:<15}")

except Exception as e:
    print(f"❌ Erro ao buscar amostra: {e}")

# 4. Estatísticas gerais
try:
    response = supabase.rpc('get_stats_clientes').execute()
    if response.data:
        stats = response.data[0] if isinstance(response.data, list) else response.data
        print(f"\n📊 Estatísticas gerais:")
        print(f"  - Total de clientes: {stats.get('total_clientes', 0):,}")
        print(f"  - Clientes com vendas: {stats.get('clientes_com_vendas', 0):,}")
        print(f"  - Clientes sem vendas: {stats.get('clientes_sem_vendas', 0):,}")
except Exception as e:
    # Não é crítico se a função RPC não existir
    pass

print("\n✅ Verificação concluída!")
