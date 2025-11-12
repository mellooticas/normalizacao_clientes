-- ========================================
-- NORMALIZAÇÃO NÚMEROS VENDA - VERSÃO ULTRA SIMPLES
-- Remove prefixos 4801 e 4201 de forma direta
-- CORRIGIDO: Trata valores com ".0" no final (ex: 420003060.0)
-- ========================================

-- PASSO 1: VER SITUAÇÃO ATUAL
SELECT 
    'Análise Atual' as etapa,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as com_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as com_4201
FROM vendas.vendas;

-- PASSO 2: CRIAR BACKUP
CREATE TABLE vendas.backup_numeros_venda AS 
SELECT id, numero_venda 
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

SELECT COUNT(*) as registros_backup FROM vendas.backup_numeros_venda;

-- PASSO 3: PREVIEW DAS MUDANÇAS (10 exemplos)
SELECT 
    'PREVIEW' as tipo,
    numero_venda as antes,
    CASE 
        WHEN LENGTH(SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)) > 0 
        THEN SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)::bigint
        ELSE NULL
    END as depois
FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
LIMIT 10;

-- PASSO 4: VERIFICAR CONFLITOS SIMPLES
-- Ver se algum número normalizado já existe
SELECT 
    'VERIFICAÇÃO' as status,
    COUNT(*) as possiveis_conflitos
FROM (
    SELECT SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5) as num_texto
    FROM vendas.vendas 
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
    AND LENGTH(SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)) > 0
) normalizados
INNER JOIN vendas.vendas existentes 
ON existentes.numero_venda = normalizados.num_texto::bigint
WHERE existentes.numero_venda::text NOT LIKE '4801%' 
  AND existentes.numero_venda::text NOT LIKE '4201%';

-- IDENTIFICAR REGISTROS PROBLEMÁTICOS (que ficariam vazios)
SELECT 
    'REGISTROS PROBLEMÁTICOS' as alerta,
    COUNT(*) as quantidade,
    'Registros que ficariam vazios após remover prefixo' as motivo
FROM vendas.vendas 
WHERE (numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%')
  AND LENGTH(SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)) = 0;

-- ========================================
-- PASSO 5: EXECUTAR NORMALIZAÇÃO
-- SÓ DESCOMENTE SE VERIFICAÇÃO RETORNOU 0 CONFLITOS
-- ========================================

/*
-- NORMALIZAR PREFIXO 4801 (apenas números válidos)
UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)::bigint
WHERE numero_venda::text LIKE '4801%'
  AND LENGTH(SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)) > 0;

-- NORMALIZAR PREFIXO 4201 (apenas números válidos)
UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)::bigint
WHERE numero_venda::text LIKE '4201%'
  AND LENGTH(SUBSTRING(REPLACE(numero_venda::text, '.0', ''), 5)) > 0;
*/

-- PASSO 6: VERIFICAÇÃO FINAL
-- Descomente após executar a normalização

/*
SELECT 
    'Resultado' as etapa,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_4201,
    MIN(numero_venda) as menor_numero,
    MAX(numero_venda) as maior_numero
FROM vendas.vendas;

-- Testar se foreign keys ainda funcionam
SELECT COUNT(*) as entregas_com_venda_valida
FROM vendas.entregas_carne ec
INNER JOIN vendas.vendas v ON ec.venda_id = v.id;
*/

-- ========================================
-- ROLLBACK DE EMERGÊNCIA (SE NECESSÁRIO)
-- ========================================

/*
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.backup_numeros_venda backup
WHERE vendas.vendas.id = backup.id;

-- Verificar rollback
SELECT COUNT(*) FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';
*/

-- ========================================
-- LIMPEZA (APÓS CONFIRMAR QUE ESTÁ TUDO OK)
-- ========================================

/*
DROP TABLE vendas.backup_numeros_venda;
*/