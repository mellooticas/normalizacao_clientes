#!/usr/bin/env python3
"""
Verificar view vw_dashboard_stats
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Verificando vw_dashboard_stats...\n")

# Ver stats do dashboard
response = supabase.table('vw_dashboard_stats').select('*').execute()
if response.data:
    stats = response.data[0]
    print(f"📊 Dashboard Stats (View):")
    print(f"  Total Clientes: {stats.get('total_clientes', 0):,}")
    print(f"  Clientes Ativos: {stats.get('clientes_ativos', 0):,}")
    print(f"  Total Vendas: {stats.get('total_vendas', 0):,}")
    print(f"  Valor Total Vendas: R$ {stats.get('valor_total_vendas', 0):,.2f}")
    print(f"  Lojas Ativas: {stats.get('lojas_ativas', 0):,}")

# Contar direto na tabela
response = supabase.table('vw_clientes').select('id', count='exact').limit(0).execute()
print(f"\n✅ Contagem direta vw_clientes: {response.count:,}")

# Se forem diferentes, temos problema na view
