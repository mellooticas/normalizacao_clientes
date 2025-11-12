import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Carregar .env.local do frontend
env_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env.local')
load_dotenv(env_path)

# Verificar se variáveis foram carregadas
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not url or not key:
    print("❌ ERRO: Variáveis de ambiente não encontradas!")
    print(f"   Procurado em: {env_path}")
    print(f"   NEXT_PUBLIC_SUPABASE_URL: {'✅' if url else '❌'}")
    print(f"   Chave: {'✅' if key else '❌'}")
    sys.exit(1)

print(f"🔗 Conectando ao Supabase...")
supabase = create_client(url, key)

print("🔍 VERIFICANDO FUNÇÃO: get_clientes_lista()\n")
print("="*70)

# Teste 1: Buscar primeiros 5 clientes sem filtros
print("\n✅ Teste 1: Primeiros 5 clientes (sem filtros)")
try:
    result = supabase.rpc('get_clientes_lista', {
        'p_limit': 5,
        'p_offset': 0
    }).execute()
    
    if result.data:
        print(f"   📊 Encontrados: {len(result.data)} clientes")
        print(f"   📈 Total no banco: {result.data[0].get('total_count', 'N/A')}")
        for cliente in result.data[:3]:
            print(f"   - {cliente['nome']} (Vendas: {cliente['total_vendas']})")
    else:
        print("   ⚠️  Nenhum cliente retornado")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# Teste 2: Buscar com filtro de loja
print("\n\n✅ Teste 2: Clientes com filtro de LOJA")
try:
    # Buscar primeira loja ativa
    lojas = supabase.table('lojas').select('id, nome').eq('ativo', True).limit(1).execute()
    
    if lojas.data:
        loja = lojas.data[0]
        print(f"   🏪 Testando com loja: {loja['nome']}")
        
        result = supabase.rpc('get_clientes_lista', {
            'p_loja_id': loja['id'],
            'p_limit': 5,
            'p_offset': 0
        }).execute()
        
        if result.data:
            print(f"   📊 Clientes da loja: {len(result.data)}")
            print(f"   📈 Total da loja: {result.data[0].get('total_count', 'N/A')}")
            for cliente in result.data[:3]:
                print(f"   - {cliente['nome']} (Vendas: {cliente['total_vendas']})")
        else:
            print("   ⚠️  Nenhum cliente encontrado para esta loja")
    else:
        print("   ⚠️  Nenhuma loja ativa encontrada")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# Teste 3: Buscar com termo de pesquisa
print("\n\n✅ Teste 3: Busca por 'MARIA'")
try:
    result = supabase.rpc('get_clientes_lista', {
        'p_search_term': 'MARIA',
        'p_limit': 5,
        'p_offset': 0
    }).execute()
    
    if result.data:
        print(f"   📊 Encontrados: {len(result.data)} clientes")
        print(f"   📈 Total com MARIA: {result.data[0].get('total_count', 'N/A')}")
        for cliente in result.data[:3]:
            print(f"   - {cliente['nome']}")
    else:
        print("   ⚠️  Nenhum cliente com MARIA encontrado")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# Teste 4: Buscar com múltiplos filtros (loja + busca)
print("\n\n✅ Teste 4: MARIA + Filtro de LOJA")
try:
    lojas = supabase.table('lojas').select('id, nome').eq('ativo', True).limit(1).execute()
    
    if lojas.data:
        loja = lojas.data[0]
        print(f"   🏪 Loja: {loja['nome']}")
        print(f"   🔍 Busca: MARIA")
        
        result = supabase.rpc('get_clientes_lista', {
            'p_search_term': 'MARIA',
            'p_loja_id': loja['id'],
            'p_limit': 5,
            'p_offset': 0
        }).execute()
        
        if result.data:
            print(f"   📊 Encontrados: {len(result.data)} clientes")
            print(f"   📈 Total: {result.data[0].get('total_count', 'N/A')}")
            for cliente in result.data[:3]:
                print(f"   - {cliente['nome']} (Vendas: {cliente['total_vendas']})")
        else:
            print("   ⚠️  Nenhum cliente encontrado com esses filtros")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# Teste 5: Paginação
print("\n\n✅ Teste 5: Paginação (página 2)")
try:
    result = supabase.rpc('get_clientes_lista', {
        'p_limit': 5,
        'p_offset': 5  # Pular os primeiros 5
    }).execute()
    
    if result.data:
        print(f"   📊 Página 2: {len(result.data)} clientes")
        print(f"   📈 Total: {result.data[0].get('total_count', 'N/A')}")
        for cliente in result.data[:3]:
            print(f"   - {cliente['nome']}")
    else:
        print("   ⚠️  Nenhum cliente na página 2")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

print("\n\n" + "="*70)
print("✅ VERIFICAÇÃO COMPLETA!")
print("\nSe todos os testes passaram, o filtro de loja está funcionando! 🎉")
