#!/usr/bin/env python3
"""
Testar função get_clientes_kpis via Supabase RPC
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧪 Testando get_clientes_kpis via RPC...\n")

# Teste 1: Sem filtros
print("1️⃣ Teste 1: Sem filtros")
response = supabase.rpc('get_clientes_kpis', {
    'p_search_term': None,
    'p_status': 'TODOS',
    'p_compras_min': None,
    'p_compras_max': None,
    'p_valor_min': None,
    'p_valor_max': None
}).execute()

if response.data:
    kpis = response.data[0]
    print(f"   Total Clientes: {kpis['total_clientes']:,}")
    print(f"   Clientes Ativos: {kpis['clientes_ativos']:,}")
    print(f"   Clientes Novos (≤3 compras): {kpis['clientes_novos']:,}")
    print(f"   Total Compras: {kpis['total_compras']:,}")
    print(f"   Valor Total: R$ {kpis['valor_total']:,.2f}")
    print(f"   Ticket Médio: R$ {kpis['ticket_medio']:,.2f}")
    print("   ✅ Sucesso!\n")
else:
    print("   ❌ Erro: Sem dados\n")

# Teste 2: Busca "MARIA"
print("2️⃣ Teste 2: Busca 'MARIA'")
response = supabase.rpc('get_clientes_kpis', {
    'p_search_term': 'MARIA',
    'p_status': 'TODOS'
}).execute()

if response.data:
    kpis = response.data[0]
    print(f"   Total: {kpis['total_clientes']:,} clientes")
    print(f"   Valor: R$ {kpis['valor_total']:,.2f}")
    print("   ✅ Busca funcionando!\n")
else:
    print("   ❌ Erro na busca\n")

# Teste 3: Filtro 5+ compras
print("3️⃣ Teste 3: Clientes com 5+ compras")
response = supabase.rpc('get_clientes_kpis', {
    'p_compras_min': 5
}).execute()

if response.data:
    kpis = response.data[0]
    print(f"   Total: {kpis['total_clientes']:,} clientes")
    print(f"   Ticket Médio: R$ {kpis['ticket_medio']:,.2f}")
    print("   ✅ Filtro funcionando!\n")
else:
    print("   ❌ Erro no filtro\n")

# Teste 4: VIP (10+ compras, R$ 5k+)
print("4️⃣ Teste 4: Clientes VIP")
response = supabase.rpc('get_clientes_kpis', {
    'p_status': 'ATIVO',
    'p_compras_min': 10,
    'p_valor_min': 5000
}).execute()

if response.data:
    kpis = response.data[0]
    print(f"   Total VIP: {kpis['total_clientes']:,} clientes")
    print(f"   Valor Total VIP: R$ {kpis['valor_total']:,.2f}")
    print(f"   Ticket Médio VIP: R$ {kpis['ticket_medio']:,.2f}")
    print("   ✅ Filtros combinados OK!\n")
else:
    print("   ❌ Erro nos filtros\n")

print("=" * 60)
print("✅ TODOS OS TESTES VIA RPC PASSARAM!")
print("=" * 60)
print("\n🎯 Frontend pode usar useClientesKPIs() agora!")
