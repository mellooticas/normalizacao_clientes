-- ========================================
-- EXTENSÕES PARA SCHEMA PAGAMENTOS
-- Suporte para vendas completas com múltiplas modalidades
-- ========================================

-- ========================================
-- TABELA: pagamentos.vendas_completas
-- Controla o fluxo completo de uma venda com múltiplas modalidades
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.vendas_completas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- IDENTIFICAÇÃO DA VENDA
    numero_venda TEXT UNIQUE,
    numero_os TEXT,
    
    -- RELACIONAMENTOS
    cliente_uuid UUID NOT NULL, -- FK para core.clientes
    loja_uuid UUID NOT NULL,    -- FK para core.lojas
    vendedor_uuid UUID,         -- FK para funcionários/vendedores
    
    -- VALORES TOTAIS
    valor_total_venda DECIMAL(10,2) NOT NULL,
    valor_produtos DECIMAL(10,2),
    valor_servicos DECIMAL(10,2),
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    
    -- MODALIDADES DE PAGAMENTO
    valor_entrada DECIMAL(10,2) DEFAULT 0,     -- Pago no ato da compra
    valor_retirada DECIMAL(10,2) DEFAULT 0,    -- Pago na entrega
    valor_financiado DECIMAL(10,2) DEFAULT 0,  -- Valor do carnê
    
    -- CONTROLE DO CARNÊ
    numero_parcelas INTEGER DEFAULT 0,
    valor_parcela DECIMAL(10,2),
    data_primeira_parcela DATE,
    data_ultima_parcela DATE,
    
    -- DATAS IMPORTANTES
    data_venda DATE NOT NULL,
    data_prevista_entrega DATE,
    data_entrega_efetiva DATE,
    
    -- STATUS DA VENDA
    status_venda TEXT DEFAULT 'ATIVA', -- 'ATIVA', 'ENTREGUE', 'CANCELADA', 'QUITADA'
    status_pagamento TEXT DEFAULT 'PENDENTE', -- 'PENDENTE', 'PARCIAL', 'QUITADO'
    
    -- OBSERVAÇÕES
    observacoes TEXT,
    condicoes_especiais TEXT,
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    
    -- CONSTRAINTS
    CONSTRAINT chk_valor_total CHECK (valor_total_venda > 0),
    CONSTRAINT chk_modalidades CHECK (
        (valor_entrada + valor_retirada + valor_financiado) = valor_total_venda
    ),
    CONSTRAINT chk_parcelas CHECK (
        (numero_parcelas = 0 AND valor_financiado = 0) OR
        (numero_parcelas > 0 AND valor_financiado > 0)
    )
);

-- ========================================
-- TABELA: pagamentos.modalidades_pagamento
-- Controla cada modalidade de pagamento de uma venda
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.modalidades_pagamento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- RELACIONAMENTOS
    venda_uuid UUID NOT NULL REFERENCES pagamentos.vendas_completas(id),
    movimento_caixa_id UUID REFERENCES pagamentos.movimentos_caixa(id),
    
    -- TIPO DA MODALIDADE
    tipo_modalidade TEXT NOT NULL, -- 'ENTRADA', 'RETIRADA', 'PARCELA_CARNE'
    sequencia INTEGER, -- Para parcelas: 1, 2, 3... / Para outras: 0
    
    -- VALORES
    valor_previsto DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2) DEFAULT 0,
    valor_pendente DECIMAL(10,2) GENERATED ALWAYS AS (valor_previsto - valor_pago) STORED,
    
    -- DATAS
    data_prevista DATE,
    data_pagamento DATE,
    data_vencimento DATE,
    
    -- STATUS
    status_modalidade TEXT DEFAULT 'PENDENTE', -- 'PENDENTE', 'PAGO', 'ATRASADO', 'CANCELADO'
    
    -- INFORMAÇÕES ADICIONAIS
    forma_pagamento TEXT, -- 'DINHEIRO', 'CARTAO', 'PIX', 'CARNE'
    observacoes TEXT,
    
    -- AUDITORIA
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- CONSTRAINTS
    CONSTRAINT chk_valor_previsto CHECK (valor_previsto > 0),
    CONSTRAINT chk_valor_pago CHECK (valor_pago >= 0),
    CONSTRAINT chk_sequencia CHECK (
        (tipo_modalidade = 'PARCELA_CARNE' AND sequencia > 0) OR
        (tipo_modalidade != 'PARCELA_CARNE' AND sequencia = 0)
    )
);

-- ========================================
-- TABELA: pagamentos.controle_quitacao
-- View materializada para controle rápido de quitação
-- ========================================
CREATE TABLE IF NOT EXISTS pagamentos.controle_quitacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- RELACIONAMENTOS
    venda_uuid UUID NOT NULL UNIQUE REFERENCES pagamentos.vendas_completas(id),
    cliente_uuid UUID NOT NULL,
    
    -- TOTAIS CALCULADOS
    valor_total_venda DECIMAL(10,2) NOT NULL,
    valor_total_previsto DECIMAL(10,2) NOT NULL,
    valor_total_pago DECIMAL(10,2) DEFAULT 0,
    valor_total_pendente DECIMAL(10,2) GENERATED ALWAYS AS (valor_total_previsto - valor_total_pago) STORED,
    
    -- DETALHAMENTO POR MODALIDADE
    entrada_prevista DECIMAL(10,2) DEFAULT 0,
    entrada_paga DECIMAL(10,2) DEFAULT 0,
    retirada_prevista DECIMAL(10,2) DEFAULT 0,
    retirada_paga DECIMAL(10,2) DEFAULT 0,
    carne_previsto DECIMAL(10,2) DEFAULT 0,
    carne_pago DECIMAL(10,2) DEFAULT 0,
    
    -- ANÁLISE DE PARCELAS
    parcelas_total INTEGER DEFAULT 0,
    parcelas_pagas INTEGER DEFAULT 0,
    parcelas_pendentes INTEGER GENERATED ALWAYS AS (parcelas_total - parcelas_pagas) STORED,
    
    -- STATUS CONSOLIDADO
    situacao_geral TEXT, -- 'QUITADO', 'EM_DIA', 'ATRASADO', 'INADIMPLENTE'
    percentual_quitado DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN valor_total_previsto = 0 THEN 0
            ELSE ROUND((valor_total_pago / valor_total_previsto * 100), 2)
        END
    ) STORED,
    
    -- ANÁLISE TEMPORAL
    dias_desde_venda INTEGER,
    dias_desde_ultimo_pagamento INTEGER,
    proxima_parcela_vence DATE,
    
    -- AUDITORIA
    last_calculated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- ATUALIZAÇÕES NA TABELA MOVIMENTOS_CAIXA
-- Adicionar relacionamento com venda
-- ========================================
ALTER TABLE pagamentos.movimentos_caixa 
ADD COLUMN IF NOT EXISTS venda_completa_uuid UUID REFERENCES pagamentos.vendas_completas(id);

ALTER TABLE pagamentos.movimentos_caixa 
ADD COLUMN IF NOT EXISTS modalidade_pagamento_id UUID REFERENCES pagamentos.modalidades_pagamento(id);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

-- Vendas Completas
CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON pagamentos.vendas_completas(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_vendas_status ON pagamentos.vendas_completas(status_venda, status_pagamento);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON pagamentos.vendas_completas(data_venda);
CREATE INDEX IF NOT EXISTS idx_vendas_numero ON pagamentos.vendas_completas(numero_venda);

-- Modalidades
CREATE INDEX IF NOT EXISTS idx_modalidades_venda ON pagamentos.modalidades_pagamento(venda_uuid);
CREATE INDEX IF NOT EXISTS idx_modalidades_tipo ON pagamentos.modalidades_pagamento(tipo_modalidade);
CREATE INDEX IF NOT EXISTS idx_modalidades_status ON pagamentos.modalidades_pagamento(status_modalidade);
CREATE INDEX IF NOT EXISTS idx_modalidades_vencimento ON pagamentos.modalidades_pagamento(data_vencimento);

-- Controle Quitação
CREATE INDEX IF NOT EXISTS idx_quitacao_cliente ON pagamentos.controle_quitacao(cliente_uuid);
CREATE INDEX IF NOT EXISTS idx_quitacao_situacao ON pagamentos.controle_quitacao(situacao_geral);
CREATE INDEX IF NOT EXISTS idx_quitacao_percentual ON pagamentos.controle_quitacao(percentual_quitado);

-- ========================================
-- VIEWS ESPECÍFICAS PARA O CENÁRIO
-- ========================================

-- View: Vendas com múltiplas modalidades
CREATE OR REPLACE VIEW pagamentos.v_vendas_multimodais AS
SELECT 
    vc.id as venda_id,
    vc.numero_venda,
    vc.cliente_uuid,
    c.nome as cliente_nome,
    vc.valor_total_venda,
    
    -- Modalidades
    vc.valor_entrada,
    vc.valor_retirada, 
    vc.valor_financiado,
    vc.numero_parcelas,
    
    -- Status detalhado
    cq.entrada_paga,
    cq.retirada_paga,
    cq.carne_pago,
    cq.percentual_quitado,
    cq.situacao_geral,
    
    -- Análise
    CASE 
        WHEN cq.entrada_paga < vc.valor_entrada THEN 'ENTRADA_PENDENTE'
        WHEN cq.retirada_paga < vc.valor_retirada THEN 'RETIRADA_PENDENTE'  
        WHEN cq.carne_pago < vc.valor_financiado THEN 'CARNE_PENDENTE'
        ELSE 'QUITADO'
    END as status_detalhado,
    
    vc.data_venda,
    vc.status_venda
    
FROM pagamentos.vendas_completas vc
LEFT JOIN pagamentos.controle_quitacao cq ON vc.id = cq.venda_uuid
LEFT JOIN core.clientes c ON vc.cliente_uuid = c.id;

-- View: Próximas ações necessárias
CREATE OR REPLACE VIEW pagamentos.v_acoes_pendentes AS
SELECT 
    mp.venda_uuid,
    vc.numero_venda,
    vc.cliente_uuid,
    c.nome as cliente_nome,
    
    mp.tipo_modalidade,
    mp.sequencia,
    mp.valor_previsto,
    mp.valor_pago,
    mp.valor_pendente,
    mp.data_prevista,
    mp.data_vencimento,
    mp.status_modalidade,
    
    -- Análise de prioridade
    CASE 
        WHEN mp.data_vencimento < CURRENT_DATE THEN 'VENCIDO'
        WHEN mp.data_vencimento <= CURRENT_DATE + INTERVAL '7 days' THEN 'VENCE_SEMANA'
        WHEN mp.data_vencimento <= CURRENT_DATE + INTERVAL '30 days' THEN 'VENCE_MES'
        ELSE 'FUTURO'
    END as prioridade,
    
    (CURRENT_DATE - mp.data_vencimento) as dias_atraso
    
FROM pagamentos.modalidades_pagamento mp
JOIN pagamentos.vendas_completas vc ON mp.venda_uuid = vc.id  
LEFT JOIN core.clientes c ON vc.cliente_uuid = c.id
WHERE mp.status_modalidade = 'PENDENTE'
ORDER BY mp.data_vencimento;

-- ========================================
-- FUNÇÕES PARA AUTOMAÇÃO
-- ========================================

-- Função: Criar venda completa com modalidades
CREATE OR REPLACE FUNCTION pagamentos.criar_venda_completa(
    p_cliente_uuid UUID,
    p_loja_uuid UUID,
    p_numero_venda TEXT,
    p_valor_total DECIMAL,
    p_valor_entrada DECIMAL DEFAULT 0,
    p_valor_retirada DECIMAL DEFAULT 0,
    p_numero_parcelas INTEGER DEFAULT 0
) RETURNS UUID AS $$
DECLARE
    v_venda_id UUID;
    v_valor_financiado DECIMAL;
    v_valor_parcela DECIMAL;
    i INTEGER;
BEGIN
    -- Calcular valor financiado
    v_valor_financiado := p_valor_total - p_valor_entrada - p_valor_retirada;
    
    IF p_numero_parcelas > 0 THEN
        v_valor_parcela := v_valor_financiado / p_numero_parcelas;
    ELSE
        v_valor_parcela := 0;
    END IF;
    
    -- Criar venda principal
    INSERT INTO pagamentos.vendas_completas (
        numero_venda, cliente_uuid, loja_uuid, valor_total_venda,
        valor_entrada, valor_retirada, valor_financiado,
        numero_parcelas, valor_parcela, data_venda
    ) VALUES (
        p_numero_venda, p_cliente_uuid, p_loja_uuid, p_valor_total,
        p_valor_entrada, p_valor_retirada, v_valor_financiado,
        p_numero_parcelas, v_valor_parcela, CURRENT_DATE
    ) RETURNING id INTO v_venda_id;
    
    -- Criar modalidade ENTRADA (se houver)
    IF p_valor_entrada > 0 THEN
        INSERT INTO pagamentos.modalidades_pagamento (
            venda_uuid, tipo_modalidade, sequencia, valor_previsto, data_prevista
        ) VALUES (
            v_venda_id, 'ENTRADA', 0, p_valor_entrada, CURRENT_DATE
        );
    END IF;
    
    -- Criar modalidade RETIRADA (se houver)  
    IF p_valor_retirada > 0 THEN
        INSERT INTO pagamentos.modalidades_pagamento (
            venda_uuid, tipo_modalidade, sequencia, valor_previsto, data_prevista
        ) VALUES (
            v_venda_id, 'RETIRADA', 0, p_valor_retirada, CURRENT_DATE + INTERVAL '30 days'
        );
    END IF;
    
    -- Criar parcelas do carnê (se houver)
    IF p_numero_parcelas > 0 AND v_valor_financiado > 0 THEN
        FOR i IN 1..p_numero_parcelas LOOP
            INSERT INTO pagamentos.modalidades_pagamento (
                venda_uuid, tipo_modalidade, sequencia, valor_previsto, 
                data_prevista, data_vencimento
            ) VALUES (
                v_venda_id, 'PARCELA_CARNE', i, v_valor_parcela,
                CURRENT_DATE + (i * INTERVAL '1 month'),
                CURRENT_DATE + (i * INTERVAL '1 month')
            );
        END LOOP;
    END IF;
    
    -- Criar registro de controle
    INSERT INTO pagamentos.controle_quitacao (
        venda_uuid, cliente_uuid, valor_total_venda, valor_total_previsto,
        entrada_prevista, retirada_prevista, carne_previsto, parcelas_total
    ) VALUES (
        v_venda_id, p_cliente_uuid, p_valor_total, p_valor_total,
        p_valor_entrada, p_valor_retirada, v_valor_financiado, p_numero_parcelas
    );
    
    RETURN v_venda_id;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA
-- ========================================
CREATE OR REPLACE FUNCTION pagamentos.atualizar_controle_quitacao()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalcular totais pagos por modalidade
    UPDATE pagamentos.controle_quitacao cq
    SET 
        entrada_paga = COALESCE((
            SELECT SUM(mp.valor_pago) 
            FROM pagamentos.modalidades_pagamento mp 
            WHERE mp.venda_uuid = cq.venda_uuid AND mp.tipo_modalidade = 'ENTRADA'
        ), 0),
        retirada_paga = COALESCE((
            SELECT SUM(mp.valor_pago) 
            FROM pagamentos.modalidades_pagamento mp 
            WHERE mp.venda_uuid = cq.venda_uuid AND mp.tipo_modalidade = 'RETIRADA'
        ), 0),
        carne_pago = COALESCE((
            SELECT SUM(mp.valor_pago) 
            FROM pagamentos.modalidades_pagamento mp 
            WHERE mp.venda_uuid = cq.venda_uuid AND mp.tipo_modalidade = 'PARCELA_CARNE'
        ), 0),
        parcelas_pagas = COALESCE((
            SELECT COUNT(*) 
            FROM pagamentos.modalidades_pagamento mp 
            WHERE mp.venda_uuid = cq.venda_uuid 
              AND mp.tipo_modalidade = 'PARCELA_CARNE' 
              AND mp.status_modalidade = 'PAGO'
        ), 0),
        valor_total_pago = (
            SELECT SUM(mp.valor_pago) 
            FROM pagamentos.modalidades_pagamento mp 
            WHERE mp.venda_uuid = cq.venda_uuid
        ),
        last_calculated = NOW()
    WHERE cq.venda_uuid = COALESCE(NEW.venda_uuid, OLD.venda_uuid);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_atualizar_quitacao
    AFTER INSERT OR UPDATE OR DELETE ON pagamentos.modalidades_pagamento
    FOR EACH ROW
    EXECUTE FUNCTION pagamentos.atualizar_controle_quitacao();

-- ========================================
-- COMENTÁRIOS
-- ========================================
COMMENT ON TABLE pagamentos.vendas_completas IS 'Controle completo de vendas com múltiplas modalidades de pagamento';
COMMENT ON TABLE pagamentos.modalidades_pagamento IS 'Cada modalidade específica de pagamento de uma venda (entrada, retirada, parcelas)';
COMMENT ON TABLE pagamentos.controle_quitacao IS 'Visão consolidada para controle rápido de quitação por venda';

COMMENT ON FUNCTION pagamentos.criar_venda_completa IS 'Cria uma venda completa com todas as modalidades automaticamente';