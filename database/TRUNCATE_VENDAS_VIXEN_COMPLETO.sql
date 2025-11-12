-- ============================================================================
-- TRUNCATE SEGURO - Apenas vendas do dataset completo VIXEN
-- Remove apenas as vendas que estamos tentando importar agora
-- ============================================================================

-- IMPORTANTE: Este script remove apenas as vendas do dataset completo VIXEN
-- que estamos tentando importar, preservando outras vendas já existentes

-- ============================================================================
-- ANÁLISE ANTES DA LIMPEZA
-- ============================================================================

-- Verificar vendas existentes por fonte
SELECT 
    observacoes,
    COUNT(*) as total_vendas,
    SUM(valor_total) as valor_total,
    MIN(data_venda) as data_min,
    MAX(data_venda) as data_max
FROM vendas.vendas 
WHERE deleted_at IS NULL
GROUP BY observacoes
ORDER BY total_vendas DESC;

-- Verificar vendas por loja
SELECT 
    l.nome as loja_nome,
    COUNT(v.*) as total_vendas,
    SUM(v.valor_total) as valor_total
FROM vendas.vendas v
JOIN core.lojas l ON v.loja_id = l.id
WHERE v.deleted_at IS NULL
GROUP BY l.nome
ORDER BY total_vendas DESC;

-- ============================================================================
-- LIMPEZA ESPECÍFICA - Dataset VIXEN Completo
-- ============================================================================

-- Opção 1: Soft Delete (Recomendado - preserva dados para auditoria)
UPDATE vendas.vendas 
SET 
    deleted_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP,
    updated_by = 'SISTEMA_LIMPEZA_VIXEN_COMPLETO'
WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
  AND deleted_at IS NULL;

-- Verificar quantas foram marcadas como deletadas
SELECT COUNT(*) as vendas_soft_deleted
FROM vendas.vendas 
WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
  AND deleted_at IS NOT NULL;

-- ============================================================================
-- ALTERNATIVA: Hard Delete (SE NECESSÁRIO)
-- ============================================================================
-- CUIDADO: Esta opção remove permanentemente os dados!
-- Descomente apenas se necessário:

/*
DELETE FROM vendas.vendas 
WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas';

-- Verificar se foram removidas
SELECT COUNT(*) as vendas_removidas_permanentemente
FROM vendas.vendas 
WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas';
*/

-- ============================================================================
-- VERIFICAÇÃO PÓS-LIMPEZA
-- ============================================================================

-- Contar vendas restantes
SELECT 
    'Vendas ativas' as status,
    COUNT(*) as total_vendas,
    SUM(valor_total) as valor_total
FROM vendas.vendas 
WHERE deleted_at IS NULL
UNION ALL
SELECT 
    'Vendas deletadas' as status,
    COUNT(*) as total_vendas,
    SUM(valor_total) as valor_total
FROM vendas.vendas 
WHERE deleted_at IS NOT NULL;

-- Verificar se constraint está limpa para reimportação
-- Esta query deve retornar 0 linhas se a limpeza foi bem-sucedida
SELECT 
    loja_id,
    numero_venda,
    COUNT(*) as duplicatas
FROM vendas.vendas 
WHERE deleted_at IS NULL
  AND loja_id IN (
    '52f92716-d2ba-441a-ac3c-94bdfabd9722', -- SUZANO
    'aa7a5646-f7d6-4239-831c-6602fbabb10a'  -- MAUÁ
  )
  AND numero_venda IN (
    '457.0', '491.0', '510.0', '558.0', '564.0'  -- Primeiros números que causaram erro
  )
GROUP BY loja_id, numero_venda
HAVING COUNT(*) > 1;

-- ============================================================================
-- REATIVAR CASO NECESSÁRIO (Para reverter soft delete)
-- ============================================================================
/*
-- Para reativar vendas soft deleted (se necessário):
UPDATE vendas.vendas 
SET 
    deleted_at = NULL,
    updated_at = CURRENT_TIMESTAMP,
    updated_by = 'SISTEMA_REATIVACAO'
WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
  AND deleted_at IS NOT NULL;
*/

-- ============================================================================
-- RELATÓRIO FINAL
-- ============================================================================
SELECT 
    'LIMPEZA_CONCLUIDA' as status,
    'Vendas VIXEN completo removidas para reimportação' as mensagem,
    CURRENT_TIMESTAMP as executado_em;