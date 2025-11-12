-- ========================================
-- CORREÇÃO SIMPLES: MULTIPLICAR NEGATIVOS POR -1
-- Converter todos os números negativos para positivos
-- ========================================

-- 1. VERIFICAR SITUAÇÃO ATUAL
SELECT 
    'ANTES DA CORREÇÃO' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as numeros_negativos,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201
FROM vendas.vendas;


| status            | total_vendas | numeros_negativos | ainda_4801 | ainda_4201 |
| ----------------- | ------------ | ----------------- | ---------- | ---------- |
| ANTES DA CORREÇÃO | 15281        | 1235              | 0          | 1          |

-- 2. MULTIPLICAR NÚMEROS NEGATIVOS POR -1
UPDATE vendas.vendas 
SET numero_venda = (TRIM(numero_venda::text)::bigint * -1)::text
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$';

-- 3. VERIFICAR RESULTADO
SELECT 
    'APÓS CORREÇÃO' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as numeros_negativos,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    (SELECT MIN(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^[0-9]+$') as menor,
    (SELECT MAX(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^[0-9]+$') as maior
FROM vendas.vendas;

-- 4. TESTAR FOREIGN KEYS
SELECT COUNT(*) as fks_funcionando
FROM vendas.entregas_carne ec
INNER JOIN vendas.vendas v ON ec.venda_id = v.id;

-- 5. VER EXEMPLOS DOS NÚMEROS CONVERTIDOS
SELECT 
    'EXEMPLOS NÚMEROS CONVERTIDOS' as info,
    numero_venda,
    'Convertido de negativo para positivo' as origem
FROM vendas.vendas 
WHERE TRIM(numero_venda::text)::bigint > 1000 
  AND TRIM(numero_venda::text)::bigint < 10000
ORDER BY TRIM(numero_venda::text)::bigint
LIMIT 10;

-- 6. VERIFICAR SE AINDA HÁ DUPLICAÇÕES
WITH numeros_finais AS (
    SELECT 
        loja_id,
        TRIM(numero_venda::text)::bigint as numero_final
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^[0-9]+$'
),
duplicacoes AS (
    SELECT 
        loja_id,
        numero_final,
        COUNT(*) as quantidade
    FROM numeros_finais
    GROUP BY loja_id, numero_final
    HAVING COUNT(*) > 1
)
SELECT 
    'DUPLICAÇÕES RESTANTES' as info,
    COUNT(*) as total_duplicacoes
FROM duplicacoes;