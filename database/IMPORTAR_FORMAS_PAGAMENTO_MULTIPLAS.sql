-- ============================================================================
-- SCRIPT COMPLETO: Importação de Formas de Pagamento Múltiplas
-- Para Supabase (usando staging em vez de temp)
-- ============================================================================

-- ============================================================================
-- PASSO 1: Criar tabela staging
-- ============================================================================

DROP TABLE IF EXISTS staging.vendas_formas_pagamento_temp;

CREATE TABLE staging.vendas_formas_pagamento_temp (
    venda_numero VARCHAR(50) NOT NULL,
    venda_loja_id UUID NOT NULL,
    forma_pagamento_id UUID NOT NULL,
    valor NUMERIC(12,2) NOT NULL,
    valor_liquido NUMERIC(12,2) NOT NULL,
    desconto NUMERIC(12,2) DEFAULT 0,
    valor_entrada NUMERIC(12,2) DEFAULT 0,
    parcelas INTEGER DEFAULT 1,
    observacao TEXT
);

-- ============================================================================
-- PASSO 2: Importar CSV para staging
-- ============================================================================
-- Use o Supabase Dashboard para importar:
-- vendas_formas_pagamento_MULTIPLAS.csv → staging.vendas_formas_pagamento_temp

-- ============================================================================
-- PASSO 3: Validar dados importados
-- ============================================================================

-- Verificar importação
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT venda_numero, venda_loja_id) as vendas_unicas,
    SUM(valor) as valor_total,
    SUM(valor_liquido) as valor_liquido_total,
    SUM(desconto) as desconto_total
FROM staging.vendas_formas_pagamento_temp;

-- Verificar formas de pagamento
SELECT 
    forma_pagamento_id,
    COUNT(*) as total_registros,
    SUM(valor) as valor_total,
    SUM(desconto) as desconto_total
FROM staging.vendas_formas_pagamento_temp
GROUP BY forma_pagamento_id
ORDER BY total_registros DESC;

-- ============================================================================
-- PASSO 4: Verificar consistência com vendas
-- ============================================================================

-- Vendas que existem no staging mas não no banco
SELECT DISTINCT 
    t.venda_numero, 
    t.venda_loja_id
FROM staging.vendas_formas_pagamento_temp t
LEFT JOIN vendas.vendas v ON (
    v.numero_venda = t.venda_numero 
    AND v.loja_id = t.venda_loja_id
)
WHERE v.id IS NULL
LIMIT 10;

-- Verificar se todas as formas de pagamento existem
SELECT DISTINCT 
    t.forma_pagamento_id
FROM staging.vendas_formas_pagamento_temp t
LEFT JOIN vendas.formas_pagamento fp ON fp.id = t.forma_pagamento_id
WHERE fp.id IS NULL;

-- ============================================================================
-- PASSO 5: Validar valores por venda
-- ============================================================================

-- Comparar valor total da venda vs soma das formas
WITH comparacao AS (
    SELECT 
        v.id as venda_id,
        v.numero_venda,
        v.valor_total as valor_venda,
        SUM(t.valor) as valor_formas,
        SUM(t.valor_liquido) as valor_liquido_formas,
        COUNT(t.*) as qtd_formas
    FROM vendas.vendas v
    JOIN staging.vendas_formas_pagamento_temp t ON (
        v.numero_venda = t.venda_numero 
        AND v.loja_id = t.venda_loja_id
    )
    GROUP BY v.id, v.numero_venda, v.valor_total
)
SELECT 
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN ABS(valor_venda - valor_formas) < 0.01 THEN 1 END) as vendas_ok,
    COUNT(CASE WHEN ABS(valor_venda - valor_formas) >= 0.01 THEN 1 END) as vendas_erro,
    AVG(qtd_formas) as media_formas_por_venda
FROM comparacao;

-- ============================================================================
-- PASSO 6: Inserir na tabela final
-- ============================================================================

INSERT INTO vendas.vendas_formas_pagamento (
    venda_id,
    forma_pagamento_id,
    valor,
    valor_entrada,
    parcelas,
    observacao
)
SELECT 
    v.id as venda_id,
    t.forma_pagamento_id,
    t.valor_liquido as valor,  -- Usa valor líquido (com desconto)
    t.valor_entrada,
    t.parcelas,
    t.observacao || 
    CASE 
        WHEN t.desconto > 0 THEN 
            ' | Desconto aplicado: R$ ' || t.desconto::TEXT
        ELSE ''
    END as observacao
FROM staging.vendas_formas_pagamento_temp t
JOIN vendas.vendas v ON (
    v.numero_venda = t.venda_numero 
    AND v.loja_id = t.venda_loja_id
)
WHERE EXISTS (
    SELECT 1 FROM vendas.formas_pagamento fp 
    WHERE fp.id = t.forma_pagamento_id
);

-- ============================================================================
-- PASSO 7: Validação final
-- ============================================================================

-- Verificar inserção
SELECT 
    COUNT(*) as total_formas_inseridas,
    COUNT(DISTINCT venda_id) as vendas_com_formas,
    SUM(valor) as valor_total_formas
FROM vendas.vendas_formas_pagamento;

-- Estatísticas por forma de pagamento
SELECT 
    fp.nome as forma_pagamento,
    COUNT(vfp.*) as total_registros,
    SUM(vfp.valor) as valor_total,
    AVG(vfp.parcelas) as media_parcelas
FROM vendas.vendas_formas_pagamento vfp
JOIN vendas.formas_pagamento fp ON fp.id = vfp.forma_pagamento_id
GROUP BY fp.nome
ORDER BY total_registros DESC;

-- Vendas com múltiplas formas
SELECT 
    COUNT(DISTINCT venda_id) as vendas_multiplas_formas
FROM (
    SELECT venda_id, COUNT(*) as qtd_formas
    FROM vendas.vendas_formas_pagamento
    GROUP BY venda_id
    HAVING COUNT(*) > 1
) multiplas;

-- ============================================================================
-- PASSO 8: Limpeza (opcional)
-- ============================================================================

-- Remover tabela staging após confirmação
-- DROP TABLE staging.vendas_formas_pagamento_temp;

-- ============================================================================
-- RELATÓRIO FINAL
-- ============================================================================

SELECT 
    'IMPORTACAO_FORMAS_PAGAMENTO_CONCLUIDA' as status,
    CURRENT_TIMESTAMP as executado_em,
    (SELECT COUNT(*) FROM vendas.vendas_formas_pagamento) as total_formas,
    (SELECT COUNT(DISTINCT venda_id) FROM vendas.vendas_formas_pagamento) as vendas_com_formas,
    (SELECT SUM(valor) FROM vendas.vendas_formas_pagamento) as valor_total;