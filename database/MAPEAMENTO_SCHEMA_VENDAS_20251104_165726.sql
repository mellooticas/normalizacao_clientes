
-- ========================================
-- MAPEAMENTO COMPLETO DO SCHEMA VENDAS
-- ========================================
-- Gerado em: 2025-11-04 16:57:26
-- Objetivo: Mapear todas as tabelas, estruturas e dados
-- 
-- INSTRUÇÕES:
-- 1. Execute cada query separadamente no Supabase
-- 2. Salve cada resultado como CSV no diretório indicado
-- 3. Organize os arquivos para análise posterior
-- ========================================

-- ========================================
-- 1. LISTAR TODAS AS TABELAS DO SCHEMA VENDAS
-- ========================================
-- Salve como: tabelas_schema_vendas.csv

SELECT 
    table_name,
    table_type,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'vendas'
ORDER BY table_name;

-- ========================================
-- 2. ESTRUTURA COMPLETA DE TODAS AS TABELAS
-- ========================================
-- Salve como: estrutura_completa_vendas.csv

SELECT 
    table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'vendas'
ORDER BY table_name, ordinal_position;

-- ========================================
-- 3. CONSTRAINTS E RELACIONAMENTOS
-- ========================================
-- Salve como: constraints_relacionamentos_vendas.csv

SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name 
    AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
LEFT JOIN information_schema.referential_constraints rc 
    ON tc.constraint_name = rc.constraint_name
WHERE tc.table_schema = 'vendas'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- ========================================
-- 4. ÍNDICES E PERFORMANCE
-- ========================================
-- Salve como: indices_vendas.csv

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'vendas'
ORDER BY tablename, indexname;

-- ========================================
-- 5. CONTAGEM DE REGISTROS EM TODAS AS TABELAS
-- ========================================
-- Execute e salve como: contagem_registros_vendas.csv
-- NOTA: Execute cada SELECT separadamente e compile o resultado

-- Tabelas principais conhecidas:
SELECT 'vendas' as tabela, COUNT(*) as registros, 
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.vendas;

SELECT 'formas_pagamento' as tabela, COUNT(*) as registros,
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.formas_pagamento;

SELECT 'vendas_formas_pagamento' as tabela, COUNT(*) as registros,
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.vendas_formas_pagamento;

-- ========================================
-- 6. VERIFICAR OUTRAS TABELAS (se existirem)
-- ========================================
-- Execute apenas as que existirem baseado no resultado da query 1

-- Possíveis tabelas que podem existir:
/*
SELECT 'clientes' as tabela, COUNT(*) as registros FROM vendas.clientes;
SELECT 'enderecos' as tabela, COUNT(*) as registros FROM vendas.enderecos;
SELECT 'telefones' as tabela, COUNT(*) as registros FROM vendas.telefones;
SELECT 'lojas' as tabela, COUNT(*) as registros FROM vendas.lojas;
SELECT 'vendedores' as tabela, COUNT(*) as registros FROM vendas.vendedores;
SELECT 'parcelas' as tabela, COUNT(*) as registros FROM vendas.parcelas;
SELECT 'pagamentos' as tabela, COUNT(*) as registros FROM vendas.pagamentos;
SELECT 'produtos' as tabela, COUNT(*) as registros FROM vendas.produtos;
SELECT 'vendas_itens' as tabela, COUNT(*) as registros FROM vendas.vendas_itens;
SELECT 'auditoria' as tabela, COUNT(*) as registros FROM vendas.auditoria;
*/

-- ========================================
-- 7. AMOSTRA DE DADOS DAS TABELAS PRINCIPAIS
-- ========================================
-- Salve como: amostra_vendas.csv

SELECT 
    id,
    numero_venda,
    cliente_id,
    loja_id,
    vendedor_id,
    data_venda,
    valor_total,
    status,
    created_at
FROM vendas.vendas 
ORDER BY created_at DESC 
LIMIT 100;

-- ========================================
-- 8. AMOSTRA FORMAS DE PAGAMENTO UTILIZADAS
-- ========================================
-- Salve como: amostra_vendas_formas_pagamento.csv

SELECT 
    vfp.id,
    vfp.venda_id,
    v.numero_venda,
    vfp.forma_pagamento_id,
    fp.nome as forma_pagamento_nome,
    vfp.valor,
    vfp.valor_entrada,
    vfp.parcelas,
    vfp.observacao,
    vfp.created_at
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.vendas v ON vfp.venda_id = v.id
LEFT JOIN vendas.formas_pagamento fp ON vfp.forma_pagamento_id = fp.id
ORDER BY vfp.created_at DESC 
LIMIT 100;

-- ========================================
-- 9. ESTATÍSTICAS GERAIS
-- ========================================
-- Salve como: estatisticas_vendas.csv

-- Vendas por status
SELECT 
    status,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as valor_medio
FROM vendas.vendas 
GROUP BY status
ORDER BY quantidade DESC;

-- Vendas por loja
SELECT 
    loja_id,
    COUNT(*) as quantidade_vendas,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as valor_medio
FROM vendas.vendas 
GROUP BY loja_id
ORDER BY quantidade_vendas DESC
LIMIT 20;

-- Formas de pagamento mais utilizadas
SELECT 
    fp.nome,
    COUNT(*) as quantidade_usos,
    SUM(vfp.valor) as valor_total,
    AVG(vfp.valor) as valor_medio,
    AVG(vfp.parcelas) as parcelas_media
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.formas_pagamento fp ON vfp.forma_pagamento_id = fp.id
GROUP BY fp.nome
ORDER BY quantidade_usos DESC;

-- ========================================
-- 10. VERIFICAÇÃO DE INTEGRIDADE
-- ========================================
-- Salve como: verificacao_integridade_vendas.csv

-- Vendas sem formas de pagamento
SELECT 'vendas_sem_formas_pagamento' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas v
LEFT JOIN vendas.vendas_formas_pagamento vfp ON v.id = vfp.venda_id
WHERE vfp.venda_id IS NULL;

-- Formas de pagamento órfãs
SELECT 'formas_pagamento_orfas' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.vendas v ON vfp.venda_id = v.id
WHERE v.id IS NULL;

-- Valores inconsistentes (soma das formas != valor total da venda)
WITH soma_formas AS (
    SELECT 
        venda_id,
        SUM(valor) as soma_valor_formas
    FROM vendas.vendas_formas_pagamento 
    GROUP BY venda_id
)
SELECT 'valores_inconsistentes' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas v
JOIN soma_formas sf ON v.id = sf.venda_id
WHERE ABS(v.valor_total - sf.soma_valor_formas) > 0.01;

-- ========================================
-- FIM DAS QUERIES
-- ========================================

/*
PRÓXIMOS PASSOS APÓS EXECUTAR AS QUERIES:

1. Salvar todos os CSVs na pasta: 
   d:/projetos/carne_facil/carne_facil/data/mapeamento_schema/

2. Organizar os arquivos:
   - tabelas_schema_vendas.csv
   - estrutura_completa_vendas.csv  
   - constraints_relacionamentos_vendas.csv
   - indices_vendas.csv
   - contagem_registros_vendas.csv
   - amostra_vendas.csv
   - amostra_vendas_formas_pagamento.csv
   - estatisticas_vendas.csv
   - verificacao_integridade_vendas.csv

3. Executar script de análise para processar todos os dados

4. Gerar plano de implementação das próximas tabelas
*/

