#!/usr/bin/env python3
"""
Verificar estrutura da view vw_clientes
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Verificando colunas de vw_clientes...\n")

# Buscar 1 registro para ver estrutura
response = supabase.table('vw_clientes').select('*').limit(1).execute()

if response.data and len(response.data) > 0:
    cliente = response.data[0]
    print("📋 Colunas disponíveis:")
    for coluna in sorted(cliente.keys()):
        valor = cliente[coluna]
        tipo = type(valor).__name__
        print(f"  - {coluna:30s} ({tipo})")
    
    print(f"\n🔍 Tem coluna 'loja_id'? {'loja_id' in cliente}")
    print(f"🔍 Tem coluna relacionada a loja? {any('loja' in k.lower() for k in cliente.keys())}")
else:
    print("❌ Não foi possível buscar dados")

# Buscar lojas disponíveis
print("\n\n📊 Lojas disponíveis no sistema:")
response = supabase.table('lojas').select('id, nome, codigo').execute()
if response.data:
    for loja in response.data:
        print(f"  - {loja.get('nome', 'N/A')} (código: {loja.get('codigo', 'N/A')})")
        
# Verificar relação cliente -> vendas -> loja
print("\n\n🔗 Verificando relação Cliente -> Vendas -> Loja:")
response = supabase.rpc('exec_sql', {
    'sql': '''
        SELECT 
            COUNT(DISTINCT c.id) as total_clientes,
            COUNT(DISTINCT v.loja_id) as lojas_relacionadas,
            l.nome as loja_nome
        FROM core.clientes c
        LEFT JOIN vendas.vendas v ON v.cliente_id = c.id
        LEFT JOIN core.lojas l ON l.id = v.loja_id
        WHERE c.deleted_at IS NULL
        GROUP BY l.nome
        ORDER BY total_clientes DESC
    '''
}).execute()
print(response)
