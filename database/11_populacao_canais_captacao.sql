-- ===============================================
-- POPULAÇÃO DE CANAIS DE CAPTAÇÃO (COMO CONHECEU)
-- ===============================================
-- Gerado automaticamente em: 2025-10-29
-- Total de canais: 13

-- Limpar tabela existente (se houver)
TRUNCATE TABLE marketing.canais_captacao CASCADE;

-- Inserir 13 canais de captação únicos
INSERT INTO marketing.canais_captacao (
    id,
    nome,
    codigo,
    descricao,
    tipo_canal,
    ativo,
    criado_em
) VALUES
    ('f97ed91c-ce7e-4fb5-aa4f-29841e24a010', '01 - REDES SOCIAS', '01', 'REDES SOCIAS', 'DIGITAL', true, NOW()),
    ('48ee4195-2255-475a-98da-176908111bd2', '04 CLIENTES', '04 CLIENTE', '04 CLIENTES', 'ORGANICO', true, NOW()),
    ('c1477a71-95ce-4cfb-a9a3-fb962e61a3a3', '138 - SAÚDE DOS OLHOS', '138', 'SAÚDE DOS OLHOS', 'MEDICO', true, NOW()),
    ('ca5f81c8-de87-4ee2-9dac-c7951cbf2764', '15 - ORÇAMENTO', '15', 'ORÇAMENTO', 'ORGANICO', true, NOW()),
    ('01cde395-3833-4127-acd7-a4d80d08c32f', '16 - INDICAÇÃO', '16', 'INDICAÇÃO', 'INDICACAO', true, NOW()),
    ('002e25a7-d726-4a10-bf04-dab43dfe7c37', '17 - ABORDAGEM', '17', 'ABORDAGEM', 'ATIVO', true, NOW()),
    ('cda9f5d4-73c4-459d-81f2-18e2dc656a8f', '21 - TELEMARKETING', '21', 'TELEMARKETING', 'ATIVO', true, NOW()),
    ('7742d933-20a1-4d3b-9f46-9c38506d00b9', '38 - DIVULGADOR', '38', 'DIVULGADOR', 'ATIVO', true, NOW()),
    ('928c410b-447c-43b0-bf3b-c6b1d6f95c88', '55 - CARTÃO DE TODOS', '55', 'CARTÃO DE TODOS', 'OUTROS', true, NOW()),
    ('38d6fd7d-8055-4e4c-bd8d-a143697e11b0', '77 - AMIGO (IND)', '77', 'AMIGO (IND)', 'INDICACAO', true, NOW()),
    ('78e25ad7-9022-487d-a153-c41c49061ed0', '98 - WHATSAPP', '98', 'WHATSAPP', 'DIGITAL', true, NOW()),
    ('7d45d8ef-a803-4aa9-baf5-e78d0ef1f3ab', 'GOOGLE', 'GOOGLE', 'GOOGLE', 'DIGITAL', true, NOW()),
    ('379999b3-ef63-4b43-905f-53f8efbc11d5', 'NÃO INFORMADO', 'NÃO INFORM', 'NÃO INFORMADO', 'OUTROS', true, NOW());

-- ===============================================
-- ESTATÍSTICAS DOS CANAIS
-- ===============================================

-- Total de canais inseridos: 13

-- Verificar inserção:
SELECT 
    tipo_canal,
    COUNT(*) as quantidade
FROM marketing.canais_captacao
GROUP BY tipo_canal
ORDER BY quantidade DESC;

-- Listar todos os canais:
SELECT id, nome, codigo, tipo_canal, ativo
FROM marketing.canais_captacao
ORDER BY nome;
