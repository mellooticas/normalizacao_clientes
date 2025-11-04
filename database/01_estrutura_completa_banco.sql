-- =========================================
-- SCRIPT COMPLETO - ESTRUTURA BANCO CARNE FÁCIL
-- Sistema de Gestão de Óticas
-- =========================================

-- Configurações iniciais
SET timezone = 'America/Sao_Paulo';
SET datestyle = 'ISO, DMY';

-- =========================================
-- 1. CRIAÇÃO DE SCHEMAS
-- =========================================

CREATE SCHEMA IF NOT EXISTS vendas;
CREATE SCHEMA IF NOT EXISTS marketing;

-- =========================================
-- 2. TABELAS PRINCIPAIS
-- =========================================

-- 2.1 TABELA DE LOJAS
CREATE TABLE vendas.lojas (
    id UUID PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- 2.2 TABELA DE VENDEDORES
CREATE TABLE vendas.vendedores (
    id UUID PRIMARY KEY,
    nome_normalizado VARCHAR(100) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- 2.3 TABELA DE CANAIS DE AQUISIÇÃO (já criada pelo script anterior)
-- Será executada separadamente: database/12_estrutura_canais_aquisicao.sql

-- 2.4 RELACIONAMENTO N:N VENDEDORES-LOJAS
CREATE TABLE vendas.vendedores_lojas (
    vendedor_id UUID REFERENCES vendas.vendedores(id) ON DELETE CASCADE,
    loja_id UUID REFERENCES vendas.lojas(id) ON DELETE CASCADE,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (vendedor_id, loja_id)
);

-- 2.5 TABELA PRINCIPAL DE ORDENS DE SERVIÇO
CREATE TABLE vendas.ordens_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Chaves estrangeiras
    loja_id UUID REFERENCES vendas.lojas(id),
    vendedor_id UUID REFERENCES vendas.vendedores(id),
    canal_aquisicao_id UUID REFERENCES marketing.canais_aquisicao(id),
    
    -- Identificação única da OS
    numero_os VARCHAR(50) NOT NULL,
    os_chave VARCHAR(100) UNIQUE NOT NULL, -- formato: LOJA_NUMERO
    arquivo_origem VARCHAR(100),
    
    -- Dados principais da venda
    data_compra DATE NOT NULL,
    tem_venda BOOLEAN DEFAULT false, -- campo "VENDA"
    previsao_entrega DATE,
    venda_avista BOOLEAN, -- campo "VTA?"
    
    -- Dados do cliente
    cliente_nome VARCHAR(200),
    cliente_cpf VARCHAR(20),
    cliente_rg VARCHAR(20),
    cliente_data_nascimento DATE,
    cliente_cep VARCHAR(10),
    cliente_endereco VARCHAR(300),
    cliente_numero VARCHAR(20),
    cliente_bairro VARCHAR(100),
    cliente_complemento VARCHAR(100),
    cliente_telefone VARCHAR(20),
    cliente_celular VARCHAR(20),
    cliente_email VARCHAR(150),
    
    -- Dados técnicos da receita (JSONB para flexibilidade)
    receita_dados JSONB, -- Todos os campos técnicos (ESF, CIL, EIXO, etc.)
    
    -- Dados financeiros
    valor_total DECIMAL(12,2),
    forma_pagamento_1 VARCHAR(50),
    valor_pagamento_1 DECIMAL(12,2),
    forma_pagamento_2 VARCHAR(50),
    valor_pagamento_2 DECIMAL(12,2),
    valor_restante DECIMAL(12,2),
    
    -- Produtos e serviços (JSONB para flexibilidade)
    produtos JSONB, -- Array de produtos com códigos, descrições e valores
    
    -- Observações e garantias
    observacoes TEXT,
    armacao_garantia BOOLEAN,
    observacoes_armacao TEXT,
    trello_codigo VARCHAR(50),
    
    -- Campos de auditoria
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- =========================================
-- 3. ÍNDICES PARA PERFORMANCE
-- =========================================

-- Índices na tabela de ordens de serviço
CREATE INDEX idx_os_loja ON vendas.ordens_servico(loja_id);
CREATE INDEX idx_os_vendedor ON vendas.ordens_servico(vendedor_id);
CREATE INDEX idx_os_canal ON vendas.ordens_servico(canal_aquisicao_id);
CREATE INDEX idx_os_data_compra ON vendas.ordens_servico(data_compra);
CREATE INDEX idx_os_cliente_cpf ON vendas.ordens_servico(cliente_cpf);
CREATE INDEX idx_os_cliente_nome ON vendas.ordens_servico USING gin(to_tsvector('portuguese', cliente_nome));
CREATE INDEX idx_os_numero ON vendas.ordens_servico(numero_os);
CREATE INDEX idx_os_chave ON vendas.ordens_servico(os_chave);

-- Índices nas tabelas de relacionamento
CREATE INDEX idx_vendedores_lojas_vendedor ON vendas.vendedores_lojas(vendedor_id);
CREATE INDEX idx_vendedores_lojas_loja ON vendas.vendedores_lojas(loja_id);

-- Índices para busca textual
CREATE INDEX idx_vendedores_nome ON vendas.vendedores USING gin(to_tsvector('portuguese', nome_normalizado));
CREATE INDEX idx_lojas_nome ON vendas.lojas USING gin(to_tsvector('portuguese', nome));

-- =========================================
-- 4. TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- =========================================

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualização automática
CREATE TRIGGER trigger_atualizar_lojas
    BEFORE UPDATE ON vendas.lojas
    FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

CREATE TRIGGER trigger_atualizar_vendedores
    BEFORE UPDATE ON vendas.vendedores
    FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

CREATE TRIGGER trigger_atualizar_ordens
    BEFORE UPDATE ON vendas.ordens_servico
    FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

-- =========================================
-- 5. VIEWS PARA CONSULTAS FREQUENTES
-- =========================================

-- View completa com todos os relacionamentos
CREATE VIEW vendas.vw_ordens_completas AS
SELECT 
    os.id,
    os.numero_os,
    os.os_chave,
    
    -- Dados da loja
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    
    -- Dados do vendedor
    v.nome_normalizado as vendedor_nome,
    
    -- Dados do canal
    ca.nome as canal_nome,
    ca.categoria as canal_categoria,
    
    -- Dados da venda
    os.data_compra,
    os.tem_venda,
    os.previsao_entrega,
    os.valor_total,
    
    -- Dados do cliente
    os.cliente_nome,
    os.cliente_cpf,
    os.cliente_data_nascimento,
    os.cliente_telefone,
    os.cliente_celular,
    os.cliente_email,
    
    -- Timestamps
    os.criado_em,
    os.atualizado_em
    
FROM vendas.ordens_servico os
LEFT JOIN vendas.lojas l ON os.loja_id = l.id
LEFT JOIN vendas.vendedores v ON os.vendedor_id = v.id
LEFT JOIN marketing.canais_aquisicao ca ON os.canal_aquisicao_id = ca.id;

-- View para dashboard analytics
CREATE VIEW vendas.vw_analytics_vendas AS
SELECT 
    DATE_TRUNC('month', os.data_compra) as mes,
    l.nome as loja,
    v.nome_normalizado as vendedor,
    ca.categoria as canal_categoria,
    ca.nome as canal_nome,
    COUNT(*) as total_os,
    COUNT(CASE WHEN os.tem_venda THEN 1 END) as total_vendas,
    SUM(os.valor_total) as valor_total,
    AVG(os.valor_total) as ticket_medio
FROM vendas.ordens_servico os
LEFT JOIN vendas.lojas l ON os.loja_id = l.id
LEFT JOIN vendas.vendedores v ON os.vendedor_id = v.id
LEFT JOIN marketing.canais_aquisicao ca ON os.canal_aquisicao_id = ca.id
GROUP BY 
    DATE_TRUNC('month', os.data_compra),
    l.nome,
    v.nome_normalizado,
    ca.categoria,
    ca.nome;

-- =========================================
-- 6. FUNÇÃO PARA ESTATÍSTICAS RÁPIDAS
-- =========================================

CREATE OR REPLACE FUNCTION vendas.estatisticas_sistema()
RETURNS TABLE (
    total_lojas BIGINT,
    total_vendedores BIGINT,
    total_canais BIGINT,
    total_os BIGINT,
    total_vendas BIGINT,
    valor_total_geral NUMERIC,
    periodo_inicial DATE,
    periodo_final DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM vendas.lojas WHERE ativo = true) as total_lojas,
        (SELECT COUNT(*) FROM vendas.vendedores WHERE ativo = true) as total_vendedores,
        (SELECT COUNT(*) FROM marketing.canais_aquisicao WHERE ativo = true) as total_canais,
        (SELECT COUNT(*) FROM vendas.ordens_servico) as total_os,
        (SELECT COUNT(*) FROM vendas.ordens_servico WHERE tem_venda = true) as total_vendas,
        (SELECT SUM(valor_total) FROM vendas.ordens_servico) as valor_total_geral,
        (SELECT MIN(data_compra) FROM vendas.ordens_servico) as periodo_inicial,
        (SELECT MAX(data_compra) FROM vendas.ordens_servico) as periodo_final;
END;
$$ LANGUAGE plpgsql;

-- =========================================
-- 7. COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =========================================

COMMENT ON SCHEMA vendas IS 'Schema principal para dados de vendas e operações';
COMMENT ON SCHEMA marketing IS 'Schema para dados de marketing e canais de aquisição';

COMMENT ON TABLE vendas.lojas IS 'Cadastro das lojas/unidades do sistema';
COMMENT ON TABLE vendas.vendedores IS 'Cadastro de vendedores normalizados';
COMMENT ON TABLE vendas.vendedores_lojas IS 'Relacionamento N:N entre vendedores e lojas';
COMMENT ON TABLE vendas.ordens_servico IS 'Tabela principal com todas as ordens de serviço';

COMMENT ON COLUMN vendas.ordens_servico.os_chave IS 'Chave única no formato LOJA_NUMERO';
COMMENT ON COLUMN vendas.ordens_servico.receita_dados IS 'Dados técnicos da receita em formato JSON';
COMMENT ON COLUMN vendas.ordens_servico.produtos IS 'Lista de produtos e serviços em formato JSON';

-- =========================================
-- 8. GRANTS E PERMISSÕES (opcional)
-- =========================================

-- Criar role para aplicação
-- CREATE ROLE app_carne_facil;
-- GRANT USAGE ON SCHEMA vendas TO app_carne_facil;
-- GRANT USAGE ON SCHEMA marketing TO app_carne_facil;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA vendas TO app_carne_facil;
-- GRANT SELECT ON ALL TABLES IN SCHEMA marketing TO app_carne_facil;

-- =========================================
-- ESTRUTURA CRIADA COM SUCESSO!
-- =========================================

-- Para verificar a criação:
SELECT 'Estrutura criada com sucesso!' as status;
SELECT schemaname, tablename FROM pg_tables 
WHERE schemaname IN ('vendas', 'marketing') 
ORDER BY schemaname, tablename;