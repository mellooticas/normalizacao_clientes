-- ========================================
-- CORREÇÃO SEGURA PARA CONFLITOS DE DUPLICAÇÃO
-- Aplica offset apenas aos números que causariam conflito
-- ========================================

-- 1. VERIFICAR O CONFLITO ESPECÍFICO REPORTADO (numero 1104)
SELECT 
    'ANÁLISE DO CONFLITO 1104' as info,
    loja_id,
    numero_venda,
    id,
    created_at
FROM vendas.vendas 
WHERE loja_id = 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
  AND (TRIM(numero_venda::text) = '1104' OR TRIM(numero_venda::text) = '-1104')
ORDER BY numero_venda, created_at;


| info                     | loja_id                              | numero_venda | id                                   | created_at          |
| ------------------------ | ------------------------------------ | ------------ | ------------------------------------ | ------------------- |
| ANÁLISE DO CONFLITO 1104 | aa7a5646-f7d6-4239-831c-6602fbabb10a | -1104        | 03b69a5e-e627-48d0-b844-8ae222c779b5 | 2025-11-04 14:31:16 |
| ANÁLISE DO CONFLITO 1104 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 1104         | 25bc8877-0cdb-4609-90f1-f2ab8968db57 | 2025-11-04 02:07:46 |

-- 2. ESTRATÉGIA: APLICAR OFFSET DE 100000 APENAS AOS NÚMEROS NEGATIVOS CONFLITANTES
-- Isso garante que -1104 vire 101104 (sem conflito com 1104)

-- 2.1 Primeiro verificar quantos conflitos temos
WITH conflitos AS (
    SELECT 
        v1.loja_id,
        TRIM(v1.numero_venda::text) as numero_negativo,
        (TRIM(v1.numero_venda::text)::bigint * -1)::text as seria_convertido,
        v1.id as id_negativo,
        v2.id as id_positivo_existente
    FROM vendas.vendas v1
    INNER JOIN vendas.vendas v2 ON v1.loja_id = v2.loja_id 
                                AND TRIM(v2.numero_venda::text) = (TRIM(v1.numero_venda::text)::bigint * -1)::text
    WHERE TRIM(v1.numero_venda::text) ~ '^-[0-9]+$'
      AND TRIM(v2.numero_venda::text) ~ '^[0-9]+$'
      AND v1.id != v2.id
)
SELECT 
    'TOTAL DE CONFLITOS' as info,
    COUNT(*) as quantidade_conflitos,
    array_agg(numero_negativo) as numeros_conflitantes
FROM conflitos;

| info               | quantidade_conflitos | numeros_conflitantes |
| ------------------ | -------------------- | -------------------- |
| TOTAL DE CONFLITOS | 2                    | ["-1104","-1108"]    |

-- 2.2 Aplicar correção apenas aos números negativos SEM conflito (multiplicar por -1)
UPDATE vendas.vendas 
SET numero_venda = (TRIM(numero_venda::text)::bigint * -1)::text
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$'
  AND NOT EXISTS (
      SELECT 1 FROM vendas.vendas v2 
      WHERE v2.loja_id = vendas.vendas.loja_id 
        AND TRIM(v2.numero_venda::text) = (TRIM(vendas.vendas.numero_venda::text)::bigint * -1)::text
        AND v2.id != vendas.vendas.id
  );

-- 2.3 Para os números negativos COM conflito, aplicar offset de 100000
UPDATE vendas.vendas 
SET numero_venda = ((TRIM(numero_venda::text)::bigint * -1) + 100000)::text
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$'
  AND EXISTS (
      SELECT 1 FROM vendas.vendas v2 
      WHERE v2.loja_id = vendas.vendas.loja_id 
        AND TRIM(v2.numero_venda::text) = (TRIM(vendas.vendas.numero_venda::text)::bigint * -1)::text
        AND v2.id != vendas.vendas.id
  );

-- 3. VERIFICAÇÃO DOS RESULTADOS
SELECT 
    'APÓS CORREÇÃO HÍBRIDA' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as ainda_negativos,
    COUNT(CASE WHEN TRIM(numero_venda::text)::bigint > 100000 THEN 1 END) as com_offset,
    MIN(TRIM(numero_venda::text)::bigint) as menor_numero,
    MAX(TRIM(numero_venda::text)::bigint) as maior_numero
FROM vendas.vendas
WHERE TRIM(numero_venda::text) ~ '^[0-9]+$';

| status                | total_vendas | ainda_negativos | com_offset | menor_numero | maior_numero |
| --------------------- | ------------ | --------------- | ---------- | ------------ | ------------ |
| APÓS CORREÇÃO HÍBRIDA | 5200         | 0               | 2          | 0            | 101108       |

-- 4. VERIFICAR SE O CONFLITO 1104 FOI RESOLVIDO
SELECT 
    'VERIFICAÇÃO ESPECÍFICA 1104' as info,
    loja_id,
    numero_venda,
    'Resolvido' as status
FROM vendas.vendas 
WHERE loja_id = 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
  AND (TRIM(numero_venda::text) = '1104' OR TRIM(numero_venda::text) = '101104')
ORDER BY numero_venda;

| info                        | loja_id                              | numero_venda | status    |
| --------------------------- | ------------------------------------ | ------------ | --------- |
| VERIFICAÇÃO ESPECÍFICA 1104 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 101104       | Resolvido |
| VERIFICAÇÃO ESPECÍFICA 1104 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 1104         | Resolvido |

-- 5. TESTE FINAL DE DUPLICAÇÕES
WITH duplicacoes AS (
    SELECT 
        loja_id,
        TRIM(numero_venda::text)::bigint as numero_final,
        COUNT(*) as quantidade
    FROM vendas.vendas
    WHERE TRIM(numero_venda::text) ~ '^[0-9]+$'
    GROUP BY loja_id, TRIM(numero_venda::text)::bigint
    HAVING COUNT(*) > 1
)
SELECT 
    'RESULTADO FINAL' as info,
    COUNT(*) as duplicacoes_restantes,
    CASE WHEN COUNT(*) = 0 THEN '✅ SUCESSO TOTAL!' 
         ELSE '❌ Ainda há ' || COUNT(*) || ' duplicações' 
    END as status
FROM duplicacoes;


| info            | duplicacoes_restantes | status           |
| --------------- | --------------------- | ---------------- |
| RESULTADO FINAL | 0                     | ✅ SUCESSO TOTAL! |