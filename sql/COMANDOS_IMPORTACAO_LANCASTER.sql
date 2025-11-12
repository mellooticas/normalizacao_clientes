-- ========================================
-- COMANDOS PARA IMPORTAÇÃO LANCASTER ENTREGAS
-- Data: 2025-11-05 16:58:16 - COM CRUZAMENTO DE VENDAS
-- Arquivo: LANCASTER_ENTREGAS_FINAL_20251105_165816.csv
-- ========================================

-- VERIFICAÇÃO ANTES DA IMPORTAÇÃO
SELECT COUNT(*) as total_entregas_atual FROM vendas.entregas_carne;

-- BACKUP OPCIONAL (caso já existam dados)
-- CREATE TABLE vendas.entregas_carne_backup AS SELECT * FROM vendas.entregas_carne;

-- ========================================
-- COMANDO DE IMPORTAÇÃO PRINCIPAL - LANCASTER
-- ========================================

\copy vendas.entregas_carne (id, venda_id, loja_id, os_numero, parcela, data_entrega, valor_total, observacoes, created_at, updated_at, deleted_at) FROM 'LANCASTER_ENTREGAS_FINAL_20251105_165816.csv' WITH CSV HEADER;

-- ========================================
-- VERIFICAÇÕES PÓS-IMPORTAÇÃO LANCASTER
-- ========================================

-- 1. Verificar total de registros importados
SELECT COUNT(*) as total_entregas_importadas FROM vendas.entregas_carne;

-- 2. Verificar registros Lancaster especificamente
SELECT COUNT(*) as registros_lancaster 
FROM vendas.entregas_carne 
WHERE observacoes LIKE 'Lancaster%';

-- 3. Verificar valores totais por loja (Lancaster)
SELECT 
    l.nome_loja,
    COUNT(*) as total_parcelas_lancaster,
    SUM(ec.valor_total) as valor_total_lancaster,
    MIN(ec.data_entrega) as primeira_entrega,
    MAX(ec.data_entrega) as ultima_entrega
FROM vendas.entregas_carne ec
JOIN vendas.lojas l ON ec.loja_id = l.id
WHERE ec.observacoes LIKE 'Lancaster%'
GROUP BY l.nome_loja
ORDER BY valor_total_lancaster DESC;

-- 4. Verificar distribuição de parcelas Lancaster
SELECT 
    parcela,
    COUNT(*) as total_parcelas,
    SUM(valor_total) as valor_total
FROM vendas.entregas_carne
WHERE observacoes LIKE 'Lancaster%'
GROUP BY parcela
ORDER BY parcela;

-- 5. Verificar período temporal Lancaster
SELECT 
    DATE_TRUNC('year', data_entrega) as ano,
    COUNT(*) as total_parcelas,
    SUM(valor_total) as valor_anual
FROM vendas.entregas_carne
WHERE observacoes LIKE 'Lancaster%'
GROUP BY DATE_TRUNC('year', data_entrega)
ORDER BY ano;

-- 6. Verificar OS únicas Lancaster
SELECT 
    COUNT(DISTINCT os_numero) as os_unicas_lancaster
FROM vendas.entregas_carne
WHERE observacoes LIKE 'Lancaster%';

-- ========================================
-- ESTATÍSTICAS ESPERADAS LANCASTER
-- ========================================

/*
RESULTADOS ESPERADOS LANCASTER - CORRIGIDO COM CRUZAMENTO:
- Total de registros: 6,352 parcelas
- Valor total: R$ 571,933.39
- Período: 2020-11-13 a 2024-07-15
- Lojas: Suzano (4,602 parcelas - R$ 418,906.16) e Mauá (1,750 parcelas - R$ 153,027.23)
- Parcelas com venda_id: 853 (13.4% - CRUZAMENTO REALIZADO!)
  * Suzano: 639 parcelas com venda_id
  * Mauá: 214 parcelas com venda_id
- Processamento: OS corretamente extraída removendo prefixo da loja (42/48)
- Zeros à esquerda: Removidos para compatibilidade com banco
- Cruzamento: Arquivo vendas_totais_com_uuid.csv encontrado e processado
*/

-- ========================================
-- VERIFICAÇÃO TOTAL (ENTREGAS + LANCASTER)
-- ========================================

-- Total geral após importar ambos os datasets
SELECT 
    'ENTREGAS CARNE' as tipo,
    COUNT(*) as registros,
    SUM(valor_total) as valor_total
FROM vendas.entregas_carne
WHERE observacoes NOT LIKE 'Lancaster%'

UNION ALL

SELECT 
    'LANCASTER' as tipo,
    COUNT(*) as registros,
    SUM(valor_total) as valor_total
FROM vendas.entregas_carne
WHERE observacoes LIKE 'Lancaster%'

UNION ALL

SELECT 
    'TOTAL GERAL' as tipo,
    COUNT(*) as registros,
    SUM(valor_total) as valor_total
FROM vendas.entregas_carne;