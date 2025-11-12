-- ========================================
-- COMANDOS PARA IMPORTAÇÃO ENTREGAS CARNE
-- Data: 2025-11-05 16:32:54 - CORRIGIDO COM UUIDS REAIS
-- Arquivo: ENTREGAS_CARNE_PARCELAS_FINAL_20251105_163254.csv
-- ========================================

-- VERIFICAÇÃO ANTES DA IMPORTAÇÃO
SELECT COUNT(*) as total_entregas_atual FROM vendas.entregas_carne;

-- BACKUP OPCIONAL (caso já existam dados)
-- CREATE TABLE vendas.entregas_carne_backup AS SELECT * FROM vendas.entregas_carne;

-- ========================================
-- COMANDO DE IMPORTAÇÃO PRINCIPAL - CORRIGIDO
-- ========================================

\copy vendas.entregas_carne (id, venda_id, loja_id, os_numero, parcela, data_entrega, valor_total, observacoes, created_at, updated_at, deleted_at) FROM 'ENTREGAS_CARNE_PARCELAS_FINAL_20251105_163254.csv' WITH CSV HEADER;

-- ========================================
-- VERIFICAÇÕES PÓS-IMPORTAÇÃO
-- ========================================

-- 1. Verificar total de registros importados
SELECT COUNT(*) as total_entregas_importadas FROM vendas.entregas_carne;

-- 2. Verificar valores totais por loja
SELECT 
    l.nome_loja,
    COUNT(*) as total_parcelas,
    SUM(ec.valor_total) as valor_total,
    MIN(ec.data_entrega) as primeira_entrega,
    MAX(ec.data_entrega) as ultima_entrega
FROM vendas.entregas_carne ec
JOIN vendas.lojas l ON ec.loja_id = l.id
GROUP BY l.nome_loja
ORDER BY valor_total DESC;

-- 3. Verificar parcelas por OS
SELECT 
    os_numero,
    COUNT(*) as total_parcelas,
    SUM(valor_total) as valor_total_os,
    MIN(data_entrega) as primeira_parcela,
    MAX(data_entrega) as ultima_parcela
FROM vendas.entregas_carne
GROUP BY os_numero
HAVING COUNT(*) > 1
ORDER BY total_parcelas DESC
LIMIT 10;

-- 4. Verificar integridade de venda_id
SELECT 
    COUNT(*) as entregas_com_venda,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vendas.entregas_carne) as percentual_com_venda
FROM vendas.entregas_carne 
WHERE venda_id IS NOT NULL;

-- 5. Verificar distribuição temporal
SELECT 
    DATE_TRUNC('month', data_entrega) as mes_entrega,
    COUNT(*) as total_parcelas,
    SUM(valor_total) as valor_mensal
FROM vendas.entregas_carne
GROUP BY DATE_TRUNC('month', data_entrega)
ORDER BY mes_entrega;

-- ========================================
-- ESTATÍSTICAS ESPERADAS APÓS IMPORTAÇÃO
-- ========================================

/*
RESULTADOS ESPERADOS:
- Total de registros: 3,644 parcelas
- Valor total: R$ 429,163.46
- Período: 2023-05-12 a 2026-06-17
- Parcelas com venda_id: ~72.5% (494/704 OS originais)
- Lojas: 6 lojas (suzano, rio_pequeno, perus, maua, sao_mateus, suzano2)
- Expansão: 5.2x (704 registros originais → 3,644 parcelas)
*/