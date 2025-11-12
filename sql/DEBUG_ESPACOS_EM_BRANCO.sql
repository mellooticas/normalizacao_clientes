-- ========================================
-- DEBUG: ENCONTRAR EXATAMENTE ONDE ESTÃO OS ESPAÇOS
-- ========================================

-- 1. Ver os registros problemáticos EXATOS
SELECT 
    'REGISTROS PROBLEMÁTICOS' as info,
    id,
    numero_venda,
    numero_venda::text as texto,
    LENGTH(numero_venda::text) as tamanho_total,
    SPLIT_PART(numero_venda::text, '.', 1) as sem_decimal,
    LENGTH(SPLIT_PART(numero_venda::text, '.', 1)) as tamanho_sem_decimal,
    SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5) as sem_prefixo,
    LENGTH(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) as tamanho_sem_prefixo,
    TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) as trimmed,
    LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) as tamanho_trimmed,
    ASCII(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) as primeiro_ascii
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
ORDER BY LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)))
LIMIT 10;


| info                    | id                                   | numero_venda | texto       | tamanho_total | sem_decimal | tamanho_sem_decimal | sem_prefixo | tamanho_sem_prefixo | trimmed | tamanho_trimmed | primeiro_ascii |
| ----------------------- | ------------------------------------ | ------------ | ----------- | ------------- | ----------- | ------------------- | ----------- | ------------------- | ------- | --------------- | -------------- |
| REGISTROS PROBLEMÁTICOS | e333f9dd-9f1f-432a-a919-0f3aa4198ffe | 4201.0       | 4201.0      | 6             | 4201        | 4                   |             | 0                   |         | 0               | 0              |
| REGISTROS PROBLEMÁTICOS | 9f048dc4-6311-4d17-b4e9-2e9a0903adbc | 420102251.0  | 420102251.0 | 11            | 420102251   | 9                   | 02251       | 5                   | 02251   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | 6490192a-2bd0-4388-ab2b-5008afe4b350 | 420102294.0  | 420102294.0 | 11            | 420102294   | 9                   | 02294       | 5                   | 02294   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | 19885c42-4a36-401f-86a0-dc0cead3e069 | 420102242.0  | 420102242.0 | 11            | 420102242   | 9                   | 02242       | 5                   | 02242   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | a875e1b1-ae4c-48d5-93e5-a9cf62e7dad0 | 420102292.0  | 420102292.0 | 11            | 420102292   | 9                   | 02292       | 5                   | 02292   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | 06bf3851-9ab8-47d8-b36d-77be232c0fbb | 420102300.0  | 420102300.0 | 11            | 420102300   | 9                   | 02300       | 5                   | 02300   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | f07ec3e9-3b81-48ab-b03e-fcb8e86131d0 | 420102219.0  | 420102219.0 | 11            | 420102219   | 9                   | 02219       | 5                   | 02219   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | ce4b0123-5ee0-4b18-be7b-277f01d5fd14 | 420102319.0  | 420102319.0 | 11            | 420102319   | 9                   | 02319       | 5                   | 02319   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | bdf45d81-1a8f-4f5c-bf2b-5723105a8527 | 420102328.0  | 420102328.0 | 11            | 420102328   | 9                   | 02328       | 5                   | 02328   | 5               | 48             |
| REGISTROS PROBLEMÁTICOS | e8d08b3d-4364-4dab-8932-15ea61c6d24b | 420102194.0  | 420102194.0 | 11            | 420102194   | 9                   | 02194       | 5                   | 02194   | 5               | 48             |


-- 2. Ver especificamente o registro que tem apenas "4201.0"
SELECT 
    'REGISTRO 4201.0' as info,
    id,
    numero_venda,
    numero_venda::text,
    SPLIT_PART(numero_venda::text, '.', 1),
    SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5),
    LENGTH(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)),
    TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)),
    LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)))
FROM vendas.vendas 
WHERE numero_venda::text = '4201.0';


| info            | id                                   | numero_venda | split_part | substring | length | btrim |
| --------------- | ------------------------------------ | ------------ | ---------- | --------- | ------ | ----- |
| REGISTRO 4201.0 | e333f9dd-9f1f-432a-a919-0f3aa4198ffe | 4201.0       | 4201       |           | 0      |       |



-- 3. Contar todos os tipos de problemas
SELECT 
    'ANÁLISE COMPLETA' as tipo,
    CASE 
        WHEN numero_venda::text IN ('4201.0', '4801.0') THEN 'APENAS_PREFIXO'
        WHEN LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) = 0 THEN 'STRING_VAZIA'
        WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) = '' THEN 'STRING_ESPACO'
        WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 'OK'
        ELSE 'OUTROS_CARACTERES'
    END as categoria,
    COUNT(*) as quantidade
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
GROUP BY 2
ORDER BY 3 DESC;



| tipo             | categoria      | quantidade |
| ---------------- | -------------- | ---------- |
| ANÁLISE COMPLETA | OK             | 1235       |
| ANÁLISE COMPLETA | APENAS_PREFIXO | 1          |


-- 4. Ver exemplos de cada categoria
SELECT DISTINCT
    'EXEMPLOS' as info,
    CASE 
        WHEN numero_venda::text IN ('4201.0', '4801.0') THEN 'APENAS_PREFIXO'
        WHEN LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) = 0 THEN 'STRING_VAZIA'
        WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) = '' THEN 'STRING_ESPACO'
        WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 'OK'
        ELSE 'OUTROS_CARACTERES'
    END as categoria,
    numero_venda::text as exemplo
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
ORDER BY 2, 3
LIMIT 20;

| info     | categoria      | exemplo     |
| -------- | -------------- | ----------- |
| EXEMPLOS | APENAS_PREFIXO | 4201.0      |
| EXEMPLOS | OK             | 420102194.0 |
| EXEMPLOS | OK             | 420102219.0 |
| EXEMPLOS | OK             | 420102242.0 |
| EXEMPLOS | OK             | 420102251.0 |
| EXEMPLOS | OK             | 420102292.0 |
| EXEMPLOS | OK             | 420102294.0 |
| EXEMPLOS | OK             | 420102300.0 |
| EXEMPLOS | OK             | 420102319.0 |
| EXEMPLOS | OK             | 420102328.0 |
| EXEMPLOS | OK             | 420102335.0 |
| EXEMPLOS | OK             | 420102336.0 |
| EXEMPLOS | OK             | 420102338.0 |
| EXEMPLOS | OK             | 420102347.0 |
| EXEMPLOS | OK             | 420102353.0 |
| EXEMPLOS | OK             | 420102356.0 |
| EXEMPLOS | OK             | 420102379.0 |
| EXEMPLOS | OK             | 420102384.0 |
| EXEMPLOS | OK             | 420102395.0 |
| EXEMPLOS | OK             | 420102404.0 |