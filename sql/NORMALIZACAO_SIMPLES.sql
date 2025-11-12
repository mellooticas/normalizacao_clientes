-- ========================================
-- SCRIPT SIMPLIFICADO - NORMALIZAÇÃO NÚMEROS VENDA
-- Versão mais direta e segura
-- ========================================

-- ETAPA 1: ANÁLISE (SEMPRE EXECUTAR PRIMEIRO)
SELECT 
    'Situação Atual' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as prefixo_4201
FROM vendas.vendas;

-- ETAPA 2: BACKUP AUTOMÁTICO
CREATE TABLE IF NOT EXISTS vendas.vendas_backup_prefixos AS 
SELECT * FROM vendas.vendas WHERE 1=0; -- Estrutura vazia

DELETE FROM vendas.vendas_backup_prefixos; -- Limpar se já existir

INSERT INTO vendas.vendas_backup_prefixos 
SELECT * FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

SELECT COUNT(*) as "Registros no Backup" FROM vendas.vendas_backup_prefixos;

-- ETAPA 3: VERIFICAÇÃO DE CONFLITOS
WITH preview_normalizacao AS (
    SELECT 
        id,
        numero_venda as numero_original,
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(numero_venda::text, 5)::bigint
            WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(numero_venda::text, 5)::bigint
            ELSE numero_venda::bigint
        END as numero_novo
    FROM vendas.vendas
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
)
SELECT 
    'PREVIEW - Primeiros 10 registros a serem alterados:' as info,
    numero_original,
    numero_novo
FROM preview_normalizacao
LIMIT 10;

-- Verificar se novos números já existem na base
WITH numeros_a_normalizar AS (
    SELECT 
        id,
        numero_venda as numero_atual,
        SUBSTRING(numero_venda::text, 5)::bigint as numero_normalizado
    FROM vendas.vendas
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
),
conflitos AS (
    SELECT 
        n.numero_normalizado,
        COUNT(*) as quantidade_conflitos
    FROM numeros_a_normalizar n
    INNER JOIN vendas.vendas v ON v.numero_venda = n.numero_normalizado
    WHERE v.numero_venda::text NOT LIKE '4801%' 
      AND v.numero_venda::text NOT LIKE '4201%'
    GROUP BY n.numero_normalizado
)
SELECT 
    'CONFLITOS DETECTADOS' as alerta,
    COALESCE(SUM(quantidade_conflitos), 0) as total_conflitos
FROM conflitos;

-- ETAPA 4: NORMALIZAÇÃO (SÓ EXECUTAR SE NÃO HOUVER CONFLITOS)
-- Descomente as linhas abaixo apenas se a verificação acima retornar 0 conflitos

/*
BEGIN;

UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(numero_venda::text, 5)::bigint
WHERE numero_venda::text LIKE '4801%';

UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(numero_venda::text, 5)::bigint
WHERE numero_venda::text LIKE '4201%';

COMMIT;
*/

-- ETAPA 5: VALIDAÇÃO FINAL
-- Executar após a normalização para confirmar

/*
SELECT 
    'Resultado Final' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_com_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_com_4201,
    MIN(numero_venda) as menor_numero,
    MAX(numero_venda) as maior_numero
FROM vendas.vendas;

-- Testar foreign keys
SELECT 'FK Test' as teste, COUNT(*) as entregas_validas
FROM vendas.entregas_carne ec
JOIN vendas.vendas v ON ec.venda_id = v.id;
*/

-- ========================================
-- ROLLBACK DE EMERGÊNCIA
-- ========================================

/*
-- USAR APENAS EM CASO DE PROBLEMA
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.vendas_backup_prefixos backup
WHERE vendas.vendas.id = backup.id;
*/