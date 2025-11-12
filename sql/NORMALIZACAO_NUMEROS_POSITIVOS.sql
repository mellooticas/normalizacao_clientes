-- ========================================
-- CORREÇÃO: NÚMEROS NEGATIVOS PARA POSITIVOS COM OFFSET
-- Usar offset de 100,000 para evitar conflitos
-- ========================================

-- 1. ROLLBACK dos números negativos para prefixos originais
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.backup_numeros_original backup
WHERE vendas.vendas.id = backup.id;

-- 2. VERIFICAR ROLLBACK
SELECT 
    'PÓS-ROLLBACK' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as prefixo_4201,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as numeros_negativos
FROM vendas.vendas;

-- 3. NOVA ESTRATÉGIA: OFFSET DE 100,000
-- Prefixos 4801 -> 100,000 + número (ex: 480101104 -> 101104)
-- Prefixos 4201 -> 200,000 + número (ex: 420102194 -> 202194)

-- ATUALIZAR PREFIXO 4801 -> 100,000 + número
UPDATE vendas.vendas 
SET numero_venda = (100000 + TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint)::text
WHERE numero_venda::text LIKE '4801%'
  AND numero_venda::text != '4801.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';

-- ATUALIZAR PREFIXO 4201 -> 200,000 + número
UPDATE vendas.vendas 
SET numero_venda = (200000 + TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint)::text
WHERE numero_venda::text LIKE '4201%'
  AND numero_venda::text != '4201.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';

-- 4. VALIDAÇÃO FINAL
SELECT 
    'RESULTADO FINAL' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    COUNT(CASE WHEN TRIM(numero_venda::text)::bigint >= 100000 AND TRIM(numero_venda::text)::bigint < 200000 THEN 1 END) as range_100k,
    COUNT(CASE WHEN TRIM(numero_venda::text)::bigint >= 200000 AND TRIM(numero_venda::text)::bigint < 300000 THEN 1 END) as range_200k,
    (SELECT MIN(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^[0-9]+$') as menor,
    (SELECT MAX(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^[0-9]+$') as maior
FROM vendas.vendas;

-- 5. TESTAR FOREIGN KEYS
SELECT COUNT(*) as fks_funcionando
FROM vendas.entregas_carne ec
INNER JOIN vendas.vendas v ON ec.venda_id = v.id;

-- 6. EXEMPLOS DE CONVERSÃO
SELECT 
    'EXEMPLOS CONVERSÃO' as info,
    numero_venda,
    CASE 
        WHEN TRIM(numero_venda::text)::bigint >= 100000 AND TRIM(numero_venda::text)::bigint < 200000 
        THEN 'ERA 4801xxxx (Suzano/Mauá)'
        WHEN TRIM(numero_venda::text)::bigint >= 200000 AND TRIM(numero_venda::text)::bigint < 300000 
        THEN 'ERA 4201xxxx (outras lojas)'
        ELSE 'ORIGINAL'
    END as origem
FROM vendas.vendas 
WHERE TRIM(numero_venda::text)::bigint >= 100000
ORDER BY TRIM(numero_venda::text)::bigint
LIMIT 10;