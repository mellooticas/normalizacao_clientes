
# PLANO DE IMPLEMENTAÇÃO - SCHEMA VENDAS

**Data:** 2025-11-04 17:17:13  
**Objetivo:** Completar implementação do schema vendas com todas as tabelas essenciais

## 🎯 RESUMO EXECUTIVO

✅ **CONCLUÍDO:**
- `vendas` - 15.281 registros
- `formas_pagamento` - 9 registros  
- `vendas_formas_pagamento` - 19.737 registros

🚀 **PRÓXIMAS IMPLEMENTAÇÕES:**
- `itens_venda` - Produtos das vendas
- `entregas_os` - Controle de entregas
- `recebimentos_carne` - Controle financeiro

## 📋 TABELAS IDENTIFICADAS

### 📊 Tabelas Base (10)
1. ✅ `vendas` - IMPLEMENTADA
2. ✅ `formas_pagamento` - IMPLEMENTADA  
3. ✅ `vendas_formas_pagamento` - IMPLEMENTADA
4. 🔥 `itens_venda` - **PRÓXIMA**
5. 🔥 `entregas_os` - **PRÓXIMA**
6. 💰 `recebimentos_carne` - **MÉDIA PRIORIDADE**
7. 💰 `restantes_entrada` - **MÉDIA PRIORIDADE**
8. 🚚 `entregas_carne` - **BAIXA PRIORIDADE**
9. ⚡ `restituicoes` - **EXTRA**
10. ❓ `formas_pagamento_venda` - **DUPLICADA**

### 👁️ Views (10)
- `v_vendas_completas` - Vendas com todos os dados
- `v_vendas_reais` - Vendas válidas/ativas
- `v_entregas_pendentes` - Entregas não realizadas
- `v_resumo_recebimentos` - Resumo financeiro
- `v_saldo_a_receber` - Valores pendentes
- E mais 5 views operacionais...

## 🔥 PRIORIDADE 1 - ESSENCIAIS

### 1️⃣ itens_venda
**Objetivo:** Detalhar produtos de cada venda

```sql
CREATE TABLE vendas.itens_venda (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  tipo_produto varchar(100) NOT NULL, -- 'OCULOS', 'LENTE', 'ARMACAO'
  descricao varchar(300) NOT NULL,
  marca varchar(100),
  modelo varchar(100), 
  quantidade integer NOT NULL DEFAULT 1,
  valor_unitario numeric(12,2) NOT NULL,
  valor_total numeric(12,2),
  requer_encomenda boolean DEFAULT false,
  data_prevista_chegada date,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Dados Mock:** Gerar 1-3 itens por venda (principalmente óculos completos)

### 2️⃣ entregas_os  
**Objetivo:** Controlar entregas ao cliente

```sql
CREATE TABLE vendas.entregas_os (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  data_entrega date NOT NULL,
  tem_carne boolean DEFAULT false,
  created_at timestamp DEFAULT now()
);
```

**Dados Mock:** 80% das vendas já entregues, 20% pendentes

## 💰 PRIORIDADE 2 - FINANCEIRO

### 3️⃣ recebimentos_carne
**Objetivo:** Controlar pagamentos do carnê

```sql
CREATE TABLE vendas.recebimentos_carne (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  data_recebimento date NOT NULL,
  valor_recebido numeric(12,2) NOT NULL,
  parcela_numero integer,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Dados Mock:** Baseado nas vendas com forma carnê (1.844 registros)

## 🛠️ SCRIPTS A DESENVOLVER

### Imediatos (Esta Semana)
1. `01_criar_itens_venda.sql` - Estrutura da tabela
2. `02_gerar_itens_vendas_mock.py` - Dados mock realistas  
3. `03_criar_entregas_os.sql` - Estrutura da tabela
4. `04_gerar_entregas_mock.py` - Dados mock de entregas

### Médio Prazo (Próxima Semana)  
5. `05_criar_recebimentos_carne.sql` - Controle financeiro
6. `06_gerar_recebimentos_mock.py` - Dados mock de pagamentos
7. `07_views_operacionais.sql` - Recriar todas as views

## 📊 ANÁLISE DE DADOS ATUAIS

### Vendas (15.281 registros)
- **Valor Total:** R$ 7.889.566,44
- **Valor Médio:** R$ 516,30
- **Status:** 100% ATIVO

### Formas de Pagamento (19.737 registros)
- **Parcelado Cartão:** 6.254 (31.7%)
- **PIX:** 4.389 (22.2%) 
- **Cartão Crédito:** 3.765 (19.1%)
- **Dinheiro:** 3.485 (17.7%)
- **Carnê:** 1.844 (9.3%)

## ⚠️ PONTOS DE ATENÇÃO

1. **Consistência de Dados:** Manter alinhamento com estrutura atual
2. **Performance:** Criar índices apropriados nas novas tabelas
3. **Integridade:** Garantir FKs corretas em todas as relações
4. **Mock Realista:** Dados de teste baseados em padrões reais
5. **Views:** Recriar views que dependem das novas tabelas

## 🎯 CRITÉRIOS DE SUCESSO

✅ **itens_venda implementada** com dados mock realistas  
✅ **entregas_os implementada** com controle de status  
✅ **recebimentos_carne implementada** para controle financeiro  
✅ **Views principais** funcionando corretamente  
✅ **Performance** mantida com novos dados  

## 📅 CRONOGRAMA

- **Semana 1:** itens_venda + entregas_os
- **Semana 2:** recebimentos_carne + restantes_entrada  
- **Semana 3:** entregas_carne + views
- **Semana 4:** Testes e otimizações

---

**Status:** 🚀 Pronto para implementação  
**Próximo Passo:** Criar script `01_criar_itens_venda.sql`
