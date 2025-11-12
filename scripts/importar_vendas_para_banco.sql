-- =====================================================
-- SCRIPT DE IMPORTAÇÃO DE VENDAS
-- Importa dados do arquivo vendas_oss.csv
-- Total esperado: ~7.549 vendas
-- =====================================================

BEGIN;

-- Desabilitar triggers temporariamente para performance
ALTER TABLE vendas.vendas DISABLE TRIGGER trigger_vendas_updated_at;

-- Criar tabela temporária para staging
CREATE TEMP TABLE temp_vendas_import (
    numero_venda VARCHAR(50),
    cliente_id UUID,
    loja_id UUID,
    vendedor_id UUID,
    data_venda DATE,
    valor_total NUMERIC(12,2),
    valor_entrada NUMERIC(12,2),
    nome_cliente_temp VARCHAR(200),
    observacoes TEXT,
    cancelado BOOLEAN,
    data_cancelamento TIMESTAMP,
    motivo_cancelamento TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    version INTEGER,
    tipo_operacao VARCHAR(20)
);

-- =====================================================
-- PASSO 1: COPIAR DADOS DO CSV PARA TABELA TEMPORÁRIA
-- =====================================================
-- Execute este comando substituindo o caminho do arquivo:
-- 
-- COPY temp_vendas_import FROM 'D:/projetos/carne_facil/carne_facil/1_normalizacao/dados_processados/vendas_para_importar/vendas_oss.csv'
-- WITH (FORMAT CSV, HEADER true, DELIMITER ';', NULL '', ENCODING 'UTF8');
--
-- OU via psql:
-- \copy temp_vendas_import FROM 'D:/projetos/carne_facil/carne_facil/1_normalizacao/dados_processados/vendas_para_importar/vendas_oss.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ';', NULL '', ENCODING 'UTF8');

-- =====================================================
-- PASSO 2: VALIDAÇÕES PRÉ-IMPORTAÇÃO
-- =====================================================

-- Verificar quantos registros foram carregados
SELECT COUNT(*) as registros_staging FROM temp_vendas_import;

-- Verificar lojas referenciadas
SELECT DISTINCT 
    t.loja_id,
    l.nome as loja_nome
FROM temp_vendas_import t
LEFT JOIN core.lojas l ON t.loja_id = l.id
ORDER BY l.nome;

-- Verificar vendedores referenciados
SELECT DISTINCT 
    t.vendedor_id,
    v.nome as vendedor_nome
FROM temp_vendas_import t
LEFT JOIN core.vendedores v ON t.vendedor_id = v.id
WHERE t.vendedor_id IS NOT NULL
ORDER BY v.nome;

-- Verificar clientes sem match (NULL)
SELECT COUNT(*) as clientes_null 
FROM temp_vendas_import 
WHERE cliente_id IS NULL;

-- Verificar duplicatas na tabela temporária
SELECT 
    loja_id,
    numero_venda,
    COUNT(*) as qtd
FROM temp_vendas_import
GROUP BY loja_id, numero_venda
HAVING COUNT(*) > 1;

-- Verificar valores inválidos
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN valor_total < 0 THEN 1 END) as valor_total_negativo,
    COUNT(CASE WHEN valor_entrada < 0 THEN 1 END) as valor_entrada_negativo,
    COUNT(CASE WHEN valor_entrada > valor_total THEN 1 END) as entrada_maior_total
FROM temp_vendas_import;

-- =====================================================
-- PASSO 3: IMPORTAÇÃO PARA TABELA DEFINITIVA
-- =====================================================

INSERT INTO vendas.vendas (
    numero_venda,
    cliente_id,
    loja_id,
    vendedor_id,
    data_venda,
    valor_total,
    valor_entrada,
    nome_cliente_temp,
    observacoes,
    status,
    cancelado,
    data_cancelamento,
    motivo_cancelamento,
    created_at,
    updated_at,
    created_by,
    updated_by,
    deleted_at,
    version,
    tipo_operacao
)
SELECT 
    numero_venda,
    cliente_id,
    loja_id,
    vendedor_id,
    data_venda,
    COALESCE(valor_total, 0) as valor_total,
    COALESCE(valor_entrada, 0) as valor_entrada,
    nome_cliente_temp,
    observacoes,
    'ATIVO'::public.status_type as status,
    COALESCE(cancelado, false) as cancelado,
    data_cancelamento,
    motivo_cancelamento,
    COALESCE(created_at, CURRENT_TIMESTAMP) as created_at,
    COALESCE(updated_at, CURRENT_TIMESTAMP) as updated_at,
    created_by,
    updated_by,
    deleted_at,
    COALESCE(version, 1) as version,
    COALESCE(tipo_operacao, 'VENDA') as tipo_operacao
FROM temp_vendas_import;

-- =====================================================
-- PASSO 4: VERIFICAÇÕES PÓS-IMPORTAÇÃO
-- =====================================================

-- Verificar total importado
SELECT COUNT(*) as total_vendas_importadas FROM vendas.vendas;

-- Verificar por loja
SELECT 
    l.codigo,
    l.nome as loja_nome,
    COUNT(*) as qtd_vendas,
    SUM(v.valor_total) as total_vendas,
    SUM(v.valor_entrada) as total_entradas
FROM vendas.vendas v
JOIN core.lojas l ON v.loja_id = l.id
GROUP BY l.codigo, l.nome
ORDER BY l.codigo;

-- Verificar por tipo de operação
SELECT 
    tipo_operacao,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total,
    SUM(valor_entrada) as valor_entrada
FROM vendas.vendas
GROUP BY tipo_operacao
ORDER BY tipo_operacao;

-- Verificar garantias
SELECT 
    COUNT(*) as total_garantias,
    COUNT(CASE WHEN valor_total = 0 THEN 1 END) as garantias_valor_zero
FROM vendas.vendas
WHERE tipo_operacao = 'GARANTIA';

-- Verificar vendas sem cliente
SELECT 
    COUNT(*) as vendas_sem_cliente,
    SUM(valor_total) as valor_total
FROM vendas.vendas
WHERE cliente_id IS NULL;

-- Verificar período das vendas
SELECT 
    MIN(data_venda) as primeira_venda,
    MAX(data_venda) as ultima_venda,
    COUNT(DISTINCT data_venda) as dias_com_venda
FROM vendas.vendas;

-- =====================================================
-- PASSO 5: REABILITAR TRIGGERS E LIMPAR
-- =====================================================

-- Reabilitar trigger
ALTER TABLE vendas.vendas ENABLE TRIGGER trigger_vendas_updated_at;

-- Limpar tabela temporária
DROP TABLE IF EXISTS temp_vendas_import;

-- Atualizar estatísticas
ANALYZE vendas.vendas;

COMMIT;

-- =====================================================
-- RELATÓRIO FINAL
-- =====================================================
SELECT 
    'IMPORTAÇÃO CONCLUÍDA' as status,
    (SELECT COUNT(*) FROM vendas.vendas) as total_vendas,
    (SELECT COUNT(DISTINCT loja_id) FROM vendas.vendas) as total_lojas,
    (SELECT COUNT(DISTINCT cliente_id) FROM vendas.vendas WHERE cliente_id IS NOT NULL) as total_clientes,
    (SELECT SUM(valor_total) FROM vendas.vendas) as valor_total_geral,
    (SELECT MIN(data_venda) FROM vendas.vendas) as primeira_venda,
    (SELECT MAX(data_venda) FROM vendas.vendas) as ultima_venda;
