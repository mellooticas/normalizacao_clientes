-- CORREÇÃO DE ENTREGAS OS - STAGING
-- Gerado em: 2025-11-04 18:06:20
-- 
-- EXECUÇÃO:
-- 1. Importar entregas_os_staging.csv na tabela staging.entregas_os_temp
-- 2. Executar os SQLs abaixo em sequência
-- 3. Verificar relatórios antes de cada passo

-- ===== PASSO 1 =====

-- 1. CRIAR TABELA DE STAGING
CREATE TABLE IF NOT EXISTS staging.entregas_os_temp (
    id UUID NOT NULL,
    venda_id UUID NULL,              -- NULL permitido em staging
    vendedor_id UUID NULL,
    data_entrega DATE NOT NULL,
    tem_carne BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Campos auxiliares para correção
    os_numero TEXT,
    loja_id UUID,
    loja_origem TEXT,
    carne_original TEXT,
    observacoes TEXT,
    PRIMARY KEY (id)
);


-- ===== PASSO 2 =====

-- 2. ANÁLISES APÓS IMPORTAÇÃO DOS DADOS

-- Contagem geral
SELECT 
    COUNT(*) as total_registros,
    COUNT(venda_id) as com_venda_id,
    COUNT(*) - COUNT(venda_id) as sem_venda_id,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as percentual_com_venda
FROM staging.entregas_os_temp;

-- Por loja
SELECT 
    loja_origem,
    COUNT(*) as total,
    COUNT(venda_id) as com_venda_id,
    COUNT(vendedor_id) as com_vendedor,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as pct_venda
FROM staging.entregas_os_temp
GROUP BY loja_origem
ORDER BY total DESC;

-- Análise campo tem_carne
SELECT 
    tem_carne,
    carne_original,
    COUNT(*) as quantidade
FROM staging.entregas_os_temp
GROUP BY tem_carne, carne_original
ORDER BY quantidade DESC;


-- ===== PASSO 3 =====

-- 3. CORREÇÃO DE VENDA_ID POR OS_NUMERO

-- Buscar vendas por numero_venda = os_numero
UPDATE staging.entregas_os_temp 
SET venda_id = v.id
FROM vendas.vendas v
WHERE staging.entregas_os_temp.venda_id IS NULL
  AND staging.entregas_os_temp.os_numero = v.numero_venda::text;

-- Verificar correções
SELECT 
    'Após correção OS' as status,
    COUNT(*) as total,
    COUNT(venda_id) as com_venda_id,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as percentual
FROM staging.entregas_os_temp;


-- ===== PASSO 4 =====

-- 4. MIGRAÇÃO PARA PRODUÇÃO

-- Inserir apenas registros com venda_id válido
INSERT INTO vendas.entregas_os (
    id,
    venda_id,
    vendedor_id,
    data_entrega,
    tem_carne,
    created_at,
    updated_at
)
SELECT 
    id,
    venda_id,
    vendedor_id,
    data_entrega,
    tem_carne,
    created_at,
    updated_at
FROM staging.entregas_os_temp
WHERE venda_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM vendas.entregas_os p 
      WHERE p.venda_id = staging.entregas_os_temp.venda_id 
        AND p.data_entrega = staging.entregas_os_temp.data_entrega
  );

-- Verificar inserções
SELECT COUNT(*) as registros_inseridos FROM vendas.entregas_os;


-- ===== PASSO 5 =====

-- 5. RELATÓRIO FINAL

-- Registros não migrados (para análise)
SELECT 
    'Registros não migrados' as tipo,
    COUNT(*) as quantidade,
    string_agg(DISTINCT loja_origem, ', ') as lojas
FROM staging.entregas_os_temp
WHERE venda_id IS NULL;

-- Resumo final por loja
SELECT 
    loja_origem,
    COUNT(*) as total_staging,
    COUNT(CASE WHEN venda_id IS NOT NULL THEN 1 END) as migrados,
    COUNT(CASE WHEN venda_id IS NULL THEN 1 END) as nao_migrados
FROM staging.entregas_os_temp
GROUP BY loja_origem
ORDER BY total_staging DESC;

-- Limpeza (comentado para segurança)
-- DROP TABLE staging.entregas_os_temp;


