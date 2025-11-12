-- ========================================
-- VERIFICAR SE OS UPDATES FUNCIONARAM
-- ========================================

-- 1. Contar quantos registros foram atualizados
SELECT 
    'STATUS ATUAL' as info,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    COUNT(CASE WHEN TRIM(numero_venda::text) ~ '^-[0-9]+$' THEN 1 END) as numeros_negativos,
    (SELECT MIN(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^-?[0-9]+$') as menor,
    (SELECT MAX(TRIM(numero_venda::text)::bigint) FROM vendas.vendas WHERE TRIM(numero_venda::text) ~ '^-?[0-9]+$') as maior
FROM vendas.vendas;


| info         | total_vendas | ainda_4801 | ainda_4201 | numeros_negativos | menor | maior |
| ------------ | ------------ | ---------- | ---------- | ----------------- | ----- | ----- |
| STATUS ATUAL | 15281        | 0          | 1          | 1235              | -8274 | 88302 |


-- 2. Ver se ainda há registros com prefixo (exceto os problemáticos)
SELECT 
    'PREFIXOS RESTANTES' as info,
    numero_venda::text,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
GROUP BY numero_venda::text
ORDER BY COUNT(*) DESC;

| info               | numero_venda | quantidade |
| ------------------ | ------------ | ---------- |
| PREFIXOS RESTANTES | 4201.0       | 1          |


-- 3. Verificar se há números negativos (evidência de conversão)
SELECT 
    'NÚMEROS NEGATIVOS' as info,
    numero_venda,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE TRIM(numero_venda::text) ~ '^-[0-9]+$'
GROUP BY numero_venda
ORDER BY TRIM(numero_venda::text)::bigint
LIMIT 10;

| info              | numero_venda | quantidade |
| ----------------- | ------------ | ---------- |
| NÚMEROS NEGATIVOS | -8274        | 1          |
| NÚMEROS NEGATIVOS | -8266        | 1          |
| NÚMEROS NEGATIVOS | -8265        | 1          |
| NÚMEROS NEGATIVOS | -8263        | 1          |
| NÚMEROS NEGATIVOS | -8261        | 1          |
| NÚMEROS NEGATIVOS | -8260        | 1          |
| NÚMEROS NEGATIVOS | -8256        | 1          |
| NÚMEROS NEGATIVOS | -8253        | 1          |
| NÚMEROS NEGATIVOS | -8248        | 1          |
| NÚMEROS NEGATIVOS | -8236        | 1          |


-- 4. Se os UPDATEs não funcionaram, vamos tentar manualmente um por vez
-- Teste com apenas 1 registro primeiro:
SELECT 
    'TESTE MANUAL' as info,
    id,
    numero_venda as original,
    numero_venda::text as texto,
    SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5) as sem_prefixo,
    TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) as trimmed,
    CASE 
        WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
             AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
             AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
        THEN -(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint)
        ELSE NULL
    END as numero_convertido
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' AND numero_venda::text != '4801.0'
LIMIT 5;

Success. No rows returned


