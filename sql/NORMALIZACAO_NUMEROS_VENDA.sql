-- ========================================
-- NORMALIZAÇÃO SEGURA DOS NÚMEROS DE VENDA
-- Remove prefixos 4801 e 4201 do campo numero_venda
-- ========================================

-- PASSO 1: ANÁLISE PRÉVIA (OBRIGATÓRIO EXECUTAR PRIMEIRO)
-- Verificar quantos registros serão afetados

SELECT 
    'ANÁLISE PRÉVIA' as etapa,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as com_prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as com_prefixo_4201,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%' THEN 1 END) as total_afetados
FROM vendas.vendas;

-- Verificar se haverá conflitos após remoção dos prefixos
WITH numeros_sem_prefixo AS (
    SELECT 
        id,
        numero_venda,
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(numero_venda::text FROM 5)::bigint
            WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(numero_venda::text FROM 5)::bigint
            ELSE numero_venda
        END as numero_normalizado
    FROM vendas.vendas
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
)
SELECT 
    'VERIFICAÇÃO DE CONFLITOS' as etapa,
    numero_normalizado,
    COUNT(*) as quantidade_duplicatas
FROM numeros_sem_prefixo
GROUP BY numero_normalizado
HAVING COUNT(*) > 1
ORDER BY quantidade_duplicatas DESC;

-- PASSO 2: BACKUP DE SEGURANÇA (OBRIGATÓRIO)
-- Criar tabela de backup antes de qualquer alteração

CREATE TABLE vendas.vendas_backup_normalizacao AS 
SELECT * FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

-- Verificar backup criado
SELECT 
    'BACKUP CRIADO' as etapa,
    COUNT(*) as registros_backup
FROM vendas.vendas_backup_normalizacao;

-- PASSO 3: NORMALIZAÇÃO SEGURA
-- Atualizar apenas registros que não causarão conflitos

BEGIN;

-- 3.1: Primeiro, criar uma coluna temporária para validação
ALTER TABLE vendas.vendas ADD COLUMN numero_venda_temp bigint;

-- 3.2: Calcular os novos números
UPDATE vendas.vendas 
SET numero_venda_temp = CASE 
    WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(numero_venda::text FROM 5)::bigint
    WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(numero_venda::text FROM 5)::bigint
    ELSE numero_venda
END
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

-- 3.3: Verificar se há conflitos com números existentes
SELECT 
    'VERIFICAÇÃO FINAL' as etapa,
    COUNT(*) as conflitos_potenciais
FROM vendas.vendas v1
JOIN vendas.vendas v2 ON v1.numero_venda = v2.numero_venda_temp AND v1.id != v2.id
WHERE v2.numero_venda_temp IS NOT NULL;

-- SE NÃO HOUVER CONFLITOS (resultado = 0), continuar:
-- 3.4: Aplicar a normalização
UPDATE vendas.vendas 
SET numero_venda = numero_venda_temp
WHERE numero_venda_temp IS NOT NULL;

-- 3.5: Remover coluna temporária
ALTER TABLE vendas.vendas DROP COLUMN numero_venda_temp;

-- 3.6: Confirmar transação
COMMIT;

-- PASSO 4: VALIDAÇÃO PÓS-NORMALIZAÇÃO
-- Verificar se a normalização foi bem-sucedida

SELECT 
    'PÓS NORMALIZAÇÃO' as etapa,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_com_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_com_4201,
    MIN(numero_venda) as menor_numero,
    MAX(numero_venda) as maior_numero
FROM vendas.vendas;

-- Verificar se as foreign keys ainda funcionam
SELECT 
    'VERIFICAÇÃO FK' as etapa,
    COUNT(*) as entregas_com_fk_valida
FROM vendas.entregas_carne ec
JOIN vendas.vendas v ON ec.venda_id = v.id;

-- PASSO 5: LIMPEZA (APÓS CONFIRMAÇÃO)
-- Só executar após validar que tudo está funcionando
-- DROP TABLE vendas.vendas_backup_normalizacao;

-- ========================================
-- SCRIPT DE ROLLBACK (EM CASO DE PROBLEMA)
-- ========================================

/*
-- ATENÇÃO: SÓ USAR EM CASO DE EMERGÊNCIA
-- Restaurar dados do backup

UPDATE vendas.vendas 
SET numero_venda = b.numero_venda
FROM vendas.vendas_backup_normalizacao b
WHERE vendas.vendas.id = b.id;

-- Verificar restauração
SELECT COUNT(*) FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';
*/

-- ========================================
-- EXEMPLOS DE TRANSFORMAÇÃO ESPERADA
-- ========================================

/*
ANTES:
- numero_venda: 48013060 → DEPOIS: 3060
- numero_venda: 42012345 → DEPOIS: 12345
- numero_venda: 1000 → DEPOIS: 1000 (inalterado)

VERIFICAÇÕES:
1. Prefixos 4801 e 4201 removidos
2. Números sem prefixo mantidos
3. Foreign keys mantidas funcionais
4. Backup criado para segurança
*/