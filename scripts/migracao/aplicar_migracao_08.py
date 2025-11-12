import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

print("🚀 APLICANDO MIGRAÇÃO: 08_funcao_lista_clientes_com_loja.sql\n")
print("="*70)

# Ler arquivo SQL
with open('../../database/migrations/08_funcao_lista_clientes_com_loja.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Executar apenas a criação da função (sem os testes comentados)
sql_function = sql_content.split('-- ============================================================================\n-- Testes de Validação')[0]

print("\n📝 Executando criação da função get_clientes_lista()...")
try:
    # Aqui você precisaria executar o SQL no Supabase
    # Via SQL Editor ou API
    print("✅ Execute manualmente no SQL Editor do Supabase:")
    print("\n" + "="*70)
    print(sql_function)
    print("="*70)
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n\n🧪 APÓS APLICAR, TESTE COM:")
print("""
-- Teste 1: Buscar primeiros 10 clientes
SELECT id, nome, total_vendas, total_count
FROM public.get_clientes_lista(p_limit := 10, p_offset := 0);

-- Teste 2: Filtrar por loja
WITH loja_teste AS (
    SELECT id, nome FROM public.lojas WHERE ativo = true LIMIT 1
)
SELECT c.nome, c.total_vendas, c.total_count
FROM loja_teste l,
     LATERAL public.get_clientes_lista(p_loja_id := l.id, p_limit := 5) c;
""")
