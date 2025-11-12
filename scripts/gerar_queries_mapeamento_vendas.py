#!/usr/bin/env python3
"""
Gerador de queries para mapear completamente o schema VENDAS
Cria queries SQL para análise completa das tabelas
"""

from pathlib import Path
from datetime import datetime

def gerar_queries_mapeamento_vendas():
    """Gera arquivo com todas as queries necessárias para mapear o schema vendas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    output_dir = base_dir / "database"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_queries = output_dir / f"MAPEAMENTO_SCHEMA_VENDAS_{timestamp}.sql"
    
    queries_sql = """
-- ========================================
-- MAPEAMENTO COMPLETO DO SCHEMA VENDAS
-- ========================================
-- Gerado em: {timestamp}
-- Objetivo: Mapear todas as tabelas, estruturas e dados
-- 
-- INSTRUÇÕES:
-- 1. Execute cada query separadamente no Supabase
-- 2. Salve cada resultado como CSV no diretório indicado
-- 3. Organize os arquivos para análise posterior
-- ========================================

-- ========================================
-- 1. LISTAR TODAS AS TABELAS DO SCHEMA VENDAS
-- ========================================
-- Salve como: tabelas_schema_vendas.csv

SELECT 
    table_name,
    table_type,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'vendas'
ORDER BY table_name;

| table_name                 | table_type | table_schema |
| -------------------------- | ---------- | ------------ |
| entregas_carne             | BASE TABLE | vendas       |
| entregas_os                | BASE TABLE | vendas       |
| formas_pagamento           | BASE TABLE | vendas       |
| formas_pagamento_venda     | BASE TABLE | vendas       |
| itens_venda                | BASE TABLE | vendas       |
| recebimentos_carne         | BASE TABLE | vendas       |
| restantes_entrada          | BASE TABLE | vendas       |
| restituicoes               | BASE TABLE | vendas       |
| v_entregas_pendentes       | VIEW       | vendas       |
| v_garantias                | VIEW       | vendas       |
| v_resumo_recebimentos      | VIEW       | vendas       |
| v_resumo_recebimentos_loja | VIEW       | vendas       |
| v_resumo_restituicoes      | VIEW       | vendas       |
| v_resumo_vendas_loja       | VIEW       | vendas       |
| v_saldo_a_receber          | VIEW       | vendas       |
| v_vendas_completas         | VIEW       | vendas       |
| v_vendas_completo          | VIEW       | vendas       |
| v_vendas_reais             | VIEW       | vendas       |
| vendas                     | BASE TABLE | vendas       |
| vendas_formas_pagamento    | BASE TABLE | vendas       |


-- ========================================
-- 2. ESTRUTURA COMPLETA DE TODAS AS TABELAS
-- ========================================
-- Salve como: estrutura_completa_vendas.csv

SELECT 
    table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'vendas'
ORDER BY table_name, ordinal_position;


| table_name                 | column_name                 | data_type                   | is_nullable | column_default             | character_maximum_length | numeric_precision | numeric_scale | ordinal_position |
| -------------------------- | --------------------------- | --------------------------- | ----------- | -------------------------- | ------------------------ | ----------------- | ------------- | ---------------- |
| entregas_carne             | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| entregas_carne             | venda_id                    | uuid                        | YES         | null                       | null                     | null              | null          | 2                |
| entregas_carne             | loja_id                     | uuid                        | NO          | null                       | null                     | null              | null          | 3                |
| entregas_carne             | os_numero                   | character varying           | YES         | null                       | 50                       | null              | null          | 4                |
| entregas_carne             | parcela                     | character varying           | YES         | null                       | 50                       | null              | null          | 5                |
| entregas_carne             | data_entrega                | date                        | NO          | null                       | null                     | null              | null          | 6                |
| entregas_carne             | valor_total                 | numeric                     | NO          | null                       | null                     | 12                | 2             | 7                |
| entregas_carne             | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 8                |
| entregas_carne             | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 9                |
| entregas_carne             | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 10               |
| entregas_carne             | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 11               |
| entregas_os                | id                          | uuid                        | NO          | gen_random_uuid()          | null                     | null              | null          | 1                |
| entregas_os                | venda_id                    | uuid                        | NO          | null                       | null                     | null              | null          | 2                |
| entregas_os                | vendedor_id                 | uuid                        | YES         | null                       | null                     | null              | null          | 3                |
| entregas_os                | data_entrega                | date                        | NO          | null                       | null                     | null              | null          | 4                |
| entregas_os                | tem_carne                   | boolean                     | YES         | false                      | null                     | null              | null          | 5                |
| entregas_os                | created_at                  | timestamp with time zone    | YES         | now()                      | null                     | null              | null          | 6                |
| entregas_os                | updated_at                  | timestamp with time zone    | YES         | now()                      | null                     | null              | null          | 7                |
| entregas_os                | deleted_at                  | timestamp with time zone    | YES         | null                       | null                     | null              | null          | 8                |
| formas_pagamento           | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| formas_pagamento           | codigo                      | character varying           | NO          | null                       | 20                       | null              | null          | 2                |
| formas_pagamento           | nome                        | character varying           | NO          | null                       | 100                      | null              | null          | 3                |
| formas_pagamento           | categoria                   | character varying           | YES         | null                       | 50                       | null              | null          | 4                |
| formas_pagamento           | ativo                       | boolean                     | YES         | true                       | null                     | null              | null          | 5                |
| formas_pagamento           | ordem_exibicao              | integer                     | YES         | null                       | null                     | 32                | 0             | 6                |
| formas_pagamento           | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 7                |
| formas_pagamento           | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 8                |
| formas_pagamento_venda     | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| formas_pagamento_venda     | venda_id                    | uuid                        | NO          | null                       | null                     | null              | null          | 2                |
| formas_pagamento_venda     | forma_pagamento             | USER-DEFINED                | NO          | null                       | null                     | null              | null          | 3                |
| formas_pagamento_venda     | valor                       | numeric                     | NO          | null                       | null                     | 12                | 2             | 4                |
| formas_pagamento_venda     | parcelas                    | integer                     | YES         | 1                          | null                     | 32                | 0             | 5                |
| formas_pagamento_venda     | numero_autorizacao          | character varying           | YES         | null                       | 50                       | null              | null          | 6                |
| formas_pagamento_venda     | numero_cheque               | character varying           | YES         | null                       | 50                       | null              | null          | 7                |
| formas_pagamento_venda     | banco                       | character varying           | YES         | null                       | 100                      | null              | null          | 8                |
| formas_pagamento_venda     | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 9                |
| formas_pagamento_venda     | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 10               |
| itens_venda                | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| itens_venda                | venda_id                    | uuid                        | NO          | null                       | null                     | null              | null          | 2                |
| itens_venda                | tipo_produto                | character varying           | NO          | null                       | 100                      | null              | null          | 3                |
| itens_venda                | descricao                   | character varying           | NO          | null                       | 300                      | null              | null          | 4                |
| itens_venda                | marca                       | character varying           | YES         | null                       | 100                      | null              | null          | 5                |
| itens_venda                | modelo                      | character varying           | YES         | null                       | 100                      | null              | null          | 6                |
| itens_venda                | codigo_produto              | character varying           | YES         | null                       | 100                      | null              | null          | 7                |
| itens_venda                | codigo_barras               | character varying           | YES         | null                       | 50                       | null              | null          | 8                |
| itens_venda                | cor                         | character varying           | YES         | null                       | 50                       | null              | null          | 9                |
| itens_venda                | tamanho                     | character varying           | YES         | null                       | 50                       | null              | null          | 10               |
| itens_venda                | material                    | character varying           | YES         | null                       | 100                      | null              | null          | 11               |
| itens_venda                | fornecedor                  | character varying           | YES         | null                       | 200                      | null              | null          | 12               |
| itens_venda                | codigo_fornecedor           | character varying           | YES         | null                       | 100                      | null              | null          | 13               |
| itens_venda                | quantidade                  | integer                     | NO          | 1                          | null                     | 32                | 0             | 14               |
| itens_venda                | valor_unitario              | numeric                     | NO          | null                       | null                     | 12                | 2             | 15               |
| itens_venda                | valor_desconto              | numeric                     | YES         | 0                          | null                     | 12                | 2             | 16               |
| itens_venda                | valor_total                 | numeric                     | YES         | null                       | null                     | 12                | 2             | 17               |
| itens_venda                | possui_estoque              | boolean                     | YES         | true                       | null                     | null              | null          | 18               |
| itens_venda                | requer_encomenda            | boolean                     | YES         | false                      | null                     | null              | null          | 19               |
| itens_venda                | data_encomenda              | date                        | YES         | null                       | null                     | null              | null          | 20               |
| itens_venda                | data_prevista_chegada       | date                        | YES         | null                       | null                     | null              | null          | 21               |
| itens_venda                | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 22               |
| itens_venda                | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 23               |
| itens_venda                | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 24               |
| itens_venda                | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 25               |
| itens_venda                | updated_by                  | character varying           | YES         | null                       | 100                      | null              | null          | 26               |
| recebimentos_carne         | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| recebimentos_carne         | venda_id                    | uuid                        | YES         | null                       | null                     | null              | null          | 2                |
| recebimentos_carne         | loja_id                     | uuid                        | NO          | null                       | null                     | null              | null          | 3                |
| recebimentos_carne         | os_numero                   | character varying           | YES         | null                       | 50                       | null              | null          | 4                |
| recebimentos_carne         | parcela_numero              | integer                     | NO          | null                       | null                     | 32                | 0             | 5                |
| recebimentos_carne         | data_recebimento            | date                        | NO          | null                       | null                     | null              | null          | 6                |
| recebimentos_carne         | valor_parcela               | numeric                     | NO          | null                       | null                     | 12                | 2             | 7                |
| recebimentos_carne         | forma_pagamento             | USER-DEFINED                | YES         | null                       | null                     | null              | null          | 8                |
| recebimentos_carne         | nome_cliente_temp           | character varying           | YES         | null                       | 200                      | null              | null          | 9                |
| recebimentos_carne         | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 10               |
| recebimentos_carne         | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 11               |
| recebimentos_carne         | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 12               |
| recebimentos_carne         | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 13               |
| recebimentos_carne         | parcela_total               | integer                     | YES         | null                       | null                     | 32                | 0             | 14               |
| recebimentos_carne         | cliente_id                  | uuid                        | YES         | null                       | null                     | null              | null          | 15               |
| restantes_entrada          | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| restantes_entrada          | venda_id                    | uuid                        | YES         | null                       | null                     | null              | null          | 2                |
| restantes_entrada          | loja_id                     | uuid                        | NO          | null                       | null                     | null              | null          | 3                |
| restantes_entrada          | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 4                |
| restantes_entrada          | data_registro               | date                        | NO          | null                       | null                     | null              | null          | 5                |
| restantes_entrada          | valor_venda                 | numeric                     | NO          | null                       | null                     | 12                | 2             | 6                |
| restantes_entrada          | valor_entrada               | numeric                     | NO          | null                       | null                     | 12                | 2             | 7                |
| restantes_entrada          | valor_restante              | numeric                     | YES         | null                       | null                     | 12                | 2             | 8                |
| restantes_entrada          | forma_pagamento             | USER-DEFINED                | YES         | null                       | null                     | null              | null          | 9                |
| restantes_entrada          | nome_cliente_temp           | character varying           | YES         | null                       | 200                      | null              | null          | 10               |
| restantes_entrada          | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 11               |
| restantes_entrada          | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 12               |
| restantes_entrada          | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 13               |
| restantes_entrada          | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 14               |
| restituicoes               | id                          | uuid                        | NO          | gen_random_uuid()          | null                     | null              | null          | 1                |
| restituicoes               | loja_id                     | uuid                        | NO          | null                       | null                     | null              | null          | 2                |
| restituicoes               | cliente_id                  | uuid                        | YES         | null                       | null                     | null              | null          | 3                |
| restituicoes               | data_restituicao            | date                        | NO          | null                       | null                     | null              | null          | 4                |
| restituicoes               | valor_restante              | numeric                     | YES         | 0                          | null                     | 12                | 2             | 5                |
| restituicoes               | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 6                |
| restituicoes               | info_adicional              | text                        | YES         | null                       | null                     | null              | null          | 7                |
| restituicoes               | arquivo_origem              | character varying           | YES         | null                       | 100                      | null              | null          | 8                |
| restituicoes               | linha_origem                | integer                     | YES         | null                       | null                     | 32                | 0             | 9                |
| restituicoes               | created_at                  | timestamp with time zone    | YES         | now()                      | null                     | null              | null          | 10               |
| restituicoes               | updated_at                  | timestamp with time zone    | YES         | now()                      | null                     | null              | null          | 11               |
| restituicoes               | deleted_at                  | timestamp with time zone    | YES         | null                       | null                     | null              | null          | 12               |
| v_entregas_pendentes       | venda_id                    | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_entregas_pendentes       | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_entregas_pendentes       | loja                        | character varying           | YES         | null                       | 100                      | null              | null          | 3                |
| v_entregas_pendentes       | data_entrega_os             | date                        | YES         | null                       | null                     | null              | null          | 4                |
| v_entregas_pendentes       | tem_carne                   | boolean                     | YES         | null                       | null                     | null              | null          | 5                |
| v_entregas_pendentes       | carne_pendente              | boolean                     | YES         | null                       | null                     | null              | null          | 6                |
| v_garantias                | id                          | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_garantias                | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_garantias                | data_venda                  | date                        | YES         | null                       | null                     | null              | null          | 3                |
| v_garantias                | loja                        | character varying           | YES         | null                       | 100                      | null              | null          | 4                |
| v_garantias                | cliente                     | character varying           | YES         | null                       | 200                      | null              | null          | 5                |
| v_garantias                | vendedor                    | character varying           | YES         | null                       | 200                      | null              | null          | 6                |
| v_garantias                | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 7                |
| v_resumo_recebimentos      | venda_id                    | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_resumo_recebimentos      | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_resumo_recebimentos      | loja                        | character varying           | YES         | null                       | 100                      | null              | null          | 3                |
| v_resumo_recebimentos      | parcelas_recebidas          | bigint                      | YES         | null                       | null                     | 64                | 0             | 4                |
| v_resumo_recebimentos      | total_parcelas              | integer                     | YES         | null                       | null                     | 32                | 0             | 5                |
| v_resumo_recebimentos      | valor_total_recebido        | numeric                     | YES         | null                       | null                     | null              | null          | 6                |
| v_resumo_recebimentos      | primeira_parcela            | date                        | YES         | null                       | null                     | null              | null          | 7                |
| v_resumo_recebimentos      | ultima_parcela              | date                        | YES         | null                       | null                     | null              | null          | 8                |
| v_resumo_recebimentos      | status_pagamento            | text                        | YES         | null                       | null                     | null              | null          | 9                |
| v_resumo_recebimentos_loja | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 1                |
| v_resumo_recebimentos_loja | loja_nome                   | character varying           | YES         | null                       | 100                      | null              | null          | 2                |
| v_resumo_recebimentos_loja | total_recebimentos          | bigint                      | YES         | null                       | null                     | 64                | 0             | 3                |
| v_resumo_recebimentos_loja | valor_total_recebido        | numeric                     | YES         | null                       | null                     | null              | null          | 4                |
| v_resumo_recebimentos_loja | mes_ano                     | timestamp with time zone    | YES         | null                       | null                     | null              | null          | 5                |
| v_resumo_restituicoes      | loja                        | character varying           | YES         | null                       | 100                      | null              | null          | 1                |
| v_resumo_restituicoes      | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 2                |
| v_resumo_restituicoes      | total_restituicoes          | bigint                      | YES         | null                       | null                     | 64                | 0             | 3                |
| v_resumo_restituicoes      | valor_total_restante        | numeric                     | YES         | null                       | null                     | null              | null          | 4                |
| v_resumo_restituicoes      | total_clientes              | bigint                      | YES         | null                       | null                     | 64                | 0             | 5                |
| v_resumo_restituicoes      | primeira_restituicao        | date                        | YES         | null                       | null                     | null              | null          | 6                |
| v_resumo_restituicoes      | ultima_restituicao          | date                        | YES         | null                       | null                     | null              | null          | 7                |
| v_resumo_vendas_loja       | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 1                |
| v_resumo_vendas_loja       | loja_nome                   | character varying           | YES         | null                       | 100                      | null              | null          | 2                |
| v_resumo_vendas_loja       | total_vendas                | bigint                      | YES         | null                       | null                     | 64                | 0             | 3                |
| v_resumo_vendas_loja       | valor_total                 | numeric                     | YES         | null                       | null                     | null              | null          | 4                |
| v_resumo_vendas_loja       | total_entradas              | numeric                     | YES         | null                       | null                     | null              | null          | 5                |
| v_resumo_vendas_loja       | total_restante              | numeric                     | YES         | null                       | null                     | null              | null          | 6                |
| v_resumo_vendas_loja       | ticket_medio                | numeric                     | YES         | null                       | null                     | null              | null          | 7                |
| v_resumo_vendas_loja       | mes_ano                     | timestamp with time zone    | YES         | null                       | null                     | null              | null          | 8                |
| v_saldo_a_receber          | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 1                |
| v_saldo_a_receber          | loja_nome                   | character varying           | YES         | null                       | 100                      | null              | null          | 2                |
| v_saldo_a_receber          | quantidade                  | bigint                      | YES         | null                       | null                     | 64                | 0             | 3                |
| v_saldo_a_receber          | saldo_total                 | numeric                     | YES         | null                       | null                     | null              | null          | 4                |
| v_saldo_a_receber          | saldo_medio                 | numeric                     | YES         | null                       | null                     | null              | null          | 5                |
| v_saldo_a_receber          | data_mais_antiga            | date                        | YES         | null                       | null                     | null              | null          | 6                |
| v_saldo_a_receber          | data_mais_recente           | date                        | YES         | null                       | null                     | null              | null          | 7                |
| v_vendas_completas         | id                          | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_vendas_completas         | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_vendas_completas         | data_venda                  | date                        | YES         | null                       | null                     | null              | null          | 3                |
| v_vendas_completas         | tipo_operacao               | character varying           | YES         | null                       | 20                       | null              | null          | 4                |
| v_vendas_completas         | is_garantia                 | boolean                     | YES         | null                       | null                     | null              | null          | 5                |
| v_vendas_completas         | valor_total                 | numeric                     | YES         | null                       | null                     | 12                | 2             | 6                |
| v_vendas_completas         | valor_entrada               | numeric                     | YES         | null                       | null                     | 12                | 2             | 7                |
| v_vendas_completas         | valor_restante              | numeric                     | YES         | null                       | null                     | 12                | 2             | 8                |
| v_vendas_completas         | status                      | USER-DEFINED                | YES         | null                       | null                     | null              | null          | 9                |
| v_vendas_completas         | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 10               |
| v_vendas_completas         | loja_nome                   | character varying           | YES         | null                       | 100                      | null              | null          | 11               |
| v_vendas_completas         | cliente_nome                | character varying           | YES         | null                       | 200                      | null              | null          | 12               |
| v_vendas_completas         | cliente_nome_completo       | character varying           | YES         | null                       | 200                      | null              | null          | 13               |
| v_vendas_completas         | cliente_cpf                 | character varying           | YES         | null                       | 14                       | null              | null          | 14               |
| v_vendas_completas         | vendedor_nome               | character varying           | YES         | null                       | 200                      | null              | null          | 15               |
| v_vendas_completas         | vendedor_codigo             | character varying           | YES         | null                       | 50                       | null              | null          | 16               |
| v_vendas_completas         | formas_pagamento            | text                        | YES         | null                       | null                     | null              | null          | 17               |
| v_vendas_completas         | quantidade_formas_pagamento | bigint                      | YES         | null                       | null                     | 64                | 0             | 18               |
| v_vendas_completas         | created_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 19               |
| v_vendas_completas         | updated_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 20               |
| v_vendas_completo          | id                          | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_vendas_completo          | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_vendas_completo          | codigo_completo             | text                        | YES         | null                       | null                     | null              | null          | 3                |
| v_vendas_completo          | cliente_id                  | uuid                        | YES         | null                       | null                     | null              | null          | 4                |
| v_vendas_completo          | cliente_nome                | character varying           | YES         | null                       | 200                      | null              | null          | 5                |
| v_vendas_completo          | loja_id                     | uuid                        | YES         | null                       | null                     | null              | null          | 6                |
| v_vendas_completo          | loja_codigo                 | character varying           | YES         | null                       | 20                       | null              | null          | 7                |
| v_vendas_completo          | loja_nome                   | character varying           | YES         | null                       | 100                      | null              | null          | 8                |
| v_vendas_completo          | vendedor_id                 | uuid                        | YES         | null                       | null                     | null              | null          | 9                |
| v_vendas_completo          | vendedor_nome               | character varying           | YES         | null                       | 200                      | null              | null          | 10               |
| v_vendas_completo          | data_venda                  | date                        | YES         | null                       | null                     | null              | null          | 11               |
| v_vendas_completo          | valor_total                 | numeric                     | YES         | null                       | null                     | 12                | 2             | 12               |
| v_vendas_completo          | valor_entrada               | numeric                     | YES         | null                       | null                     | 12                | 2             | 13               |
| v_vendas_completo          | valor_restante              | numeric                     | YES         | null                       | null                     | 12                | 2             | 14               |
| v_vendas_completo          | status                      | USER-DEFINED                | YES         | null                       | null                     | null              | null          | 15               |
| v_vendas_completo          | cancelado                   | boolean                     | YES         | null                       | null                     | null              | null          | 16               |
| v_vendas_completo          | created_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 17               |
| v_vendas_reais             | id                          | uuid                        | YES         | null                       | null                     | null              | null          | 1                |
| v_vendas_reais             | numero_venda                | character varying           | YES         | null                       | 50                       | null              | null          | 2                |
| v_vendas_reais             | data_venda                  | date                        | YES         | null                       | null                     | null              | null          | 3                |
| v_vendas_reais             | tipo_operacao               | character varying           | YES         | null                       | 20                       | null              | null          | 4                |
| v_vendas_reais             | forma_pagamento             | character varying           | YES         | null                       | 50                       | null              | null          | 5                |
| v_vendas_reais             | valor_total                 | numeric                     | YES         | null                       | null                     | 12                | 2             | 6                |
| v_vendas_reais             | valor_entrada               | numeric                     | YES         | null                       | null                     | 12                | 2             | 7                |
| v_vendas_reais             | valor_restante              | numeric                     | YES         | null                       | null                     | 12                | 2             | 8                |
| v_vendas_reais             | loja                        | character varying           | YES         | null                       | 100                      | null              | null          | 9                |
| v_vendas_reais             | cliente                     | character varying           | YES         | null                       | 200                      | null              | null          | 10               |
| v_vendas_reais             | vendedor                    | character varying           | YES         | null                       | 200                      | null              | null          | 11               |
| v_vendas_reais             | status                      | USER-DEFINED                | YES         | null                       | null                     | null              | null          | 12               |
| vendas                     | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| vendas                     | numero_venda                | character varying           | NO          | null                       | 50                       | null              | null          | 2                |
| vendas                     | cliente_id                  | uuid                        | YES         | null                       | null                     | null              | null          | 3                |
| vendas                     | loja_id                     | uuid                        | NO          | null                       | null                     | null              | null          | 4                |
| vendas                     | vendedor_id                 | uuid                        | YES         | null                       | null                     | null              | null          | 5                |
| vendas                     | data_venda                  | date                        | NO          | null                       | null                     | null              | null          | 6                |
| vendas                     | valor_total                 | numeric                     | NO          | null                       | null                     | 12                | 2             | 7                |
| vendas                     | valor_entrada               | numeric                     | YES         | 0                          | null                     | 12                | 2             | 8                |
| vendas                     | valor_restante              | numeric                     | YES         | null                       | null                     | 12                | 2             | 9                |
| vendas                     | nome_cliente_temp           | character varying           | YES         | null                       | 200                      | null              | null          | 10               |
| vendas                     | observacoes                 | text                        | YES         | null                       | null                     | null              | null          | 11               |
| vendas                     | status                      | USER-DEFINED                | YES         | 'ATIVO'::status_type       | null                     | null              | null          | 12               |
| vendas                     | cancelado                   | boolean                     | YES         | false                      | null                     | null              | null          | 13               |
| vendas                     | data_cancelamento           | timestamp without time zone | YES         | null                       | null                     | null              | null          | 14               |
| vendas                     | motivo_cancelamento         | text                        | YES         | null                       | null                     | null              | null          | 15               |
| vendas                     | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 16               |
| vendas                     | updated_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 17               |
| vendas                     | created_by                  | character varying           | YES         | null                       | 100                      | null              | null          | 18               |
| vendas                     | updated_by                  | character varying           | YES         | null                       | 100                      | null              | null          | 19               |
| vendas                     | deleted_at                  | timestamp without time zone | YES         | null                       | null                     | null              | null          | 20               |
| vendas                     | version                     | integer                     | YES         | 1                          | null                     | 32                | 0             | 21               |
| vendas                     | tipo_operacao               | character varying           | YES         | 'VENDA'::character varying | 20                       | null              | null          | 22               |
| vendas                     | is_garantia                 | boolean                     | YES         | null                       | null                     | null              | null          | 23               |
| vendas                     | forma_pagamento             | character varying           | YES         | null                       | 50                       | null              | null          | 24               |
| vendas_formas_pagamento    | id                          | uuid                        | NO          | uuid_generate_v4()         | null                     | null              | null          | 1                |
| vendas_formas_pagamento    | venda_id                    | uuid                        | NO          | null                       | null                     | null              | null          | 2                |
| vendas_formas_pagamento    | forma_pagamento_id          | uuid                        | NO          | null                       | null                     | null              | null          | 3                |
| vendas_formas_pagamento    | valor                       | numeric                     | NO          | null                       | null                     | 12                | 2             | 4                |
| vendas_formas_pagamento    | valor_entrada               | numeric                     | YES         | 0                          | null                     | 12                | 2             | 5                |
| vendas_formas_pagamento    | parcelas                    | integer                     | YES         | null                       | null                     | 32                | 0             | 6                |
| vendas_formas_pagamento    | observacao                  | text                        | YES         | null                       | null                     | null              | null          | 7                |
| vendas_formas_pagamento    | created_at                  | timestamp without time zone | YES         | CURRENT_TIMESTAMP          | null                     | null              | null          | 8                |


-- ========================================
-- 3. CONSTRAINTS E RELACIONAMENTOS
-- ========================================
-- Salve como: constraints_relacionamentos_vendas.csv

SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name 
    AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
LEFT JOIN information_schema.referential_constraints rc 
    ON tc.constraint_name = rc.constraint_name
WHERE tc.table_schema = 'vendas'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

| table_name              | constraint_name                                 | constraint_type | column_name        | foreign_table_name      | foreign_column_name | update_rule | delete_rule |
| ----------------------- | ----------------------------------------------- | --------------- | ------------------ | ----------------------- | ------------------- | ----------- | ----------- |
| entregas_carne          | 17891_18279_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_carne          | 17891_18279_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_carne          | 17891_18279_6_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_carne          | 17891_18279_7_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_carne          | entregas_carne_valor_total_check                | CHECK           | null               | entregas_carne          | valor_total         | null        | null        |
| entregas_carne          | entregas_carne_loja_id_fkey                     | FOREIGN KEY     | loja_id            | lojas                   | id                  | NO ACTION   | RESTRICT    |
| entregas_carne          | entregas_carne_venda_id_fkey                    | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | SET NULL    |
| entregas_carne          | entregas_carne_pkey                             | PRIMARY KEY     | id                 | entregas_carne          | id                  | null        | null        |
| entregas_carne          | entregas_carne_pkey                             | PRIMARY KEY     | id                 | entregas_carne          | id                  | null        | null        |
| entregas_os             | 17891_24642_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_os             | 17891_24642_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_os             | 17891_24642_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| entregas_os             | entregas_os_venda_id_fkey                       | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | CASCADE     |
| entregas_os             | entregas_os_vendedor_id_fkey                    | FOREIGN KEY     | vendedor_id        | vendedores              | id                  | NO ACTION   | SET NULL    |
| entregas_os             | entregas_os_pkey                                | PRIMARY KEY     | id                 | entregas_os             | id                  | null        | null        |
| entregas_os             | entregas_os_pkey                                | PRIMARY KEY     | id                 | entregas_os             | id                  | null        | null        |
| entregas_os             | uq_entrega_os_venda_data                        | UNIQUE          | venda_id           | entregas_os             | data_entrega        | null        | null        |
| entregas_os             | uq_entrega_os_venda_data                        | UNIQUE          | venda_id           | entregas_os             | venda_id            | null        | null        |
| entregas_os             | uq_entrega_os_venda_data                        | UNIQUE          | data_entrega       | entregas_os             | data_entrega        | null        | null        |
| entregas_os             | uq_entrega_os_venda_data                        | UNIQUE          | data_entrega       | entregas_os             | venda_id            | null        | null        |
| formas_pagamento        | 17891_21780_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento        | 17891_21780_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento        | 17891_21780_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento        | formas_pagamento_pkey                           | PRIMARY KEY     | id                 | formas_pagamento        | id                  | null        | null        |
| formas_pagamento        | formas_pagamento_codigo_key                     | UNIQUE          | codigo             | formas_pagamento        | codigo              | null        | null        |
| formas_pagamento_venda  | 17891_18231_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento_venda  | 17891_18231_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento_venda  | 17891_18231_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento_venda  | 17891_18231_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| formas_pagamento_venda  | formas_pagamento_venda_parcelas_check           | CHECK           | null               | formas_pagamento_venda  | parcelas            | null        | null        |
| formas_pagamento_venda  | formas_pagamento_venda_valor_check              | CHECK           | null               | formas_pagamento_venda  | valor               | null        | null        |
| formas_pagamento_venda  | formas_pagamento_venda_venda_id_fkey            | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | CASCADE     |
| formas_pagamento_venda  | formas_pagamento_venda_pkey                     | PRIMARY KEY     | id                 | formas_pagamento_venda  | id                  | null        | null        |
| formas_pagamento_venda  | formas_pagamento_venda_pkey                     | PRIMARY KEY     | id                 | formas_pagamento_venda  | id                  | null        | null        |
| itens_venda             | 17891_41934_14_not_null                         | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | 17891_41934_15_not_null                         | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | 17891_41934_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | 17891_41934_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | 17891_41934_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | 17891_41934_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| itens_venda             | itens_venda_quantidade_check                    | CHECK           | null               | itens_venda             | quantidade          | null        | null        |
| itens_venda             | itens_venda_tipo_produto_check                  | CHECK           | null               | itens_venda             | tipo_produto        | null        | null        |
| itens_venda             | itens_venda_valor_desconto_check                | CHECK           | null               | itens_venda             | valor_desconto      | null        | null        |
| itens_venda             | itens_venda_valor_unitario_check                | CHECK           | null               | itens_venda             | valor_unitario      | null        | null        |
| itens_venda             | itens_venda_venda_id_fkey                       | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | CASCADE     |
| itens_venda             | itens_venda_pkey                                | PRIMARY KEY     | id                 | itens_venda             | id                  | null        | null        |
| recebimentos_carne      | 17891_18249_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| recebimentos_carne      | 17891_18249_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| recebimentos_carne      | 17891_18249_5_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| recebimentos_carne      | 17891_18249_6_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| recebimentos_carne      | 17891_18249_7_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| recebimentos_carne      | recebimentos_carne_numero_parcela_check         | CHECK           | null               | recebimentos_carne      | parcela_numero      | null        | null        |
| recebimentos_carne      | recebimentos_carne_parcela_total_check          | CHECK           | null               | recebimentos_carne      | parcela_total       | null        | null        |
| recebimentos_carne      | recebimentos_carne_valor_parcela_check          | CHECK           | null               | recebimentos_carne      | valor_parcela       | null        | null        |
| recebimentos_carne      | recebimentos_carne_cliente_id_fkey              | FOREIGN KEY     | cliente_id         | clientes                | id                  | NO ACTION   | SET NULL    |
| recebimentos_carne      | recebimentos_carne_loja_id_fkey                 | FOREIGN KEY     | loja_id            | lojas                   | id                  | NO ACTION   | RESTRICT    |
| recebimentos_carne      | recebimentos_carne_venda_id_fkey                | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | SET NULL    |
| recebimentos_carne      | recebimentos_carne_pkey                         | PRIMARY KEY     | id                 | recebimentos_carne      | id                  | null        | null        |
| recebimentos_carne      | recebimentos_carne_pkey                         | PRIMARY KEY     | id                 | recebimentos_carne      | id                  | null        | null        |
| restantes_entrada       | 17891_18306_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restantes_entrada       | 17891_18306_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restantes_entrada       | 17891_18306_5_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restantes_entrada       | 17891_18306_6_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restantes_entrada       | 17891_18306_7_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restantes_entrada       | restantes_entrada_valor_entrada_check           | CHECK           | null               | restantes_entrada       | valor_entrada       | null        | null        |
| restantes_entrada       | restantes_entrada_valor_venda_check             | CHECK           | null               | restantes_entrada       | valor_venda         | null        | null        |
| restantes_entrada       | restantes_entrada_loja_id_fkey                  | FOREIGN KEY     | loja_id            | lojas                   | id                  | NO ACTION   | RESTRICT    |
| restantes_entrada       | restantes_entrada_venda_id_fkey                 | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | SET NULL    |
| restantes_entrada       | restantes_entrada_pkey                          | PRIMARY KEY     | id                 | restantes_entrada       | id                  | null        | null        |
| restituicoes            | 17891_24670_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restituicoes            | 17891_24670_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restituicoes            | 17891_24670_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| restituicoes            | restituicoes_valor_restante_check               | CHECK           | null               | restituicoes            | valor_restante      | null        | null        |
| restituicoes            | restituicoes_cliente_id_fkey                    | FOREIGN KEY     | cliente_id         | clientes                | id                  | NO ACTION   | SET NULL    |
| restituicoes            | restituicoes_loja_id_fkey                       | FOREIGN KEY     | loja_id            | lojas                   | id                  | NO ACTION   | CASCADE     |
| restituicoes            | restituicoes_pkey                               | PRIMARY KEY     | id                 | restituicoes            | id                  | null        | null        |
| vendas                  | 17891_18185_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas                  | 17891_18185_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas                  | 17891_18185_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas                  | 17891_18185_6_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas                  | 17891_18185_7_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas                  | chk_vendas_entrada_menor_total                  | CHECK           | null               | vendas                  | valor_total         | null        | null        |
| vendas                  | chk_vendas_entrada_menor_total                  | CHECK           | null               | vendas                  | valor_entrada       | null        | null        |
| vendas                  | vendas_tipo_operacao_check                      | CHECK           | null               | vendas                  | tipo_operacao       | null        | null        |
| vendas                  | vendas_valor_entrada_check                      | CHECK           | null               | vendas                  | valor_entrada       | null        | null        |
| vendas                  | vendas_valor_total_check                        | CHECK           | null               | vendas                  | valor_total         | null        | null        |
| vendas                  | vendas_cliente_id_fkey                          | FOREIGN KEY     | cliente_id         | clientes                | id                  | NO ACTION   | SET NULL    |
| vendas                  | vendas_loja_id_fkey                             | FOREIGN KEY     | loja_id            | lojas                   | id                  | NO ACTION   | RESTRICT    |
| vendas                  | vendas_vendedor_id_fkey                         | FOREIGN KEY     | vendedor_id        | vendedores              | id                  | NO ACTION   | SET NULL    |
| vendas                  | vendas_pkey                                     | PRIMARY KEY     | id                 | vendas                  | id                  | null        | null        |
| vendas                  | uq_vendas_loja_numero                           | UNIQUE          | loja_id            | vendas                  | numero_venda        | null        | null        |
| vendas                  | uq_vendas_loja_numero                           | UNIQUE          | numero_venda       | vendas                  | numero_venda        | null        | null        |
| vendas                  | uq_vendas_loja_numero                           | UNIQUE          | loja_id            | vendas                  | loja_id             | null        | null        |
| vendas                  | uq_vendas_loja_numero                           | UNIQUE          | numero_venda       | vendas                  | loja_id             | null        | null        |
| vendas_formas_pagamento | 17891_21791_1_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas_formas_pagamento | 17891_21791_2_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas_formas_pagamento | 17891_21791_3_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas_formas_pagamento | 17891_21791_4_not_null                          | CHECK           | null               | null                    | null                | null        | null        |
| vendas_formas_pagamento | chk_vfp_entrada_menor_valor                     | CHECK           | null               | vendas_formas_pagamento | valor               | null        | null        |
| vendas_formas_pagamento | chk_vfp_entrada_menor_valor                     | CHECK           | null               | vendas_formas_pagamento | valor_entrada       | null        | null        |
| vendas_formas_pagamento | vendas_formas_pagamento_parcelas_check          | CHECK           | null               | vendas_formas_pagamento | parcelas            | null        | null        |
| vendas_formas_pagamento | vendas_formas_pagamento_valor_check             | CHECK           | null               | vendas_formas_pagamento | valor               | null        | null        |
| vendas_formas_pagamento | vendas_formas_pagamento_valor_entrada_check     | CHECK           | null               | vendas_formas_pagamento | valor_entrada       | null        | null        |
| vendas_formas_pagamento | vendas_formas_pagamento_forma_pagamento_id_fkey | FOREIGN KEY     | forma_pagamento_id | formas_pagamento        | id                  | NO ACTION   | RESTRICT    |
| vendas_formas_pagamento | vendas_formas_pagamento_venda_id_fkey           | FOREIGN KEY     | venda_id           | vendas                  | id                  | NO ACTION   | CASCADE     |
| vendas_formas_pagamento | vendas_formas_pagamento_pkey                    | PRIMARY KEY     | id                 | vendas_formas_pagamento | id                  | null        | null        |
| vendas_formas_pagamento | vendas_formas_pagamento_pkey                    | PRIMARY KEY     | id                 | vendas_formas_pagamento | id                  | null        | null        |
| vendas_formas_pagamento | uq_venda_forma_pagamento                        | UNIQUE          | venda_id           | vendas_formas_pagamento | forma_pagamento_id  | null        | null        |
| vendas_formas_pagamento | uq_venda_forma_pagamento                        | UNIQUE          | venda_id           | vendas_formas_pagamento | venda_id            | null        | null        |
| vendas_formas_pagamento | uq_venda_forma_pagamento                        | UNIQUE          | forma_pagamento_id | vendas_formas_pagamento | forma_pagamento_id  | null        | null        |
| vendas_formas_pagamento | uq_venda_forma_pagamento                        | UNIQUE          | forma_pagamento_id | vendas_formas_pagamento | venda_id            | null        | null        |



-- ========================================
-- 4. ÍNDICES E PERFORMANCE
-- ========================================
-- Salve como: indices_vendas.csv

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'vendas'
ORDER BY tablename, indexname;


| schemaname | tablename               | indexname                       | indexdef                                                                                                                                 |
| ---------- | ----------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| vendas     | entregas_carne          | entregas_carne_pkey             | CREATE UNIQUE INDEX entregas_carne_pkey ON vendas.entregas_carne USING btree (id)                                                        |
| vendas     | entregas_carne          | idx_entregas_carne_data         | CREATE INDEX idx_entregas_carne_data ON vendas.entregas_carne USING btree (data_entrega)                                                 |
| vendas     | entregas_carne          | idx_entregas_carne_deleted_at   | CREATE INDEX idx_entregas_carne_deleted_at ON vendas.entregas_carne USING btree (deleted_at) WHERE (deleted_at IS NULL)                  |
| vendas     | entregas_carne          | idx_entregas_carne_loja_id      | CREATE INDEX idx_entregas_carne_loja_id ON vendas.entregas_carne USING btree (loja_id)                                                   |
| vendas     | entregas_carne          | idx_entregas_carne_os_numero    | CREATE INDEX idx_entregas_carne_os_numero ON vendas.entregas_carne USING btree (os_numero)                                               |
| vendas     | entregas_carne          | idx_entregas_carne_venda_id     | CREATE INDEX idx_entregas_carne_venda_id ON vendas.entregas_carne USING btree (venda_id)                                                 |
| vendas     | entregas_os             | entregas_os_pkey                | CREATE UNIQUE INDEX entregas_os_pkey ON vendas.entregas_os USING btree (id)                                                              |
| vendas     | entregas_os             | idx_entregas_os_carne           | CREATE INDEX idx_entregas_os_carne ON vendas.entregas_os USING btree (tem_carne) WHERE (tem_carne = true)                                |
| vendas     | entregas_os             | idx_entregas_os_data            | CREATE INDEX idx_entregas_os_data ON vendas.entregas_os USING btree (data_entrega)                                                       |
| vendas     | entregas_os             | idx_entregas_os_deleted_at      | CREATE INDEX idx_entregas_os_deleted_at ON vendas.entregas_os USING btree (deleted_at) WHERE (deleted_at IS NULL)                        |
| vendas     | entregas_os             | idx_entregas_os_venda           | CREATE INDEX idx_entregas_os_venda ON vendas.entregas_os USING btree (venda_id)                                                          |
| vendas     | entregas_os             | idx_entregas_os_vendedor        | CREATE INDEX idx_entregas_os_vendedor ON vendas.entregas_os USING btree (vendedor_id)                                                    |
| vendas     | entregas_os             | uq_entrega_os_venda_data        | CREATE UNIQUE INDEX uq_entrega_os_venda_data ON vendas.entregas_os USING btree (venda_id, data_entrega)                                  |
| vendas     | formas_pagamento        | formas_pagamento_codigo_key     | CREATE UNIQUE INDEX formas_pagamento_codigo_key ON vendas.formas_pagamento USING btree (codigo)                                          |
| vendas     | formas_pagamento        | formas_pagamento_pkey           | CREATE UNIQUE INDEX formas_pagamento_pkey ON vendas.formas_pagamento USING btree (id)                                                    |
| vendas     | formas_pagamento_venda  | formas_pagamento_venda_pkey     | CREATE UNIQUE INDEX formas_pagamento_venda_pkey ON vendas.formas_pagamento_venda USING btree (id)                                        |
| vendas     | formas_pagamento_venda  | idx_formas_pagamento_deleted_at | CREATE INDEX idx_formas_pagamento_deleted_at ON vendas.formas_pagamento_venda USING btree (deleted_at) WHERE (deleted_at IS NULL)        |
| vendas     | formas_pagamento_venda  | idx_formas_pagamento_forma      | CREATE INDEX idx_formas_pagamento_forma ON vendas.formas_pagamento_venda USING btree (forma_pagamento)                                   |
| vendas     | formas_pagamento_venda  | idx_formas_pagamento_venda_id   | CREATE INDEX idx_formas_pagamento_venda_id ON vendas.formas_pagamento_venda USING btree (venda_id)                                       |
| vendas     | itens_venda             | idx_itens_venda_codigo          | CREATE INDEX idx_itens_venda_codigo ON vendas.itens_venda USING btree (codigo_produto)                                                   |
| vendas     | itens_venda             | idx_itens_venda_deleted_at      | CREATE INDEX idx_itens_venda_deleted_at ON vendas.itens_venda USING btree (deleted_at) WHERE (deleted_at IS NULL)                        |
| vendas     | itens_venda             | idx_itens_venda_marca           | CREATE INDEX idx_itens_venda_marca ON vendas.itens_venda USING btree (marca)                                                             |
| vendas     | itens_venda             | idx_itens_venda_tipo            | CREATE INDEX idx_itens_venda_tipo ON vendas.itens_venda USING btree (tipo_produto)                                                       |
| vendas     | itens_venda             | idx_itens_venda_venda_id        | CREATE INDEX idx_itens_venda_venda_id ON vendas.itens_venda USING btree (venda_id)                                                       |
| vendas     | itens_venda             | itens_venda_pkey                | CREATE UNIQUE INDEX itens_venda_pkey ON vendas.itens_venda USING btree (id)                                                              |
| vendas     | recebimentos_carne      | idx_recebimentos_cliente_id     | CREATE INDEX idx_recebimentos_cliente_id ON vendas.recebimentos_carne USING btree (cliente_id)                                           |
| vendas     | recebimentos_carne      | idx_recebimentos_data           | CREATE INDEX idx_recebimentos_data ON vendas.recebimentos_carne USING btree (data_recebimento)                                           |
| vendas     | recebimentos_carne      | idx_recebimentos_data_loja      | CREATE INDEX idx_recebimentos_data_loja ON vendas.recebimentos_carne USING btree (data_recebimento, loja_id)                             |
| vendas     | recebimentos_carne      | idx_recebimentos_deleted_at     | CREATE INDEX idx_recebimentos_deleted_at ON vendas.recebimentos_carne USING btree (deleted_at) WHERE (deleted_at IS NULL)                |
| vendas     | recebimentos_carne      | idx_recebimentos_loja_id        | CREATE INDEX idx_recebimentos_loja_id ON vendas.recebimentos_carne USING btree (loja_id)                                                 |
| vendas     | recebimentos_carne      | idx_recebimentos_os_numero      | CREATE INDEX idx_recebimentos_os_numero ON vendas.recebimentos_carne USING btree (os_numero)                                             |
| vendas     | recebimentos_carne      | idx_recebimentos_parcela        | CREATE INDEX idx_recebimentos_parcela ON vendas.recebimentos_carne USING btree (parcela_numero)                                          |
| vendas     | recebimentos_carne      | idx_recebimentos_venda_id       | CREATE INDEX idx_recebimentos_venda_id ON vendas.recebimentos_carne USING btree (venda_id)                                               |
| vendas     | recebimentos_carne      | recebimentos_carne_pkey         | CREATE UNIQUE INDEX recebimentos_carne_pkey ON vendas.recebimentos_carne USING btree (id)                                                |
| vendas     | restantes_entrada       | idx_restantes_data              | CREATE INDEX idx_restantes_data ON vendas.restantes_entrada USING btree (data_registro)                                                  |
| vendas     | restantes_entrada       | idx_restantes_deleted_at        | CREATE INDEX idx_restantes_deleted_at ON vendas.restantes_entrada USING btree (deleted_at) WHERE (deleted_at IS NULL)                    |
| vendas     | restantes_entrada       | idx_restantes_loja_id           | CREATE INDEX idx_restantes_loja_id ON vendas.restantes_entrada USING btree (loja_id)                                                     |
| vendas     | restantes_entrada       | idx_restantes_numero_venda      | CREATE INDEX idx_restantes_numero_venda ON vendas.restantes_entrada USING btree (numero_venda)                                           |
| vendas     | restantes_entrada       | idx_restantes_valor_restante    | CREATE INDEX idx_restantes_valor_restante ON vendas.restantes_entrada USING btree (valor_restante) WHERE (valor_restante > (0)::numeric) |
| vendas     | restantes_entrada       | idx_restantes_venda_id          | CREATE INDEX idx_restantes_venda_id ON vendas.restantes_entrada USING btree (venda_id)                                                   |
| vendas     | restantes_entrada       | restantes_entrada_pkey          | CREATE UNIQUE INDEX restantes_entrada_pkey ON vendas.restantes_entrada USING btree (id)                                                  |
| vendas     | restituicoes            | idx_restituicoes_arquivo        | CREATE INDEX idx_restituicoes_arquivo ON vendas.restituicoes USING btree (arquivo_origem)                                                |
| vendas     | restituicoes            | idx_restituicoes_cliente        | CREATE INDEX idx_restituicoes_cliente ON vendas.restituicoes USING btree (cliente_id)                                                    |
| vendas     | restituicoes            | idx_restituicoes_data           | CREATE INDEX idx_restituicoes_data ON vendas.restituicoes USING btree (data_restituicao)                                                 |
| vendas     | restituicoes            | idx_restituicoes_deleted_at     | CREATE INDEX idx_restituicoes_deleted_at ON vendas.restituicoes USING btree (deleted_at) WHERE (deleted_at IS NULL)                      |
| vendas     | restituicoes            | idx_restituicoes_loja           | CREATE INDEX idx_restituicoes_loja ON vendas.restituicoes USING btree (loja_id)                                                          |
| vendas     | restituicoes            | idx_restituicoes_valor          | CREATE INDEX idx_restituicoes_valor ON vendas.restituicoes USING btree (valor_restante) WHERE (valor_restante > (0)::numeric)            |
| vendas     | restituicoes            | restituicoes_pkey               | CREATE UNIQUE INDEX restituicoes_pkey ON vendas.restituicoes USING btree (id)                                                            |
| vendas     | vendas                  | idx_vendas_cancelado            | CREATE INDEX idx_vendas_cancelado ON vendas.vendas USING btree (cancelado) WHERE (cancelado = false)                                     |
| vendas     | vendas                  | idx_vendas_cliente_id           | CREATE INDEX idx_vendas_cliente_id ON vendas.vendas USING btree (cliente_id)                                                             |
| vendas     | vendas                  | idx_vendas_data_venda           | CREATE INDEX idx_vendas_data_venda ON vendas.vendas USING btree (data_venda)                                                             |
| vendas     | vendas                  | idx_vendas_data_venda_loja      | CREATE INDEX idx_vendas_data_venda_loja ON vendas.vendas USING btree (data_venda, loja_id)                                               |
| vendas     | vendas                  | idx_vendas_deleted_at           | CREATE INDEX idx_vendas_deleted_at ON vendas.vendas USING btree (deleted_at) WHERE (deleted_at IS NULL)                                  |
| vendas     | vendas                  | idx_vendas_forma_pagamento      | CREATE INDEX idx_vendas_forma_pagamento ON vendas.vendas USING btree (forma_pagamento) WHERE (forma_pagamento IS NOT NULL)               |
| vendas     | vendas                  | idx_vendas_garantias            | CREATE INDEX idx_vendas_garantias ON vendas.vendas USING btree (is_garantia) WHERE (is_garantia = true)                                  |
| vendas     | vendas                  | idx_vendas_is_garantia          | CREATE INDEX idx_vendas_is_garantia ON vendas.vendas USING btree (is_garantia) WHERE (is_garantia = true)                                |
| vendas     | vendas                  | idx_vendas_loja_id              | CREATE INDEX idx_vendas_loja_id ON vendas.vendas USING btree (loja_id)                                                                   |
| vendas     | vendas                  | idx_vendas_numero               | CREATE INDEX idx_vendas_numero ON vendas.vendas USING btree (numero_venda)                                                               |
| vendas     | vendas                  | idx_vendas_status               | CREATE INDEX idx_vendas_status ON vendas.vendas USING btree (status)                                                                     |
| vendas     | vendas                  | idx_vendas_tipo_operacao        | CREATE INDEX idx_vendas_tipo_operacao ON vendas.vendas USING btree (tipo_operacao)                                                       |
| vendas     | vendas                  | idx_vendas_valor_total          | CREATE INDEX idx_vendas_valor_total ON vendas.vendas USING btree (valor_total)                                                           |
| vendas     | vendas                  | idx_vendas_vendedor_id          | CREATE INDEX idx_vendas_vendedor_id ON vendas.vendas USING btree (vendedor_id)                                                           |
| vendas     | vendas                  | uq_vendas_loja_numero           | CREATE UNIQUE INDEX uq_vendas_loja_numero ON vendas.vendas USING btree (loja_id, numero_venda)                                           |
| vendas     | vendas                  | vendas_pkey                     | CREATE UNIQUE INDEX vendas_pkey ON vendas.vendas USING btree (id)                                                                        |
| vendas     | vendas_formas_pagamento | idx_vfp_forma_pagamento_id      | CREATE INDEX idx_vfp_forma_pagamento_id ON vendas.vendas_formas_pagamento USING btree (forma_pagamento_id)                               |
| vendas     | vendas_formas_pagamento | idx_vfp_venda_id                | CREATE INDEX idx_vfp_venda_id ON vendas.vendas_formas_pagamento USING btree (venda_id)                                                   |
| vendas     | vendas_formas_pagamento | uq_venda_forma_pagamento        | CREATE UNIQUE INDEX uq_venda_forma_pagamento ON vendas.vendas_formas_pagamento USING btree (venda_id, forma_pagamento_id)                |
| vendas     | vendas_formas_pagamento | vendas_formas_pagamento_pkey    | CREATE UNIQUE INDEX vendas_formas_pagamento_pkey ON vendas.vendas_formas_pagamento USING btree (id)                                      |


-- ========================================
-- 5. CONTAGEM DE REGISTROS EM TODAS AS TABELAS
-- ========================================
-- Execute e salve como: contagem_registros_vendas.csv
-- NOTA: Execute cada SELECT separadamente e compile o resultado

-- Tabelas principais conhecidas:
SELECT 'vendas' as tabela, COUNT(*) as registros, 
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.vendas;


| tabela | registros | data_mais_antiga    | data_mais_recente   |
| ------ | --------- | ------------------- | ------------------- |
| vendas | 15281     | 2025-11-04 02:07:46 | 2025-11-04 14:31:16 |


SELECT 'formas_pagamento' as tabela, COUNT(*) as registros,
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.formas_pagamento;


| tabela           | registros | data_mais_antiga          | data_mais_recente         |
| ---------------- | --------- | ------------------------- | ------------------------- |
| formas_pagamento | 9         | 2025-10-13 01:57:11.61134 | 2025-10-13 01:57:11.61134 |



SELECT 'vendas_formas_pagamento' as tabela, COUNT(*) as registros,
       MIN(created_at) as data_mais_antiga, 
       MAX(created_at) as data_mais_recente
FROM vendas.vendas_formas_pagamento;

| tabela                  | registros | data_mais_antiga           | data_mais_recente          |
| ----------------------- | --------- | -------------------------- | -------------------------- |
| vendas_formas_pagamento | 19737     | 2025-11-04 19:45:14.699578 | 2025-11-04 19:45:58.742821 |


-- ========================================
-- 6. VERIFICAR OUTRAS TABELAS (se existirem)
-- ========================================
-- Execute apenas as que existirem baseado no resultado da query 1

-- Possíveis tabelas que podem existir:
/*
SELECT 'clientes' as tabela, COUNT(*) as registros FROM vendas.clientes;
SELECT 'enderecos' as tabela, COUNT(*) as registros FROM vendas.enderecos;
SELECT 'telefones' as tabela, COUNT(*) as registros FROM vendas.telefones;
SELECT 'lojas' as tabela, COUNT(*) as registros FROM vendas.lojas;
SELECT 'vendedores' as tabela, COUNT(*) as registros FROM vendas.vendedores;
SELECT 'parcelas' as tabela, COUNT(*) as registros FROM vendas.parcelas;
SELECT 'pagamentos' as tabela, COUNT(*) as registros FROM vendas.pagamentos;
SELECT 'produtos' as tabela, COUNT(*) as registros FROM vendas.produtos;
SELECT 'vendas_itens' as tabela, COUNT(*) as registros FROM vendas.vendas_itens;
SELECT 'auditoria' as tabela, COUNT(*) as registros FROM vendas.auditoria;
*/

-- ========================================
-- 7. AMOSTRA DE DADOS DAS TABELAS PRINCIPAIS
-- ========================================
-- Salve como: amostra_vendas.csv

SELECT 
    id,
    numero_venda,
    cliente_id,
    loja_id,
    vendedor_id,
    data_venda,
    valor_total,
    status,
    created_at
FROM vendas.vendas 
ORDER BY created_at DESC 
LIMIT 100;


| id                                   | numero_venda | cliente_id                           | loja_id                              | vendedor_id                          | data_venda | valor_total | status | created_at |
| ------------------------------------ | ------------ | ------------------------------------ | ------------------------------------ | ------------------------------------ | ---------- | ----------- | ------ | ---------- |
| 9c7e0580-0a95-40be-96da-7087cfd75efb | 202249.0     | bc60f4ba-9743-4a3f-92fc-27fc15aeed01 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 149.00      | ATIVO  | null       |
| 22fd626c-0f7f-4e05-83c6-2fc356270610 | 202273.0     | b7660f1f-263e-435c-b5e6-abd2c42783e0 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-26 | 199.00      | ATIVO  | null       |
| 6c87af10-4b6d-45a3-baf3-1aa0be055424 | 202212.0     | bb2f47bf-c8c5-48a1-8fc9-3e931505a21e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 1050.00     | ATIVO  | null       |
| 2458ccb6-009b-47de-a4cd-349736b77380 | 202245.0     | 89073fb8-5d03-4ca2-96fb-24313283f0f3 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 430.00      | ATIVO  | null       |
| 19d91e87-484e-45a5-bb5c-2c51723d87ef | 202225.0     | 314d9c74-d6d0-41dc-97db-d0b5ef23c50b | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-13 | 942.00      | ATIVO  | null       |
| e798e022-578d-4cd2-9fe4-dc0708ae6560 | 202275.0     | b80eb243-9757-45f5-b40d-799c9bd0bf20 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-26 | 150.00      | ATIVO  | null       |
| 149ed42e-d52e-408a-9a40-5453b5532041 | 202196.0     | 49dbd704-d5fa-41cf-9a5d-a9e4c9c9680c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-06 | 550.00      | ATIVO  | null       |
| e02ce7d8-5043-49ff-a8c5-e6aae2f84282 | 202189.0     | 44f60382-803d-4673-81d6-99e690e4080e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 210.57      | ATIVO  | null       |
| ca7a8c1a-d3d9-445b-bc8d-2d3706177b59 | 202233.0     | 55911b7b-386f-4fcd-86ae-7fba95b11bde | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 99.99       | ATIVO  | null       |
| c1b8251c-73c5-4cde-81bd-2526fdbf6a6d | 202247.0     | 29a55484-412c-4066-9027-b01e78591fbf | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 400.00      | ATIVO  | null       |
| cfb816a3-6500-4271-af56-99a3d70483e7 | 202251.0     | 21b13ee2-e950-4e23-8e0c-18a78090e79c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-19 | 100.00      | ATIVO  | null       |
| 94fafec4-7db6-4ea9-8b76-9b67f9413cfb | 202211.0     | aff542b6-864e-4c2f-8c41-0734cc9459c2 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 298.00      | ATIVO  | null       |
| 0951054d-059b-4ddd-b41d-75aa39820e79 | 202263.0     | 7dcb3e46-2e18-44b1-a479-0cdf8363ec06 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-23 | 765.00      | ATIVO  | null       |
| 33fc4136-8676-4000-ba9b-02d19bb1526b | 202260.0     | 7bdeed7f-8307-4404-bbac-1fd0436d3c6e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-21 | 249.00      | ATIVO  | null       |
| 0afe50f8-ec05-4364-9a63-24e82501a5e4 | 202181.0     | f0890e04-0e8c-4be4-95c1-20af0a8733ac | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 220.00      | ATIVO  | null       |
| 686a38b1-ce8e-4fc8-b44a-45c51cae3219 | 202192.0     | 1ea0aae1-66cd-4b76-b2e4-c13ca5a01cdf | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 99.00       | ATIVO  | null       |
| d1a6ed90-d87c-465e-aa84-be31c3bfad03 | 202202.0     | 0a4c84df-a0e6-4f33-bd17-13748e5b7bee | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 1908.00     | ATIVO  | null       |
| fce81497-de08-4000-8bb6-f5eda58bf370 | 202208.0     | d2135fb8-28d8-44b7-9be0-5584aa11e274 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-09 | 240.00      | ATIVO  | null       |
| 58da9ae1-7420-4335-b20a-6b9ccb58aab0 | 202224.0     | 2088be06-eebd-43c3-b128-b62df933a22d | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-13 | 139.00      | ATIVO  | null       |
| 61d64c06-5c8d-4642-83a4-df78f17b3733 | 202229.0     | 11e00f87-0307-49c3-82e8-2440b803630d | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 190.00      | ATIVO  | null       |
| d3fa3021-4646-4188-af78-720633781e0b | 202185.0     | 3e2ead89-ec88-4a3a-9ecc-26cd951c84ef | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 890.00      | ATIVO  | null       |
| 2df1c8a7-ec28-44eb-b7a9-c93233fac10e | 202248.0     | 722c2ba2-5fe0-4cb6-b67a-ca170b0734f7 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 2790.00     | ATIVO  | null       |
| 63115124-9928-439a-b918-425ace48f06b | 202184.0     | ed8c44d6-c68e-42a6-85c3-d2fbaa88fc28 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 500.00      | ATIVO  | null       |
| 6dba7828-b239-46eb-a441-b5471b1eda74 | 202252.0     | 76c3db03-5607-4df6-8957-241a19cd4127 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-19 | 1999.00     | ATIVO  | null       |
| fc600591-e0e1-4daf-a928-8615d68da1ff | 202257.0     | b9d9b67c-aa62-46c7-8dbe-fbdd43906193 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-20 | 444.00      | ATIVO  | null       |
| f723ae17-6917-4858-9ac6-76a6d54a3252 | 200575.0     | 9b22447c-5428-420e-9ade-87d099678daf | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-21 | 590.00      | ATIVO  | null       |
| 96440889-8bad-4106-a33c-5f7f9c907117 | 200576.0     | 152cbbda-fc73-40a5-9d77-10067a9953bb | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-22 | 420.00      | ATIVO  | null       |
| e93f0958-8cce-4b97-9449-d857276a89bb | 202200.0     | 7ad74cee-d2a1-4a74-9da8-c0d5288247dd | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 508.00      | ATIVO  | null       |
| 1a44dffb-9d06-4b8e-ab70-e6773c155b75 | 202267.0     | 687d2a17-09f3-4e10-b97c-e3f19c286ee3 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-24 | 330.00      | ATIVO  | null       |
| 90086470-d800-4a02-9e64-5fbe630560b2 | 202268.0     | 188056b2-ab9a-482f-9f4e-d49ec9735b87 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-24 | 900.00      | ATIVO  | null       |
| 8bfd56e9-6487-4cfd-9a6c-6308c622621c | 200510.0     | 7bc01eba-77ac-4711-ae40-20eb4dacea28 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-12-16 | 560.00      | ATIVO  | null       |
| 7fbf6143-fd93-4074-adc0-52162008bc43 | 200565.0     | 729c58c2-b34e-44cd-a5e6-06839f55c315 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 200.00      | ATIVO  | null       |
| dab7c2b6-5421-491f-bfe7-ea08455b0bad | 200566.0     | 094ef2a0-eac9-4194-aa77-52359ea1f6fe | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 160.00      | ATIVO  | null       |
| 6ecf4921-2961-4e95-8c6d-92536de09efa | 202175.0     | 1b774f36-ec35-4a68-ac14-2d1f26423bd9 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 799.00      | ATIVO  | null       |
| fbce03ff-8140-4b23-bbbe-4f052aec487f | 202201.0     | 4d09725e-4f3a-4f17-aa86-1fd08d5dde25 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 150.00      | ATIVO  | null       |
| acae7d94-dd6b-48c9-8bbc-e686b574d793 | 202203.0     | bb4321e2-8adc-4c4d-821a-400e1db58f64 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 250.00      | ATIVO  | null       |
| 8e86be2b-769a-4b17-84c9-96dee7a560bb | 202177.0     | eac4cdd0-4054-47ad-bf77-a3ec261e1e15 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 315.00      | ATIVO  | null       |
| 056f11dd-ce96-460d-b841-20dffc767401 | 202178.0     | f751bd42-cffc-4114-9a41-667c88741a35 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 315.00      | ATIVO  | null       |
| 8fde9543-d066-4907-a720-19d0497a64d8 | 200570.0     | 9ce63463-2833-41e1-920b-b303afced2b5 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-28 | 410.00      | ATIVO  | null       |
| 1fe4a253-540b-47a0-8ed7-d8a8846b6860 | 202222.0     | 39868898-6524-4429-befb-8dd080f04aa7 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-13 | 1098.00     | ATIVO  | null       |
| f1752051-dd0e-4cc3-8755-9911f05bb938 | 202221.0     | 51803877-7e9b-42df-aa09-d89a01b951cf | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-13 | 0.01        | ATIVO  | null       |
| 9ffc2adb-c878-4645-8b23-ea6b4be3db41 | 202227.0     | 1bde53e3-06e0-4222-8de2-94b842ea8d10 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 480.00      | ATIVO  | null       |
| dd612cd2-cb7e-458b-adfe-e4701767bf1c | 202234.0     | 8e208606-8a99-44c9-a05a-ca4bee6d4567 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-15 | 50.00       | ATIVO  | null       |
| b43bfbf6-3b74-444d-a850-deb507d3c9a4 | 202237.0     | 98703f92-e6dd-462d-8939-39e6539dac21 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-15 | 230.00      | ATIVO  | null       |
| c0f4fb2c-d30d-4ab1-8b89-414029b8575f | 202240.0     | 2c223253-d7d7-4896-b0fd-6d0131d25d4c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 712.50      | ATIVO  | null       |
| c8db8472-3af4-45ee-b03e-5f8487385fa8 | 202243.0     | 860b064f-a3cd-4f27-8f36-707436cbd7f0 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 55.00       | ATIVO  | null       |
| 886b1822-50df-41d6-b9c0-321cf7facf78 | 202187.0     | 01aaf63e-9fdd-4f4d-a858-ebd4f72c2b67 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 1080.00     | ATIVO  | null       |
| 17a01279-719a-4851-a8b3-f8d401991799 | 202246.0     | 21b13ee2-e950-4e23-8e0c-18a78090e79c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 530.00      | ATIVO  | null       |
| 4fc9f42d-32d0-4243-9676-c3ee37c36ba3 | 202254.0     | 2f687ef1-35ea-4cae-84ba-1bc64f3f7918 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-19 | 590.00      | ATIVO  | null       |
| 88422191-dfc4-4a3e-ac7e-7b6ca6d9d7d5 | 202253.0     | 42bf2b7d-4bd1-489d-a485-2c43dc9497d8 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-19 | 990.00      | ATIVO  | null       |
| cea7ce61-a6fc-4525-9fc5-e897691295a0 | 202218.0     | e3e7596f-9111-4f1c-8940-afe3797644eb | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 495.00      | ATIVO  | null       |
| 05831f22-cfa1-4895-93ca-2b7158881a20 | 202258.0     | 4de38cd3-04cb-43b5-83cb-a551e9a26ce5 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-20 | 130.00      | ATIVO  | null       |
| 1e204386-8f7d-4949-a783-c8e71ce4eb81 | 202190.0     | 33ade349-b4d1-4ef4-aa47-91bb16f551ee | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 600.00      | ATIVO  | null       |
| b508885e-032c-46c1-9d9a-1b595ce94cca | 200574.0     | 22ce5ad3-6f2e-4f08-b573-bd5b76777990 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-21 | 1320.00     | ATIVO  | null       |
| 8f890da5-bd56-478a-aaa8-9f3ccca519ab | 202228.0     | 7bdeed7f-8307-4404-bbac-1fd0436d3c6e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 370.00      | ATIVO  | null       |
| 10e1a95b-df02-4b85-99bc-1c140f240647 | 202219.0     | 837a11c0-2ed7-4767-9333-762f4549a4e4 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 400.00      | ATIVO  | null       |
| cb28957f-5ff7-4b13-87e0-d61b7abab625 | 202259.0     | 44f60382-803d-4673-81d6-99e690e4080e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-20 | 421.14      | ATIVO  | null       |
| c9c0bd5b-93f4-4f95-b038-c14f99b1ad42 | 202239.0     | becdeec0-0627-413e-80c7-cb48c30ccf98 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 210.01      | ATIVO  | null       |
| c3178560-d194-4dea-8afe-a45cdcec2747 | 202183.0     | ff3f5fbb-4605-4fde-9489-9371f3940b6e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 2214.01     | ATIVO  | null       |
| c657a368-2ae8-449e-9164-922fb8fe87a0 | 202270.0     | a2363929-01a3-4a91-b93b-897a67f9c446 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-24 | 680.00      | ATIVO  | null       |
| cc3551f0-b76c-4486-b7cf-69923dfc27cf | 202226.0     | 6280d475-3d92-4471-8ea6-1d1af1de6af5 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 1490.00     | ATIVO  | null       |
| ee5aad5b-7888-4a9a-8862-fcaecad8a33a | 202269.0     | 2135b5bf-08ab-4a29-a07e-639381cbe335 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-24 | 474.00      | ATIVO  | null       |
| 372e6957-2e68-4b62-8062-c3ee56b7d309 | 200457.0     | aae700ea-2a37-4607-b38f-181c0ef6388a | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-12-01 | 530.00      | ATIVO  | null       |
| ff2e0b1f-319a-4994-89dc-de2da7ce32d4 | 200491.0     | ea14148d-13bc-43de-9090-18b834e4e292 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-08 | 280.00      | ATIVO  | null       |
| 2da907fd-5960-4a1a-be1c-240d69ce92bd | 200558.0     | 7b4d4d4b-7324-41ee-88bd-5948f9048ab9 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-08 | 272.00      | ATIVO  | null       |
| 670d30e5-e71a-40b1-8826-ac5d6ccb315d | 200564.0     | ef82e248-edf7-4fe6-a7e2-93f720a10c94 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-01 | 1100.00     | ATIVO  | null       |
| f7330687-a9ff-45f0-be1a-22d28e69b848 | 202172.0     | 94678885-2968-48c4-8c85-ff1303dcaf27 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-01 | 0.01        | ATIVO  | null       |
| 740f2d01-b202-4d3e-8873-4066a191f55f | 202171.0     | 8ca4f2dd-faee-496d-8919-90e8c951fe3e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-01 | 0.01        | ATIVO  | null       |
| b23292f8-ca84-4525-a17c-7eebc66acaec | 202182.0     | ff3f5fbb-4605-4fde-9489-9371f3940b6e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 0.01        | ATIVO  | null       |
| 25ef2ea4-0ffd-4f38-b223-937bc439fe1c | 200567.0     | dd214caa-7901-4d7c-9a75-85d3b63b18cc | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 290.00      | ATIVO  | null       |
| 98d885ff-5135-4457-bb79-d287fcd4dbfd | 202198.0     | e5eb2374-76d2-477d-a16b-126a8fdfb958 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-06 | 165.00      | ATIVO  | null       |
| ce050e59-a32d-4738-ac2b-1d59921be457 | 202195.0     | 49dbd704-d5fa-41cf-9a5d-a9e4c9c9680c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-06 | 0.01        | ATIVO  | null       |
| 9860f226-8c0e-44ab-bc69-f5c326a78674 | 200568.0     | 5b776026-6a60-443a-85a6-a32c73c76187 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 238.00      | ATIVO  | null       |
| 022b400d-d9fe-4247-8a1a-03c0fa6063b7 | 200569.0     | ef82e248-edf7-4fe6-a7e2-93f720a10c94 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 279.31      | ATIVO  | null       |
| c6b5aec7-6bc5-40e8-babb-027b6a3c8dad | 202205.0     | d6703f8c-7b4d-487d-8430-2baa4b4469f0 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 490.00      | ATIVO  | null       |
| 50cd5fe0-2f39-40c1-8a12-87c434745195 | 202204.0     | b63c3ab7-fc46-4782-9a0d-1a9b136a9627 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-07 | 135.00      | ATIVO  | null       |
| f99a3bf3-7243-4fd2-b4c4-ff38a8ebe02f | 202207.0     | 8829c073-0c9c-49b7-a5b9-ba7a2d9fd7ff | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-09 | 275.00      | ATIVO  | null       |
| 16b00387-29b4-4c8f-947a-8380462c14a6 | 202188.0     | 5d6686a6-68a1-4333-b70d-4d669d18a82c | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 534.00      | ATIVO  | null       |
| 7af00c3b-05f5-4592-80e6-4626ea40de0f | 202209.0     | 09ac190b-cf56-456b-a71d-c20719645105 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-09 | 650.00      | ATIVO  | null       |
| 0489f0c5-08ae-403c-83d6-83c2fdc86ee9 | 202215.0     | 34732199-12e7-44eb-9296-57a3b79c0e26 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 1050.00     | ATIVO  | null       |
| 8a155155-16f5-44c9-8dd4-bb70fdc2b4de | 202213.0     | 071b464c-8fba-4b9a-b310-1f472e0130ef | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 690.00      | ATIVO  | null       |
| d4e93a68-2166-407a-bafe-2737999e433e | 202216.0     | 425ae2a7-9868-43c7-a6bc-5de8b4469882 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-10 | 180.00      | ATIVO  | null       |
| d4ca32ae-ff3d-4525-b58b-6f83337c035e | 202191.0     | 721c265d-eb80-4804-ab04-54ec05cf006f | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 2154.00     | ATIVO  | null       |
| ca2c3a64-4dd9-4566-b670-c909e9c251be | 202176.0     | 6aa269f0-5835-45d3-9cd5-d5a4a4c3310d | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 588.00      | ATIVO  | null       |
| 4b3d655f-106a-4d54-bf15-87af5559808e | 202220.0     | 39868898-6524-4429-befb-8dd080f04aa7 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-13 | 0.01        | ATIVO  | null       |
| 0fa360af-d507-47cb-8bc8-0d686b80c1c2 | 202174.0     | 94678885-2968-48c4-8c85-ff1303dcaf27 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 1000.00     | ATIVO  | null       |
| 54950f4f-3a44-4b80-87d4-796aea3c6bfe | 202180.0     | ed82a4a5-ae4b-4574-bb05-d5662a3085dd | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 1200.00     | ATIVO  | null       |
| dd007d25-7ee4-4f82-8297-86264f6f1b36 | 202230.0     | f7e817cc-f51a-43ed-a436-173d39099f21 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-14 | 350.00      | ATIVO  | null       |
| af053374-581e-4ef9-97e8-8ab53bc3d638 | 202186.0     | 6eaa43fc-7b16-42d9-ab70-85735d3e9b1d | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-03 | 720.00      | ATIVO  | null       |
| 47e3e45f-6fbb-47c0-95cd-d6f615f38cce | 202173.0     | 8ca4f2dd-faee-496d-8919-90e8c951fe3e | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-02 | 1938.00     | ATIVO  | null       |
| dc1daf6a-a3b9-4193-a1ae-7bc4313b3d13 | 200572.0     | 7d271b77-6dc6-4d6a-8778-915bc489f861 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 150.00      | ATIVO  | null       |
| 0987d61a-1824-4feb-8099-621ae445daf6 | 202241.0     | 71fa01da-093d-4d63-a0dd-c9daf32d4677 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 380.00      | ATIVO  | null       |
| f5e21b62-3b3a-42d1-acec-18cd6e63b569 | 202244.0     | ef5eb7d6-daa5-43ac-badf-5669e6823cd1 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 1345.00     | ATIVO  | null       |
| 9ed89905-dc5f-4b8a-acc1-efdde679df2d | 202238.0     | 511c2481-8c16-47f8-9eef-06f9d7ee91e9 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-16 | 510.00      | ATIVO  | null       |
| 4b0fe5e4-98fa-418d-9e33-3d665a407996 | 202199.0     | 891c2179-07a3-4b2b-9853-4a9731479f82 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-06 | 387.00      | ATIVO  | null       |
| 778ca00f-5f9e-4365-820d-d129962396a0 | 202194.0     | 024bd976-d37a-4883-ad06-f1e303c8af32 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 50.00       | ATIVO  | null       |
| 97d5b1bc-081a-40b0-91a6-ac6f6a423dbd | 202193.0     | 024bd976-d37a-4883-ad06-f1e303c8af32 | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-05 | 359.46      | ATIVO  | null       |
| fb5fcde0-8d96-4236-807b-ea2e5ccd1eec | 202250.0     | 7d32e913-8eac-4404-8022-e5fd17e937fb | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-17 | 420.00      | ATIVO  | null       |
| 110d9f30-8030-4747-ae08-c7d84ac6e186 | 200573.0     | 92d844bb-3f3d-45de-b9b7-6ea274be5308 | aa7a5646-f7d6-4239-831c-6602fbabb10a | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-19 | 0.01        | ATIVO  | null       |
| 5d9f7342-d35e-43d0-8fd4-d19bbdad05ed | 202272.0     | e4ac326c-b2b2-4110-86b3-64e9e303644d | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 2fec96c8-d492-49ab-b38a-a5d5452af4d2 | 2020-10-26 | 499.00      | ATIVO  | null       |


-- ========================================
-- 8. AMOSTRA FORMAS DE PAGAMENTO UTILIZADAS
-- ========================================
-- Salve como: amostra_vendas_formas_pagamento.csv

SELECT 
    vfp.id,
    vfp.venda_id,
    v.numero_venda,
    vfp.forma_pagamento_id,
    fp.nome as forma_pagamento_nome,
    vfp.valor,
    vfp.valor_entrada,
    vfp.parcelas,
    vfp.observacao,
    vfp.created_at
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.vendas v ON vfp.venda_id = v.id
LEFT JOIN vendas.formas_pagamento fp ON vfp.forma_pagamento_id = fp.id
ORDER BY vfp.created_at DESC 
LIMIT 100;


| id                                   | venda_id                             | numero_venda | forma_pagamento_id                   | forma_pagamento_nome | valor   | valor_entrada | parcelas | observacao                | created_at                 |
| ------------------------------------ | ------------------------------------ | ------------ | ------------------------------------ | -------------------- | ------- | ------------- | -------- | ------------------------- | -------------------------- |
| ac5b93ec-7627-4424-983c-cb018593f8f6 | fbd3a468-a5c3-4a50-ac21-7acaaa501915 | 202306.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 550.32  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| bb37bb54-0d77-4836-aeca-14657d704372 | fc630c5f-302e-4eb1-ad1e-785f72a8bab9 | 202865.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 156.00  | 156.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| d0bf459d-1e86-489d-9232-8cc41b92fb61 | fb6cf9ce-03af-4459-976d-949841cb459c | 203577.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 500.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 06370c6d-a5b9-457e-a272-a81710d4da32 | fbd0489e-99ce-4645-a02d-985c12f30f32 | 206483.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 2480.00 | 0.00          | 6        | Cartão Parcelado 6x - 80% | 2025-11-04 19:45:58.742821 |
| 23d83322-d784-4134-bbfc-a48c1086954a | fc262535-df07-4259-9b99-d71042ff6da3 | 4373.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 790.00  | 790.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| c2f5b544-d64e-4809-b5c4-bf88f59d7572 | fc600591-e0e1-4daf-a928-8615d68da1ff | 202257.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 444.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 05dcb43e-8637-44bd-a889-9f22bad5634d | fb438cd8-a964-41a5-abf3-f158315202e5 | 991          | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 30.00   | 30.00         | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| cff5bb56-b9c5-42d8-a20e-6b481005fd10 | fb69eb1f-2010-4e99-a3da-f48b2937f39e | 205558.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 569.60  | 0.00          | 3        | Cartão Parcelado 3x - 80% | 2025-11-04 19:45:58.742821 |
| 93ee3535-338e-4c12-9a0d-6afd16a840e1 | fbaea6fe-1616-4e25-ac1d-9e327c7d092b | 207671.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 20.00   | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| dcf6aa8f-8de7-4c79-84fc-5db788b88e68 | fbd0489e-99ce-4645-a02d-985c12f30f32 | 206483.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 620.00  | 620.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 32f96c6e-d015-4c90-9ecc-d4d0d2ce28d9 | fbfc996e-5f41-40da-9a94-f6f8cfbca4b1 | 202434.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 2.50    | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 0802e239-fb0f-46c7-8bc3-7cf264ce5603 | fc1d43df-1d71-48cd-bb71-2d3c4d01713d | 6600         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 250.00  | 250.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 1c25af6f-604d-4a65-b534-e3d7a9b76fa7 | fc44ec62-d8aa-46da-97b6-ca99d14a90d6 | 4035.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 0.00    | 0.00          | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 0bd417b7-eed1-4ba6-91c8-86d8571959fa | fc5fe8c8-41ab-4675-9963-631397b3453b | 480102160.0  | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 500.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 9b81a9ac-25cf-417d-9fee-71d5a20a8ab3 | fb2d8fd5-56c1-4266-b649-3dbb0131370d | 8899         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 779.50  | 779.50        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| e15fed94-c2b7-47f6-a3ff-d165ca859897 | fb419db6-f528-4271-b8de-881d18c812f1 | 3399         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 100.00  | 100.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 2d0207ea-e619-4b94-8469-6d8df47b85c2 | fb56ef32-ddcc-4774-a8c7-a86ed0545c95 | 202099.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 400.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 8c05baf6-dbb4-4cef-b625-5150b96e3497 | fb69eb1f-2010-4e99-a3da-f48b2937f39e | 205558.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 142.40  | 142.40        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 03460e5b-fe0b-4811-90ea-4b8f5b28c45a | fb9518d5-f4ec-4b4b-8565-48408829f010 | 4093.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 450.00  | 450.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| d1721078-f8b4-4aff-ad80-3479da944a9f | fba8b3f2-a3e6-41c4-97b0-ca67d0fde444 | 203675.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 560.00  | 0.00          | 3        | Cartão Parcelado 3x - 80% | 2025-11-04 19:45:58.742821 |
| 2c00cd57-cac4-4232-b3c0-b896b9c59d83 | fbba00a1-e331-4a94-bbf6-7af201937a71 | 203658.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 365.20  | 365.20        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 9abb0e64-67b5-4aba-8816-8c86a5367283 | fbce4842-a319-49a1-b974-78599ee4bc3b | 203016.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 1000.80 | 0.00          | 6        | Cartão Parcelado 6x - 80% | 2025-11-04 19:45:58.742821 |
| e7c7c021-c789-428a-8f93-37f0d07718ef | fbe4c6f6-d588-49b5-896d-11bf20412554 | 420106390.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 250.00  | 250.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 704e3b3a-9d8e-4589-9a5b-d80abf803863 | fbf517ce-5815-4349-b758-0ea5dde8ffdd | 3520         | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 945.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 6d80c7df-04c4-4630-9e80-faa741e6b842 | fbfe89f0-a642-4479-b2fc-db0d3d521c5e | 11223        | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 150.00  | 0.00          | 3        | Carnê 3x                  | 2025-11-04 19:45:58.742821 |
| 96c0859e-67d5-49f8-9633-37a0ddf3f9cb | fc0c8692-fd2c-45cd-b0ba-6a84959fe2c1 | 202648.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 150.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 3dd3877a-def6-407a-bc3b-04d9405fe212 | fc39e7ba-592d-4180-bfe4-51d7858624f9 | 11059.0      | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 0.00    | 0.00          | 3        | Carnê 3x                  | 2025-11-04 19:45:58.742821 |
| 36beb4e9-8f13-42a5-ba3c-559795a2fb78 | fc43944f-8c05-49b8-b186-138eab22267a | 201476.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 100.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 8da17626-0178-494b-bedc-9f3ce2d7722e | fc554d74-fb18-444c-951a-75df3481db94 | 9650         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 290.00  | 290.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| ed89bac8-3b6c-46d1-a2e3-6fadd055f2d8 | fc5fe8c8-41ab-4675-9963-631397b3453b | 480102160.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 500.00  | 500.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| 6652bc15-4825-47d4-b6f9-b26ae3d45fb9 | fb210575-226a-4b5b-adc4-fc59ffda6aab | 420103948.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 280.00  | 280.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 01491d1c-8d93-4eed-a48f-f166845fa345 | fb28ccce-f86d-4f89-bd4b-b24a56a86425 | 202813.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 0.01    | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 20c0f8bb-f951-4921-8dfc-8afe40a622cf | fb31b9cd-a503-4877-b4b8-62fbcdc9559b | 420104166.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 177.88  | 177.88        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 7c317b48-0149-4fdf-aaf7-94480302a6b6 | fb362953-709c-4719-b65e-de51c091b046 | 9031         | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 435.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| e36de00b-a0d5-4296-a1b7-d1b6221ce35b | fb4ac26c-fe87-4d1a-ac36-e4f9a16cba9c | 203660.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 300.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| f81c152f-3da4-45dd-b920-5b0edaa620ed | fb552cc0-2bc5-4536-b9ed-f3a79ee17dec | 203082.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 60.00   | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 850939da-5146-4c80-83cb-c0b86e273caa | fb5fcde0-8d96-4236-807b-ea2e5ccd1eec | 202250.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 420.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 0fb5ebc3-fdc0-4a98-9ee1-fe7f579e1fe1 | fb675cca-94ad-49fe-947c-82facc420c2b | 207839.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 550.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 25426d87-14be-4a6e-8d2f-ae3377b5eacd | fb8d2254-e726-4904-81f1-c85cfa6826e6 | 11318        | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 239.70  | 239.70        | 1        | Entrada - Carnê           | 2025-11-04 19:45:58.742821 |
| 0973c84d-bd2c-49ab-95d9-e976c9160879 | fb8ed331-0be6-4f06-8581-5867548ce045 | 204968.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 800.00  | 0.00          | 5        | Cartão Parcelado 5x - 80% | 2025-11-04 19:45:58.742821 |
| 95e35962-4b7f-4aca-9130-a87554068c93 | fb9b5860-c776-4ca0-89d8-61e3303a2152 | 6589         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 290.00  | 290.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 69564399-8cc4-48a8-9943-14cb66514e61 | fba8b3f2-a3e6-41c4-97b0-ca67d0fde444 | 203675.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 140.00  | 140.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 67b1f36a-3e61-4849-be7f-650387d3d5f5 | fbb02320-fcd2-411f-bdc9-fad85f312a87 | 4435.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 270.00  | 270.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 86afec3e-322f-4482-bc71-eaebf2d073e6 | fbb76a74-e6fb-4a62-996b-fae716acf9f4 | 689          | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 474.50  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 26067d0a-4317-48a1-a17e-17aa570bf9cb | fbc8e38c-154e-4284-910b-f5245e2227d8 | 207906.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 200.00  | 200.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| e175c8a9-309d-4a4c-8e78-d7c1196a9758 | fbce4842-a319-49a1-b974-78599ee4bc3b | 203016.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 250.20  | 250.20        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 5a19a334-2f37-4f4e-9cb1-1fc686ec1590 | fbd6bff2-67c3-4d24-b341-2137bff13fc5 | 203169.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 520.00  | 0.00          | 3        | Cartão Parcelado 3x - 80% | 2025-11-04 19:45:58.742821 |
| d6c0a895-d82d-48ef-a06b-325ce404e11e | fbdeb84f-cd3a-40a5-b8c4-966184156417 | 480102333.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 400.00  | 400.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| a4e4af78-861d-48eb-8550-a2bae44f06d2 | fbf45b7d-aa12-4982-8697-ec5d7a5ba4d9 | 202615.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 180.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| f5856425-c228-4dba-9091-f87635db9cea | fbf517ce-5815-4349-b758-0ea5dde8ffdd | 3520         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 945.00  | 945.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| ef9a476f-2f53-4371-a9c4-d37290c7b657 | fbfc9bfe-7630-4999-bf51-b2f1e6c688fa | 204087.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 450.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 926ba9b4-51c8-445f-8d21-aede2c45f96e | fbfd394e-7875-4dd8-9c93-8f8beee0aefe | 420106201.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 590.00  | 590.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 2051ddeb-8ee6-4873-935d-f450ad5c6e90 | fc0226a0-246d-46c3-a0d9-2c474f9f96bb | 420102404.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 549.00  | 549.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| d9340d0e-16ae-4ed4-928b-f8133a6010f8 | fc0a3d76-f76b-4d61-bf2d-0907ca634553 | 202302.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 140.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 245900e8-0faa-4eeb-b61b-21ee223fe754 | fc2fef3b-eeb6-4fa5-a806-2d6ad4afe33a | 11066        | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 116.70  | 116.70        | 1        | Entrada - Carnê           | 2025-11-04 19:45:58.742821 |
| 6af54422-031a-4436-ae6c-7356e9bb3f6e | fc2fef3b-eeb6-4fa5-a806-2d6ad4afe33a | 11066        | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 272.30  | 0.00          | 6        | Carnê 6x                  | 2025-11-04 19:45:58.742821 |
| 9d308012-2f9a-4111-81d6-d5bfd30e834a | fc3f2625-b7fb-4af0-97a6-56248c4b26b7 | 4681.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 640.00  | 640.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| ffdd1e12-be95-4f15-8b6f-7ece8611db62 | fc3f2625-b7fb-4af0-97a6-56248c4b26b7 | 4681.0       | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 640.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| b05da8dc-0259-43a9-81ed-4842077a7c21 | fc4b4295-9f67-4edf-9a98-349775986aa0 | 207841.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 600.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| dc8d61bf-9555-411d-8c1f-326dee598553 | fc4c6064-12db-4618-93b7-90dccdbfc3ea | 200780.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 200.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 0b4a8104-4ee3-4789-ba26-a05e94c3c952 | fc5954b5-21b9-42f4-a1a2-3bb7778670b8 | 201201.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 154.00  | 154.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| c814afd1-9bbd-47de-aac1-7a568733a9a4 | fc5954b5-21b9-42f4-a1a2-3bb7778670b8 | 201201.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 616.00  | 0.00          | 4        | Cartão Parcelado 4x - 80% | 2025-11-04 19:45:58.742821 |
| 99101d84-cfe5-4f6e-a5b9-bbf842af294d | fb20f31b-b2a9-48dd-9ded-a0f0b209edac | 203126.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 138.00  | 138.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 7cccc7ae-08fb-4207-9f67-c956d981acad | fb20f31b-b2a9-48dd-9ded-a0f0b209edac | 203126.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 552.00  | 0.00          | 3        | Cartão Parcelado 3x - 80% | 2025-11-04 19:45:58.742821 |
| a5ed76f6-b937-4699-b4b1-6436bec29744 | fb287e00-8101-4577-86f7-24990c26b137 | 205709.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 240.00  | 240.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 6d01f932-9ad2-4ca5-a9ee-87d878926e27 | fb287e00-8101-4577-86f7-24990c26b137 | 205709.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 960.00  | 0.00          | 6        | Cartão Parcelado 6x - 80% | 2025-11-04 19:45:58.742821 |
| 16003969-17d5-4e6d-a3ec-e27083fa5a74 | fb2d8fd5-56c1-4266-b649-3dbb0131370d | 8899         | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 779.50  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 0cb61db3-b781-4c9b-b5c0-8e24a327f820 | fb3175d0-d62a-4ea4-990c-8268e182ea34 | 11777        | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 0.00    | 0.00          | 3        | Carnê 3x                  | 2025-11-04 19:45:58.742821 |
| ec980241-b112-4692-ac1b-13b88f34e3e2 | fb31cd6f-a254-47c8-ae23-0433cb11c356 | 202900.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 297.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 8208fec5-afb3-4f00-8b79-a06b64e9ed2e | fb362953-709c-4719-b65e-de51c091b046 | 9031         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 435.00  | 435.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| 0b450037-70c2-40e7-ab75-5c0aee1727c3 | fb47bdc5-083e-4767-98dd-cdb6e811b427 | 10731        | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 220.00  | 0.00          | 3        | Carnê 3x                  | 2025-11-04 19:45:58.742821 |
| 526038ef-3da6-4ae2-86f7-0b0b21df3f2e | fb47e377-450a-4788-97f3-d857aea7fb4d | 10969.0      | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 20.00   | 0.00          | 3        | Carnê 3x                  | 2025-11-04 19:45:58.742821 |
| e424aa33-8af1-4579-a959-6fde26de7f79 | fb4dc793-84b5-4387-ac7c-18287f0a48a5 | 204223.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 50.00   | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 51eb4954-b150-45c1-98c7-0bdedc3efcdf | fb552a33-a77f-4cac-80c4-c1805fd5c963 | 4024.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 200.00  | 200.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 57c3aa6e-d5e5-4a1b-89b2-2bf332d6057a | fb5d2460-503d-4fb5-9936-fe73e2d24b5d | 8682.0       | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 800.00  | 800.00        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| a13904a7-9fba-4c21-8b96-32e26c4ce497 | fb5d2460-503d-4fb5-9936-fe73e2d24b5d | 8682.0       | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 800.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 321e0a6e-f186-4656-b9cd-0961237a7212 | fb606fd5-7515-450f-85b8-8b8a336d8ac7 | 1987         | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 195.00  | 195.00        | 1        | Entrada - Carnê           | 2025-11-04 19:45:58.742821 |
| ec851c95-b1a7-408a-bdc7-7c07befbf0fa | fb606fd5-7515-450f-85b8-8b8a336d8ac7 | 1987         | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 455.00  | 0.00          | 6        | Carnê 6x                  | 2025-11-04 19:45:58.742821 |
| e2d29e69-8399-4546-9035-3c353dfa4519 | fb7e40ee-0bda-4263-a4b7-f1d5ebbfc760 | 206743.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 164.00  | 164.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 149dfe25-b94c-4efe-b22e-5aaa51ff9ae6 | fb7e40ee-0bda-4263-a4b7-f1d5ebbfc760 | 206743.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 656.00  | 0.00          | 4        | Cartão Parcelado 4x - 80% | 2025-11-04 19:45:58.742821 |
| 830781ce-ff10-4763-b45a-4af65cc9273c | fb8d2254-e726-4904-81f1-c85cfa6826e6 | 11318        | 26e2d011-d3b6-4ded-9259-4d4f37a000bc | Carnê                | 559.30  | 0.00          | 6        | Carnê 6x                  | 2025-11-04 19:45:58.742821 |
| 0e208197-40ce-4d50-8f84-63edc4cd27f3 | fb8ed331-0be6-4f06-8581-5867548ce045 | 204968.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 200.00  | 200.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 9cff2fb7-f2f7-43a8-9b38-b860e723b805 | fb9518d5-f4ec-4b4b-8565-48408829f010 | 4093.0       | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 450.00  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 62727868-3023-4e7c-bb52-5e4e273c3815 | fb9521e6-c1d7-436d-b63a-63adc2efdc59 | 207310.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 450.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 05465fa0-d3e4-476e-a233-24bc107f7792 | fba076df-b91f-4a9e-becd-2c090f64404e | 203046.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 90.00   | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| c4654fb3-8827-448a-9828-aaebd0bb96b0 | fba561a1-aebb-4b59-ac39-8792e5ca0a67 | 205580.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 552.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 221f9707-7575-4cc3-88c3-51b540cd9743 | fbafb339-3c26-47ab-9133-a286f8f29ad7 | 480103666.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 747.50  | 747.50        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| ff0848d8-3f95-4ccb-a61b-da47945cc196 | fbafb339-3c26-47ab-9133-a286f8f29ad7 | 480103666.0  | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 747.50  | 0.00          | 3        | Cartão Parcelado 3x - 50% | 2025-11-04 19:45:58.742821 |
| 59f6775c-0f3a-45d6-a7ea-3806b77a4f4b | fbb3e082-d834-484d-a7ff-6d5e60bc7ba9 | 201055.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 230.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| ac84df35-cecb-4b3c-9cf4-bce68ab7f5b1 | fbb76a74-e6fb-4a62-996b-fae716acf9f4 | 689          | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 474.50  | 474.50        | 1        | PIX - 50%                 | 2025-11-04 19:45:58.742821 |
| ae9a8108-9129-408c-ac9d-bd881cf717ec | fbba00a1-e331-4a94-bbf6-7af201937a71 | 203658.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 1460.80 | 0.00          | 6        | Cartão Parcelado 6x - 80% | 2025-11-04 19:45:58.742821 |
| 460fe43b-ae82-4bb5-bd76-180b088edc09 | fbbd62ce-7de8-43ba-833a-75ecd0988bd2 | 204725.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 0.01    | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 59e2f1dc-2eb0-494a-a1b4-0ea0ba838b7f | fbc8e38c-154e-4284-910b-f5245e2227d8 | 207906.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 800.00  | 0.00          | 5        | Cartão Parcelado 5x - 80% | 2025-11-04 19:45:58.742821 |
| 4ccece6e-2cfb-44fa-a2ff-a56c2b61e0dc | fbce03ff-8140-4b23-bbbe-4f052aec487f | 202201.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 150.00  | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 4a5db8d4-88d3-4a07-b968-3c49eaf14ece | fbd3dc63-8c3b-465c-af55-3aa008798dfc | 205502.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 450.00  | 0.00          | 2        | Cartão 2x                 | 2025-11-04 19:45:58.742821 |
| 3af39a4d-18c9-40fa-a522-9f5b3c3aa33b | fbd6bff2-67c3-4d24-b341-2137bff13fc5 | 203169.0     | 203527b1-d871-4f29-8c81-88fb0efaebd1 | Dinheiro             | 130.00  | 130.00        | 1        | Entrada - 20%             | 2025-11-04 19:45:58.742821 |
| 742f85bd-5096-475d-ac36-5580c23eaa71 | fbd9cfeb-6a93-473b-abeb-5fd192b2f47a | 6632         | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 800.00  | 800.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| 0b5abee2-1c43-48f6-a823-2c6e4ba172b4 | fbde5d98-e217-4a75-92ff-03089ef13143 | 202733.0     | 4854a683-31c3-4355-a03c-2bf398ebb4d5 | Cartão de Crédito    | 0.01    | 0.00          | 1        | Cartão 1x                 | 2025-11-04 19:45:58.742821 |
| 94d3dbe4-0a41-47fb-ab2f-5b9502991b60 | fbf363a4-b4a2-4122-97dd-b8e8f08a2eff | 420105939.0  | cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d | PIX                  | 669.00  | 669.00        | 1        | PIX à vista               | 2025-11-04 19:45:58.742821 |
| faf64b25-7db0-40ee-a2df-9e6c4f7f0abb | fc630c5f-302e-4eb1-ad1e-785f72a8bab9 | 202865.0     | 66c4f61d-b264-46c2-a29b-69a1c2e6aba2 | Parcelado no Cartão  | 624.00  | 0.00          | 4        | Cartão Parcelado 4x - 80% | 2025-11-04 19:45:58.742821 |



-- ========================================
-- 9. ESTATÍSTICAS GERAIS
-- ========================================
-- Salve como: estatisticas_vendas.csv

-- Vendas por status
SELECT 
    status,
    COUNT(*) as quantidade,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as valor_medio
FROM vendas.vendas 
GROUP BY status
ORDER BY quantidade DESC;


| status | quantidade | valor_total | valor_medio          |
| ------ | ---------- | ----------- | -------------------- |
| ATIVO  | 15281      | 7889566.44  | 516.2990929912963811 |

-- Vendas por loja
SELECT 
    loja_id,
    COUNT(*) as quantidade_vendas,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as valor_medio
FROM vendas.vendas 
GROUP BY loja_id
ORDER BY quantidade_vendas DESC
LIMIT 20;


| loja_id                              | quantidade_vendas | valor_total | valor_medio          |
| ------------------------------------ | ----------------- | ----------- | -------------------- |
| 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 7304              | 3901172.06  | 534.1144660460021906 |
| aa7a5646-f7d6-4239-831c-6602fbabb10a | 3751              | 1642978.96  | 438.0109197547320714 |
| 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 3035              | 1586964.50  | 522.8878088962108731 |
| da3978c9-bba2-431a-91b7-970a406d3acf | 609               | 348009.94   | 571.4448932676518883 |
| 4e94f51f-3b0f-4e0f-ba73-64982b870f2c | 411               | 335586.10   | 816.5111922141119221 |
| 1c35e0ad-3066-441e-85cc-44c0eb9b3ab4 | 171               | 74854.88    | 437.7478362573099415 |


-- Formas de pagamento mais utilizadas
SELECT 
    fp.nome,
    COUNT(*) as quantidade_usos,
    SUM(vfp.valor) as valor_total,
    AVG(vfp.valor) as valor_medio,
    AVG(vfp.parcelas) as parcelas_media
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.formas_pagamento fp ON vfp.forma_pagamento_id = fp.id
GROUP BY fp.nome
ORDER BY quantidade_usos DESC;

| nome                | quantidade_usos | valor_total | valor_medio          | parcelas_media         |
| ------------------- | --------------- | ----------- | -------------------- | ---------------------- |
| Parcelado no Cartão | 6254            | 4138260.79  | 661.6982395267029101 | 3.2299328429804925     |
| PIX                 | 4389            | 1889393.43  | 430.4838072453861928 | 1.00000000000000000000 |
| Cartão de Crédito   | 3765            | 409494.20   | 108.7633997343957503 | 1.00000000000000000000 |
| Dinheiro            | 3485            | 813653.57   | 233.4730473457675753 | 1.00000000000000000000 |
| Carnê               | 1844            | 638764.68   | 346.4016702819956616 | 5.0661605206073753     |


-- ========================================
-- 10. VERIFICAÇÃO DE INTEGRIDADE
-- ========================================
-- Salve como: verificacao_integridade_vendas.csv

-- Vendas sem formas de pagamento
SELECT 'vendas_sem_formas_pagamento' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas v
LEFT JOIN vendas.vendas_formas_pagamento vfp ON v.id = vfp.venda_id
WHERE vfp.venda_id IS NULL;

| verificacao                 | quantidade |
| --------------------------- | ---------- |
| vendas_sem_formas_pagamento | 0          |

-- Formas de pagamento órfãs
SELECT 'formas_pagamento_orfas' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas_formas_pagamento vfp
LEFT JOIN vendas.vendas v ON vfp.venda_id = v.id
WHERE v.id IS NULL;


| verificacao            | quantidade |
| ---------------------- | ---------- |
| formas_pagamento_orfas | 0          |

-- Valores inconsistentes (soma das formas != valor total da venda)
WITH soma_formas AS (
    SELECT 
        venda_id,
        SUM(valor) as soma_valor_formas
    FROM vendas.vendas_formas_pagamento 
    GROUP BY venda_id
)
SELECT 'valores_inconsistentes' as verificacao, COUNT(*) as quantidade
FROM vendas.vendas v
JOIN soma_formas sf ON v.id = sf.venda_id
WHERE ABS(v.valor_total - sf.soma_valor_formas) > 0.01;


| verificacao            | quantidade |
| ---------------------- | ---------- |
| valores_inconsistentes | 0          |

-- ========================================
-- FIM DAS QUERIES
-- ========================================

/*
PRÓXIMOS PASSOS APÓS EXECUTAR AS QUERIES:

1. Salvar todos os CSVs na pasta: 
   d:/projetos/carne_facil/carne_facil/data/mapeamento_schema/

2. Organizar os arquivos:
   - tabelas_schema_vendas.csv
   - estrutura_completa_vendas.csv  
   - constraints_relacionamentos_vendas.csv
   - indices_vendas.csv
   - contagem_registros_vendas.csv
   - amostra_vendas.csv
   - amostra_vendas_formas_pagamento.csv
   - estatisticas_vendas.csv
   - verificacao_integridade_vendas.csv

3. Executar script de análise para processar todos os dados

4. Gerar plano de implementação das próximas tabelas
*/

""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Salva o arquivo
    with open(arquivo_queries, 'w', encoding='utf-8') as f:
        f.write(queries_sql)
    
    print(f"📋 === QUERIES DE MAPEAMENTO GERADAS === 📋")
    print(f"📂 Arquivo: {arquivo_queries}")
    print(f"📊 Queries organizadas por seção")
    print(f"💾 Pronto para execução no Supabase")
    print()
    
    # Cria diretório para os resultados
    resultado_dir = base_dir / "data" / "mapeamento_schema"
    resultado_dir.mkdir(exist_ok=True)
    
    print(f"📁 Diretório criado para resultados: {resultado_dir}")
    print()
    
    print(f"🎯 === INSTRUÇÕES === 🎯")
    print(f"1. Abra o arquivo: {arquivo_queries.name}")
    print(f"2. Execute cada query no Supabase separadamente")
    print(f"3. Salve cada resultado como CSV em: {resultado_dir}")
    print(f"4. Siga os nomes sugeridos nos comentários")
    print(f"5. Execute o script de análise após completar")
    
    return arquivo_queries, resultado_dir

if __name__ == "__main__":
    print("🔍 === GERADOR DE QUERIES - MAPEAMENTO VENDAS === 🔍")
    print()
    
    arquivo_queries, resultado_dir = gerar_queries_mapeamento_vendas()
    
    print(f"\n✅ QUERIES GERADAS COM SUCESSO!")
    print(f"📋 Próximo passo: Execute as queries no Supabase")
    print(f"💾 Salve os resultados em CSV conforme instruções")
    print(f"🚀 Depois execute o script de análise!")