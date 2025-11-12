-- ============================================================================
-- INSERÇÃO DO VENDEDOR: THIAGO
-- ============================================================================
-- Tabela: core.vendedores
-- Consultor encontrado na planilha consolidadas.csv com 2 registros
-- ============================================================================

-- Inserir THIAGO como vendedor
INSERT INTO core.vendedores (
    id_legado,
    nome,
    nome_padronizado,
    nome_exibicao,
    cpf,
    telefone,
    email,
    ativo,
    data_admissao,
    created_at,
    observacoes
)
VALUES (
    'VENDEDOR_THIAGO',                            -- id_legado único
    'THIAGO',                                      -- nome
    'THIAGO',                                      -- nome_padronizado
    'Thiago',                                      -- nome_exibicao
    NULL,                                          -- cpf (não temos)
    NULL,                                          -- telefone (não temos)
    NULL,                                          -- email (não temos)
    true,                                          -- ativo
    NULL,                                          -- data_admissao (não temos)
    CURRENT_TIMESTAMP,                             -- created_at
    'Vendedor importado da planilha consolidadas.csv. Total de 2 OSS registradas.' -- observacoes
)
ON CONFLICT (id_legado) DO UPDATE SET
    updated_at = CURRENT_TIMESTAMP,
    observacoes = EXCLUDED.observacoes || ' | Atualizado em: ' || CURRENT_TIMESTAMP::text;

-- ============================================================================
-- VERIFICAÇÃO
-- ============================================================================
-- Verificar se foi inserido
SELECT 
    id,
    id_legado,
    nome,
    nome_padronizado,
    nome_exibicao,
    cpf,
    telefone,
    email,
    ativo,
    data_admissao,
    observacoes,
    created_at
FROM core.vendedores
WHERE id_legado = 'VENDEDOR_THIAGO';

-- ============================================================================
-- ESTATÍSTICAS DOS VENDEDORES NO BANCO
-- ============================================================================
SELECT 
    COUNT(*) as total_vendedores,
    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos,
    COUNT(CASE WHEN data_demissao IS NULL THEN 1 END) as sem_data_demissao
FROM core.vendedores;
