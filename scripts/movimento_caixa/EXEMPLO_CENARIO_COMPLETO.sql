-- ========================================
-- EXEMPLO PRÁTICO: CENÁRIO COMPLETO
-- Cliente: R$ 100 entrada + R$ 150 retirada + 7x carnê
-- ========================================

-- EXEMPLO: Criação de uma venda completa
-- Cliente compra óculos de R$ 600 total
-- R$ 100 entrada + R$ 150 na retirada + R$ 350 em 7x parcelas

-- 1. CRIAR A VENDA COMPLETA
SELECT pagamentos.criar_venda_completa(
    'uuid-do-cliente'::UUID,           -- cliente_uuid
    'uuid-da-loja'::UUID,              -- loja_uuid  
    'OS-2024-001234',                   -- numero_venda
    600.00,                             -- valor_total
    100.00,                             -- valor_entrada
    150.00,                             -- valor_retirada
    7                                   -- numero_parcelas (R$ 350 / 7 = R$ 50 cada)
) as venda_criada;

-- Resultado automático:
-- ✅ 1 registro em vendas_completas
-- ✅ 1 modalidade ENTRADA (R$ 100)
-- ✅ 1 modalidade RETIRADA (R$ 150) 
-- ✅ 7 modalidades PARCELA_CARNE (R$ 50 cada)
-- ✅ 1 registro em controle_quitacao

-- ========================================
-- 2. REGISTRAR PAGAMENTO DA ENTRADA
-- ========================================
-- Cliente pagou a entrada de R$ 100 no ato da compra

UPDATE pagamentos.modalidades_pagamento 
SET 
    valor_pago = 100.00,
    data_pagamento = CURRENT_DATE,
    status_modalidade = 'PAGO',
    forma_pagamento = 'CARTAO'
WHERE venda_uuid = 'uuid-da-venda' 
  AND tipo_modalidade = 'ENTRADA';

-- Inserir movimento no caixa
INSERT INTO pagamentos.movimentos_caixa (
    cliente_uuid, loja_uuid, venda_completa_uuid,
    data_movimento, timestamp_movimento,
    categoria_movimento, tipo_pagamento, subtipo,
    valor_movimento, historico_completo,
    is_entrada_venda
) VALUES (
    'uuid-do-cliente', 'uuid-da-loja', 'uuid-da-venda',
    CURRENT_DATE, NOW(),
    'pagamento_venda', 'CARTAO', 'ENTRADA',
    100.00, 'PAGAMENTO ENTRADA - OS-2024-001234',
    TRUE
);

-- ========================================
-- 3. REGISTRAR PAGAMENTO DA RETIRADA
-- ========================================
-- Cliente veio buscar e pagou R$ 150

UPDATE pagamentos.modalidades_pagamento 
SET 
    valor_pago = 150.00,
    data_pagamento = CURRENT_DATE + INTERVAL '15 days',
    status_modalidade = 'PAGO',
    forma_pagamento = 'DINHEIRO'
WHERE venda_uuid = 'uuid-da-venda' 
  AND tipo_modalidade = 'RETIRADA';

-- Inserir movimento no caixa
INSERT INTO pagamentos.movimentos_caixa (
    cliente_uuid, loja_uuid, venda_completa_uuid,
    data_movimento, timestamp_movimento,
    categoria_movimento, tipo_pagamento, subtipo,
    valor_movimento, historico_completo,
    is_entrada_venda
) VALUES (
    'uuid-do-cliente', 'uuid-da-loja', 'uuid-da-venda',
    CURRENT_DATE + INTERVAL '15 days', NOW(),
    'pagamento_venda', 'DINHEIRO', 'RETIRADA',
    150.00, 'PAGAMENTO RETIRADA - OS-2024-001234',
    TRUE
);

-- ========================================
-- 4. REGISTRAR PAGAMENTOS DO CARNÊ
-- ========================================
-- Cliente pagou a 1ª parcela de R$ 50

UPDATE pagamentos.modalidades_pagamento 
SET 
    valor_pago = 50.00,
    data_pagamento = CURRENT_DATE + INTERVAL '30 days',
    status_modalidade = 'PAGO',
    forma_pagamento = 'CARNE_LANCASTER'
WHERE venda_uuid = 'uuid-da-venda' 
  AND tipo_modalidade = 'PARCELA_CARNE' 
  AND sequencia = 1;

-- Inserir movimento no caixa
INSERT INTO pagamentos.movimentos_caixa (
    cliente_uuid, loja_uuid, venda_completa_uuid,
    data_movimento, timestamp_movimento,
    categoria_movimento, tipo_pagamento, subtipo,
    valor_movimento, historico_completo,
    is_pagamento_carne
) VALUES (
    'uuid-do-cliente', 'uuid-da-loja', 'uuid-da-venda',
    CURRENT_DATE + INTERVAL '30 days', NOW(),
    'pagamento_parcela', 'CARNE_LANCASTER', 'PARCELA',
    50.00, 'PARCELA 01/07 - OS-2024-001234',
    TRUE
);

-- ========================================
-- 5. CONSULTAS DE CONTROLE
-- ========================================

-- 5.1 Situação geral da venda
SELECT 
    numero_venda,
    cliente_nome,
    valor_total_venda,
    entrada_paga || '/' || valor_entrada as entrada_status,
    retirada_paga || '/' || valor_retirada as retirada_status,
    carne_pago || '/' || valor_financiado as carne_status,
    parcelas_pagas || '/' || numero_parcelas as parcelas_status,
    percentual_quitado || '%' as percentual,
    situacao_geral
FROM pagamentos.v_vendas_multimodais 
WHERE numero_venda = 'OS-2024-001234';

-- Resultado esperado:
-- numero_venda    | OS-2024-001234
-- cliente_nome    | João Silva  
-- valor_total     | 600.00
-- entrada_status  | 100.00/100.00 ✅
-- retirada_status | 150.00/150.00 ✅  
-- carne_status    | 50.00/350.00 ⏳
-- parcelas_status | 1/7 ⏳
-- percentual      | 50.00%
-- situacao_geral  | EM_DIA

-- 5.2 Próximas parcelas a vencer
SELECT 
    numero_venda,
    cliente_nome,
    'Parcela ' || sequencia || '/' || (
        SELECT numero_parcelas 
        FROM pagamentos.vendas_completas 
        WHERE id = venda_uuid
    ) as parcela,
    valor_pendente,
    data_vencimento,
    prioridade,
    CASE 
        WHEN dias_atraso > 0 THEN dias_atraso || ' dias em atraso'
        ELSE 'No prazo'
    END as situacao
FROM pagamentos.v_acoes_pendentes 
WHERE numero_venda = 'OS-2024-001234'
  AND tipo_modalidade = 'PARCELA_CARNE'
ORDER BY sequencia;

-- 5.3 Histórico completo de pagamentos
SELECT 
    data_movimento,
    subtipo,
    valor_movimento,
    tipo_pagamento,
    historico_completo
FROM pagamentos.movimentos_caixa 
WHERE venda_completa_uuid = 'uuid-da-venda'
ORDER BY data_movimento;

-- ========================================
-- 6. RELATÓRIOS GERENCIAIS
-- ========================================

-- 6.1 Vendas por modalidade (resumo geral)
SELECT 
    'TOTAL VENDAS' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_total_venda) as valor_total,
    AVG(valor_total_venda) as ticket_medio
FROM pagamentos.vendas_completas
WHERE data_venda >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'COM ENTRADA' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_entrada) as valor_total,
    AVG(valor_entrada) as ticket_medio
FROM pagamentos.vendas_completas  
WHERE valor_entrada > 0
  AND data_venda >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'COM RETIRADA' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_retirada) as valor_total,
    AVG(valor_retirada) as ticket_medio
FROM pagamentos.vendas_completas
WHERE valor_retirada > 0
  AND data_venda >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'COM CARNÊ' as categoria,
    COUNT(*) as quantidade,
    SUM(valor_financiado) as valor_total,
    AVG(valor_financiado) as ticket_medio
FROM pagamentos.vendas_completas
WHERE numero_parcelas > 0
  AND data_venda >= CURRENT_DATE - INTERVAL '30 days';

-- 6.2 Performance de cobrança
SELECT 
    situacao_geral,
    COUNT(*) as quantidade_vendas,
    SUM(valor_total_venda) as valor_total,
    AVG(percentual_quitado) as percentual_medio,
    SUM(valor_total_pendente) as valor_pendente
FROM pagamentos.controle_quitacao cq
JOIN pagamentos.vendas_completas vc ON cq.venda_uuid = vc.id
WHERE vc.data_venda >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY situacao_geral
ORDER BY quantidade_vendas DESC;