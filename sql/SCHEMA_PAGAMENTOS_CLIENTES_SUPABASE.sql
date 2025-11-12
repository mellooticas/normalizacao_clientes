-- ========================================
-- SCHEMA PAGAMENTOS - FOCO EM CLIENTES
-- Apenas recebimentos e pagamentos de clientes
-- Data: 06/11/2025
-- ========================================

-- ========================================
-- LIMPEZA: REMOVER ESTRUTURA ANTERIOR
-- ========================================

-- 1. Remover triggers existentes
DROP TRIGGER IF EXISTS trigger_atualizar_resumo_cliente ON pagamentos.movimentos_caixa;
DROP TRIGGER IF EXISTS trigger_atualizar_resumo_entrada ON pagamentos.entradas_carne;

-- 2. Remover funções existentes
DROP FUNCTION IF EXISTS pagamentos.calcular_score_cliente(UUID);
DROP FUNCTION IF EXISTS pagamentos.calcular_score_cliente_carne(UUID);
DROP FUNCTION IF EXISTS pagamentos.atualizar_resumo_cliente();
DROP FUNCTION IF EXISTS pagamentos.atualizar_resumo_entrada();

-- 3. Remover views existentes
DROP VIEW IF EXISTS pagamentos.v_pagamentos_completos;
DROP VIEW IF EXISTS pagamentos.v_pagamentos_basicos;
DROP VIEW IF EXISTS pagamentos.v_carnes_por_cliente;
DROP VIEW IF EXISTS pagamentos.v_carnes_basico;
DROP VIEW IF EXISTS pagamentos.v_resumo_geral;
DROP VIEW IF EXISTS pagamentos.v_entradas_completas;
DROP VIEW IF EXISTS pagamentos.v_top_clientes;
DROP VIEW IF EXISTS pagamentos.v_analise_carnes;

-- 4. Remover tabelas existentes (ordem importante por causa das FKs)
DROP TABLE IF EXISTS pagamentos.parcelas_carne CASCADE;
DROP TABLE IF EXISTS pagamentos.movimentos_caixa CASCADE;
DROP TABLE IF EXISTS pagamentos.resumo_clientes CASCADE;
DROP TABLE IF EXISTS pagamentos.controle_carnes CASCADE;
DROP TABLE IF EXISTS pagamentos.entradas_carne CASCADE;

-- 5. Recriar schema limpo
DROP SCHEMA IF EXISTS pagamentos CASCADE;
CREATE SCHEMA pagamentos;

-- 6. CRIAR EXTENSÕES NECESSÁRIAS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABELA PRINCIPAL: pagamentos.entradas_carne
-- Carnês recebidos dos clientes
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.entradas_carne (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IDENTIFICAÇÃO ORIGINAL
    id_movimento_original BIGINT NOT NULL,
    numero_documento BIGINT,
    
    -- CLIENTE
    cliente_uuid UUID NOT NULL, -- FK para core.clientes
    cliente_nome TEXT NOT NULL,
    cliente_id_original BIGINT, -- ID original do sistema Lancaster
    
    -- LOJA E OPERACIONAL
    loja_uuid UUID, -- FK para core.lojas
    loja_codigo INTEGER,
    codigo_caixa BIGINT,
    
    -- INFORMAÇÕES DA PARCELA
    numero_parcela INTEGER,
    total_parcelas INTEGER,
    valor_parcela DECIMAL(10,2) NOT NULL,
    
    -- INFORMAÇÕES DO CARNÊ
    plano_pagamento TEXT, -- '3x', '5x', '12x', etc.
    
    -- TEMPORAL
    data_pagamento DATE NOT NULL,
    hora_pagamento TIME,
    timestamp_pagamento TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- DETALHES
    historico_completo TEXT,
    segmento TEXT DEFAULT 'CARNE LANCASTER',
    
    -- STATUS
    status_parcela TEXT DEFAULT 'PAGA', -- 'PAGA', 'PENDENTE', 'ATRASADA'
    
    -- METADADOS DE ORIGEM
    arquivo_origem TEXT,
    periodo_origem TEXT,
    
    -- FLAGS DE CONTROLE
    tem_parcela_info BOOLEAN DEFAULT TRUE,
    tem_cliente_id BOOLEAN DEFAULT TRUE,
    is_consumidor BOOLEAN DEFAULT FALSE,
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- CONSTRAINTS
    CONSTRAINT chk_valor_parcela CHECK (valor_parcela > 0),
    CONSTRAINT chk_data_pagamento CHECK (data_pagamento IS NOT NULL),
    CONSTRAINT chk_numero_parcela CHECK (numero_parcela > 0 OR numero_parcela IS NULL),
    CONSTRAINT chk_total_parcelas CHECK (total_parcelas > 0 OR total_parcelas IS NULL)
);

-- ========================================
-- TABELA: pagamentos.resumo_clientes
-- Situação financeira consolidada por cliente
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.resumo_clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- CLIENTE
    cliente_uuid UUID NOT NULL UNIQUE, -- FK para core.clientes
    cliente_nome TEXT NOT NULL,
    cliente_id_original BIGINT,
    
    -- ESTATÍSTICAS DE CARNÊS
    total_parcelas_pagas INTEGER DEFAULT 0,
    valor_total_pago DECIMAL(10,2) DEFAULT 0,
    total_carnes_diferentes INTEGER DEFAULT 0,
    
    -- ANÁLISE TEMPORAL
    primeiro_pagamento DATE,
    ultimo_pagamento DATE,
    periodo_ativo_meses INTEGER,
    
    -- ANÁLISE DE PARCELAS
    parcela_media DECIMAL(5,2),
    maior_parcela DECIMAL(10,2),
    menor_parcela DECIMAL(10,2),
    
    -- COMPORTAMENTO
    frequencia_pagamento TEXT, -- 'REGULAR', 'IRREGULAR', 'ESPORADICO'
    score_pagamento INTEGER DEFAULT 50, -- 0-100 baseado no histórico
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_calculated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- TABELA: pagamentos.controle_carnes
-- Agrupamento por carnê completo
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.controle_carnes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IDENTIFICAÇÃO DO CARNÊ
    cliente_uuid UUID NOT NULL, -- FK para core.clientes
    numero_carnes TEXT, -- Número do carnê se disponível
    plano_pagamento TEXT NOT NULL, -- '3x', '5x', etc.
    
    -- ESTATÍSTICAS DO CARNÊ
    total_parcelas_previstas INTEGER NOT NULL,
    parcelas_pagas INTEGER DEFAULT 0,
    valor_total_pago DECIMAL(10,2) DEFAULT 0,
    valor_parcela_padrao DECIMAL(10,2), -- Valor típico da parcela
    
    -- STATUS
    status_carne TEXT DEFAULT 'EM_ANDAMENTO', -- 'COMPLETO', 'EM_ANDAMENTO', 'ABANDONADO'
    data_inicio DATE,
    data_ultimo_pagamento DATE,
    
    -- ANÁLISE
    percentual_completude DECIMAL(5,2) DEFAULT 0, -- % de parcelas pagas
    estimativa_conclusao DATE, -- Projeção baseada no padrão
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- CONSTRAINTS
    CONSTRAINT chk_total_parcelas_previstas CHECK (total_parcelas_previstas > 0),
    CONSTRAINT chk_parcelas_pagas CHECK (parcelas_pagas >= 0),
    CONSTRAINT chk_percentual CHECK (percentual_completude >= 0 AND percentual_completude <= 100)
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

-- Entradas Carnê
CREATE INDEX IF NOT EXISTS idx_entradas_cliente ON pagamentos.entradas_carne(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_entradas_data ON pagamentos.entradas_carne(data_pagamento);
CREATE INDEX IF NOT EXISTS idx_entradas_valor ON pagamentos.entradas_carne(valor_parcela);
CREATE INDEX IF NOT EXISTS idx_entradas_parcela ON pagamentos.entradas_carne(numero_parcela, total_parcelas);
CREATE INDEX IF NOT EXISTS idx_entradas_plano ON pagamentos.entradas_carne(plano_pagamento);
CREATE INDEX IF NOT EXISTS idx_entradas_original ON pagamentos.entradas_carne(id_movimento_original);
CREATE INDEX IF NOT EXISTS idx_entradas_cliente_original ON pagamentos.entradas_carne(cliente_id_original);

-- Resumo Clientes
CREATE INDEX IF NOT EXISTS idx_resumo_cliente_nome ON pagamentos.resumo_clientes(cliente_nome);
CREATE INDEX IF NOT EXISTS idx_resumo_valor_total ON pagamentos.resumo_clientes(valor_total_pago);
CREATE INDEX IF NOT EXISTS idx_resumo_score ON pagamentos.resumo_clientes(score_pagamento);
CREATE INDEX IF NOT EXISTS idx_resumo_frequencia ON pagamentos.resumo_clientes(frequencia_pagamento);

-- Controle Carnês
CREATE INDEX IF NOT EXISTS idx_controle_cliente ON pagamentos.controle_carnes(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_controle_status ON pagamentos.controle_carnes(status_carne);
CREATE INDEX IF NOT EXISTS idx_controle_plano ON pagamentos.controle_carnes(plano_pagamento);
CREATE INDEX IF NOT EXISTS idx_controle_completude ON pagamentos.controle_carnes(percentual_completude);

-- ========================================
-- VIEWS ÚTEIS
-- ========================================

-- View: Entradas com informações completas
CREATE OR REPLACE VIEW pagamentos.v_entradas_completas AS
SELECT 
    ec.id,
    ec.cliente_uuid,
    ec.cliente_nome,
    ec.data_pagamento,
    ec.valor_parcela,
    ec.numero_parcela,
    ec.total_parcelas,
    ec.plano_pagamento,
    ec.historico_completo,
    
    -- Análise da parcela
    CASE 
        WHEN ec.numero_parcela IS NOT NULL AND ec.total_parcelas IS NOT NULL 
        THEN CONCAT(ec.numero_parcela, '/', ec.total_parcelas)
        ELSE 'N/A'
    END as parcela_info,
    
    -- Status temporal
    CASE 
        WHEN ec.data_pagamento >= CURRENT_DATE - INTERVAL '30 days' THEN 'RECENTE'
        WHEN ec.data_pagamento >= CURRENT_DATE - INTERVAL '90 days' THEN 'MEDIO'
        ELSE 'ANTIGO'
    END as status_temporal,
    
    ec.created_at
FROM pagamentos.entradas_carne ec
ORDER BY ec.data_pagamento DESC;

-- View: Top clientes por valor
CREATE OR REPLACE VIEW pagamentos.v_top_clientes AS
SELECT 
    rc.cliente_uuid,
    rc.cliente_nome,
    rc.total_parcelas_pagas,
    rc.valor_total_pago,
    rc.score_pagamento,
    rc.primeiro_pagamento,
    rc.ultimo_pagamento,
    
    -- Análise de atividade
    CASE 
        WHEN rc.ultimo_pagamento >= CURRENT_DATE - INTERVAL '30 days' THEN 'ATIVO'
        WHEN rc.ultimo_pagamento >= CURRENT_DATE - INTERVAL '90 days' THEN 'MODERADO'
        ELSE 'INATIVO'
    END as status_atividade,
    
    -- Valor médio por parcela
    ROUND(rc.valor_total_pago / GREATEST(rc.total_parcelas_pagas, 1), 2) as valor_medio_parcela
    
FROM pagamentos.resumo_clientes rc
WHERE rc.valor_total_pago > 0
ORDER BY rc.valor_total_pago DESC;

-- View: Análise de carnês
CREATE OR REPLACE VIEW pagamentos.v_analise_carnes AS
SELECT 
    cc.cliente_uuid,
    rc.cliente_nome,
    cc.plano_pagamento,
    cc.total_parcelas_previstas,
    cc.parcelas_pagas,
    cc.valor_total_pago,
    cc.percentual_completude,
    cc.status_carne,
    
    -- Análise de progresso
    CASE 
        WHEN cc.percentual_completude = 100 THEN 'FINALIZADO'
        WHEN cc.percentual_completude >= 75 THEN 'QUASE_COMPLETO'
        WHEN cc.percentual_completude >= 50 THEN 'MEIO_CAMINHO'
        WHEN cc.percentual_completude >= 25 THEN 'INICIO'
        ELSE 'ABANDONO_RISCO'
    END as fase_carne,
    
    cc.data_ultimo_pagamento
    
FROM pagamentos.controle_carnes cc
LEFT JOIN pagamentos.resumo_clientes rc ON cc.cliente_uuid = rc.cliente_uuid
ORDER BY cc.percentual_completude DESC;

-- ========================================
-- FUNÇÕES DE UTILIDADE
-- ========================================

-- Função: Calcular score de cliente baseado apenas em carnês
CREATE OR REPLACE FUNCTION pagamentos.calcular_score_cliente_carne(cliente_uuid_param UUID)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 50; -- Score base
    total_parcelas INTEGER;
    valor_total DECIMAL;
    dias_ultimo_pagamento INTEGER;
    regularidade DECIMAL;
BEGIN
    -- Buscar estatísticas do cliente
    SELECT 
        total_parcelas_pagas,
        valor_total_pago,
        EXTRACT(days FROM (CURRENT_DATE - ultimo_pagamento))
    INTO total_parcelas, valor_total, dias_ultimo_pagamento
    FROM pagamentos.resumo_clientes 
    WHERE cliente_uuid = cliente_uuid_param;
    
    -- Calcular regularidade (média de dias entre pagamentos)
    SELECT AVG(EXTRACT(days FROM (
        data_pagamento - LAG(data_pagamento) OVER (ORDER BY data_pagamento)
    )))
    INTO regularidade
    FROM pagamentos.entradas_carne 
    WHERE cliente_uuid = cliente_uuid_param;
    
    -- Ajustar score baseado no histórico
    IF total_parcelas > 10 THEN score := score + 20; END IF;
    IF valor_total > 500 THEN score := score + 15; END IF;
    IF dias_ultimo_pagamento <= 30 THEN score := score + 15; END IF;
    IF dias_ultimo_pagamento > 90 THEN score := score - 25; END IF;
    IF regularidade IS NOT NULL AND regularidade <= 30 THEN score := score + 10; END IF;
    
    -- Garantir range 0-100
    score := GREATEST(0, LEAST(100, score));
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- Função: Atualizar resumo quando nova entrada de carnê (definição apenas)
CREATE OR REPLACE FUNCTION pagamentos.atualizar_resumo_entrada()
RETURNS TRIGGER AS $$
BEGIN
    -- Esta função será definida após as tabelas estarem criadas
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- ========================================

COMMENT ON SCHEMA pagamentos IS 'Schema focado exclusivamente em pagamentos e recebimentos de clientes';
COMMENT ON TABLE pagamentos.entradas_carne IS 'Registro de todas as entradas de carnês recebidas dos clientes';
COMMENT ON TABLE pagamentos.resumo_clientes IS 'Situação financeira consolidada por cliente baseada em pagamentos';
COMMENT ON TABLE pagamentos.controle_carnes IS 'Agrupamento e controle de carnês por cliente e plano';

-- ========================================
-- TRIGGERS (CRIADOS APÓS TODAS AS TABELAS)
-- ========================================

-- Primeiro, implementar a função completa do trigger
CREATE OR REPLACE FUNCTION pagamentos.atualizar_resumo_entrada()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualizar ou inserir resumo do cliente
    INSERT INTO pagamentos.resumo_clientes (cliente_uuid, cliente_nome, cliente_id_original)
    VALUES (NEW.cliente_uuid, NEW.cliente_nome, NEW.cliente_id_original)
    ON CONFLICT (cliente_uuid) DO UPDATE SET
        cliente_nome = EXCLUDED.cliente_nome,
        updated_at = NOW();
    
    -- Recalcular estatísticas
    UPDATE pagamentos.resumo_clientes
    SET 
        total_parcelas_pagas = (
            SELECT COUNT(*) 
            FROM pagamentos.entradas_carne 
            WHERE cliente_uuid = NEW.cliente_uuid
        ),
        valor_total_pago = (
            SELECT COALESCE(SUM(valor_parcela), 0) 
            FROM pagamentos.entradas_carne 
            WHERE cliente_uuid = NEW.cliente_uuid
        ),
        primeiro_pagamento = (
            SELECT MIN(data_pagamento) 
            FROM pagamentos.entradas_carne 
            WHERE cliente_uuid = NEW.cliente_uuid
        ),
        ultimo_pagamento = (
            SELECT MAX(data_pagamento) 
            FROM pagamentos.entradas_carne 
            WHERE cliente_uuid = NEW.cliente_uuid
        ),
        score_pagamento = pagamentos.calcular_score_cliente_carne(NEW.cliente_uuid),
        last_calculated = NOW()
    WHERE cliente_uuid = NEW.cliente_uuid;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para atualizar resumo automaticamente
DROP TRIGGER IF EXISTS trigger_atualizar_resumo_entrada ON pagamentos.entradas_carne;
CREATE TRIGGER trigger_atualizar_resumo_entrada
    AFTER INSERT OR UPDATE ON pagamentos.entradas_carne
    FOR EACH ROW
    EXECUTE FUNCTION pagamentos.atualizar_resumo_entrada();

-- ========================================
-- VERIFICAÇÃO FINAL
-- ========================================

-- Verificar estrutura criada
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'pagamentos'
ORDER BY table_name;


| table_name           | table_type |
| -------------------- | ---------- |
| controle_carnes      | BASE TABLE |
| entradas_carne       | BASE TABLE |
| resumo_clientes      | BASE TABLE |
| v_analise_carnes     | VIEW       |
| v_entradas_completas | VIEW       |
| v_top_clientes       | VIEW       |

-- ========================================
-- SCHEMA PAGAMENTOS FOCADO EM CLIENTES CRIADO!
-- Próximo: Migrar dados de carnês para entradas_carne
-- ========================================