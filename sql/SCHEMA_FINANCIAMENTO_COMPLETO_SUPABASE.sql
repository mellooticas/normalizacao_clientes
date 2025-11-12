-- ========================================
-- SISTEMA COMPLETO DE FINANCIAMENTO PRÓPRIO
-- CRM Carnê Fácil - Schema Expandido
-- ========================================

-- Limpar e recriar schema completo
DROP SCHEMA IF EXISTS financeiro CASCADE;
DROP SCHEMA IF EXISTS propostas CASCADE;
DROP SCHEMA IF EXISTS documentos CASCADE;

CREATE SCHEMA financeiro;
CREATE SCHEMA propostas;
CREATE SCHEMA documentos;

-- ========================================
-- TABELA DE PROPOSTAS COMERCIAIS
-- ========================================
CREATE TABLE propostas.propostas_comerciais (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_proposta VARCHAR(20) UNIQUE NOT NULL,
    cliente_uuid UUID REFERENCES core.clientes(uuid) ON DELETE CASCADE,
    vendedor VARCHAR(100),
    loja VARCHAR(50),
    
    -- Dados da proposta
    data_proposta TIMESTAMP DEFAULT NOW(),
    valor_total DECIMAL(10,2) NOT NULL,
    entrada DECIMAL(10,2) DEFAULT 0,
    valor_financiado DECIMAL(10,2),
    quantidade_parcelas INTEGER,
    valor_parcela DECIMAL(10,2),
    taxa_juros DECIMAL(5,2) DEFAULT 0,
    
    -- Produtos/Serviços
    produtos JSONB, -- Array de produtos da proposta
    observacoes TEXT,
    
    -- Status e controle
    status VARCHAR(20) DEFAULT 'PENDENTE', -- PENDENTE, APROVADA, REJEITADA, ASSINADA
    data_aprovacao TIMESTAMP,
    aprovado_por VARCHAR(100),
    motivo_rejeicao TEXT,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- SISTEMA DE CARNÊS EXPANDIDO
-- ========================================
CREATE TABLE financeiro.carnes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_carne VARCHAR(20) UNIQUE NOT NULL,
    proposta_uuid UUID REFERENCES propostas.propostas_comerciais(id),
    cliente_uuid UUID REFERENCES core.clientes(uuid) ON DELETE CASCADE,
    
    -- Dados financeiros
    valor_total DECIMAL(10,2) NOT NULL,
    valor_entrada DECIMAL(10,2) DEFAULT 0,
    valor_financiado DECIMAL(10,2) NOT NULL,
    quantidade_parcelas INTEGER NOT NULL,
    valor_parcela DECIMAL(10,2) NOT NULL,
    taxa_juros DECIMAL(5,2),
    
    -- Controle
    data_criacao TIMESTAMP DEFAULT NOW(),
    data_primeiro_vencimento DATE NOT NULL,
    dia_vencimento INTEGER, -- Dia do mês para vencimento
    
    -- Status
    status VARCHAR(20) DEFAULT 'ATIVO', -- ATIVO, QUITADO, CANCELADO, INADIMPLENTE
    observacoes TEXT,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- PARCELAS DOS CARNÊS
-- ========================================
CREATE TABLE financeiro.parcelas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carne_uuid UUID REFERENCES financeiro.carnes(id) ON DELETE CASCADE,
    numero_parcela INTEGER NOT NULL,
    
    -- Valores
    valor_parcela DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2) DEFAULT 0,
    valor_juros DECIMAL(10,2) DEFAULT 0,
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    valor_total DECIMAL(10,2) GENERATED ALWAYS AS (valor_parcela + valor_juros - valor_desconto) STORED,
    
    -- Datas
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    dias_atraso INTEGER GENERATED ALWAYS AS (
        CASE 
            WHEN data_pagamento IS NULL AND CURRENT_DATE > data_vencimento 
            THEN CURRENT_DATE - data_vencimento
            ELSE 0 
        END
    ) STORED,
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDENTE', -- PENDENTE, PAGO, ATRASADO, CANCELADO
    forma_pagamento VARCHAR(50),
    observacoes TEXT,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(carne_uuid, numero_parcela)
);

-- ========================================
-- DOCUMENTOS E ASSINATURAS
-- ========================================
CREATE TABLE documentos.documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo VARCHAR(50) NOT NULL, -- PROPOSTA, CONTRATO, CARNE, RECIBO
    referencia_uuid UUID, -- UUID da proposta, carnê, etc.
    cliente_uuid UUID REFERENCES core.clientes(uuid),
    
    -- Dados do documento
    nome_documento VARCHAR(200),
    conteudo_html TEXT,
    conteudo_pdf_url VARCHAR(500),
    hash_documento VARCHAR(100), -- Para integridade
    
    -- Status
    status VARCHAR(20) DEFAULT 'RASCUNHO', -- RASCUNHO, FINALIZADO, ASSINADO
    data_finalizacao TIMESTAMP,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ASSINATURAS DIGITAIS
-- ========================================
CREATE TABLE documentos.assinaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_uuid UUID REFERENCES documentos.documentos(id) ON DELETE CASCADE,
    
    -- Dados da assinatura
    tipo_assinatura VARCHAR(20) NOT NULL, -- CLIENTE, VENDEDOR, GERENTE
    nome_assinante VARCHAR(150) NOT NULL,
    email_assinante VARCHAR(150),
    telefone_assinante VARCHAR(20),
    
    -- Assinatura digital
    assinatura_base64 TEXT, -- Imagem da assinatura
    ip_assinatura INET,
    user_agent TEXT,
    data_assinatura TIMESTAMP DEFAULT NOW(),
    
    -- Validação
    hash_assinatura VARCHAR(100),
    certificado_digital VARCHAR(500),
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- HISTÓRICO DE PAGAMENTOS EXPANDIDO
-- ========================================
CREATE TABLE financeiro.historico_pagamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcela_uuid UUID REFERENCES financeiro.parcelas(id),
    carne_uuid UUID REFERENCES financeiro.carnes(id),
    cliente_uuid UUID REFERENCES core.clientes(uuid),
    
    -- Dados do pagamento
    valor_pago DECIMAL(10,2) NOT NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    data_pagamento TIMESTAMP DEFAULT NOW(),
    
    -- Detalhes
    numero_transacao VARCHAR(100),
    observacoes TEXT,
    operador VARCHAR(100),
    loja VARCHAR(50),
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÉTRICAS E ANÁLISES
-- ========================================
CREATE TABLE financeiro.metricas_diarias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_referencia DATE DEFAULT CURRENT_DATE,
    loja VARCHAR(50),
    
    -- Vendas
    total_propostas INTEGER DEFAULT 0,
    propostas_aprovadas INTEGER DEFAULT 0,
    valor_total_vendas DECIMAL(12,2) DEFAULT 0,
    ticket_medio DECIMAL(10,2) DEFAULT 0,
    
    -- Financeiro
    total_carnes_ativos INTEGER DEFAULT 0,
    valor_carteira_ativa DECIMAL(12,2) DEFAULT 0,
    parcelas_vencidas INTEGER DEFAULT 0,
    valor_inadimplencia DECIMAL(12,2) DEFAULT 0,
    taxa_inadimplencia DECIMAL(5,2) DEFAULT 0,
    
    -- Recebimentos
    parcelas_pagas INTEGER DEFAULT 0,
    valor_recebido DECIMAL(12,2) DEFAULT 0,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(data_referencia, loja)
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

-- Propostas
CREATE INDEX idx_propostas_cliente ON propostas.propostas_comerciais(cliente_uuid);
CREATE INDEX idx_propostas_status ON propostas.propostas_comerciais(status);
CREATE INDEX idx_propostas_data ON propostas.propostas_comerciais(data_proposta);
CREATE INDEX idx_propostas_numero ON propostas.propostas_comerciais(numero_proposta);

-- Carnês
CREATE INDEX idx_carnes_cliente ON financeiro.carnes(cliente_uuid);
CREATE INDEX idx_carnes_status ON financeiro.carnes(status);
CREATE INDEX idx_carnes_numero ON financeiro.carnes(numero_carne);

-- Parcelas
CREATE INDEX idx_parcelas_carne ON financeiro.parcelas(carne_uuid);
CREATE INDEX idx_parcelas_vencimento ON financeiro.parcelas(data_vencimento);
CREATE INDEX idx_parcelas_status ON financeiro.parcelas(status);
CREATE INDEX idx_parcelas_atrasadas ON financeiro.parcelas(data_vencimento, status) WHERE status = 'ATRASADO';

-- Documentos
CREATE INDEX idx_documentos_cliente ON documentos.documentos(cliente_uuid);
CREATE INDEX idx_documentos_tipo ON documentos.documentos(tipo);
CREATE INDEX idx_documentos_referencia ON documentos.documentos(referencia_uuid);

-- Pagamentos
CREATE INDEX idx_pagamentos_parcela ON financeiro.historico_pagamentos(parcela_uuid);
CREATE INDEX idx_pagamentos_data ON financeiro.historico_pagamentos(data_pagamento);
CREATE INDEX idx_pagamentos_cliente ON financeiro.historico_pagamentos(cliente_uuid);

-- ========================================
-- TRIGGERS AUTOMÁTICOS
-- ========================================

-- Atualizar status das parcelas automaticamente
CREATE OR REPLACE FUNCTION atualizar_status_parcelas()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualizar parcelas vencidas
    UPDATE financeiro.parcelas 
    SET status = 'ATRASADO'
    WHERE data_vencimento < CURRENT_DATE 
    AND status = 'PENDENTE'
    AND valor_pago = 0;
    
    -- Atualizar carnês inadimplentes
    UPDATE financeiro.carnes 
    SET status = 'INADIMPLENTE'
    WHERE id IN (
        SELECT DISTINCT carne_uuid 
        FROM financeiro.parcelas 
        WHERE status = 'ATRASADO'
        AND dias_atraso > 30
    );
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger diário para atualizar status
CREATE OR REPLACE FUNCTION trigger_atualizar_status_diario()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM atualizar_status_parcelas();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Calcular métricas automaticamente
CREATE OR REPLACE FUNCTION calcular_metricas_diarias(data_ref DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    loja_rec RECORD;
BEGIN
    -- Para cada loja
    FOR loja_rec IN SELECT DISTINCT loja FROM core.clientes WHERE loja IS NOT NULL LOOP
        
        INSERT INTO financeiro.metricas_diarias (
            data_referencia, loja,
            total_propostas, propostas_aprovadas, valor_total_vendas,
            total_carnes_ativos, valor_carteira_ativa,
            parcelas_vencidas, valor_inadimplencia,
            parcelas_pagas, valor_recebido
        )
        VALUES (
            data_ref, loja_rec.loja,
            
            -- Propostas do dia
            (SELECT COUNT(*) FROM propostas.propostas_comerciais p 
             JOIN core.clientes c ON p.cliente_uuid = c.uuid 
             WHERE DATE(p.data_proposta) = data_ref AND c.loja = loja_rec.loja),
            
            -- Propostas aprovadas
            (SELECT COUNT(*) FROM propostas.propostas_comerciais p 
             JOIN core.clientes c ON p.cliente_uuid = c.uuid 
             WHERE DATE(p.data_aprovacao) = data_ref AND c.loja = loja_rec.loja AND p.status = 'APROVADA'),
             
            -- Valor total vendas
            (SELECT COALESCE(SUM(valor_total), 0) FROM propostas.propostas_comerciais p 
             JOIN core.clientes c ON p.cliente_uuid = c.uuid 
             WHERE DATE(p.data_proposta) = data_ref AND c.loja = loja_rec.loja AND p.status = 'APROVADA'),
             
            -- Carnês ativos
            (SELECT COUNT(*) FROM financeiro.carnes ca 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE ca.status = 'ATIVO' AND c.loja = loja_rec.loja),
             
            -- Valor carteira ativa
            (SELECT COALESCE(SUM(valor_financiado), 0) FROM financeiro.carnes ca 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE ca.status = 'ATIVO' AND c.loja = loja_rec.loja),
             
            -- Parcelas vencidas
            (SELECT COUNT(*) FROM financeiro.parcelas pa 
             JOIN financeiro.carnes ca ON pa.carne_uuid = ca.id 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE pa.status = 'ATRASADO' AND c.loja = loja_rec.loja),
             
            -- Valor inadimplência
            (SELECT COALESCE(SUM(pa.valor_parcela), 0) FROM financeiro.parcelas pa 
             JOIN financeiro.carnes ca ON pa.carne_uuid = ca.id 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE pa.status = 'ATRASADO' AND c.loja = loja_rec.loja),
             
            -- Parcelas pagas hoje
            (SELECT COUNT(*) FROM financeiro.parcelas pa 
             JOIN financeiro.carnes ca ON pa.carne_uuid = ca.id 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE DATE(pa.data_pagamento) = data_ref AND c.loja = loja_rec.loja),
             
            -- Valor recebido hoje
            (SELECT COALESCE(SUM(pa.valor_pago), 0) FROM financeiro.parcelas pa 
             JOIN financeiro.carnes ca ON pa.carne_uuid = ca.id 
             JOIN core.clientes c ON ca.cliente_uuid = c.uuid 
             WHERE DATE(pa.data_pagamento) = data_ref AND c.loja = loja_rec.loja)
        )
        ON CONFLICT (data_referencia, loja) 
        DO UPDATE SET
            total_propostas = EXCLUDED.total_propostas,
            propostas_aprovadas = EXCLUDED.propostas_aprovadas,
            valor_total_vendas = EXCLUDED.valor_total_vendas,
            total_carnes_ativos = EXCLUDED.total_carnes_ativos,
            valor_carteira_ativa = EXCLUDED.valor_carteira_ativa,
            parcelas_vencidas = EXCLUDED.parcelas_vencidas,
            valor_inadimplencia = EXCLUDED.valor_inadimplencia,
            parcelas_pagas = EXCLUDED.parcelas_pagas,
            valor_recebido = EXCLUDED.valor_recebido,
            updated_at = NOW();
            
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- POLÍTICAS RLS (Row Level Security)
-- ========================================

-- Ativar RLS
ALTER TABLE propostas.propostas_comerciais ENABLE ROW LEVEL SECURITY;
ALTER TABLE financeiro.carnes ENABLE ROW LEVEL SECURITY;
ALTER TABLE financeiro.parcelas ENABLE ROW LEVEL SECURITY;
ALTER TABLE documentos.documentos ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajustar conforme necessário)
CREATE POLICY "Acesso total para autenticados" ON propostas.propostas_comerciais FOR ALL TO authenticated USING (true);
CREATE POLICY "Acesso total para autenticados" ON financeiro.carnes FOR ALL TO authenticated USING (true);
CREATE POLICY "Acesso total para autenticados" ON financeiro.parcelas FOR ALL TO authenticated USING (true);
CREATE POLICY "Acesso total para autenticados" ON documentos.documentos FOR ALL TO authenticated USING (true);

-- ========================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- ========================================

COMMENT ON SCHEMA financeiro IS 'Schema para controle financeiro completo - carnês, parcelas, pagamentos';
COMMENT ON SCHEMA propostas IS 'Schema para propostas comerciais e aprovações';
COMMENT ON SCHEMA documentos IS 'Schema para documentos e assinaturas digitais';

COMMENT ON TABLE propostas.propostas_comerciais IS 'Propostas comerciais com aprovação e controle';
COMMENT ON TABLE financeiro.carnes IS 'Carnês de financiamento próprio';
COMMENT ON TABLE financeiro.parcelas IS 'Parcelas dos carnês com controle de pagamento';
COMMENT ON TABLE documentos.documentos IS 'Documentos gerados no sistema';
COMMENT ON TABLE documentos.assinaturas IS 'Assinaturas digitais dos documentos';
COMMENT ON TABLE financeiro.metricas_diarias IS 'Métricas consolidadas por loja/dia';

-- ========================================
-- DADOS INICIAIS E TESTES
-- ========================================

-- Calcular métricas iniciais
SELECT calcular_metricas_diarias(CURRENT_DATE);

-- Executar atualização de status
SELECT atualizar_status_parcelas();

-- ========================================
-- VIEWS ÚTEIS PARA DASHBOARDS
-- ========================================

-- Dashboard principal
CREATE OR REPLACE VIEW financeiro.dashboard_principal AS
SELECT 
    -- Totais gerais
    COUNT(DISTINCT c.id) as total_carnes_ativos,
    SUM(c.valor_financiado) as valor_carteira_total,
    COUNT(DISTINCT p.id) FILTER (WHERE p.status = 'ATRASADO') as parcelas_atrasadas,
    SUM(p.valor_parcela) FILTER (WHERE p.status = 'ATRASADO') as valor_inadimplencia,
    
    -- Recebimentos hoje
    COUNT(DISTINCT p.id) FILTER (WHERE DATE(p.data_pagamento) = CURRENT_DATE) as parcelas_pagas_hoje,
    SUM(p.valor_pago) FILTER (WHERE DATE(p.data_pagamento) = CURRENT_DATE) as valor_recebido_hoje,
    
    -- Vencimentos próximos (próximos 7 dias)
    COUNT(DISTINCT p.id) FILTER (WHERE p.data_vencimento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days' AND p.status = 'PENDENTE') as vencimentos_proximos,
    SUM(p.valor_parcela) FILTER (WHERE p.data_vencimento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days' AND p.status = 'PENDENTE') as valor_vencimentos_proximos
    
FROM financeiro.carnes c
LEFT JOIN financeiro.parcelas p ON c.id = p.carne_uuid
WHERE c.status = 'ATIVO';

-- Top clientes inadimplentes
CREATE OR REPLACE VIEW financeiro.top_inadimplentes AS
SELECT 
    cl.nome,
    cl.telefone,
    cl.loja,
    COUNT(p.id) as parcelas_atrasadas,
    SUM(p.valor_parcela) as valor_devido,
    MAX(p.dias_atraso) as maior_atraso
FROM financeiro.parcelas p
JOIN financeiro.carnes c ON p.carne_uuid = c.id
JOIN core.clientes cl ON c.cliente_uuid = cl.uuid
WHERE p.status = 'ATRASADO'
GROUP BY cl.uuid, cl.nome, cl.telefone, cl.loja
ORDER BY valor_devido DESC
LIMIT 20;

-- Resumo por loja
CREATE OR REPLACE VIEW financeiro.resumo_por_loja AS
SELECT 
    cl.loja,
    COUNT(DISTINCT c.id) as carnes_ativos,
    SUM(c.valor_financiado) as carteira_ativa,
    COUNT(DISTINCT p.id) FILTER (WHERE p.status = 'ATRASADO') as parcelas_atrasadas,
    SUM(p.valor_parcela) FILTER (WHERE p.status = 'ATRASADO') as valor_inadimplencia,
    ROUND(
        (SUM(p.valor_parcela) FILTER (WHERE p.status = 'ATRASADO') * 100.0 / 
         NULLIF(SUM(c.valor_financiado), 0)), 2
    ) as taxa_inadimplencia_pct
FROM financeiro.carnes c
JOIN core.clientes cl ON c.cliente_uuid = cl.uuid
LEFT JOIN financeiro.parcelas p ON c.id = p.carne_uuid
WHERE c.status = 'ATIVO'
GROUP BY cl.loja
ORDER BY carteira_ativa DESC;

-- ========================================
-- FINALIZAÇÃO
-- ========================================

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ SCHEMA COMPLETO DE FINANCIAMENTO CRIADO!';
    RAISE NOTICE '';
    RAISE NOTICE '🏢 Funcionalidades disponíveis:';
    RAISE NOTICE '   • Propostas comerciais com aprovação';
    RAISE NOTICE '   • Carnês de financiamento próprio';
    RAISE NOTICE '   • Controle de parcelas e pagamentos';
    RAISE NOTICE '   • Documentos e assinaturas digitais';
    RAISE NOTICE '   • Métricas e dashboard em tempo real';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Views criadas:';
    RAISE NOTICE '   • financeiro.dashboard_principal';
    RAISE NOTICE '   • financeiro.top_inadimplentes';
    RAISE NOTICE '   • financeiro.resumo_por_loja';
    RAISE NOTICE '';
    RAISE NOTICE '🔄 Triggers automáticos:';
    RAISE NOTICE '   • Atualização de status de parcelas';
    RAISE NOTICE '   • Cálculo de métricas diárias';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Pronto para desenvolvimento do app!';
    RAISE NOTICE '';
END $$;