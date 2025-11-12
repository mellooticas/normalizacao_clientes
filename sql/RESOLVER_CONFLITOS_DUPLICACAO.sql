-- ========================================
-- RESOLVER CONFLITOS DE DUPLICAÇÃO
-- Estratégia: Usar offset para números negativos conflitantes
-- ========================================

-- 1. DIAGNOSTICAR TODOS OS CONFLITOS POTENCIAIS
WITH numeros_negativos AS (
    SELECT 
        loja_id,
        TRIM(numero_venda::text) as numero_original,
        (TRIM(numero_venda::text)::bigint * -1)::text as numero_convertido,
        id,
        created_at
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$'
),
numeros_existentes AS (
    SELECT 
        loja_id,
        TRIM(numero_venda::text) as numero_existente
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^[0-9]+$'
),
conflitos AS (
    SELECT 
        n.loja_id,
        n.numero_original,
        n.numero_convertido,
        n.id,
        n.created_at,
        'CONFLITO: já existe' as status
    FROM numeros_negativos n
    INNER JOIN numeros_existentes e ON n.loja_id = e.loja_id 
                                   AND n.numero_convertido = e.numero_existente
)
SELECT 
    'CONFLITOS DETECTADOS' as info,
    loja_id,
    numero_original,
    numero_convertido,
    status
FROM conflitos
ORDER BY loja_id, numero_original;

-- 2. ENCONTRAR O MAIOR NÚMERO POR LOJA PARA CALCULAR OFFSET SEGURO
WITH maiores_numeros AS (
    SELECT 
        loja_id,
        MAX(TRIM(numero_venda::text)::bigint) as maior_numero
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^[0-9]+$'
    GROUP BY loja_id
)
SELECT 
    'MAIOR NÚMERO POR LOJA' as info,
    l.nome as loja_nome,
    m.loja_id,
    m.maior_numero,
    (m.maior_numero + 100000) as offset_sugerido
FROM maiores_numeros m
LEFT JOIN lojas l ON m.loja_id = l.id
ORDER BY m.maior_numero DESC;

-- 3. ESTRATÉGIA HÍBRIDA: MULTIPLICAR POR -1 SE NÃO HÁ CONFLITO, USAR OFFSET SE HÁ CONFLITO

-- 3.1 Primeiro, converter números negativos SEM conflito
UPDATE vendas.vendas 
SET numero_venda = (TRIM(numero_venda::text)::bigint * -1)::text
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$'
  AND NOT EXISTS (
      SELECT 1 FROM vendas.vendas v2 
      WHERE v2.loja_id = vendas.vendas.loja_id 
        AND TRIM(v2.numero_venda::text) = (TRIM(vendas.vendas.numero_venda::text)::bigint * -1)::text
        AND v2.id != vendas.vendas.id
  );

-- 3.2 Verificar quantos números negativos restaram (estes são os conflitantes)
SELECT 
    'NÚMEROS NEGATIVOS RESTANTES (CONFLITANTES)' as info,
    COUNT(*) as quantidade,
    array_agg(TRIM(numero_venda::text)) as numeros_conflitantes
FROM vendas.vendas
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$';

-- 3.3 Para os conflitantes, aplicar offset de +100000 por loja
WITH maiores_por_loja AS (
    SELECT 
        loja_id,
        MAX(TRIM(numero_venda::text)::bigint) as maior_numero
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^[0-9]+$'
    GROUP BY loja_id
)
UPDATE vendas.vendas 
SET numero_venda = (
    (TRIM(vendas.vendas.numero_venda::text)::bigint * -1) + 
    COALESCE(m.maior_numero, 0) + 100000
)::text
FROM maiores_por_loja m
WHERE vendas.vendas.loja_id = m.loja_id
  AND TRIM(vendas.vendas.numero_venda::text) ~ '^-[0-9]+$';

-- 4. VERIFICAÇÃO FINAL
SELECT 
    'RESULTADO FINAL' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as ainda_negativos,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    MIN(TRIM(numero_venda::text)::bigint) as menor_numero,
    MAX(TRIM(numero_venda::text)::bigint) as maior_numero
FROM vendas.vendas
WHERE TRIM(numero_venda::text) ~ '^[0-9]+$';

-- 5. VERIFICAR SE AINDA HÁ DUPLICAÇÕES
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
    COUNT(*) as total_duplicacoes,
    CASE WHEN COUNT(*) = 0 THEN '✅ SUCESSO: Nenhuma duplicação!' 
         ELSE '❌ AINDA HÁ DUPLICAÇÕES' 
    END as status_final
FROM duplicacoes;

-- 6. EXEMPLOS DE NÚMEROS CONVERTIDOS
SELECT 
    'EXEMPLOS FINAIS' as info,
    l.nome as loja,
    numero_venda,
    created_at
FROM vendas.vendas v
LEFT JOIN lojas l ON v.loja_id = l.id
WHERE TRIM(numero_venda::text)::bigint > 1000
ORDER BY l.nome, TRIM(numero_venda::text)::bigint
LIMIT 20;