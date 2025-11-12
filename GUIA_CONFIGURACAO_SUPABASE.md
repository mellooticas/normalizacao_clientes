# 🔧 Guia de Configuração Supabase

**Data:** 12 de novembro de 2025  
**Projeto:** Sistema Óticas Carnê Fácil  
**Status:** ✅ Configurado

---

## 📋 Informações do Projeto

### 🔗 URLs e Credenciais

**URL do Projeto:**
```
https://jrhevexrzaoeyhmpwvgs.supabase.co
```

**Project Reference:**
```
jrhevexrzaoeyhmpwvgs
```

**Anon Key (Pública):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyaGV2ZXhyemFvZXlobXB3dmdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNDI1MTMsImV4cCI6MjA3NTcxODUxM30.fOMiindaZq_hGdvv1AeFkRvj5LXp6K1HSAt3hqYg6mo
```

**Service Role Key (Privada - NÃO COMPARTILHAR):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyaGV2ZXhyemFvZXlobXB3dmdzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDE0MjUxMywiZXhwIjoyMDc1NzE4NTEzfQ.np2V3zE02T947ElDSo2kWDZbc21wIVgsn14HwumcAp0
```

---

## 🚀 Passo a Passo de Configuração

### 1️⃣ Obter Senha do Banco de Dados

A senha do banco **NÃO** está nos tokens JWT acima. Você precisa:

1. Acessar: https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs
2. Ir em **Settings** → **Database**
3. Na seção **Connection String**, você verá a senha ou poderá resetá-la

### 2️⃣ Configurar Arquivo .env

O arquivo `.env` já foi criado na raiz do projeto. Você precisa:

1. Abrir o arquivo `.env`
2. Substituir `[SENHA_DO_BANCO]` pela senha real do Supabase
3. Salvar o arquivo

**Exemplo:**
```env
# ANTES:
DATABASE_URL=postgresql://postgres.jrhevexrzaoeyhmpwvgs:[SENHA_DO_BANCO]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres

# DEPOIS (com sua senha):
DATABASE_URL=postgresql://postgres.jrhevexrzaoeyhmpwvgs:sua_senha_aqui@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### 3️⃣ Instalar Dependências Python

```bash
pip install python-dotenv psycopg2-binary pandas supabase
```

### 4️⃣ Testar Conexão

Execute o script de teste:

```bash
python scripts/test_supabase.py
```

---

## 🗄️ Strings de Conexão

### Pooler Connection (Recomendado para aplicações)
```
postgresql://postgres.jrhevexrzaoeyhmpwvgs:[SENHA]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### Direct Connection (Para migrations e operações administrativas)
```
postgresql://postgres:[SENHA]@db.jrhevexrzaoeyhmpwvgs.supabase.co:5432/postgres
```

### Connection URI Components:
- **Host (Pooler):** `aws-0-sa-east-1.pooler.supabase.com`
- **Port (Pooler):** `6543`
- **Host (Direct):** `db.jrhevexrzaoeyhmpwvgs.supabase.co`
- **Port (Direct):** `5432`
- **Database:** `postgres`
- **User:** `postgres.jrhevexrzaoeyhmpwvgs` (pooler) ou `postgres` (direct)

---

## 🔐 Segurança

### ⚠️ IMPORTANTE - NÃO COMPARTILHAR:

- ❌ Service Role Key (bypass RLS)
- ❌ Senha do banco de dados
- ❌ Arquivo `.env`

### ✅ Pode compartilhar (público):

- ✅ URL do projeto
- ✅ Anon Key (já é pública)
- ✅ Project Reference

### 🛡️ Boas Práticas:

1. **Nunca** commite o arquivo `.env` no Git
   - Já está no `.gitignore`
   
2. **Sempre** use Service Role Key apenas no backend
   - Scripts de importação: ✅
   - Frontend/Client: ❌

3. **Prefira** Anon Key + RLS no frontend
   - Mais seguro
   - Row Level Security protege os dados

---

## 📝 Scripts de Conexão Python

### Usando psycopg2 (Raw SQL):

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Conexão via pooler (recomendado)
conn = psycopg2.connect(
    os.getenv('DATABASE_URL'),
    sslmode='require'
)

# Ou conexão direta
conn = psycopg2.connect(
    os.getenv('SUPABASE_DB_DIRECT_URL'),
    sslmode='require'
)
```

### Usando supabase-py (SDK):

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(url, key)

# Query
data = supabase.table('clientes').select('*').execute()
```

---

## 🎯 Próximas Ações

### 1. Completar Configuração ✅
- [ ] Obter senha do banco no dashboard Supabase
- [ ] Atualizar arquivo `.env` com a senha
- [ ] Testar conexão com `test_supabase.py`

### 2. Executar Scripts SQL 📊
```bash
# Na ordem:
1. database/02_schema_core_supabase.sql
2. database/03_schema_vendas_supabase.sql
3. database/04_schema_optica_supabase.sql
4. database/05_schema_marketing_supabase.sql
5. database/06_schema_auditoria_supabase.sql
6. database/07_rls_policies_supabase.sql
7. database/08_views_functions_supabase.sql
8. database/10_populacao_vendedores_normalizado.sql
9. database/11_populacao_canais_captacao.sql
```

### 3. Importar Dados 🚀
```bash
python scripts/import_dados_completos.py
```

### 4. Validar 🔍
```bash
python scripts/validar_completo_antes_importar.py
```

---

## 🆘 Troubleshooting

### Erro: "password authentication failed"
- ✅ Verifique se a senha no `.env` está correta
- ✅ Confirme que não há espaços extras na senha
- ✅ Tente resetar a senha no dashboard

### Erro: "SSL connection required"
- ✅ Adicione `sslmode='require'` na conexão
- ✅ Use a string de conexão completa com `?sslmode=require`

### Erro: "connection timeout"
- ✅ Verifique sua conexão com internet
- ✅ Confirme que o projeto Supabase está ativo
- ✅ Tente usar a conexão direta em vez do pooler

### Erro: "relation does not exist"
- ✅ Execute os scripts SQL de criação de schemas primeiro
- ✅ Verifique se está usando o schema correto (ex: `core.clientes`)

---

## 📞 Suporte

**Dashboard Supabase:**  
https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs

**Documentação:**
- https://supabase.com/docs
- https://supabase.com/docs/guides/database

**Logs do Projeto:**
- https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs/logs/postgres-logs

---

**Configurado em:** 12 de novembro de 2025  
**Status:** ✅ Pronto para uso (após adicionar senha do banco)
