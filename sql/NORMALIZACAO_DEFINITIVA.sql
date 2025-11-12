-- ========================================
-- NORMALIZAÇÃO DEFINITIVA - VERSÃO QUE FUNCIONA
-- Remove prefixos 4801 e 4201 de forma robusta
-- ========================================

-- PASSO 1: DIAGNÓSTICO INICIAL
-- Execute primeiro para entender os dados
SELECT 
    'SITUAÇÃO ATUAL' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as prefixo_4201
FROM vendas.vendas;


| status         | total_vendas | prefixo_4801 | prefixo_4201 |
| -------------- | ------------ | ------------ | ------------ |
| SITUAÇÃO ATUAL | 15281        | 384          | 852          |



-- PASSO 2: BACKUP OBRIGATÓRIO
CREATE TABLE IF NOT EXISTS vendas.backup_numeros_original AS 
SELECT id, numero_venda FROM vendas.vendas WHERE 1=0;

DELETE FROM vendas.backup_numeros_original;

INSERT INTO vendas.backup_numeros_original 
SELECT id, numero_venda FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

SELECT COUNT(*) as "Backup Criado" FROM vendas.backup_numeros_original;


| Backup Criado |
| ------------- |
| 1236          |


-- PASSO 3: TESTE SEGURO (sem alterar dados)
-- Ver exatamente como ficarão os números
WITH teste_normalizacao AS (
    SELECT 
        id,
        numero_venda as original,
        numero_venda::text as texto_original,
        -- Usar SPLIT_PART para lidar com decimais
        SPLIT_PART(numero_venda::text, '.', 1) as sem_decimal,
        -- Remover prefixo baseado no tamanho
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN 
                SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)
            WHEN numero_venda::text LIKE '4201%' THEN 
                SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)
        END as numero_sem_prefixo,
        -- Converter para número (se possível)
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                    THEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
                    ELSE NULL
                END
            WHEN numero_venda::text LIKE '4201%' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                    THEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
                    ELSE NULL
                END
        END as numero_final
    FROM vendas.vendas 
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
)
SELECT 
    'PREVIEW NORMALIZAÇÃO' as info,
    original,
    numero_final,
    CASE WHEN numero_final IS NULL THEN 'PROBLEMA' ELSE 'OK' END as status
FROM teste_normalizacao
LIMIT 15;


| info                 | original    | numero_final | status   |
| -------------------- | ----------- | ------------ | -------- |
| PREVIEW NORMALIZAÇÃO | 4201.0      | null         | PROBLEMA |
| PREVIEW NORMALIZAÇÃO | 420102194.0 | 2194         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102219.0 | 2219         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102242.0 | 2242         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102251.0 | 2251         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102292.0 | 2292         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102294.0 | 2294         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102300.0 | 2300         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102319.0 | 2319         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102328.0 | 2328         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102335.0 | 2335         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102336.0 | 2336         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102338.0 | 2338         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102347.0 | 2347         | OK       |
| PREVIEW NORMALIZAÇÃO | 420102353.0 | 2353         | OK       |


-- PASSO 4: CONTAR REGISTROS PROBLEMÁTICOS
WITH problemas AS (
    SELECT 
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                    THEN 'OK'
                    ELSE 'PROBLEMA'
                END
            WHEN numero_venda::text LIKE '4201%' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                    THEN 'OK'
                    ELSE 'PROBLEMA'
                END
        END as status,
        numero_venda
    FROM vendas.vendas 
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
)
SELECT 
    status,
    COUNT(*) as quantidade
FROM problemas
GROUP BY status;


| status   | quantidade |
| -------- | ---------- |
| PROBLEMA | 1          |
| OK       | 1235       |



-- PASSO 5: VERIFICAR CONFLITOS
WITH novos_numeros AS (
    SELECT DISTINCT
        CASE 
            WHEN numero_venda::text LIKE '4801%' AND numero_venda::text != '4801.0' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                         AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                    THEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
                    ELSE NULL
                END
            WHEN numero_venda::text LIKE '4201%' AND numero_venda::text != '4201.0' THEN 
                CASE 
                    WHEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
                         AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
                         AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                    THEN TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
                    ELSE NULL
                END
        END as numero_novo
    FROM vendas.vendas 
    WHERE (numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%')
    AND numero_venda::text NOT IN ('4801.0', '4201.0')
)
SELECT 
    'CONFLITOS' as tipo,
    COUNT(*) as quantidade_conflitos
FROM novos_numeros nn
WHERE nn.numero_novo IS NOT NULL
AND EXISTS (
    SELECT 1 FROM vendas.vendas v 
    WHERE v.numero_venda::bigint = nn.numero_novo
    AND v.numero_venda::text NOT LIKE '4801%' 
    AND v.numero_venda::text NOT LIKE '4201%'
);

-- ========================================
-- PASSO 6: EXECUÇÃO (SÓ DEPOIS DE VALIDAR ACIMA)
-- Descomente apenas se tudo estiver OK
-- ========================================

/*
-- ATUALIZAR PREFIXO 4801
UPDATE vendas.vendas 
SET numero_venda = TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
WHERE numero_venda::text LIKE '4801%'
  AND numero_venda::text != '4801.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';

-- ATUALIZAR PREFIXO 4201
UPDATE vendas.vendas 
SET numero_venda = TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
WHERE numero_venda::text LIKE '4201%'
  AND numero_venda::text != '4201.0'
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' 
  AND LENGTH(TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))) > 0
  AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != '';
*/

-- PASSO 7: VALIDAÇÃO FINAL
/*
SELECT 
    'RESULTADO FINAL' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    MIN(numero_venda) as menor,
    MAX(numero_venda) as maior
FROM vendas.vendas;

-- Testar foreign keys
SELECT COUNT(*) as fks_funcionando
FROM vendas.entregas_carne ec
INNER JOIN vendas.vendas v ON ec.venda_id = v.id;
*/

-- ROLLBACK DE EMERGÊNCIA
/*
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.backup_numeros_original backup
WHERE vendas.vendas.id = backup.id;
*/