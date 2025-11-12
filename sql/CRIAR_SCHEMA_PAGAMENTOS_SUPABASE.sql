-- ========================================
-- SCHEMA PAGAMENTOS - CRIAÇÃO COMPLETA PARA SUPABASE
-- Execute este script inteiro no SQL Editor do Supabase
-- Data: 06/11/2025
-- ========================================

-- 1. CRIAR SCHEMA PAGAMENTOS
CREATE SCHEMA IF NOT EXISTS pagamentos;

-- 2. CRIAR EXTENSÕES NECESSÁRIAS (se não existirem)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABELA PRINCIPAL: pagamentos.movimentos_caixa
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.movimentos_caixa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IDENTIFICAÇÃO ORIGINAL
    id_movimento_original BIGINT NOT NULL UNIQUE,
    numero_documento BIGINT,
    
    -- TEMPORAL
    data_movimento DATE NOT NULL,
    hora_movimento TIME,
    timestamp_movimento TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- RELACIONAMENTOS (VIA UUID)
    cliente_uuid UUID, -- FK para core.clientes
    loja_uuid UUID,    -- FK para core.lojas (derivado do cliente ou direto)
    venda_uuid UUID,   -- FK para vendas (quando identificável)
    
    -- CATEGORIA E TIPO
    categoria_movimento TEXT NOT NULL,
    tipo_pagamento TEXT, -- 'CARNE_LANCASTER', 'CARTAO', 'DINHEIRO', 'OPERACAO_CAIXA'
    subtipo TEXT,        -- 'PARCELA', 'ENTRADA', 'SANGRIA', 'ABERTURA'
    
    -- INFORMAÇÕES FINANCEIRAS
    valor_movimento DECIMAL(10,2) NOT NULL,
    valor_original DECIMAL(10,2), -- Para histórico/auditoria
    
    -- DETALHES DO MOVIMENTO
    historico_completo TEXT,
    segmento TEXT,
    forma_pagamento TEXT,
    
    -- INFORMAÇÕES OPERACIONAIS
    codigo_funcionario INTEGER,
    codigo_caixa BIGINT,
    codigo_pdv TEXT,
    
    -- METADADOS DE ORIGEM
    arquivo_origem TEXT,
    periodo_origem TEXT,
    sistema_origem TEXT DEFAULT 'MOVIMENTO_CAIXA',
    
    -- FLAGS DE CONTROLE
    is_pagamento_carne BOOLEAN DEFAULT FALSE,
    is_operacao_caixa BOOLEAN DEFAULT FALSE,
    is_entrada_venda BOOLEAN DEFAULT FALSE,
    is_processado BOOLEAN DEFAULT FALSE,
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    
    -- CONSTRAINTS
    CONSTRAINT chk_valor_movimento CHECK (valor_movimento IS NOT NULL),
    CONSTRAINT chk_data_movimento CHECK (data_movimento IS NOT NULL)
);

-- ========================================
-- TABELA: pagamentos.parcelas_carne
-- Específica para controle detalhado de carnês
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.parcelas_carne (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- RELACIONAMENTO COM MOVIMENTO (OPCIONAL para upload inicial)
    movimento_caixa_id UUID, -- FK para pagamentos.movimentos_caixa(id) - será opcional inicialmente
    
    -- RELACIONAMENTOS PRINCIPAIS
    cliente_uuid UUID NOT NULL, -- FK para core.clientes
    venda_uuid UUID,             -- FK para vendas (quando identificado)
    
    -- INFORMAÇÕES DA PARCELA
    numero_parcela INTEGER,
    total_parcelas INTEGER,
    valor_parcela DECIMAL(10,2) NOT NULL,
    
    -- INFORMAÇÕES DO CARNÊ
    numero_carne TEXT,
    plano_pagamento TEXT, -- '6x', '12x', etc.
    valor_total_carne DECIMAL(10,2),
    
    -- STATUS DA PARCELA
    status_parcela TEXT DEFAULT 'PAGA', -- 'PAGA', 'PENDENTE', 'ATRASADA'
    data_vencimento DATE,
    data_pagamento DATE,
    
    -- INFORMAÇÕES DO CLIENTE (denormalizado para performance)
    cliente_nome TEXT,
    cliente_documento TEXT,
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- CONSTRAINTS (parcela pode ser > total_parcelas se necessário)
    CONSTRAINT chk_numero_parcela CHECK (numero_parcela > 0 OR numero_parcela IS NULL),
    CONSTRAINT chk_total_parcelas CHECK (total_parcelas > 0 OR total_parcelas IS NULL)
);

-- ========================================
-- TABELA: pagamentos.resumo_clientes
-- Visão consolidada por cliente
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.resumo_clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- CLIENTE
    cliente_uuid UUID NOT NULL UNIQUE, -- FK para core.clientes
    
    -- ESTATÍSTICAS DE PAGAMENTOS
    total_movimentos INTEGER DEFAULT 0,
    total_pago DECIMAL(10,2) DEFAULT 0,
    total_parcelas_pagas INTEGER DEFAULT 0,
    
    -- ANÁLISE DE CARNÊS
    total_carnes_ativos INTEGER DEFAULT 0,
    valor_total_carnes DECIMAL(10,2) DEFAULT 0,
    valor_total_pago_carnes DECIMAL(10,2) DEFAULT 0,
    saldo_devedor DECIMAL(10,2) DEFAULT 0,
    
    -- TEMPORAL
    primeiro_pagamento DATE,
    ultimo_pagamento DATE,
    
    -- STATUS CONSOLIDADO
    situacao_financeira TEXT, -- 'QUITADO', 'EM_DIA', 'ATRASADO', 'INADIMPLENTE'
    score_pagamento INTEGER, -- 0-100 baseado no histórico
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_calculated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

-- Movimentos Caixa
CREATE INDEX IF NOT EXISTS idx_mov_caixa_cliente ON pagamentos.movimentos_caixa(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_mov_caixa_data ON pagamentos.movimentos_caixa(data_movimento);
CREATE INDEX IF NOT EXISTS idx_mov_caixa_tipo ON pagamentos.movimentos_caixa(tipo_pagamento);
CREATE INDEX IF NOT EXISTS idx_mov_caixa_valor ON pagamentos.movimentos_caixa(valor_movimento);
CREATE INDEX IF NOT EXISTS idx_mov_caixa_carne ON pagamentos.movimentos_caixa(is_pagamento_carne) WHERE is_pagamento_carne = TRUE;
CREATE INDEX IF NOT EXISTS idx_mov_caixa_original ON pagamentos.movimentos_caixa(id_movimento_original);

-- Parcelas Carnê
CREATE INDEX IF NOT EXISTS idx_parcelas_cliente ON pagamentos.parcelas_carne(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_parcelas_movimento ON pagamentos.parcelas_carne(movimento_caixa_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_numero ON pagamentos.parcelas_carne(numero_parcela, total_parcelas);
CREATE INDEX IF NOT EXISTS idx_parcelas_status ON pagamentos.parcelas_carne(status_parcela);
CREATE INDEX IF NOT EXISTS idx_parcelas_vencimento ON pagamentos.parcelas_carne(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_parcelas_pagamento ON pagamentos.parcelas_carne(data_pagamento);

-- Resumo Clientes
CREATE INDEX IF NOT EXISTS idx_resumo_situacao ON pagamentos.resumo_clientes(situacao_financeira);
CREATE INDEX IF NOT EXISTS idx_resumo_score ON pagamentos.resumo_clientes(score_pagamento);
CREATE INDEX IF NOT EXISTS idx_resumo_saldo ON pagamentos.resumo_clientes(saldo_devedor);

-- ========================================
-- VIEWS BÁSICAS (sem JOIN com core por enquanto)
-- ========================================

-- View: Pagamentos básicos (sem informações externas)
CREATE OR REPLACE VIEW pagamentos.v_pagamentos_basicos AS
SELECT 
    mc.id,
    mc.data_movimento,
    mc.valor_movimento,
    mc.tipo_pagamento,
    mc.subtipo,
    mc.historico_completo,
    mc.cliente_uuid,
    mc.loja_uuid,
    mc.is_pagamento_carne,
    mc.is_operacao_caixa,
    mc.created_at
FROM pagamentos.movimentos_caixa mc
ORDER BY mc.data_movimento DESC;

-- View: Resumo de carnês por cliente (básico)
CREATE OR REPLACE VIEW pagamentos.v_carnes_basico AS
SELECT 
    pc.cliente_uuid,
    pc.cliente_nome,
    COUNT(DISTINCT pc.id) as total_parcelas_pagas,
    SUM(pc.valor_parcela) as total_pago,
    AVG(pc.valor_total_carne) as valor_medio_carne,
    MIN(pc.data_pagamento) as primeiro_pagamento,
    MAX(pc.data_pagamento) as ultimo_pagamento,
    
    -- Análise de completude
    CASE 
        WHEN COUNT(pc.numero_parcela) = MAX(pc.total_parcelas) THEN 'COMPLETO'
        WHEN COUNT(pc.numero_parcela) > 0 THEN 'EM_ANDAMENTO'
        ELSE 'SEM_PAGAMENTOS'
    END as status_carne
    
FROM pagamentos.parcelas_carne pc
WHERE pc.cliente_uuid IS NOT NULL
GROUP BY pc.cliente_uuid, pc.cliente_nome
ORDER BY total_pago DESC;

-- View: Resumo geral do schema
CREATE OR REPLACE VIEW pagamentos.v_resumo_geral AS
SELECT 
    'MOVIMENTOS_CAIXA' as tabela,
    COUNT(*) as total_registros,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_movimento) as valor_total,
    MIN(data_movimento) as data_inicial,
    MAX(data_movimento) as data_final
FROM pagamentos.movimentos_caixa

UNION ALL

SELECT 
    'PARCELAS_CARNE' as tabela,
    COUNT(*) as total_registros,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_parcela) as valor_total,
    MIN(data_pagamento) as data_inicial,
    MAX(data_pagamento) as data_final
FROM pagamentos.parcelas_carne

UNION ALL

SELECT 
    'RESUMO_CLIENTES' as tabela,
    COUNT(*) as total_registros,
    NULL as clientes_unicos,
    SUM(total_pago) as valor_total,
    MIN(primeiro_pagamento) as data_inicial,
    MAX(ultimo_pagamento) as data_final
FROM pagamentos.resumo_clientes;

-- ========================================
-- FUNÇÕES DE UTILIDADE
-- ========================================

-- Função: Calcular score de pagamento do cliente
CREATE OR REPLACE FUNCTION pagamentos.calcular_score_cliente(cliente_uuid_param UUID)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 50; -- Score base
    total_pagamentos INTEGER;
    atraso_medio NUMERIC;
    valor_total DECIMAL;
BEGIN
    -- Buscar estatísticas do cliente
    SELECT 
        COUNT(*),
        COALESCE(AVG(EXTRACT(days FROM (data_pagamento - data_vencimento))), 0),
        COALESCE(SUM(valor_parcela), 0)
    INTO total_pagamentos, atraso_medio, valor_total
    FROM pagamentos.parcelas_carne 
    WHERE cliente_uuid = cliente_uuid_param;
    
    -- Ajustar score baseado no histórico
    IF total_pagamentos > 10 THEN score := score + 20; END IF;
    IF atraso_medio <= 0 THEN score := score + 20; END IF;
    IF atraso_medio > 30 THEN score := score - 30; END IF;
    IF valor_total > 1000 THEN score := score + 10; END IF;
    
    -- Garantir range 0-100
    score := GREATEST(0, LEAST(100, score));
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- TRIGGERS PARA MANUTENÇÃO AUTOMÁTICA
-- ========================================

-- Trigger: Atualizar resumo do cliente quando houver novo pagamento
CREATE OR REPLACE FUNCTION pagamentos.atualizar_resumo_cliente()
RETURNS TRIGGER AS $$
BEGIN
    -- Só processar se houver cliente_uuid
    IF NEW.cliente_uuid IS NOT NULL THEN
        -- Atualizar ou inserir resumo do cliente
        INSERT INTO pagamentos.resumo_clientes (cliente_uuid)
        VALUES (NEW.cliente_uuid)
        ON CONFLICT (cliente_uuid) DO NOTHING;
        
        -- Recalcular estatísticas
        UPDATE pagamentos.resumo_clientes
        SET 
            total_movimentos = (
                SELECT COUNT(*) 
                FROM pagamentos.movimentos_caixa 
                WHERE cliente_uuid = NEW.cliente_uuid
            ),
            total_pago = (
                SELECT COALESCE(SUM(valor_movimento), 0) 
                FROM pagamentos.movimentos_caixa 
                WHERE cliente_uuid = NEW.cliente_uuid
            ),
            ultimo_pagamento = (
                SELECT MAX(data_movimento) 
                FROM pagamentos.movimentos_caixa 
                WHERE cliente_uuid = NEW.cliente_uuid
            ),
            primeiro_pagamento = (
                SELECT MIN(data_movimento) 
                FROM pagamentos.movimentos_caixa 
                WHERE cliente_uuid = NEW.cliente_uuid
            ),
            last_calculated = NOW()
        WHERE cliente_uuid = NEW.cliente_uuid;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger
DROP TRIGGER IF EXISTS trigger_atualizar_resumo_cliente ON pagamentos.movimentos_caixa;
CREATE TRIGGER trigger_atualizar_resumo_cliente
    AFTER INSERT OR UPDATE ON pagamentos.movimentos_caixa
    FOR EACH ROW
    EXECUTE FUNCTION pagamentos.atualizar_resumo_cliente();

-- ========================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- ========================================

-- Schema
COMMENT ON SCHEMA pagamentos IS 'Schema centralizado para todas as informações de pagamentos e movimentações financeiras';

-- Tabelas
COMMENT ON TABLE pagamentos.movimentos_caixa IS 'Registro de todos os movimentos de caixa normalizados e relacionados via UUID';
COMMENT ON TABLE pagamentos.parcelas_carne IS 'Controle detalhado específico para pagamentos de carnê Lancaster';
COMMENT ON TABLE pagamentos.resumo_clientes IS 'Visão consolidada da situação financeira de cada cliente';

-- Colunas importantes
COMMENT ON COLUMN pagamentos.movimentos_caixa.cliente_uuid IS 'Relacionamento com core.clientes - chave principal de integração';
COMMENT ON COLUMN pagamentos.parcelas_carne.status_parcela IS 'Status da parcela: PAGA, PENDENTE, ATRASADA';
COMMENT ON COLUMN pagamentos.resumo_clientes.score_pagamento IS 'Score de 0-100 baseado no histórico de pagamentos do cliente';

-- ========================================
-- VERIFICAÇÃO FINAL
-- ========================================

-- Verificar se tudo foi criado corretamente
SELECT 
    'SCHEMA_CRIADO' as status,
    COUNT(*) as tabelas_criadas
FROM information_schema.tables 
WHERE table_schema = 'pagamentos';

-- Listar tabelas criadas
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'pagamentos'
ORDER BY table_name;

-- ========================================
-- SUCESSO!
-- Schema pagamentos criado e pronto para receber dados
-- Próximo passo: Upload dos arquivos CSV
-- ========================================