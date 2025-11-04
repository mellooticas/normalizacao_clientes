-- =========================================
-- SCRIPT DE POPULAÇÃO INICIAL
-- Sistema Carne Fácil - Dados Base
-- =========================================

-- =========================================
-- 1. POPULAR LOJAS
-- =========================================

INSERT INTO vendas.lojas (id, codigo, nome, ativo) VALUES
('9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'MAUA', 'Ótica Mauá', true),
('7c8d4e2f-91a6-4b3c-8d7e-f2a5b6c9d3e1', 'PERUS', 'Ótica Perus', true),
('3e5f7a9b-2c4d-6e8f-1a3b-5c7d9e2f4a6b', 'RIO_PEQUENO', 'Ótica Rio Pequeno', true),
('8b1c3d5e-7f9a-2b4c-6d8e-1f3a5b7c9d2e', 'SAO_MATEUS', 'Ótica São Mateus', false), -- Loja fechada
('2a4b6c8d-5e7f-9a1b-3c5d-7e9f2a4b6c8d', 'SUZANO2', 'Ótica Suzano 2', true),
('6c8d1e3f-9a2b-4c6d-8e1f-3a5b7c9d2e4f', 'SUZANO', 'Ótica Suzano', true);

-- =========================================
-- 2. POPULAR VENDEDORES
-- (Baseado nos dados únicos extraídos dos CSVs)
-- =========================================

INSERT INTO vendas.vendedores (id, nome_normalizado, ativo) VALUES
('d2eb5739-5887-4c3f-86e9-822f60469650', 'MARIA ELIZABETH', true),
('fa125c8b-7932-4e65-b891-dc567890abcd', 'BRUNA', true),
('8e7f6a9b-3c4d-5e8f-2a6b-1c9d7e4f2a5b', 'CARLA HELENA', true),
('7d6c5a9b-2e4f-7a8c-1d5e-3f9a6b8c2d4e', 'CLEIDE', true),
('5f8a7c9d-1e3f-6a9b-4c7d-2e5f8a1b3c6d', 'FABIANA', true),
('3c6d9e2f-8a1b-4c7d-5e9f-7a2b4c6d8e1f', 'GLEICE KELLY', true),
('9b2d5e8f-6a3c-7d1e-8f2a-5b9c3d6e8f1a', 'IARA', true),
('7a4c8e1f-3d6e-9a2b-5c8d-1f4a7c9e2b5d', 'LILIAN', true),
('4e7a9c2d-6f1a-8c3e-2d5f-9a4b7c1e6d8f', 'LUCIANA', true),
('8c1e5a9d-2f4a-7c9e-6d2f-4a8b1c5e9d3f', 'MARCOS', true),
('6d9f2a5c-8e1a-4c7d-9f3a-6b8c2d5e8f1c', 'MARIA APARECIDA', true),
('2a5c8f1d-9e3a-6c8d-1f4a-8b2c5d9f3e6a', 'MARIA SANTOS', true),
('9f3a6c8d-1e5a-8c2d-4f7a-3b6c9e1d5f8a', 'MICHELE', true),
('5c8d1f4a-7e2a-9c5d-8f1a-4b7c2e5d8f9c', 'PATRICIA', true),
('1f4a7c9e-3d6a-8c1f-5a9c-2d4f7a9c3e6d', 'REGINA', true),
('7c9e2d5f-8a1c-4e7a-9c2d-6f8a3c5e2d7f', 'ROSANGELA', true),
('3e6a9c2d-5f8a-7c1e-4a8c-9d2f5a8c1e4d', 'SANDRA', true),
('9c2d5f8a-1e4a-7c9d-2f5a-6c8e1a4c7d9f', 'SELMA', true),
('5f8a1c4e-7d9a-3c6e-8f1a-2d5f8a3c6e9d', 'SILVIA', true),
('1c4e7a9d-3f6a-8c2e-5a9c-1d4f7a2c5e8f', 'SIMONE', true),
('7a9d3f6c-8e1a-4c7d-9f2a-5c8e3a6c9d1f', 'TEREZA', true),
('3f6c8e1a-5d9a-7c2e-4f8a-1c5e8a3c6e9f', 'VERA LUCIA', true),
('8e1a4c7d-9f3a-6c2e-5a8c-3e6a9c1e4a7c', 'VIRGINIA', true),
-- Vendedores adicionais que podem aparecer nos dados
('4c7d9f2a-5e8a-1c6e-9f3a-6c2e5a8c3e6a', 'ANA PAULA', true),
('9f2a5e8c-1c4e-7a9d-3f6a-8c2e5a9c1e4f', 'BEATRIZ', true),
('5e8c1c4e-7a9d-2f5a-6c8e-1a4c7d9f2a5e', 'CRISTINA', true),
('1c4e7a9d-2f5a-6c8e-9f3a-5c8e1a4c7d9f', 'DANIELA', true),
('7a9d2f5a-6c8e-1a4c-7d9f-3a5c8e1a4c7d', 'ELIANE', true),
('2f5a6c8e-1a4c-7d9f-2a5c-8e1a4c7d9f2a', 'FERNANDA', true),
('6c8e1a4c-7d9f-2a5c-8e1a-4c7d9f2a5c8e', 'GABRIELA', true),
('1a4c7d9f-2a5c-8e1a-4c7d-9f2a5c8e1a4c', 'HELENA', true),
('4c7d9f2a-5c8e-1a4c-7d9f-2a5c8e1a4c7d', 'ISABELA', true),
('7d9f2a5c-8e1a-4c7d-9f2a-5c8e1a4c7d9f', 'JULIANA', true),
('9f2a5c8e-1a4c-7d9f-2a5c-8e1a4c7d9f2a', 'KAMILA', true),
('2a5c8e1a-4c7d-9f2a-5c8e-1a4c7d9f2a5c', 'LETICIA', true),
('5c8e1a4c-7d9f-2a5c-8e1a-4c7d9f2a5c8e', 'MARIANA', true),
('8e1a4c7d-9f2a-5c8e-1a4c-7d9f2a5c8e1a', 'NATALIA', true),
('1a4c7d9f-2a5c-8e1a-4c7d-9f2a5c8e1a4c', 'OLIVIA', true),
('4c7d9f2a-5c8e-1a4c-7d9f-2a5c8e1a4c7d', 'PRISCILA', true);

-- =========================================
-- 3. RELACIONAMENTOS VENDEDORES-LOJAS
-- (Baseado na análise dos dados reais)
-- =========================================

-- MARIA ELIZABETH (BETH) - trabalha em MAUA
INSERT INTO vendas.vendedores_lojas (vendedor_id, loja_id) VALUES
('d2eb5739-5887-4c3f-86e9-822f60469650', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e');

-- Outros relacionamentos serão inseridos baseados na análise dos CSVs
-- Exemplo de como inserir múltiplos relacionamentos:
-- INSERT INTO vendas.vendedores_lojas (vendedor_id, loja_id) 
-- SELECT v.id, l.id 
-- FROM vendas.vendedores v, vendas.lojas l 
-- WHERE v.nome_normalizado = 'NOME_VENDEDOR' AND l.codigo = 'CODIGO_LOJA';

-- =========================================
-- 4. VERIFICAÇÕES PÓS-INSERÇÃO
-- =========================================

-- Verificar lojas inseridas
SELECT 'Lojas inseridas:' as verificacao;
SELECT codigo, nome, ativo FROM vendas.lojas ORDER BY codigo;

-- Verificar vendedores inseridos  
SELECT 'Vendedores inseridos:' as verificacao;
SELECT nome_normalizado, ativo FROM vendas.vendedores ORDER BY nome_normalizado;

-- Verificar relacionamentos
SELECT 'Relacionamentos vendedores-lojas:' as verificacao;
SELECT v.nome_normalizado, l.codigo, l.nome 
FROM vendas.vendedores_lojas vl
JOIN vendas.vendedores v ON vl.vendedor_id = v.id
JOIN vendas.lojas l ON vl.loja_id = l.id
ORDER BY l.codigo, v.nome_normalizado;

-- Estatísticas iniciais
SELECT 
    (SELECT COUNT(*) FROM vendas.lojas) as total_lojas,
    (SELECT COUNT(*) FROM vendas.vendedores) as total_vendedores,
    (SELECT COUNT(*) FROM vendas.vendedores_lojas) as total_relacionamentos;

-- =========================================
-- POPULAÇÃO INICIAL CONCLUÍDA!
-- =========================================