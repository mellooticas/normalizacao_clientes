-- =============================================
-- POPULAÇÃO CORRETA USANDO DADOS DO EXCEL
-- =============================================
-- Gerado automaticamente em: 2025-10-29 16:39:05
-- Baseado em: PADRONIZACAO_VENDEDORES_COMPLETA.xlsx
-- 54 vendedores únicos + 112 relacionamentos

-- =============================================
-- 1. LIMPAR TABELAS PARA NOVA POPULAÇÃO
-- =============================================

-- Limpar relacionamentos primeiro (por causa da FK)
TRUNCATE TABLE core.vendedores_lojas CASCADE;

-- Limpar vendedores
TRUNCATE TABLE core.vendedores CASCADE;

-- =============================================
-- 2. INSERIR VENDEDORES ÚNICOS (54 registros)
-- =============================================

INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at) VALUES
('9ee0c5d8-b45a-4a18-ad45-29ad2c195937', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', true, NOW(), NOW()),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', 'MARIA ELIZABETH', 'MARIA ELIZABETH', 'MARIA ELIZABETH', true, NOW(), NOW()),
('2a13e1f0-32dc-4d4f-a326-9fc93704bf1f', 'ERICA DE CASSIA JESUS SILVA', 'ERICA DE CASSIA JESUS SILVA', 'ERICA DE CASSIA JESUS SILVA', true, NOW(), NOW()),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', 'GARANTIA', 'GARANTIA', 'GARANTIA', true, NOW(), NOW()),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', 'LARISSA', 'LARISSA', 'LARISSA', true, NOW(), NOW()),
('75d8d166-4090-4378-96f7-a7203bcf8e1d', 'LUANA', 'LUANA', 'LUANA', true, NOW(), NOW()),
('6e860343-3e25-4a82-a206-4758c36aeb00', 'MARIA DA SILVA OZORIO', 'MARIA DA SILVA OZORIO', 'MARIA DA SILVA OZORIO', true, NOW(), NOW()),
('5492deb2-2680-4836-a715-f8e8ae7e7f97', 'RENAN  NAZARO', 'RENAN  NAZARO', 'RENAN  NAZARO', true, NOW(), NOW()),
('47ded0cf-daad-415f-bc27-3c98a18e218b', 'ROGERIO APARECIDO DE MORAIS', 'ROGERIO APARECIDO DE MORAIS', 'ROGERIO APARECIDO DE MORAIS', true, NOW(), NOW()),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', 'TATIANA MELLO DE CAMARGO', 'TATIANA MELLO DE CAMARGO', 'TATIANA MELLO DE CAMARGO', true, NOW(), NOW()),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', 'WEVILLY', 'WEVILLY', 'WEVILLY', true, NOW(), NOW()),
('afee1d1c-d69f-4b0f-81e9-3260d427f60c', 'ANA', 'ANA', 'ANA', true, NOW(), NOW()),
('c1629499-3949-4c61-a4de-3b2e1b11bc19', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', true, NOW(), NOW()),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'ÉRIKA', 'ÉRIKA', 'ÉRIKA', true, NOW(), NOW()),
('9a1505b1-2abc-424c-9d19-70d3dde91b78', 'JOANA', 'JOANA', 'JOANA', true, NOW(), NOW()),
('6b293cd6-8880-4538-b68c-04261e594947', 'MARIA', 'MARIA', 'MARIA', true, NOW(), NOW()),
('87133dca-e9d5-4afd-8afb-2f5a32f6ba8d', 'NAN', 'NAN', 'NAN', true, NOW(), NOW()),
('c5080cad-498f-4f67-b0b8-3d2d269e1a0f', 'SAMUEL', 'SAMUEL', 'SAMUEL', true, NOW(), NOW()),
('aaaed13d-8525-496b-bb63-539d53b215a5', 'SANDY', 'SANDY', 'SANDY', true, NOW(), NOW()),
('91463f30-2e94-4caf-a6bc-fe05751488ea', 'WILLIAM', 'WILLIAM', 'WILLIAM', true, NOW(), NOW()),
('e9a3f24a-5d63-499e-bcb9-04f337f8755a', 'BRUNO', 'BRUNO', 'BRUNO', true, NOW(), NOW()),
('c39ed723-4cea-4032-be28-9879c0a1f506', 'KEREN', 'KEREN', 'KEREN', true, NOW(), NOW()),
('d91a52b1-040e-4394-9603-c2f11585bd4c', 'MARIA RAMOS', 'MARIA RAMOS', 'MARIA RAMOS', true, NOW(), NOW()),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', 'ROSÂNGELA', 'ROSÂNGELA', 'ROSÂNGELA', true, NOW(), NOW()),
('3dd36b22-3b42-42b7-9428-2775273b22a5', 'ALINE DA CRUZ SANTOS', 'ALINE DA CRUZ SANTOS', 'ALINE DA CRUZ SANTOS', true, NOW(), NOW()),
('af114e24-4c62-4564-91af-eec845eae094', 'ANA CLAUDIA SANTOS', 'ANA CLAUDIA SANTOS', 'ANA CLAUDIA SANTOS', true, NOW(), NOW()),
('3dd26d4d-03f8-4b4e-ae92-553e534a061d', 'ANA MARIA', 'ANA MARIA', 'ANA MARIA', true, NOW(), NOW()),
('9c1f5693-8d67-4440-9e27-e97641636126', 'BRUNO HENRIQUE SIMÃO', 'BRUNO HENRIQUE SIMÃO', 'BRUNO HENRIQUE SIMÃO', true, NOW(), NOW()),
('8552d97c-0d15-44ba-b9d3-df0165729494', 'CAROLINE OLIVEIRA LEITE', 'CAROLINE OLIVEIRA LEITE', 'CAROLINE OLIVEIRA LEITE', true, NOW(), NOW()),
('03f0a6ba-88ed-4d38-ba44-fd82755a1a70', 'EMERSON WILLIAN', 'EMERSON WILLIAN', 'EMERSON WILLIAN', true, NOW(), NOW()),
('f972c716-f446-4eae-a346-4e870948504a', 'ERIKA SERRAO FERREIRA', 'ERIKA SERRAO FERREIRA', 'ERIKA SERRAO FERREIRA', true, NOW(), NOW()),
('a7eae81a-482e-490a-90d8-6e3636c3c9f2', 'GINA KELLY FIGUEIREDO DOS SANTOS', 'GINA KELLY FIGUEIREDO DOS SANTOS', 'GINA KELLY FIGUEIREDO DOS SANTOS', true, NOW(), NOW()),
('0c7fc47d-fa3b-47f1-a7ce-e632b9bcb190', 'JOCICREIDE BARBOSA', 'JOCICREIDE BARBOSA', 'JOCICREIDE BARBOSA', true, NOW(), NOW()),
('7f55dbad-9354-47c1-beb3-e6b290b54e3e', 'MARYANE ALVES DE FREITAS', 'MARYANE ALVES DE FREITAS', 'MARYANE ALVES DE FREITAS', true, NOW(), NOW()),
('89025cb5-b4a4-4078-b131-7404793234ab', 'MATHEUS RAFAEL NASCIMENTO FERREIRA', 'MATHEUS RAFAEL NASCIMENTO FERREIRA', 'MATHEUS RAFAEL NASCIMENTO FERREIRA', true, NOW(), NOW()),
('3a399314-6403-4f52-a093-b37b15ecd471', 'NADILEIA GOMES GONÇALVES', 'NADILEIA GOMES GONÇALVES', 'NADILEIA GOMES GONÇALVES', true, NOW(), NOW()),
('e36f3dbd-d3cd-4de6-a8a3-acb1a4ef1efd', 'NATHALIA CAROLINA', 'NATHALIA CAROLINA', 'NATHALIA CAROLINA', true, NOW(), NOW()),
('98a75672-de3d-4696-9b60-d639fac6c867', 'RAIMUNDA MIRELY GOMES DE SOUZA', 'RAIMUNDA MIRELY GOMES DE SOUZA', 'RAIMUNDA MIRELY GOMES DE SOUZA', true, NOW(), NOW()),
('e4c3c6cd-b286-4529-9ace-efce66eab682', 'SAMUEL HENRIQUE DA SILVA', 'SAMUEL HENRIQUE DA SILVA', 'SAMUEL HENRIQUE DA SILVA', true, NOW(), NOW()),
('b481a467-f3bc-4c33-815d-995b0255926a', 'TAMIRES DOS SANTOS MACIEL', 'TAMIRES DOS SANTOS MACIEL', 'TAMIRES DOS SANTOS MACIEL', true, NOW(), NOW()),
('b4d65783-a8a5-4242-87c7-9fd4d3d6c3f9', 'VENDEDOR FREELANCE', 'VENDEDOR FREELANCE', 'VENDEDOR FREELANCE', true, NOW(), NOW()),
('21590199-972c-495d-8c9d-d267bde4d8be', 'WILMA CRISTINA SILVA', 'WILMA CRISTINA SILVA', 'WILMA CRISTINA SILVA', true, NOW(), NOW()),
('405ba7d8-4f35-44ce-a8b6-844487d1718b', 'YASMIN DOS SANTOS', 'YASMIN DOS SANTOS', 'YASMIN DOS SANTOS', true, NOW(), NOW()),
('504e7df6-f254-4bc9-9ae3-ae1cd439b00a', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', true, NOW(), NOW()),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', 'FELIPE MIRANDA', 'FELIPE MIRANDA', 'FELIPE MIRANDA', true, NOW(), NOW()),
('d6f8e245-292e-4d8c-9981-64609b392324', 'GUILHERME SILVA', 'GUILHERME SILVA', 'GUILHERME SILVA', true, NOW(), NOW()),
('489b163e-be8e-4d9e-b361-d8cb02343f90', 'KAYLLAINE', 'KAYLLAINE', 'KAYLLAINE', true, NOW(), NOW()),
('8e6810b4-2f60-4ae9-ba5d-34b672be5874', 'PIX', 'PIX', 'PIX', true, NOW(), NOW()),
('ada37f49-2aa5-4b38-970e-a1abff91786d', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', true, NOW(), NOW()),
('76ae87ec-012d-4c66-a714-be5316f31f84', 'CARLA CRISTINA', 'CARLA CRISTINA', 'CARLA CRISTINA', true, NOW(), NOW()),
('3488b57f-ee00-4b1b-9980-6ee8f0197c23', 'JULIANA CERA', 'JULIANA CERA', 'JULIANA CERA', true, NOW(), NOW()),
('cadbbf95-6761-4fc5-a26c-977f85adc430', 'MARIA DE LOURDES', 'MARIA DE LOURDES', 'MARIA DE LOURDES', true, NOW(), NOW()),
('b3a5865e-22b7-4e7e-b7c7-4e8392636e66', '/////////////////////////', '/////////////////////////', '/////////////////////////', true, NOW(), NOW()),
('6f996a13-ebee-4ae0-b709-060a405e5aaa', 'CHINASA DORIS', 'CHINASA DORIS', 'CHINASA DORIS', true, NOW(), NOW());

-- =============================================
-- 3. INSERIR RELACIONAMENTOS USANDO DADOS DO EXCEL (112 registros)
-- =============================================

-- Mauá (048) - 15 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('9ee0c5d8-b45a-4a18-ad45-29ad2c195937', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ANDSOU', true, '2023-01-01'),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ETH', true, '2023-01-01'),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48BETH', true, '2023-01-01'),
('2a13e1f0-32dc-4d4f-a326-9fc93704bf1f', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ERICAS', true, '2023-01-01'),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48GARA', true, '2023-01-01'),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48LARI', true, '2023-01-01'),
('75d8d166-4090-4378-96f7-a7203bcf8e1d', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48LUAN', true, '2023-01-01'),
('6e860343-3e25-4a82-a206-4758c36aeb00', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48MARSIL', true, '2023-01-01'),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48MARELI', true, '2023-01-01'),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48MARELI', true, '2023-01-01'),
('5492deb2-2680-4836-a715-f8e8ae7e7f97', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48RENNAZ', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ROGÉ', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48TATY', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48WEVE', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48WEVI', true, '2023-01-01');

-- Perus (009) - 18 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('afee1d1c-d69f-4b0f-81e9-3260d427f60c', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ANA', true, '2023-01-01'),
('c1629499-3949-4c61-a4de-3b2e1b11bc19', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ARIA', true, '2023-01-01'),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ERIK', true, '2023-01-01'),
('9a1505b1-2abc-424c-9d19-70d3dde91b78', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9JOAN', true, '2023-01-01'),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9LARI', true, '2023-01-01'),
('75d8d166-4090-4378-96f7-a7203bcf8e1d', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9LUAN', true, '2023-01-01'),
('6b293cd6-8880-4538-b68c-04261e594947', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9MARI', true, '2023-01-01'),
('87133dca-e9d5-4afd-8afb-2f5a32f6ba8d', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9NAN', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ROGE', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ROGÉ', true, '2023-01-01'),
('c5080cad-498f-4f67-b0b8-3d2d269e1a0f', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9SAMU', true, '2023-01-01'),
('aaaed13d-8525-496b-bb63-539d53b215a5', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9SAND', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9TATY', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9TATY', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9WEVI', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9WILL', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9WILL', true, '2023-01-01'),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ÉRIK', true, '2023-01-01');

-- Rio Pequeno (011) - 16 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('e9a3f24a-5d63-499e-bcb9-04f337f8755a', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11BRUN', true, '2023-01-01'),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11GARA', true, '2023-01-01'),
('c39ed723-4cea-4032-be28-9879c0a1f506', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11KERE', true, '2023-01-01'),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11LARI', true, '2023-01-01'),
('d91a52b1-040e-4394-9603-c2f11585bd4c', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11MARRAM', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11R0GE', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROGE', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROGÉ', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSA', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSA', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSN', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSÂ', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSÃ', true, '2023-01-01'),
('2b8a5584-581f-43dc-8c47-8e6f265a9e30', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSÃ', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11TATY', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11WEVI', true, '2023-01-01');

-- Suzano (042) - 23 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('c1629499-3949-4c61-a4de-3b2e1b11bc19', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ARIA', true, '2023-01-01'),
('c1629499-3949-4c61-a4de-3b2e1b11bc19', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ARIA', true, '2023-01-01'),
('0b2dca92-d8e6-4c8a-88d9-48f5c6b5ad8a', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42BETH', true, '2023-01-01'),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42FELI', true, '2023-01-01'),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42GARA', true, '2023-01-01'),
('d6f8e245-292e-4d8c-9981-64609b392324', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42GUISIL', true, '2023-01-01'),
('0c7fc47d-fa3b-47f1-a7ce-e632b9bcb190', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42JOCI', true, '2023-01-01'),
('0c7fc47d-fa3b-47f1-a7ce-e632b9bcb190', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42JOCX', true, '2023-01-01'),
('0c7fc47d-fa3b-47f1-a7ce-e632b9bcb190', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42JOCY', true, '2023-01-01'),
('489b163e-be8e-4d9e-b361-d8cb02343f90', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42KAYL', true, '2023-01-01'),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42LARI', true, '2023-01-01'),
('87133dca-e9d5-4afd-8afb-2f5a32f6ba8d', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42NAN', true, '2023-01-01'),
('8e6810b4-2f60-4ae9-ba5d-34b672be5874', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42PIX', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ROGE', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ROGÉ', true, '2023-01-01'),
('c5080cad-498f-4f67-b0b8-3d2d269e1a0f', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42SAMU', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42TATI', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42TATR', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42TATY', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42WILL', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42WILL', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42WILL', true, '2023-01-01'),
('504e7df6-f254-4bc9-9ae3-ae1cd439b00a', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ZAIN', true, '2023-01-01');

-- Suzano 2 (010) - 22 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('ada37f49-2aa5-4b38-970e-a1abff91786d', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ADRANS', true, '2023-01-01'),
('76ae87ec-012d-4c66-a714-be5316f31f84', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10CARCRI', true, '2023-01-01'),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ERIC', true, '2023-01-01'),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ERIK', true, '2023-01-01'),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10FELI', true, '2023-01-01'),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10FELMIR', true, '2023-01-01'),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10FELMIR', true, '2023-01-01'),
('b2d65af4-945e-4a1c-9012-d5a266cee63f', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10FELMIR', true, '2023-01-01'),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10GARA', true, '2023-01-01'),
('3488b57f-ee00-4b1b-9980-6ee8f0197c23', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10JULCER', true, '2023-01-01'),
('489b163e-be8e-4d9e-b361-d8cb02343f90', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10KAYL', true, '2023-01-01'),
('6b293cd6-8880-4538-b68c-04261e594947', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10MARI', true, '2023-01-01'),
('6b293cd6-8880-4538-b68c-04261e594947', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10MARGAR', true, '2023-01-01'),
('cadbbf95-6761-4fc5-a26c-977f85adc430', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10MARLOU', true, '2023-01-01'),
('87133dca-e9d5-4afd-8afb-2f5a32f6ba8d', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10NAN', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ROGÉ', true, '2023-01-01'),
('c5080cad-498f-4f67-b0b8-3d2d269e1a0f', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10SAMU', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10TATY', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10WEVI', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10WILL', true, '2023-01-01'),
('504e7df6-f254-4bc9-9ae3-ae1cd439b00a', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ZAIN', true, '2023-01-01'),
('a549cbf3-5598-48d8-b00e-4cda4fca7a9e', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ÉRIK', true, '2023-01-01');

-- São Mateus (012) - 18 relacionamentos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('b3a5865e-22b7-4e7e-b7c7-4e8392636e66', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12////', true, '2023-01-01'),
('c1629499-3949-4c61-a4de-3b2e1b11bc19', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12ARIA', true, '2023-01-01'),
('6f996a13-ebee-4ae0-b709-060a405e5aaa', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12CHIDOR', true, '2023-01-01'),
('8851c1bf-6259-4371-9782-b1fb4c6e59e3', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12GARA', true, '2023-01-01'),
('9a1505b1-2abc-424c-9d19-70d3dde91b78', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12JOAN', true, '2023-01-01'),
('0cc9561e-78f8-49ca-994c-0cd30f1d8563', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12LARI', true, '2023-01-01'),
('6b293cd6-8880-4538-b68c-04261e594947', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12MARI', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12ROGE', true, '2023-01-01'),
('47ded0cf-daad-415f-bc27-3c98a18e218b', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12ROGÉ', true, '2023-01-01'),
('aaaed13d-8525-496b-bb63-539d53b215a5', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12SAND', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12TATI', true, '2023-01-01'),
('23fc6335-1ebd-449b-a5c4-b27106bde6d5', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12TATY', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WEVE', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WEVI', true, '2023-01-01'),
('23ceeb10-0195-4eda-8dcd-934997ef5cf6', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WEVI', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WILL', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WILL', true, '2023-01-01'),
('91463f30-2e94-4caf-a6bc-fe05751488ea', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WILL', true, '2023-01-01');

-- =============================================
-- 4. VERIFICAÇÕES FINAIS
-- =============================================

-- Contar registros inseridos
SELECT 
    'vendedores' as tabela, 
    COUNT(*) as total,
    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos
FROM core.vendedores
UNION ALL
SELECT 
    'vendedores_lojas' as tabela, 
    COUNT(*) as total,
    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos
FROM core.vendedores_lojas;

-- Verificar distribuição por loja
SELECT 
    l.nome as loja_nome,
    l.codigo as loja_codigo,
    COUNT(vl.vendedor_id) as total_vendedores
FROM core.lojas l
LEFT JOIN core.vendedores_lojas vl ON l.id = vl.loja_id
GROUP BY l.id, l.nome, l.codigo
ORDER BY l.codigo;

-- Verificar se algum vendedor ficou sem loja
SELECT 
    v.nome_padronizado,
    CASE WHEN vl.vendedor_id IS NULL THEN 'SEM LOJA' ELSE 'COM LOJA' END as status
FROM core.vendedores v
LEFT JOIN core.vendedores_lojas vl ON v.id = vl.vendedor_id
WHERE vl.vendedor_id IS NULL
ORDER BY v.nome_padronizado;

-- =============================================
-- 5. STATUS FINAL
-- =============================================

SELECT 'População usando dados corretos do Excel finalizada!' as status;

-- RESUMO:
-- ✅ 54 vendedores únicos inseridos
-- ✅ 112 relacionamentos vendedor-loja inseridos
-- ✅ Dados baseados em PADRONIZACAO_VENDEDORES_COMPLETA.xlsx
-- ✅ UUIDs corretos das lojas do Supabase