-- ===================================================================
-- CONSULTAS SQL PARA VERIFICAÇÃO DE FORMAS DE PAGAMENTO NO SUPABASE
-- ===================================================================

-- 1. VERIFICAR SE EXISTE TABELA DE FORMAS DE PAGAMENTO
-- ===================================================================
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_name ILIKE '%pagamento%' 
   OR table_name ILIKE '%forma%'
   OR table_name ILIKE '%payment%'
ORDER BY table_name;

| table_name                      | table_schema       |
| ------------------------------- | ------------------ |
| formas_pagamento                | vendas             |
| formas_pagamento_venda          | vendas             |
| formas_pagamento_venda          | staging            |
| information_schema_catalog_name | information_schema |
| pagamentos_carne                | staging            |
| v_performance_campanhas         | marketing          |
| v_performance_lojas_mensal      | public             |
| vendas_formas_pagamento         | staging            |
| vendas_formas_pagamento         | vendas             |

-- ===================================================================

-- 2. LISTAR TODAS AS TABELAS DO ESQUEMA PUBLIC
-- ===================================================================
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;


| table_name                 | table_type |
| -------------------------- | ---------- |
| v_analise_inadimplencia    | VIEW       |
| v_analise_produtos_os      | VIEW       |
| v_dashboard_executivo      | VIEW       |
| v_funil_vendas             | VIEW       |
| v_performance_lojas_mensal | VIEW       |
| v_ranking_vendedores       | VIEW       |
| v_top_clientes_vip         | VIEW       |

-- ===================================================================

-- 3. SE EXISTIR TABELA formas_pagamento, VERIFICAR ESTRUTURA
-- ===================================================================
-- (Execute esta consulta apenas se a tabela existir)
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'formas_pagamento' 
  AND table_schema = 'public'
ORDER BY ordinal_position;


Success. No rows returned




-- ===================================================================

-- 4. SE EXISTIR TABELA formas_pagamento, VERIFICAR DADOS EXISTENTES
-- ===================================================================
-- (Execute esta consulta apenas se a tabela existir)
SELECT 
    id,
    uuid,
    nome_original,
    nome_normalizado,
    descricao,
    ativo,
    created_at,
    updated_at
FROM formas_pagamento 
ORDER BY nome_normalizado;

ERROR:  42P01: relation "formas_pagamento" does not exist
LINE 17: FROM formas_pagamento 
              ^


-- ===================================================================

-- 5. VERIFICAR SE HÁ COLUNAS COM FORMAS DE PAGAMENTO EM OUTRAS TABELAS
-- ===================================================================
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE (column_name ILIKE '%forma%' 
    OR column_name ILIKE '%pagamento%'
    OR column_name ILIKE '%payment%')
  AND table_schema = 'public'
ORDER BY table_name, column_name;
Success. No rows returned



Success. No rows returned




-- ===================================================================

-- 6. VERIFICAR TABELA DE VENDAS (SE EXISTIR)
-- ===================================================================
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'vendas' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

Success. No rows returned





-- ===================================================================

-- 7. SE EXISTIR TABELA DE VENDAS, VERIFICAR FORMAS DE PAGAMENTO NELA
-- ===================================================================
-- (Execute esta consulta apenas se a tabela vendas existir)
SELECT 
    forma_pagamento,
    COUNT(*) as quantidade
FROM vendas 
WHERE forma_pagamento IS NOT NULL
GROUP BY forma_pagamento 
ORDER BY quantidade DESC;

-- ===================================================================
-- INSTRUÇÕES:
-- 1. Execute as consultas na ordem apresentada
-- 2. Me envie os resultados de cada consulta
-- 3. Se alguma tabela não existir, pule as consultas específicas dela
-- 4. Isso me ajudará a entender a estrutura atual e criar o plano de normalização
-- ===================================================================

ERROR:  42P01: relation "vendas" does not exist
LINE 11: FROM vendas 
              ^

-- ===================================================================
-- 8. VERIFICAR ESTRUTURA DAS TABELAS DE FORMAS DE PAGAMENTO (ESQUEMA VENDAS)
-- ===================================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'formas_pagamento' 
  AND table_schema = 'vendas'
ORDER BY ordinal_position;

| column_name    | data_type                   | is_nullable | column_default     |
| -------------- | --------------------------- | ----------- | ------------------ |
| id             | uuid                        | NO          | uuid_generate_v4() |
| codigo         | character varying           | NO          | null               |
| nome           | character varying           | NO          | null               |
| categoria      | character varying           | YES         | null               |
| ativo          | boolean                     | YES         | true               |
| ordem_exibicao | integer                     | YES         | null               |
| created_at     | timestamp without time zone | YES         | CURRENT_TIMESTAMP  |
| updated_at     | timestamp without time zone | YES         | CURRENT_TIMESTAMP  |

-- ===================================================================

-- 9. VERIFICAR DADOS NA TABELA vendas.formas_pagamento (CORRIGIDO)
-- ===================================================================
SELECT 
    id,
    codigo,
    nome,
    categoria,
    ativo,
    ordem_exibicao,
    created_at,
    updated_at
FROM vendas.formas_pagamento 
ORDER BY nome;


| id                                   | codigo   | nome                 | categoria     | ativo | ordem_exibicao | created_at                | updated_at                |
| ------------------------------------ | -------- | -------------------- | ------------- | ----- | -------------- | ------------------------- | ------------------------- |
| 26e2d011-d3b6-4ded-9259-4d4f37a000bc | CARNE    | Carnê                | CARNE         | true  | 6              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| 4854a683-31c3-4355-a03c-2bf398ebb4d5 | CTC      | Cartão de Crédito    | CARTAO        | true  | 4              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| e80028d4-ddf2-4e4b-9347-78044a6316f1 | CTD      | Cartão de Débito     | CARTAO        | true  | 3              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| 203527b1-d871-4f29-8c81-88fb0efaebd1 | DN       | Dinheiro             | DINHEIRO      | true  | 1              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| 9c8ce174-8212-41f7-a637-980f581c8ca9 | GARANTIA | Garantia (Sem Custo) | OUTROS        | true  | 8              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | PCTC     | Parcelado no Cartão  | CARTAO        | true  | 5              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX      | PIX                  | TRANSFERENCIA | true  | 2              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| b36056fa-47df-4f7a-b0e0-cda6a1bb5073 | SS       | Sem Sinal            | OUTROS        | true  | 7              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |
| 19d5c0b9-21c0-4f57-954e-3c6d0b3f108c | TROCA    | Troca                | OUTROS        | true  | 9              | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |


-- ===================================================================

-- 10. VERIFICAR ESTRUTURA DA TABELA vendas.vendas_formas_pagamento
-- ===================================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'vendas_formas_pagamento' 
  AND table_schema = 'vendas'
ORDER BY ordinal_position;


| column_name        | data_type                   | is_nullable | column_default     |
| ------------------ | --------------------------- | ----------- | ------------------ |
| id                 | uuid                        | NO          | uuid_generate_v4() |
| venda_id           | uuid                        | NO          | null               |
| forma_pagamento_id | uuid                        | NO          | null               |
| valor              | numeric                     | NO          | null               |
| valor_entrada      | numeric                     | YES         | 0                  |
| parcelas           | integer                     | YES         | null               |
| observacao         | text                        | YES         | null               |
| created_at         | timestamp without time zone | YES         | CURRENT_TIMESTAMP  |

-- ===================================================================

-- 11. VERIFICAR DADOS EM vendas.vendas_formas_pagamento (CORRIGIDO)
-- ===================================================================
SELECT 
    venda_id,
    forma_pagamento_id,
    valor,
    valor_entrada,
    parcelas,
    created_at
FROM vendas.vendas_formas_pagamento 
ORDER BY created_at DESC
LIMIT 20;

Success. No rows returned




-- ===================================================================

-- 12. CONTAR REGISTROS NAS TABELAS DE FORMAS DE PAGAMENTO
-- ===================================================================
SELECT 'formas_pagamento' as tabela, COUNT(*) as total FROM vendas.formas_pagamento
UNION ALL
SELECT 'vendas_formas_pagamento' as tabela, COUNT(*) as total FROM vendas.vendas_formas_pagamento;

| tabela                  | total |
| ----------------------- | ----- |
| formas_pagamento        | 9     |
| vendas_formas_pagamento | 0     |


-- ===================================================================

-- 13. VERIFICAR MAPEAMENTO ID -> NOME DAS FORMAS DE PAGAMENTO (CORRIGIDO)
-- ===================================================================
SELECT 
    id,
    codigo,
    nome,
    categoria,
    ativo
FROM vendas.formas_pagamento 
WHERE ativo = true
ORDER BY nome;

| id                                   | codigo   | nome                 | categoria     | ativo |
| ------------------------------------ | -------- | -------------------- | ------------- | ----- |
| 26e2d011-d3b6-4ded-9259-4d4f37a000bc | CARNE    | Carnê                | CARNE         | true  |
| 4854a683-31c3-4355-a03c-2bf398ebb4d5 | CTC      | Cartão de Crédito    | CARTAO        | true  |
| e80028d4-ddf2-4e4b-9347-78044a6316f1 | CTD      | Cartão de Débito     | CARTAO        | true  |
| 203527b1-d871-4f29-8c81-88fb0efaebd1 | DN       | Dinheiro             | DINHEIRO      | true  |
| 9c8ce174-8212-41f7-a637-980f581c8ca9 | GARANTIA | Garantia (Sem Custo) | OUTROS        | true  |
| 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | PCTC     | Parcelado no Cartão  | CARTAO        | true  |
| cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX      | PIX                  | TRANSFERENCIA | true  |
| b36056fa-47df-4f7a-b0e0-cda6a1bb5073 | SS       | Sem Sinal            | OUTROS        | true  |
| 19d5c0b9-21c0-4f57-954e-3c6d0b3f108c | TROCA    | Troca                | OUTROS        | true  |


-- ===================================================================
-- EXECUTE ESTAS CONSULTAS CORRIGIDAS (9, 11, 13) PARA OBTER OS IDs DAS FORMAS DE PAGAMENTO
-- A consulta 9 e 13 são as mais importantes para o mapeamento!
-- ===================================================================