-- ============================================================================
-- INSERÇÃO DE TODOS OS VENDEDORES NORMALIZADOS
-- ============================================================================
-- Fonte: consolidadas.csv após normalização completa
-- Total: 13 vendedores únicos
-- Data: 08/11/2025
-- Tabela: core.vendedores
-- ============================================================================

BEGIN;

-- 1. TATIANA MELLO DE CAMARGO (1,938 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_TATIANA_MELLO_DE_CAMARGO',
    'TATIANA MELLO DE CAMARGO',
    'TATIANA MELLO DE CAMARGO',
    'Tatiana Mello de Camargo',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor mais ativo. Total de 1,938 OSS registradas (inclui 6 sem consultor atribuído).'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 2. ARIANI DIAS FERNANDES CARDOSO (1,425 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_ARIANI_DIAS_FERNANDES_CARDOSO',
    'ARIANI DIAS FERNANDES CARDOSO',
    'ARIANI DIAS FERNANDES CARDOSO',
    'Ariani Dias Fernandes Cardoso',
    true,
    CURRENT_TIMESTAMP,
    'Segundo vendedor mais ativo. Total de 1,425 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 3. JOCICREIDE BARBOSA (1,288 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_JOCICREIDE_BARBOSA',
    'JOCICREIDE BARBOSA',
    'JOCICREIDE BARBOSA',
    'Jocicreide Barbosa',
    true,
    CURRENT_TIMESTAMP,
    'Terceiro vendedor mais ativo. Total de 1,288 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 4. MARIA ELIZABETH (793 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_MARIA_ELIZABETH',
    'MARIA ELIZABETH',
    'MARIA ELIZABETH',
    'Maria Elizabeth',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 793 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 5. LUANA (528 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_LUANA',
    'LUANA',
    'LUANA',
    'Luana',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 528 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 6. ROGERIO APARECIDO DE MORAIS (499 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_ROGERIO_APARECIDO_DE_MORAIS',
    'ROGERIO APARECIDO DE MORAIS',
    'ROGERIO APARECIDO DE MORAIS',
    'Rogério Aparecido de Morais',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 499 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 7. FELIPE MIRANDA (343 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_FELIPE_MIRANDA',
    'FELIPE MIRANDA',
    'FELIPE MIRANDA',
    'Felipe Miranda',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 343 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 8. ROSÂNGELA (299 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_ROSANGELA',
    'ROSÂNGELA',
    'ROSANGELA',
    'Rosângela',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 299 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 9. WEVILLY (277 OSS - inclui 3 de BRUNA)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_WEVILLY',
    'WEVILLY',
    'WEVILLY',
    'Wevilly',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 277 OSS registradas (inclui 3 registradas como BRUNA).'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 10. LARISSA (121 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_LARISSA',
    'LARISSA',
    'LARISSA',
    'Larissa',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 121 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 11. ÉRIKA (27 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_ERIKA',
    'ÉRIKA',
    'ERIKA',
    'Érika',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 27 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 12. KAYLLAINE (7 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_KAYLLAINE',
    'KAYLLAINE',
    'KAYLLAINE',
    'Kayllaine',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 7 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 13. THIAGO (2 OSS)
INSERT INTO core.vendedores (id_legado, nome, nome_padronizado, nome_exibicao, ativo, created_at, observacoes)
VALUES (
    'VENDEDOR_THIAGO',
    'THIAGO',
    'THIAGO',
    'Thiago',
    true,
    CURRENT_TIMESTAMP,
    'Vendedor ativo. Total de 2 OSS registradas.'
)
ON CONFLICT (id_legado) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ============================================================================
-- VERIFICAÇÕES
-- ============================================================================

-- Listar todos os vendedores inseridos
SELECT 
    id_legado,
    nome,
    nome_exibicao,
    ativo,
    LEFT(observacoes, 50) as observacoes_resumo,
    created_at
FROM core.vendedores
WHERE id_legado LIKE 'VENDEDOR_%'
ORDER BY nome;

-- Estatísticas
SELECT 
    COUNT(*) as total_vendedores,
    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos_count,
    COUNT(CASE WHEN data_demissao IS NULL THEN 1 END) as sem_demissao
FROM core.vendedores
WHERE id_legado LIKE 'VENDEDOR_%';

-- ============================================================================
-- RESUMO DA IMPORTAÇÃO
-- ============================================================================
-- Total de vendedores: 13
-- Total de OSS: 7,547
-- Distribuição:
--   1. TATIANA MELLO DE CAMARGO: 1,938 OSS (25.7%)
--   2. ARIANI DIAS FERNANDES CARDOSO: 1,425 OSS (18.9%)
--   3. JOCICREIDE BARBOSA: 1,288 OSS (17.1%)
--   4. MARIA ELIZABETH: 793 OSS (10.5%)
--   5. LUANA: 528 OSS (7.0%)
--   6. ROGERIO APARECIDO DE MORAIS: 499 OSS (6.6%)
--   7. FELIPE MIRANDA: 343 OSS (4.5%)
--   8. ROSÂNGELA: 299 OSS (4.0%)
--   9. WEVILLY: 277 OSS (3.7%)
--  10. LARISSA: 121 OSS (1.6%)
--  11. ÉRIKA: 27 OSS (0.4%)
--  12. KAYLLAINE: 7 OSS (0.1%)
--  13. THIAGO: 2 OSS (0.03%)
-- ============================================================================
