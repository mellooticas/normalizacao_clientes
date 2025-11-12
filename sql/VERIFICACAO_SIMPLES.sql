-- ========================================
-- VERIFICAÇÃO SIMPLES - SEM CONVERSÕES DE TIPO
-- ========================================

-- 1. STATUS BÁSICO (sem conversão para bigint)
SELECT 
    'STATUS ATUAL' as info,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    COUNT(CASE WHEN LEFT(numero_venda::text, 1) = '-' THEN 1 END) as numeros_negativos
FROM vendas.vendas;

-- 2. VER PREFIXOS RESTANTES
SELECT 
    'PREFIXOS RESTANTES' as info,
    LEFT(numero_venda::text, 10) as exemplo,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
GROUP BY LEFT(numero_venda::text, 10)
ORDER BY COUNT(*) DESC
LIMIT 10;

-- 3. VER SE HÁ NÚMEROS NEGATIVOS
SELECT 
    'NÚMEROS NEGATIVOS' as info,
    numero_venda::text,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE LEFT(numero_venda::text, 1) = '-'
GROUP BY numero_venda::text
ORDER BY numero_venda::text
LIMIT 10;

-- 4. VERIFICAR O TIPO DO CAMPO numero_venda
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vendas' 
  AND table_name = 'vendas' 
  AND column_name = 'numero_venda';

-- 5. SE OS UPDATES NÃO FUNCIONARAM, EXECUTAR MANUALMENTE UM POR VEZ
-- Verificar um registro específico que deveria ter sido convertido:
SELECT 
    'TESTE ESPECÍFICO' as info,
    id,
    numero_venda as valor_atual,
    numero_venda::text as texto,
    'Deveria ser -1104' as deveria_ser
FROM vendas.vendas 
WHERE id = '03b69a5e-e627-48d0-b844-8ae222c779b5'  -- ID do 480101104.0 que deveria virar -1104
LIMIT 1;