-- ============================================================================
-- ADICIONAR COLUNA cliente_desde NA TABELA core.clientes
-- ============================================================================
-- Data: 09/11/2025
-- Descrição: Adiciona coluna para armazenar a data da primeira compra/relacionamento
--            com o cliente (cliente desde quando)
-- ============================================================================

-- 1. Adicionar a coluna cliente_desde (tipo DATE, pode ser NULL)
ALTER TABLE core.clientes 
ADD COLUMN IF NOT EXISTS cliente_desde DATE;

-- 2. Adicionar comentário explicativo na coluna
COMMENT ON COLUMN core.clientes.cliente_desde IS 
'Data da primeira compra ou início do relacionamento com o cliente. Utilizado para análises de tempo de relacionamento, segmentação temporal e cálculo de métricas de retenção.';

-- 3. (Opcional) Criar índice para melhorar consultas por período
CREATE INDEX IF NOT EXISTS idx_clientes_cliente_desde 
ON core.clientes(cliente_desde);

-- 4. (Opcional) Criar índice composto para consultas de análise temporal
CREATE INDEX IF NOT EXISTS idx_clientes_status_cliente_desde 
ON core.clientes(status, cliente_desde) 
WHERE status = 'ATIVO';

-- ============================================================================
-- VERIFICAÇÕES APÓS EXECUÇÃO
-- ============================================================================

-- Verificar se a coluna foi criada
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'core'
    AND table_name = 'clientes'
    AND column_name = 'cliente_desde';


    | column_name   | data_type | is_nullable | column_default |
| ------------- | --------- | ----------- | -------------- |
| cliente_desde | date      | YES         | null           |



-- Verificar índices criados
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'core'
    AND tablename = 'clientes'
    AND indexname LIKE '%cliente_desde%';

| indexname                         | indexdef                                                                                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| idx_clientes_cliente_desde        | CREATE INDEX idx_clientes_cliente_desde ON core.clientes USING btree (cliente_desde)                                                      |
| idx_clientes_status_cliente_desde | CREATE INDEX idx_clientes_status_cliente_desde ON core.clientes USING btree (status, cliente_desde) WHERE (status = 'ATIVO'::status_type) |



-- ============================================================================
-- QUERIES ÚTEIS PARA ANÁLISE APÓS IMPORTAÇÃO
-- ============================================================================

-- 1. Contar clientes por ano de entrada
SELECT 
    EXTRACT(YEAR FROM cliente_desde) as ano_entrada,
    COUNT(*) as total_clientes,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentual
FROM core.clientes
WHERE cliente_desde IS NOT NULL
GROUP BY EXTRACT(YEAR FROM cliente_desde)
ORDER BY ano_entrada DESC;

-- 2. Clientes por antiguidade (tempo de relacionamento)
SELECT 
    CASE 
        WHEN cliente_desde IS NULL THEN 'Sem data'
        WHEN CURRENT_DATE - cliente_desde < 365 THEN 'Menos de 1 ano'
        WHEN CURRENT_DATE - cliente_desde < 730 THEN '1-2 anos'
        WHEN CURRENT_DATE - cliente_desde < 1095 THEN '2-3 anos'
        WHEN CURRENT_DATE - cliente_desde < 1825 THEN '3-5 anos'
        ELSE 'Mais de 5 anos'
    END as faixa_tempo,
    COUNT(*) as total_clientes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual
FROM core.clientes
GROUP BY 
    CASE 
        WHEN cliente_desde IS NULL THEN 'Sem data'
        WHEN CURRENT_DATE - cliente_desde < 365 THEN 'Menos de 1 ano'
        WHEN CURRENT_DATE - cliente_desde < 730 THEN '1-2 anos'
        WHEN CURRENT_DATE - cliente_desde < 1095 THEN '2-3 anos'
        WHEN CURRENT_DATE - cliente_desde < 1825 THEN '3-5 anos'
        ELSE 'Mais de 5 anos'
    END
ORDER BY 
    MIN(CASE 
        WHEN cliente_desde IS NULL THEN 0
        WHEN CURRENT_DATE - cliente_desde < 365 THEN 1
        WHEN CURRENT_DATE - cliente_desde < 730 THEN 2
        WHEN CURRENT_DATE - cliente_desde < 1095 THEN 3
        WHEN CURRENT_DATE - cliente_desde < 1825 THEN 4
        ELSE 5
    END);


Error: Failed to run sql query: ERROR: 42803: column "clientes.cliente_desde" must appear in the GROUP BY clause or be used in an aggregate function LINE 27: WHEN cliente_desde IS NULL THEN 0 ^



-- 3. Top 10 datas com mais clientes entrando (campanhas bem-sucedidas?)
SELECT 
    cliente_desde,
    COUNT(*) as novos_clientes,
    ARRAY_AGG(nome ORDER BY nome) as nomes_clientes
FROM core.clientes
WHERE cliente_desde IS NOT NULL
GROUP BY cliente_desde
HAVING COUNT(*) >= 3
ORDER BY COUNT(*) DESC, cliente_desde DESC
LIMIT 10;

-- 4. Clientes mais antigos (Top 20)
SELECT 
    id_legado,
    nome,
    cliente_desde,
    CURRENT_DATE - cliente_desde as dias_relacionamento,
    ROUND((CURRENT_DATE - cliente_desde)::numeric / 365.25, 1) as anos_relacionamento,
    status
FROM core.clientes
WHERE cliente_desde IS NOT NULL
ORDER BY cliente_desde ASC
LIMIT 20;

-- 5. Estatísticas gerais
SELECT 
    COUNT(*) as total_clientes,
    COUNT(cliente_desde) as com_data_cliente_desde,
    COUNT(*) - COUNT(cliente_desde) as sem_data,
    ROUND(COUNT(cliente_desde) * 100.0 / COUNT(*), 2) as percentual_preenchimento,
    MIN(cliente_desde) as cliente_mais_antigo,
    MAX(cliente_desde) as cliente_mais_recente,
    ROUND(AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - cliente_desde)) / 86400 / 365.25), 2) as media_anos_relacionamento
FROM core.clientes;


Error: Failed to run sql query: ERROR: 22012: division by zero




-- ============================================================================
-- ROLLBACK (caso necessário desfazer)
-- ============================================================================
-- ATENÇÃO: Execute apenas se precisar reverter a mudança!
-- 
-- DROP INDEX IF EXISTS core.idx_clientes_status_cliente_desde;
-- DROP INDEX IF EXISTS core.idx_clientes_cliente_desde;
-- ALTER TABLE core.clientes DROP COLUMN IF EXISTS cliente_desde;
-- ============================================================================
