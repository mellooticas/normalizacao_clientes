import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

print("🔍 INVESTIGANDO DUPLICAÇÃO: public.vendas vs vendas.vendas\n")
print("="*70)

# 1. Contar registros em ambas as tabelas
print("\n📊 CONTAGEM DE REGISTROS:")
try:
    public_count = supabase.table('vendas').select('id', count='exact').execute()
    print(f"  • public.vendas: {public_count.count} registros")
except Exception as e:
    print(f"  • public.vendas: ERRO - {e}")

try:
    # Supabase não tem suporte direto para schema.table, precisa usar RPC
    from supabase import PostgrestAPIError
    vendas_vendas = supabase.rpc('exec_raw_sql', {
        'query': 'SELECT COUNT(*) FROM vendas.vendas WHERE deleted_at IS NULL'
    }).execute()
    print(f"  • vendas.vendas: {vendas_vendas.data} registros ativos")
except Exception as e:
    print(f"  • vendas.vendas: Verificar manualmente")

# 2. Verificar estrutura das colunas
print("\n\n📋 ESTRUTURA DAS TABELAS:")
print("\n  public.vendas:")
try:
    sample = supabase.table('vendas').select('*').limit(1).execute()
    if sample.data:
        colunas_public = list(sample.data[0].keys())
        print(f"    Colunas ({len(colunas_public)}): {', '.join(sorted(colunas_public))}")
except Exception as e:
    print(f"    ERRO: {e}")

# 3. Verificar relacionamentos
print("\n\n🔗 RELACIONAMENTOS IMPORTANTES:")
print("\n  Verificar se outras tabelas referenciam public.vendas:")
print("    - vw_clientes usa public.vendas? ❓")
print("    - Outras views/funções usam public.vendas? ❓")
print("    - Frontend usa public.vendas diretamente? ❓")

# 4. Recomendação
print("\n\n💡 RECOMENDAÇÃO:")
print("  1️⃣  Se public.vendas é réplica exata → ELIMINAR e usar apenas vendas.vendas")
print("  2️⃣  Se public.vendas tem dados diferentes → CONSOLIDAR em uma única tabela")
print("  3️⃣  Atualizar todas as referências (views, functions, frontend) para vendas.vendas")
print("  4️⃣  Criar VIEW em public se necessário: CREATE VIEW public.vendas AS SELECT * FROM vendas.vendas")

print("\n\n⚠️  PRÓXIMO PASSO:")
print("  Execute no SQL Editor do Supabase:")
print("  ")
print("  -- Verificar se são idênticas")
print("  SELECT ")
print("    (SELECT COUNT(*) FROM public.vendas) as public_count,")
print("    (SELECT COUNT(*) FROM vendas.vendas WHERE deleted_at IS NULL) as vendas_count;")
print("  ")
print("  -- Verificar dependências")
print("  SELECT ")
print("    schemaname, ")
print("    viewname, ")
print("    definition")
print("  FROM pg_views ")
print("  WHERE definition ILIKE '%public.vendas%';")
print("  ")
print("  -- Verificar funções que usam public.vendas")
print("  SELECT ")
print("    proname as function_name,")
print("    pg_get_functiondef(oid) as definition")
print("  FROM pg_proc ")
print("  WHERE pg_get_functiondef(oid) ILIKE '%public.vendas%';")

print("\n" + "="*70)
