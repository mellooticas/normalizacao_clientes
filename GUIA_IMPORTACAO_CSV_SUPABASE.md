# 📊 Guia de Importação CSV → Supabase

**Fluxo de Trabalho:** Gerar CSVs normalizados → Importar direto nas tabelas

**Data:** 12 de novembro de 2025  
**Status:** 🟢 Pronto para executar

---

## 🎯 FLUXO DE TRABALHO

### 1. Gerar CSVs Normalizados
```python
# Scripts já prontos para gerar CSVs:
python scripts/gerar_arquivos_finais_banco_final.py
python scripts/gerar_vendas_completas_finais.py
python scripts/gerar_telefones_core_final.py
python scripts/gerar_clientes_uuid.py
```

### 2. Importar Direto no Supabase
- Via **Table Editor** (interface gráfica)
- Via **SQL Editor** (comando COPY)
- Via **psycopg2** (Python COPY)

---

## 📁 ARQUIVOS CSV DISPONÍVEIS

### CSVs Prontos em `data_backup/`:

```
✅ vendas_os_completo.csv                      (6.117 linhas)
✅ marketing_origens_vixen_correto.csv
✅ marketing_origens_vixen_vendedores_normalizados.csv
```

### Estrutura do CSV Principal (vendas_os_completo.csv):

**Colunas principais:**
- `os_n` - Número da OS
- `loja` - Nome da loja
- `data_de_compra` - Data da venda
- `consultor` - Vendedor/Consultor
- `nome` - Nome do cliente
- `cpf`, `rg`, `dt_nasc` - Dados pessoais
- `telefone`, `celular`, `email` - Contatos
- `cep`, `end`, `n`, `bairro`, `comp` - Endereço
- `total` - Valor total
- `pagto_1`, `sinal_1`, etc. - Pagamentos
- `como_conheceu` - Canal de aquisição

---

## 🚀 MÉTODOS DE IMPORTAÇÃO

### Método 1: Table Editor (Interface Gráfica) ⭐ RECOMENDADO

**Passo a passo:**

1. Acesse: https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs
2. Vá em **Table Editor**
3. Selecione a tabela de destino
4. Clique em **Import data via spreadsheet**
5. Selecione o arquivo CSV
6. Mapeie as colunas
7. Clique em **Import**

**Vantagens:**
- ✅ Visual e intuitivo
- ✅ Valida dados automaticamente
- ✅ Mostra erros linha por linha
- ✅ Permite corrigir antes de importar

**Limitações:**
- ⚠️ Arquivos até 50MB
- ⚠️ Pode ser lento para muitos registros

---

### Método 2: SQL Editor (COPY Command) 🚀 RÁPIDO

**Para importar via SQL:**

```sql
-- 1. Criar tabela temporária (se necessário)
CREATE TEMP TABLE temp_vendas (
    os_n VARCHAR,
    loja VARCHAR,
    data_de_compra TIMESTAMP,
    consultor VARCHAR,
    nome VARCHAR,
    cpf VARCHAR,
    total NUMERIC,
    -- ... outras colunas
);

-- 2. Copiar dados do CSV
-- Nota: Você precisa fazer upload do CSV primeiro via Storage
COPY temp_vendas 
FROM '/path/to/vendas_os_completo.csv'
DELIMITER ',' 
CSV HEADER;

-- 3. Inserir na tabela final com transformações
INSERT INTO vendas.vendas (
    numero_os,
    loja_id,
    data_venda,
    cliente_id,
    valor_total
)
SELECT 
    os_n::INTEGER,
    (SELECT id FROM core.lojas WHERE nome_normalizado = UPPER(loja) LIMIT 1),
    data_de_compra,
    (SELECT id FROM core.clientes WHERE cpf = temp_vendas.cpf LIMIT 1),
    total::NUMERIC
FROM temp_vendas
WHERE os_n IS NOT NULL;

-- 4. Limpar temporária
DROP TABLE temp_vendas;
```

**Vantagens:**
- ✅ Muito rápido
- ✅ Processa milhares de linhas
- ✅ Permite transformações em SQL

**Limitações:**
- ⚠️ Precisa criar tabela temporária
- ⚠️ Upload via Storage ou servidor

---

### Método 3: Python com psycopg2 (Programático) 💻 FLEXÍVEL

**Script de importação:**

```python
#!/usr/bin/env python3
"""
Importação CSV → Supabase via Python
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

def importar_csv_para_supabase(csv_path, table_name, schema='vendas'):
    """Importa CSV diretamente para tabela do Supabase"""
    
    # Conectar
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
    cursor = conn.cursor()
    
    # Ler CSV
    print(f"📖 Lendo {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✅ {len(df):,} linhas carregadas")
    
    # Preparar dados
    colunas = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    
    # Inserir em lote
    print(f"⬆️  Importando para {schema}.{table_name}...")
    
    query = f"""
        INSERT INTO {schema}.{table_name} ({colunas})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    # Converter DataFrame para lista de tuplas
    dados = [tuple(x) for x in df.to_numpy()]
    
    # Executar em lote (mais rápido)
    execute_values(cursor, query, dados, page_size=1000)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Importação concluída!")

# Uso
if __name__ == "__main__":
    importar_csv_para_supabase(
        csv_path='data_backup/vendas_os_completo.csv',
        table_name='vendas_raw',
        schema='staging'
    )
```

**Vantagens:**
- ✅ Muito flexível
- ✅ Permite transformações complexas
- ✅ Controle total do processo
- ✅ Logs detalhados
- ✅ Tratamento de erros

**Uso:**
```bash
python scripts/importar_csv_direto.py
```

---

## 📋 PREPARAÇÃO DOS CSVS

### Script para Gerar CSVs Prontos para Importação:

```python
#!/usr/bin/env python3
"""
Gera CSVs prontos para importação no Supabase
"""

import pandas as pd
from pathlib import Path

def preparar_vendas_csv():
    """Prepara CSV de vendas com estrutura correta"""
    
    # Ler arquivo original
    df = pd.read_csv('data_backup/vendas_os_completo.csv')
    
    # Mapear colunas para estrutura do banco
    df_final = pd.DataFrame({
        'numero_os': df['os_n'],
        'loja_nome': df['loja'],
        'data_venda': pd.to_datetime(df['data_de_compra']),
        'vendedor_nome': df['consultor'],
        'cliente_nome': df['nome'],
        'cliente_cpf': df['cpf'].str.replace(r'\D', '', regex=True),  # Limpar
        'cliente_telefone': df['telefone'],
        'cliente_celular': df['celular'],
        'cliente_email': df['email'],
        'valor_total': pd.to_numeric(df['total'], errors='coerce'),
        'forma_pagamento': df['pagto_1'],
        'valor_entrada': pd.to_numeric(df['sinal_1'], errors='coerce'),
        'canal_aquisicao': df['como_conheceu']
    })
    
    # Remover linhas inválidas
    df_final = df_final.dropna(subset=['numero_os'])
    
    # Salvar
    output_dir = Path('outputs/import_supabase')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arquivo_saida = output_dir / 'vendas_pronto_importar.csv'
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print(f"✅ Arquivo gerado: {arquivo_saida}")
    print(f"📊 Total de registros: {len(df_final):,}")
    
    return df_final

if __name__ == "__main__":
    preparar_vendas_csv()
```

---

## 🗺️ MAPEAMENTO DE TABELAS

### Tabelas Supabase vs CSVs:

```
core.clientes           ← clientes_normalizados.csv
├── core.telefones      ← telefones_core_final.csv
└── core.endereco_cliente ← enderecos_clientes.csv

core.lojas              ← lojas.csv (6 lojas fixas)
core.vendedores         ← vendedores_normalizados.csv

vendas.vendas           ← vendas_os_completo.csv
├── vendas.itens_venda  ← itens_vendas.csv
└── vendas.formas_pagamento_venda ← pagamentos_vendas.csv

marketing.canais_aquisicao ← canais_captacao.csv
marketing.cliente_origem   ← marketing_origens.csv
```

---

## ✅ CHECKLIST DE IMPORTAÇÃO

### Antes de Importar:

- [ ] Schemas criados no Supabase (execute SQLs em `database/`)
- [ ] Senha do banco configurada no `.env`
- [ ] Teste de conexão OK: `python test_conexao_supabase.py`
- [ ] CSVs gerados e validados
- [ ] Colunas mapeadas corretamente

### Durante a Importação:

- [ ] Importar tabelas na ordem correta (dependências)
- [ ] Lojas primeiro (dados mestres)
- [ ] Depois vendedores
- [ ] Depois clientes
- [ ] Por último vendas

### Após Importação:

- [ ] Validar contagens: `SELECT COUNT(*) FROM cada_tabela`
- [ ] Verificar integridade referencial
- [ ] Testar queries principais
- [ ] Validar totais financeiros

---

## 🔄 ORDEM DE IMPORTAÇÃO (IMPORTANTE!)

```
1️⃣ core.lojas                    (dados mestres)
2️⃣ core.vendedores               (sem dependências)
3️⃣ marketing.canais_aquisicao    (sem dependências)
4️⃣ core.clientes                 (sem dependências)
5️⃣ core.telefones                (depende de clientes)
6️⃣ core.endereco_cliente         (depende de clientes)
7️⃣ vendas.vendas                 (depende de clientes, lojas, vendedores)
8️⃣ vendas.itens_venda            (depende de vendas)
9️⃣ vendas.formas_pagamento_venda (depende de vendas)
```

---

## 🛠️ SCRIPTS ÚTEIS

### Gerar Todos os CSVs para Importação:

```bash
# 1. Clientes
python scripts/gerar_clientes_uuid.py

# 2. Telefones
python scripts/gerar_telefones_core_final.py

# 3. Vendas
python scripts/gerar_vendas_completas_finais.py

# 4. Vendedores
python scripts/normalizar_vendedores_completo.py

# 5. Consolidar tudo
python scripts/gerar_arquivos_finais_banco_final.py
```

### Validar CSVs Antes de Importar:

```bash
python scripts/validar_arquivo_final_completo.py
python scripts/validar_antes_importar_supabase.py
```

---

## 🆘 TROUBLESHOOTING

### Erro: "duplicate key value violates unique constraint"
```sql
-- Verificar duplicatas antes
SELECT column_name, COUNT(*) 
FROM temp_table 
GROUP BY column_name 
HAVING COUNT(*) > 1;
```

### Erro: "foreign key constraint violation"
```sql
-- Verificar referências
SELECT DISTINCT foreign_key_column 
FROM temp_table 
WHERE foreign_key_column NOT IN (
    SELECT id FROM parent_table
);
```

### Erro: "invalid input syntax for type"
```python
# Limpar dados no Python antes
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
df = df.dropna(subset=['campo_obrigatorio'])
```

---

## 📞 PRÓXIMOS PASSOS

1. **Gerar CSVs finais** com estrutura correta
2. **Validar dados** antes da importação
3. **Criar schemas** no Supabase (executar SQLs)
4. **Importar tabelas** na ordem correta
5. **Validar importação** (contagens e integridade)

---

**Criado em:** 12 de novembro de 2025  
**Método:** Importação direta CSV → Supabase  
**Status:** 🟢 Pronto para uso
