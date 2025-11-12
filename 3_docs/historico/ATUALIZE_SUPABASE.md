# ⚠️ CREDENCIAIS SUPABASE DESATUALIZADAS

## 🔧 COMO ATUALIZAR

### 1. Acesse o Supabase Dashboard
```
https://app.supabase.com
```

### 2. Selecione seu projeto "Carnê Fácil"

### 3. Vá em Settings > Database
- Clique em "Settings" (⚙️) no menu lateral
- Clique em "Database"

### 4. Copie a Connection String
- Na seção "Connection string"
- Escolha "URI" 
- Copie a string completa (postgres://postgres:[SUA-SENHA]@...)

### 5. Atualize o arquivo .env
Substitua esta linha no arquivo `.env`:
```bash
SUPABASE_DATABASE_URL=postgresql://postgres.gzrjqlbnhkqybvqzjvms:HpKuJXrVBGkONTQN@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

Por:
```bash
SUPABASE_DATABASE_URL=[NOVA-CONNECTION-STRING]
```

### 6. Teste novamente
```bash
python test_supabase.py
```

---

## 🚨 ALTERNATIVA: CRIAR NOVO PROJETO

Se o projeto atual não existir mais:

1. **Criar novo projeto** no Supabase
2. **Nome**: `carne-facil-v2`
3. **Região**: South America (São Paulo)
4. **Copiar novas credenciais**
5. **Executar scripts de schema** em `database/`

---

## 📋 APÓS CORRIGIR CREDENCIAIS

Execute:
```bash
python test_supabase.py
```

Se aparecer "✅ SUPABASE OK", prosseguimos para:
```bash
python import_dados.py
```

---

**🎯 STATUS ATUAL:**
- ✅ Dados consolidados localizados (13,710 clientes + 6,115 vendas)
- ✅ Limpeza do repositório concluída
- ⚠️ Credenciais Supabase precisam atualização
- ⏳ Importação pronta para executar