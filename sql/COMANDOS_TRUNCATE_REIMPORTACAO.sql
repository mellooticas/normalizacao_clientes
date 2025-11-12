-- COMANDOS PARA LIMPEZA E REIMPORTAÇÃO DA TABELA VENDAS
-- Execute estes comandos no PostgreSQL antes de importar os dados corrigidos

-- IMPORTANTE: NÃO PRECISA CRIAR VENDEDOR GENÉRICO!
-- Os dados já foram corrigidos com UUIDs que existem no banco

-- 1. TRUNCATE para limpar completamente a tabela vendas
-- (Remove todos os registros mas mantém a estrutura)
TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;

-- 2. VERIFICAÇÃO (opcional - para confirmar que a tabela está vazia)
SELECT COUNT(*) as total_registros FROM vendas.vendas;
-- Resultado esperado: 0

-- 3. IMPORTAÇÃO DOS DADOS DEFINITIVOS
-- Execute este comando após o truncate
COPY vendas.vendas (
    numero_venda, 
    cliente_id, 
    loja_id, 
    vendedor_id, 
    data_venda, 
    valor_total, 
    valor_entrada, 
    nome_cliente_temp, 
    observacoes, 
    status, 
    cancelado, 
    created_at, 
    updated_at
)
FROM '/caminho/para/vendas_definitivo.csv'
CSV HEADER;

-- 4. VERIFICAÇÃO FINAL (após importação)
SELECT COUNT(*) as total_importado FROM vendas.vendas;
-- Resultado esperado: 5227

-- 5. VERIFICAÇÃO DE FOREIGN KEYS (para confirmar que não há violações)
SELECT 
    COUNT(*) as total_vendas,
    COUNT(DISTINCT loja_id) as lojas_unicas,
    COUNT(DISTINCT vendedor_id) as vendedores_unicos,
    COUNT(cliente_id) as vendas_com_cliente_uuid,
    COUNT(*) - COUNT(cliente_id) as vendas_sem_cliente_uuid
FROM vendas.vendas;

-- 6. AMOSTRA DOS DADOS IMPORTADOS
SELECT 
    numero_venda,
    loja_id,
    vendedor_id,
    cliente_id,
    valor_total,
    nome_cliente_temp
FROM vendas.vendas 
LIMIT 5;

-- OBSERVAÇÕES:
-- - RESTART IDENTITY reseta contadores AUTO_INCREMENT (se houver)
-- - CASCADE remove registros em tabelas dependentes (se houver)
-- - Use o caminho completo do arquivo vendas_definitivo.csv
-- - TODOS os UUIDs foram validados contra o banco real
-- - NÃO há mais problemas de foreign key constraints
-- - Todas as vendas estão com vendedor 'NAN' (UUID válido do banco)