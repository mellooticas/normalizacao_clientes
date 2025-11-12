-- ========================================
-- NORMALIZAÇÃO COM RESOLUÇÃO DE DUPLICAÇÕES
-- Converte números com prefixo para NEGATIVOS para evitar conflitos
-- ========================================

-- ROLLBACK PRIMEIRO (se já executou)
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.backup_numeros_original backup
WHERE vendas.vendas.id = backup.id;

-- VERIFICAR SE ROLLBACK FUNCIONOU
SELECT 
    'PÓS-ROLLBACK' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as prefixo_4201
FROM vendas.vendas;

| status       | total_vendas | prefixo_4801 | prefixo_4201 |
| ------------ | ------------ | ------------ | ------------ |
| PÓS-ROLLBACK | 15281        | 384          | 852          |

-- NOVA ESTRATÉGIA: NÚMEROS NEGATIVOS
-- ATUALIZAR PREFIXO 4801 -> NEGATIVOS
UPDATE vendas.vendas 
SET numero_venda = -(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint)
WHERE numero_venda::text LIKE '4801%'
  AND numero_venda::text != '4801.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';

-- ATUALIZAR PREFIXO 4201 -> NEGATIVOS  
UPDATE vendas.vendas 
SET numero_venda = -(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint)
WHERE numero_venda::text LIKE '4201%'
  AND numero_venda::text != '4201.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';

-- VALIDAÇÃO FINAL
SELECT 
    'RESULTADO FINAL' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    COUNT(CASE WHEN numero_venda::bigint < 0 THEN 1 END) as numeros_negativos,
    MIN(numero_venda::bigint) as menor,
    MAX(numero_venda::bigint) as maior
FROM vendas.vendas;

-- Testar foreign keys
SELECT COUNT(*) as fks_funcionando
FROM vendas.entregas_carne ec
INNER JOIN vendas.vendas v ON ec.venda_id = v.id;

| fks_funcionando |
| --------------- |
| 3892            |

-- Ver alguns exemplos dos números convertidos
SELECT 
    'EXEMPLOS CONVERSÃO' as info,
    numero_venda,
    CASE 
        WHEN numero_venda::bigint < 0 THEN 'CONVERTIDO (era prefixado)'
        ELSE 'ORIGINAL'
    END as tipo
FROM vendas.vendas 
WHERE numero_venda::bigint < 0 OR numero_venda::bigint IN (1104, 2194, 2219)
ORDER BY numero_venda::bigint
LIMIT 10;