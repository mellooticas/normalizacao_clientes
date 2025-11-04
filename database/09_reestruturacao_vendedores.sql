-- =============================================
-- REESTRUTURAÇÃO DA TABELA DE VENDEDORES
-- =============================================
-- Objetivo: 1 vendedor único + relacionamento N:N com lojas
-- Data: 2025-10-29

-- =============================================
-- 1. BACKUP DA TABELA ATUAL
-- =============================================

-- Criar backup da tabela atual
CREATE TABLE IF NOT EXISTS core.vendedores_backup AS 
SELECT * FROM core.vendedores;

-- Verificar backup
SELECT COUNT(*) as total_backup FROM core.vendedores_backup;

| total_backup |
| ------------ |
| 153          |


-- =============================================
-- 2. CRIAR NOVA TABELA VENDEDORES_LOJAS
-- =============================================

-- Tabela de relacionamento N:N entre vendedores e lojas
CREATE TABLE IF NOT EXISTS core.vendedores_lojas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendedor_id UUID NOT NULL,
    loja_id UUID NOT NULL,
    codigo_vendedor_sistema VARCHAR(50), -- Código usado no sistema da loja
    ativo BOOLEAN DEFAULT true,
    data_inicio DATE DEFAULT CURRENT_DATE,
    data_fim DATE,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_vendedores_lojas_vendedor 
        FOREIGN KEY (vendedor_id) REFERENCES core.vendedores(id) ON DELETE CASCADE,
    CONSTRAINT fk_vendedores_lojas_loja 
        FOREIGN KEY (loja_id) REFERENCES core.lojas(id) ON DELETE CASCADE,
    
    -- Índice único para evitar duplicação vendedor/loja
    CONSTRAINT uk_vendedor_loja UNIQUE (vendedor_id, loja_id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_vendedores_lojas_vendedor ON core.vendedores_lojas(vendedor_id);
CREATE INDEX IF NOT EXISTS idx_vendedores_lojas_loja ON core.vendedores_lojas(loja_id);
CREATE INDEX IF NOT EXISTS idx_vendedores_lojas_ativo ON core.vendedores_lojas(ativo);

-- Trigger para updated_at na tabela vendedores_lojas
CREATE TRIGGER trigger_vendedores_lojas_updated_at_simples
    BEFORE UPDATE ON core.vendedores_lojas
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at_simples();

Success. No rows returned





-- =============================================
-- 3. MODIFICAR TABELA VENDEDORES
-- =============================================

-- PRIMEIRO: Remover dependências (views que usam loja_id)
DROP VIEW IF EXISTS v_ranking_vendedores CASCADE;
DROP VIEW IF EXISTS public.v_ranking_vendedores CASCADE;

-- Remover outras views dependentes se existirem
DO $$
DECLARE
    view_record RECORD;
BEGIN
    -- Buscar todas as views que dependem da coluna loja_id
    FOR view_record IN 
        SELECT schemaname, viewname 
        FROM pg_views 
        WHERE definition LIKE '%vendedores%loja_id%'
    LOOP
        EXECUTE 'DROP VIEW IF EXISTS ' || view_record.schemaname || '.' || view_record.viewname || ' CASCADE';
        RAISE NOTICE 'Removida view dependente: %.%', view_record.schemaname, view_record.viewname;
    END LOOP;
END
$$;

-- Agora remover constraints e colunas
-- PRIMEIRO: Remover trigger problemático que usa updated_by (campo inexistente)
DROP TRIGGER IF EXISTS trigger_vendedores_updated_at ON core.vendedores;

-- Remover constraint de loja_id (não será mais necessária)
ALTER TABLE core.vendedores DROP CONSTRAINT IF EXISTS fk_vendedores_loja;

-- Remover coluna loja_id da tabela vendedores
ALTER TABLE core.vendedores DROP COLUMN IF EXISTS loja_id CASCADE;

-- Remover coluna codigo_vendedor (vai para vendedores_lojas)
ALTER TABLE core.vendedores DROP COLUMN IF EXISTS codigo_vendedor CASCADE;

-- Adicionar novas colunas se não existirem
ALTER TABLE core.vendedores 
ADD COLUMN IF NOT EXISTS nome_padronizado VARCHAR(255),
ADD COLUMN IF NOT EXISTS nome_exibicao VARCHAR(255),
ADD COLUMN IF NOT EXISTS observacoes TEXT;

-- Recriar trigger simples só para updated_at (sem updated_by)
CREATE OR REPLACE FUNCTION atualizar_updated_at_simples()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar o novo trigger
CREATE TRIGGER trigger_vendedores_updated_at_simples
    BEFORE UPDATE ON core.vendedores
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at_simples();

-- Atualizar campos
UPDATE core.vendedores 
SET 
    nome_padronizado = nome,
    nome_exibicao = nome
WHERE nome_padronizado IS NULL;

Success. No rows returned





-- =============================================
-- 4. MIGRAR DADOS DA ESTRUTURA ANTIGA
-- =============================================

-- ATENÇÃO: Esta seção usa dados temporários para teste
-- Para população final, usar o script 10_populacao_vendedores.sql

-- Primeiro, vamos limpar a tabela vendedores atual
TRUNCATE TABLE core.vendedores CASCADE;

-- Inserir vendedores únicos baseados nos dados do backup (TEMPORÁRIO)
INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at, observacoes)
SELECT 
    gen_random_uuid() as id,
    nome_padronizado,
    nome_padronizado,
    nome_padronizado,
    true as ativo,
    NOW() as created_at,
    NOW() as updated_at,
    '' as observacoes
FROM (
    -- Mapeamento temporário para teste - SUBSTITUIR pelos dados reais
    SELECT DISTINCT 
        CASE 
            WHEN UPPER(nome) LIKE '%BETH%' OR UPPER(nome) LIKE '%ELIZABETE%' THEN 'MARIA ELIZABETH'
            WHEN UPPER(nome) LIKE '%FELIPE%' THEN 'FELIPE MIRANDA' 
            WHEN UPPER(nome) LIKE '%LARISSA%' THEN 'LARISSA'
            WHEN UPPER(nome) LIKE '%TATY%' OR UPPER(nome) LIKE '%TATIANA%' OR UPPER(nome) LIKE '%TATIANE%' THEN 'TATIANA MELLO DE CAMARGO'
            WHEN UPPER(nome) LIKE '%WEVILLY%' OR UPPER(nome) LIKE '%WEVELY%' THEN 'WEVILLY'
            WHEN UPPER(nome) LIKE '%ERIKA%' OR UPPER(nome) LIKE '%ÉRIKA%' THEN 'ÉRIKA'
            WHEN UPPER(nome) LIKE '%ROGÉRIO%' OR UPPER(nome) LIKE '%ROGERIO%' THEN 'ROGERIO APARECIDO DE MORAIS'
            WHEN UPPER(nome) LIKE '%WILLIAM%' OR UPPER(nome) LIKE '%WILLIAN%' OR UPPER(nome) LIKE '%WILLAM%' THEN 'WILLIAM'
            WHEN UPPER(nome) LIKE '%ROSÂNGELA%' OR UPPER(nome) LIKE '%ROSANGELA%' OR UPPER(nome) LIKE '%ROSAGELA%' THEN 'ROSÂNGELA'
            WHEN UPPER(nome) LIKE '%ARIANI%' OR UPPER(nome) LIKE '%ARIANE%' THEN 'ARIANI DIAS FERNANDES CARDOSO'
            WHEN nome = 'GARANTIA' THEN 'GARANTIA'
            WHEN nome = 'PIX' THEN 'PIX'
            WHEN nome = 'NAN' THEN 'NAN'
            ELSE UPPER(TRIM(nome))
        END as nome_padronizado
    FROM core.vendedores_backup 
    WHERE nome IS NOT NULL AND nome != '' AND nome != '//////////////////////////'
) vendedores_distintos
WHERE nome_padronizado IS NOT NULL;


Success. No rows returned




-- =============================================
-- 5. VERIFICAÇÕES
-- =============================================

-- Verificar estrutura das tabelas
\d core.vendedores
\d core.vendedores_lojas

-- Contar registros
SELECT 'vendedores_backup' as tabela, COUNT(*) as total FROM core.vendedores_backup
UNION ALL
SELECT 'vendedores_novo' as tabela, COUNT(*) as total FROM core.vendedores
UNION ALL
SELECT 'vendedores_lojas' as tabela, COUNT(*) as total FROM core.vendedores_lojas;

-- =============================================
-- 6. COMENTÁRIOS DAS TABELAS
-- =============================================

COMMENT ON TABLE core.vendedores IS 'Tabela de vendedores únicos - cada vendedor tem apenas 1 registro';
COMMENT ON COLUMN core.vendedores.nome_padronizado IS 'Nome padronizado único do vendedor';
COMMENT ON COLUMN core.vendedores.nome_exibicao IS 'Nome para exibição na interface';

COMMENT ON TABLE core.vendedores_lojas IS 'Relacionamento N:N entre vendedores e lojas';
COMMENT ON COLUMN core.vendedores_lojas.codigo_vendedor_sistema IS 'Código do vendedor no sistema da loja específica';
COMMENT ON COLUMN core.vendedores_lojas.data_inicio IS 'Data de início do vendedor na loja';
COMMENT ON COLUMN core.vendedores_lojas.data_fim IS 'Data de saída do vendedor da loja (NULL = ativo)';


| tabela            | total |
| ----------------- | ----- |
| vendedores_backup | 153   |
| vendedores_novo   | 68    |
| vendedores_lojas  | 0     |

-- =============================================
-- 7. FUNCTIONS AUXILIARES
-- =============================================

-- Function para buscar vendedor por nome (com fallback)
CREATE OR REPLACE FUNCTION core.buscar_vendedor_por_nome(nome_busca TEXT)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    vendedor_id UUID;
BEGIN
    -- Busca exata pelo nome padronizado
    SELECT id INTO vendedor_id 
    FROM core.vendedores 
    WHERE UPPER(nome_padronizado) = UPPER(TRIM(nome_busca))
    LIMIT 1;
    
    -- Se não encontrar, busca por similaridade
    IF vendedor_id IS NULL THEN
        SELECT id INTO vendedor_id 
        FROM core.vendedores 
        WHERE UPPER(nome_padronizado) LIKE '%' || UPPER(TRIM(nome_busca)) || '%'
        LIMIT 1;
    END IF;
    
    RETURN vendedor_id;
END;
$$;

-- Function para adicionar vendedor a uma loja
CREATE OR REPLACE FUNCTION core.adicionar_vendedor_loja(
    p_vendedor_id UUID,
    p_loja_id UUID,
    p_codigo_sistema VARCHAR(50) DEFAULT NULL,
    p_observacoes TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    relacao_id UUID;
BEGIN
    -- Verificar se já existe a relação
    SELECT id INTO relacao_id 
    FROM core.vendedores_lojas 
    WHERE vendedor_id = p_vendedor_id AND loja_id = p_loja_id;
    
    -- Se não existe, criar
    IF relacao_id IS NULL THEN
        INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, observacoes)
        VALUES (p_vendedor_id, p_loja_id, p_codigo_sistema, p_observacoes)
        RETURNING id INTO relacao_id;
    END IF;
    
    RETURN relacao_id;
END;
$$;

-- =============================================
-- 8. VIEWS PARA COMPATIBILIDADE E FUNCIONALIDADE
-- =============================================

-- View principal para compatibilidade com código existente
CREATE OR REPLACE VIEW core.vendedores_com_lojas AS
SELECT 
    v.id as vendedor_id,
    v.nome,
    v.nome_padronizado,
    v.nome_exibicao,
    v.ativo as vendedor_ativo,
    vl.id as vendedor_loja_id,
    vl.loja_id,
    l.nome as loja_nome,
    l.codigo as loja_codigo,
    vl.codigo_vendedor_sistema,
    vl.ativo as relacao_ativa,
    vl.data_inicio,
    vl.data_fim,
    vl.observacoes as relacao_observacoes,
    v.created_at as vendedor_criado_em,
    vl.created_at as relacao_criada_em
FROM core.vendedores v
LEFT JOIN core.vendedores_lojas vl ON v.id = vl.vendedor_id
LEFT JOIN core.lojas l ON vl.loja_id = l.id;

-- Recriar view de ranking de vendedores (adaptada para nova estrutura)
CREATE OR REPLACE VIEW v_ranking_vendedores AS
SELECT 
    v.id as vendedor_id,
    v.nome_padronizado as vendedor_nome,
    v.nome_exibicao as vendedor_exibicao,
    vl.loja_id,
    l.nome as loja_nome,
    l.codigo as loja_codigo,
    vl.codigo_vendedor_sistema,
    -- Campos para ranking (serão populados por outras queries)
    0 as total_vendas,
    0.00 as valor_total,
    0 as total_os,
    v.ativo as vendedor_ativo,
    vl.ativo as ativo_na_loja
FROM core.vendedores v
INNER JOIN core.vendedores_lojas vl ON v.id = vl.vendedor_id
INNER JOIN core.lojas l ON vl.loja_id = l.id
WHERE v.ativo = true AND vl.ativo = true;

COMMENT ON VIEW core.vendedores_com_lojas IS 'View que combina vendedores com suas lojas para compatibilidade';
COMMENT ON VIEW v_ranking_vendedores IS 'View de ranking de vendedores adaptada para nova estrutura N:N';

-- =============================================
-- 9. FIM DO SCRIPT - PRÓXIMOS PASSOS
-- =============================================

-- Verificar se tudo foi executado corretamente
DO $$
BEGIN
    -- Verificar se as tabelas foram criadas
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'core' AND table_name = 'vendedores_lojas') THEN
        RAISE EXCEPTION 'ERRO: Tabela core.vendedores_lojas não foi criada!';
    END IF;
    
    -- Verificar se as colunas foram adicionadas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'core' AND table_name = 'vendedores' AND column_name = 'nome_padronizado') THEN
        RAISE EXCEPTION 'ERRO: Coluna nome_padronizado não foi adicionada!';
    END IF;
    
    -- Verificar se trigger antigo foi removido e novo foi criado
    IF EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'trigger_vendedores_updated_at' AND event_object_schema = 'core' AND event_object_table = 'vendedores') THEN
        RAISE WARNING 'AVISO: Trigger antigo ainda existe, removendo...';
        DROP TRIGGER IF EXISTS trigger_vendedores_updated_at ON core.vendedores;
    END IF;
    
    RAISE NOTICE 'SUCCESS: Reestruturação concluída com sucesso!';
    RAISE NOTICE 'INFO: Trigger problemático (updated_by) foi removido e substituído por trigger simples';
END
$$;

-- Status final
SELECT 'Reestruturação concluída! Execute 10_populacao_vendedores.sql para população completa.' as status;

-- =============================================
-- INSTRUÇÕES PARA PRÓXIMOS PASSOS:
-- =============================================
-- 1. Verificar se este script executou sem erros
-- 2. Executar o script 10_populacao_vendedores.sql (dados reais)
-- 3. Atribuir lojas aos vendedores sem loja
-- 4. Atualizar dados de vendas para usar novos UUIDs
-- 5. Recriar procedures/functions que dependiam da estrutura antiga
-- =============================================

| status                                                                                 |
| -------------------------------------------------------------------------------------- |
| Reestruturação concluída! Execute 10_populacao_vendedores.sql para população completa. |