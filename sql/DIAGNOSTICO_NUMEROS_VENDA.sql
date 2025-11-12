-- ========================================
-- DIAGNÓSTICO DOS NÚMEROS DE VENDA
-- Primeiro vamos entender exatamente o que temos
-- ========================================

-- 1. VER EXEMPLOS REAIS DOS DADOS
SELECT 
    'EXEMPLOS REAIS' as tipo,
    numero_venda,
    numero_venda::text as texto,
    LENGTH(numero_venda::text) as tamanho
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
LIMIT 5;

-- 2. VER DIFERENTES FORMATOS
SELECT 
    'FORMATOS ENCONTRADOS' as analise,
    LEFT(numero_venda::text, 6) as primeiros_6_chars,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
GROUP BY LEFT(numero_venda::text, 6)
ORDER BY quantidade DESC;

-- 3. VERIFICAR SE HÁ DECIMAIS
SELECT 
    'DECIMAIS' as tipo,
    numero_venda::text,
    CASE 
        WHEN numero_venda::text LIKE '%.%' THEN 'TEM DECIMAL'
        ELSE 'SEM DECIMAL'
    END as tem_decimal,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
GROUP BY numero_venda::text, tem_decimal
LIMIT 10;

-- 4. TESTAR DIFERENTES ABORDAGENS DE LIMPEZA
SELECT 
    'TESTES LIMPEZA' as teste,
    numero_venda::text as original,
    REPLACE(numero_venda::text, '.0', '') as sem_ponto_zero,
    SPLIT_PART(numero_venda::text, '.', 1) as antes_ponto,
    CASE 
        WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1), 5)
        WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1), 5)
    END as numero_limpo
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
LIMIT 10;

-- 5. VERIFICAR QUAL TIPO DE COLUNA É numero_venda
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vendas' 
  AND table_name = 'vendas' 
  AND column_name = 'numero_venda';