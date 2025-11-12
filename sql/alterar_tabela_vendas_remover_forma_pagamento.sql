-- =====================================================
-- ALTERAÇÕES NA TABELA vendas.vendas
-- =====================================================

-- PROBLEMA 1: Remover forma_pagamento (já existe tabela separada)
-- PROBLEMA 2: Separar data_venda de created_at para permitir dados históricos

BEGIN;

-- 1. Remove views que dependem da coluna forma_pagamento
-- IMPORTANTE: vendas.vendas é uma TABELA, public.vendas é uma VIEW
DROP VIEW IF EXISTS vendas.v_vendas_reais CASCADE;
DROP VIEW IF EXISTS public.vendas CASCADE;
DROP VIEW IF EXISTS public.vw_cliente_detalhes CASCADE;
DROP VIEW IF EXISTS public.vw_vendas CASCADE;
DROP VIEW IF EXISTS public.vw_venda_detalhes CASCADE;

-- 2. Remove índice de forma_pagamento
DROP INDEX IF EXISTS vendas.idx_vendas_forma_pagamento;

-- 3. Remove coluna forma_pagamento
ALTER TABLE vendas.vendas 
DROP COLUMN IF EXISTS forma_pagamento;

-- 3. Remove coluna forma_pagamento
ALTER TABLE vendas.vendas 
DROP COLUMN IF EXISTS forma_pagamento;

-- 4. Ajusta created_at para não ter default CURRENT_TIMESTAMP
-- Isso permite inserir com qualquer data (para dados históricos)
ALTER TABLE vendas.vendas 
ALTER COLUMN created_at DROP DEFAULT;

-- 5. Adiciona comentários nas colunas para documentar
COMMENT ON COLUMN vendas.vendas.data_venda IS 
'Data real em que a venda foi realizada (pode ser histórica de anos anteriores)';

COMMENT ON COLUMN vendas.vendas.created_at IS 
'Data/hora em que o registro foi INSERIDO no banco. Para dados históricos, será diferente de data_venda';

COMMIT;

-- =====================================================
-- RECRIAÇÃO DAS VIEWS (sem coluna forma_pagamento)
-- =====================================================

-- 1. VIEW: public.vendas (espelho da tabela, sem forma_pagamento)
CREATE OR REPLACE VIEW public.vendas AS
SELECT 
  id,
  numero_venda,
  cliente_id,
  loja_id,
  vendedor_id,
  data_venda,
  valor_total,
  valor_entrada,
  valor_restante,
  nome_cliente_temp,
  observacoes,
  status,
  cancelado,
  data_cancelamento,
  motivo_cancelamento,
  created_at,
  updated_at,
  created_by,
  updated_by,
  deleted_at,
  version,
  tipo_operacao,
  is_garantia,
  origem_venda,
  utm_source,
  utm_medium,
  utm_campaign,
  utm_content,
  campanha_id
FROM vendas.vendas;

-- 2. VIEW: vendas.v_vendas_reais (sem forma_pagamento)
CREATE OR REPLACE VIEW vendas.v_vendas_reais AS
SELECT 
  v.id,
  v.numero_venda,
  v.data_venda,
  v.tipo_operacao,
  v.valor_total,
  v.valor_entrada,
  v.valor_restante,
  l.nome AS loja,
  COALESCE(c.nome, v.nome_cliente_temp) AS cliente,
  ve.nome AS vendedor,
  v.status
FROM vendas.vendas v
JOIN core.lojas l ON v.loja_id = l.id
LEFT JOIN core.clientes c ON v.cliente_id = c.id
LEFT JOIN core.vendedores ve ON v.vendedor_id = ve.id
WHERE v.tipo_operacao = 'VENDA'
ORDER BY v.data_venda DESC;

-- 3. VIEW: public.vw_vendas (sem forma_pagamento)
CREATE OR REPLACE VIEW public.vw_vendas AS
SELECT 
  v.id,
  v.numero_venda,
  v.data_venda,
  v.valor_total,
  v.valor_entrada,
  v.valor_restante,
  v.status,
  v.cancelado,
  v.data_cancelamento,
  v.motivo_cancelamento,
  v.observacoes,
  v.tipo_operacao,
  v.is_garantia,
  v.origem_venda,
  v.created_at,
  v.cliente_id,
  COALESCE(c.nome, v.nome_cliente_temp) AS cliente_nome,
  c.cpf AS cliente_cpf,
  c.email AS cliente_email,
  v.loja_id,
  l.nome AS loja_nome,
  l.codigo AS loja_codigo,
  l.cidade AS loja_cidade,
  v.vendedor_id,
  vend.nome AS vendedor_nome,
  COALESCE((
    SELECT json_agg(json_build_object(
      'tipo_produto', i.tipo_produto,
      'descricao', i.descricao,
      'marca', i.marca,
      'modelo', i.modelo,
      'quantidade', i.quantidade,
      'valor_unitario', i.valor_unitario,
      'valor_desconto', COALESCE(i.valor_desconto, 0),
      'valor_total', i.valor_total
    ))
    FROM vendas.itens_venda i
    WHERE i.venda_id = v.id AND i.deleted_at IS NULL
  ), '[]'::json) AS itens,
  (SELECT COUNT(*) FROM vendas.itens_venda i WHERE i.venda_id = v.id AND i.deleted_at IS NULL) AS total_itens,
  (SELECT SUM(i.quantidade) FROM vendas.itens_venda i WHERE i.venda_id = v.id AND i.deleted_at IS NULL) AS quantidade_total_itens,
  (SELECT COUNT(*) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL) AS total_entregas,
  (SELECT COALESCE(SUM(e.valor_total), 0) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL) AS valor_total_entregas,
  (SELECT MIN(e.data_entrega) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL AND e.data_entrega >= CURRENT_DATE) AS proxima_entrega
FROM vendas.vendas v
LEFT JOIN core.clientes c ON c.id = v.cliente_id
LEFT JOIN core.lojas l ON l.id = v.loja_id
LEFT JOIN core.vendedores vend ON vend.id = v.vendedor_id
WHERE v.deleted_at IS NULL
ORDER BY v.data_venda DESC, v.created_at DESC;

-- 4. VIEW: public.vw_venda_detalhes (sem forma_pagamento)
CREATE OR REPLACE VIEW public.vw_venda_detalhes AS
SELECT 
  v.id AS venda_id,
  v.numero_venda,
  v.data_venda,
  v.valor_total,
  v.valor_entrada,
  v.valor_restante,
  v.status,
  v.cancelado,
  v.data_cancelamento,
  v.motivo_cancelamento,
  v.observacoes,
  v.tipo_operacao,
  v.is_garantia,
  v.origem_venda,
  v.utm_source,
  v.utm_medium,
  v.utm_campaign,
  v.utm_content,
  v.created_at,
  v.updated_at,
  json_build_object(
    'id', c.id,
    'nome', COALESCE(c.nome, v.nome_cliente_temp),
    'cpf', c.cpf,
    'email', c.email,
    'telefone', (
      SELECT t.numero 
      FROM core.telefones t 
      WHERE t.cliente_id = c.id AND t.deleted_at IS NULL AND t.ativo = true
      ORDER BY t.principal DESC NULLS LAST
      LIMIT 1
    ),
    'endereco', (
      SELECT e.logradouro || COALESCE(', ' || e.numero, '') || COALESCE(' - ' || e.cidade, '')
      FROM core.endereco_cliente e
      WHERE e.cliente_id = c.id AND e.deleted_at IS NULL
      ORDER BY e.principal DESC NULLS LAST
      LIMIT 1
    )
  ) AS cliente,
  json_build_object(
    'id', l.id,
    'nome', l.nome,
    'codigo', l.codigo,
    'cidade', l.cidade,
    'telefone', l.telefone
  ) AS loja,
  json_build_object(
    'id', vend.id,
    'nome', vend.nome,
    'email', vend.email
  ) AS vendedor,
  COALESCE((
    SELECT json_agg(items_subquery.item_json ORDER BY items_subquery.created_at)
    FROM (
      SELECT json_build_object(
        'id', i.id,
        'tipo_produto', i.tipo_produto,
        'descricao', i.descricao,
        'marca', i.marca,
        'modelo', i.modelo,
        'cor', i.cor,
        'tamanho', i.tamanho,
        'material', i.material,
        'codigo_produto', i.codigo_produto,
        'codigo_barras', i.codigo_barras,
        'quantidade', i.quantidade,
        'valor_unitario', i.valor_unitario,
        'valor_desconto', COALESCE(i.valor_desconto, 0),
        'valor_total', i.valor_total,
        'possui_estoque', i.possui_estoque,
        'requer_encomenda', i.requer_encomenda,
        'data_encomenda', i.data_encomenda,
        'data_prevista_chegada', i.data_prevista_chegada,
        'observacoes', i.observacoes
      ) AS item_json,
      i.created_at
      FROM vendas.itens_venda i
      WHERE i.venda_id = v.id AND i.deleted_at IS NULL
    ) items_subquery
  ), '[]'::json) AS itens,
  (SELECT COUNT(*) FROM vendas.itens_venda i WHERE i.venda_id = v.id AND i.deleted_at IS NULL) AS total_itens,
  (SELECT SUM(i.quantidade) FROM vendas.itens_venda i WHERE i.venda_id = v.id AND i.deleted_at IS NULL) AS quantidade_total,
  (SELECT SUM(COALESCE(i.valor_desconto, 0)) FROM vendas.itens_venda i WHERE i.venda_id = v.id AND i.deleted_at IS NULL) AS valor_total_descontos,
  COALESCE((
    SELECT json_agg(entregas_subquery.entrega_json ORDER BY entregas_subquery.data_entrega)
    FROM (
      SELECT json_build_object(
        'id', e.id,
        'data_entrega', e.data_entrega,
        'valor_total', e.valor_total,
        'parcela', e.parcela,
        'observacoes', e.observacoes
      ) AS entrega_json,
      e.data_entrega
      FROM vendas.entregas_carne e
      WHERE e.venda_id = v.id AND e.deleted_at IS NULL
    ) entregas_subquery
  ), '[]'::json) AS entregas,
  (SELECT COUNT(*) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL) AS total_entregas,
  (SELECT COUNT(*) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL AND e.data_entrega < CURRENT_DATE) AS entregas_passadas,
  (SELECT COUNT(*) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL AND e.data_entrega >= CURRENT_DATE) AS entregas_futuras,
  (SELECT COALESCE(SUM(e.valor_total), 0) FROM vendas.entregas_carne e WHERE e.venda_id = v.id AND e.deleted_at IS NULL) AS valor_total_entregas
FROM vendas.vendas v
LEFT JOIN core.clientes c ON c.id = v.cliente_id
LEFT JOIN core.lojas l ON l.id = v.loja_id
LEFT JOIN core.vendedores vend ON vend.id = v.vendedor_id
WHERE v.deleted_at IS NULL;

-- 5. VIEW: public.vw_cliente_detalhes (sem forma_pagamento na subquery)
CREATE OR REPLACE VIEW public.vw_cliente_detalhes AS
SELECT 
  c.id AS cliente_id,
  c.nome,
  c.nome_normalizado,
  c.cpf,
  c.rg,
  c.data_nascimento,
  c.sexo,
  c.email,
  c.status,
  c.origem,
  c.observacoes,
  COALESCE((
    SELECT json_agg(json_build_object(
      'id', t.id,
      'tipo', t.tipo,
      'numero', t.numero,
      'whatsapp', t.whatsapp,
      'principal', t.principal,
      'ativo', t.ativo
    ))
    FROM core.telefones t
    WHERE t.cliente_id = c.id AND t.deleted_at IS NULL
  ), '[]'::json) AS telefones,
  COALESCE((
    SELECT json_agg(json_build_object(
      'id', e.id,
      'tipo', e.tipo,
      'cep', e.cep,
      'logradouro', e.logradouro,
      'numero', e.numero,
      'complemento', e.complemento,
      'bairro', e.bairro,
      'cidade', e.cidade,
      'estado', e.estado,
      'pais', e.pais,
      'principal', e.principal
    ))
    FROM core.endereco_cliente e
    WHERE e.cliente_id = c.id AND e.deleted_at IS NULL
  ), '[]'::json) AS enderecos,
  COALESCE((
    SELECT json_agg(json_build_object(
      'id', v.id,
      'numero_venda', v.numero_venda,
      'data_venda', v.data_venda,
      'valor_total', v.valor_total,
      'valor_entrada', v.valor_entrada,
      'valor_restante', v.valor_restante,
      'status', v.status,
      'loja_nome', l.nome,
      'loja_codigo', l.codigo,
      'vendedor_nome', vend.nome
    ))
    FROM (
      SELECT * FROM vendas.vendas v1
      WHERE v1.cliente_id = c.id 
        AND v1.deleted_at IS NULL 
        AND (v1.cancelado = false OR v1.cancelado IS NULL)
      ORDER BY v1.data_venda DESC
      LIMIT 10
    ) v
    LEFT JOIN core.lojas l ON l.id = v.loja_id
    LEFT JOIN core.vendedores vend ON vend.id = v.vendedor_id
  ), '[]'::json) AS ultimas_vendas,
  (SELECT COUNT(*) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS total_vendas,
  (SELECT COALESCE(SUM(v.valor_total), 0) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS valor_total_compras,
  (SELECT COALESCE(SUM(v.valor_entrada), 0) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS valor_total_entradas,
  (SELECT COALESCE(SUM(v.valor_restante), 0) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS valor_total_pendente,
  (SELECT MIN(v.data_venda) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS primeira_compra,
  (SELECT MAX(v.data_venda) FROM vendas.vendas v WHERE v.cliente_id = c.id AND v.deleted_at IS NULL AND (v.cancelado = false OR v.cancelado IS NULL)) AS ultima_compra,
  (SELECT COUNT(*) FROM vendas.entregas_carne ec JOIN vendas.vendas v ON v.id = ec.venda_id WHERE v.cliente_id = c.id AND ec.deleted_at IS NULL AND ec.data_entrega >= CURRENT_DATE) AS entregas_pendentes
FROM core.clientes c
WHERE c.deleted_at IS NULL;

-- =====================================================
-- VERIFICAÇÕES APÓS ALTERAÇÕES
-- =====================================================

-- Verificar estrutura da tabela vendas
SELECT 
  column_name, 
  data_type, 
  column_default,
  is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vendas' 
  AND table_name = 'vendas'
  AND column_name IN ('data_venda', 'created_at', 'forma_pagamento')
ORDER BY ordinal_position;

-- =====================================================
-- EXEMPLO DE INSERT COM DADOS HISTÓRICOS
-- =====================================================

/*
-- Venda de 2023 sendo inserida em 2025
INSERT INTO vendas.vendas (
  numero_venda,
  cliente_id,
  loja_id,
  vendedor_id,
  data_venda,        -- Data REAL da venda (2023)
  valor_total,
  valor_entrada,
  created_at,        -- Data que você está inserindo no banco (2025)
  tipo_operacao,
  status
) VALUES (
  'OS-4028',
  'uuid-do-cliente',
  'uuid-da-loja',
  'uuid-do-vendedor',
  '2023-01-25'::DATE,      -- ← VENDA FOI EM 2023
  3450.00,
  345.00,
  NOW(),                   -- ← INSERINDO AGORA (2025)
  'VENDA',
  'ATIVO'
);
*/
