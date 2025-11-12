-- =============================================
-- POPULAÇÃO NORMALIZADA - SEM DUPLICAÇÕES
-- =============================================
-- 36 vendedores únicos + 77 relacionamentos

TRUNCATE TABLE core.vendedores_lojas CASCADE;
TRUNCATE TABLE core.vendedores CASCADE;

-- Inserir 36 vendedores únicos
INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at) VALUES
('de96b3f7-cf3b-428f-9cd3-c92a6042a110', '/////////////////////////', '/////////////////////////', '/////////////////////////', true, NOW(), NOW()),
('cd780caa-3cf0-42ac-ada8-17964f7cad60', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', true, NOW(), NOW()),
('28382574-3270-4a12-a820-87f03276ef33', 'ANA', 'ANA', 'ANA', true, NOW(), NOW()),
('e36a93ed-6f79-4ccd-b278-646a94367410', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', true, NOW(), NOW()),
('df105bdf-d92b-44e7-86dd-2f486b4eb17b', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', true, NOW(), NOW()),
('c9a76e06-f67b-4b36-a44f-a55716679a2a', 'BRUNO', 'BRUNO', 'BRUNO', true, NOW(), NOW()),
('2cba056b-4da2-486c-a295-485eba8a3d01', 'CARLA CRISTINA', 'CARLA CRISTINA', 'CARLA CRISTINA', true, NOW(), NOW()),
('bf95e71d-a56d-42fc-bef5-5b571f2f8ce7', 'CHINASA DORIS', 'CHINASA DORIS', 'CHINASA DORIS', true, NOW(), NOW()),
('54412296-152b-4b4a-92fe-ad72595f12a2', 'ERICA DE CASSIA JESUS SILVA', 'ERICA DE CASSIA JESUS SILVA', 'ERICA DE CASSIA JESUS SILVA', true, NOW(), NOW()),
('dda060e8-01cd-4843-a97e-75b9887292db', 'FELIPE MIRANDA', 'FELIPE MIRANDA', 'FELIPE MIRANDA', true, NOW(), NOW()),
('4ac1702f-5344-45c1-9a66-0798042678d6', 'GARANTIA', 'GARANTIA', 'GARANTIA', true, NOW(), NOW()),
('b83ff2c9-66c4-4e49-9ee5-3204e57e53f2', 'GUILHERME SILVA', 'GUILHERME SILVA', 'GUILHERME SILVA', true, NOW(), NOW()),
('f192ff87-3449-407e-aa30-b7d4e9970b93', 'JOANA', 'JOANA', 'JOANA', true, NOW(), NOW()),
('2fec96c8-d492-49ab-b38a-a5d5452af4d2', 'JOCICREIDE BARBOSA', 'JOCICREIDE BARBOSA', 'JOCICREIDE BARBOSA', true, NOW(), NOW()),
('d495c411-a99b-4893-ac9c-69da3e29f518', 'JULIANA CERA', 'JULIANA CERA', 'JULIANA CERA', true, NOW(), NOW()),
('168483ea-ef4b-4365-bdb4-e3f82c1b5d11', 'KAYLLAINE', 'KAYLLAINE', 'KAYLLAINE', true, NOW(), NOW()),
('57545079-3f88-4853-890b-ea08f121b981', 'KEREN', 'KEREN', 'KEREN', true, NOW(), NOW()),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', 'LARISSA', 'LARISSA', 'LARISSA', true, NOW(), NOW()),
('271075be-1e7b-4cb7-a4f3-adb982ada858', 'LUANA', 'LUANA', 'LUANA', true, NOW(), NOW()),
('c4ee95ea-cbbc-4341-9dec-b5ddae6750f4', 'MARIA', 'MARIA', 'MARIA', true, NOW(), NOW()),
('b6baa62e-93cb-44de-b2d7-db6fe1dc7b8a', 'MARIA DA SILVA OZORIO', 'MARIA DA SILVA OZORIO', 'MARIA DA SILVA OZORIO', true, NOW(), NOW()),
('c18dc70e-4150-4624-b3dc-b6d9c83db5b7', 'MARIA DE LOURDES', 'MARIA DE LOURDES', 'MARIA DE LOURDES', true, NOW(), NOW()),
('d2eb5739-5887-4c3f-86e9-822f60469650', 'MARIA ELIZABETH', 'MARIA ELIZABETH', 'MARIA ELIZABETH', true, NOW(), NOW()),
('a430363d-78ed-4f7d-a020-329e0e875d64', 'MARIA RAMOS', 'MARIA RAMOS', 'MARIA RAMOS', true, NOW(), NOW()),
('425938ad-7841-48a0-a856-db4b087704a6', 'NAN', 'NAN', 'NAN', true, NOW(), NOW()),
('43b0fa7d-f6cb-43ff-bfd3-b90412f40f0f', 'PIX', 'PIX', 'PIX', true, NOW(), NOW()),
('5e75ae7f-f54a-43ec-b838-3d274ac8c5f2', 'RENAN  NAZARO', 'RENAN  NAZARO', 'RENAN  NAZARO', true, NOW(), NOW()),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', 'ROGERIO APARECIDO DE MORAIS', 'ROGERIO APARECIDO DE MORAIS', 'ROGERIO APARECIDO DE MORAIS', true, NOW(), NOW()),
('b798769b-8ce6-4c9e-8be7-bb46df413eab', 'ROSÂNGELA', 'ROSÂNGELA', 'ROSÂNGELA', true, NOW(), NOW()),
('8eedfaa1-c3c5-4d17-90f5-ab6abfa18471', 'SAMUEL', 'SAMUEL', 'SAMUEL', true, NOW(), NOW()),
('d9fb3699-c609-4e9b-b291-022ebe38d3d6', 'SANDY', 'SANDY', 'SANDY', true, NOW(), NOW()),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', 'TATIANA MELLO DE CAMARGO', 'TATIANA MELLO DE CAMARGO', 'TATIANA MELLO DE CAMARGO', true, NOW(), NOW()),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', 'WEVILLY', 'WEVILLY', 'WEVILLY', true, NOW(), NOW()),
('e68a248c-43af-492a-b758-44a56e835e76', 'WILLIAM', 'WILLIAM', 'WILLIAM', true, NOW(), NOW()),
('0e9c6cc8-e1b1-47a2-b34d-42895ea5a320', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', true, NOW(), NOW()),
('28352073-a532-4304-ae71-811c51cf54ba', 'ÉRIKA', 'ÉRIKA', 'ÉRIKA', true, NOW(), NOW());

-- Inserir 77 relacionamentos únicos
-- Mauá (048) (048) - 11 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('e36a93ed-6f79-4ccd-b278-646a94367410', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ANDSOU', true, '2023-01-01'),
('54412296-152b-4b4a-92fe-ad72595f12a2', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ERICAS', true, '2023-01-01'),
('4ac1702f-5344-45c1-9a66-0798042678d6', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48GARA', true, '2023-01-01'),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48LARI', true, '2023-01-01'),
('271075be-1e7b-4cb7-a4f3-adb982ada858', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48LUAN', true, '2023-01-01'),
('b6baa62e-93cb-44de-b2d7-db6fe1dc7b8a', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48MARSIL', true, '2023-01-01'),
('d2eb5739-5887-4c3f-86e9-822f60469650', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ETH', true, '2023-01-01'),
('5e75ae7f-f54a-43ec-b838-3d274ac8c5f2', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48RENNAZ', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48ROGÉ', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48TATY', true, '2023-01-01'),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'VEN48WEVE', true, '2023-01-01');

-- Perus (009) (009) - 14 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('28382574-3270-4a12-a820-87f03276ef33', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ANA', true, '2023-01-01'),
('df105bdf-d92b-44e7-86dd-2f486b4eb17b', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ARIA', true, '2023-01-01'),
('f192ff87-3449-407e-aa30-b7d4e9970b93', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9JOAN', true, '2023-01-01'),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9LARI', true, '2023-01-01'),
('271075be-1e7b-4cb7-a4f3-adb982ada858', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9LUAN', true, '2023-01-01'),
('c4ee95ea-cbbc-4341-9dec-b5ddae6750f4', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9MARI', true, '2023-01-01'),
('425938ad-7841-48a0-a856-db4b087704a6', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9NAN', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ROGE', true, '2023-01-01'),
('8eedfaa1-c3c5-4d17-90f5-ab6abfa18471', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9SAMU', true, '2023-01-01'),
('d9fb3699-c609-4e9b-b291-022ebe38d3d6', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9SAND', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9TATY', true, '2023-01-01'),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9WEVI', true, '2023-01-01'),
('e68a248c-43af-492a-b758-44a56e835e76', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9WILL', true, '2023-01-01'),
('28352073-a532-4304-ae71-811c51cf54ba', 'da3978c9-bba2-431a-91b7-970a406d3acf', 'VEN9ERIK', true, '2023-01-01');

-- Rio Pequeno (011) (011) - 9 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('c9a76e06-f67b-4b36-a44f-a55716679a2a', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11BRUN', true, '2023-01-01'),
('4ac1702f-5344-45c1-9a66-0798042678d6', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11GARA', true, '2023-01-01'),
('57545079-3f88-4853-890b-ea08f121b981', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11KERE', true, '2023-01-01'),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11LARI', true, '2023-01-01'),
('a430363d-78ed-4f7d-a020-329e0e875d64', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11MARRAM', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11R0GE', true, '2023-01-01'),
('b798769b-8ce6-4c9e-8be7-bb46df413eab', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11ROSA', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11TATY', true, '2023-01-01'),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'VEN11WEVI', true, '2023-01-01');

-- Suzano (042) (042) - 15 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('df105bdf-d92b-44e7-86dd-2f486b4eb17b', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ARIA', true, '2023-01-01'),
('dda060e8-01cd-4843-a97e-75b9887292db', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42FELI', true, '2023-01-01'),
('4ac1702f-5344-45c1-9a66-0798042678d6', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42GARA', true, '2023-01-01'),
('b83ff2c9-66c4-4e49-9ee5-3204e57e53f2', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42GUISIL', true, '2023-01-01'),
('2fec96c8-d492-49ab-b38a-a5d5452af4d2', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42JOCI', true, '2023-01-01'),
('168483ea-ef4b-4365-bdb4-e3f82c1b5d11', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42KAYL', true, '2023-01-01'),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42LARI', true, '2023-01-01'),
('d2eb5739-5887-4c3f-86e9-822f60469650', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42BETH', true, '2023-01-01'),
('425938ad-7841-48a0-a856-db4b087704a6', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42NAN', true, '2023-01-01'),
('43b0fa7d-f6cb-43ff-bfd3-b90412f40f0f', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42PIX', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ROGE', true, '2023-01-01'),
('8eedfaa1-c3c5-4d17-90f5-ab6abfa18471', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42SAMU', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42TATI', true, '2023-01-01'),
('e68a248c-43af-492a-b758-44a56e835e76', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42WILL', true, '2023-01-01'),
('0e9c6cc8-e1b1-47a2-b34d-42895ea5a320', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42ZAIN', true, '2023-01-01');

-- Suzano 2 (010) (010) - 16 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('cd780caa-3cf0-42ac-ada8-17964f7cad60', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ADRANS', true, '2023-01-01'),
('2cba056b-4da2-486c-a295-485eba8a3d01', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10CARCRI', true, '2023-01-01'),
('dda060e8-01cd-4843-a97e-75b9887292db', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10FELI', true, '2023-01-01'),
('4ac1702f-5344-45c1-9a66-0798042678d6', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10GARA', true, '2023-01-01'),
('d495c411-a99b-4893-ac9c-69da3e29f518', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10JULCER', true, '2023-01-01'),
('168483ea-ef4b-4365-bdb4-e3f82c1b5d11', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10KAYL', true, '2023-01-01'),
('c4ee95ea-cbbc-4341-9dec-b5ddae6750f4', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10MARI', true, '2023-01-01'),
('c18dc70e-4150-4624-b3dc-b6d9c83db5b7', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10MARLOU', true, '2023-01-01'),
('425938ad-7841-48a0-a856-db4b087704a6', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10NAN', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ROGÉ', true, '2023-01-01'),
('8eedfaa1-c3c5-4d17-90f5-ab6abfa18471', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10SAMU', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10TATY', true, '2023-01-01'),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10WEVI', true, '2023-01-01'),
('e68a248c-43af-492a-b758-44a56e835e76', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10WILL', true, '2023-01-01'),
('0e9c6cc8-e1b1-47a2-b34d-42895ea5a320', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ZAIN', true, '2023-01-01'),
('28352073-a532-4304-ae71-811c51cf54ba', 'aa7a5646-f7d6-4239-831c-6602fbabb10a', 'VEN10ERIC', true, '2023-01-01');

-- São Mateus (012) (012) - 12 vendedores
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('de96b3f7-cf3b-428f-9cd3-c92a6042a110', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12////', true, '2023-01-01'),
('df105bdf-d92b-44e7-86dd-2f486b4eb17b', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12ARIA', true, '2023-01-01'),
('bf95e71d-a56d-42fc-bef5-5b571f2f8ce7', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12CHIDOR', true, '2023-01-01'),
('4ac1702f-5344-45c1-9a66-0798042678d6', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12GARA', true, '2023-01-01'),
('f192ff87-3449-407e-aa30-b7d4e9970b93', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12JOAN', true, '2023-01-01'),
('c6090f60-cb5c-4b0a-8227-31d0ff98c226', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12LARI', true, '2023-01-01'),
('c4ee95ea-cbbc-4341-9dec-b5ddae6750f4', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12MARI', true, '2023-01-01'),
('22ea8fe8-34cd-4b68-b56c-33e63f5290f8', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12ROGE', true, '2023-01-01'),
('d9fb3699-c609-4e9b-b291-022ebe38d3d6', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12SAND', true, '2023-01-01'),
('e1ff66f6-c10e-4601-a4e0-23d2318ff138', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12TATI', true, '2023-01-01'),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WEVE', true, '2023-01-01'),
('e68a248c-43af-492a-b758-44a56e835e76', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12WILL', true, '2023-01-01');

-- Verificações
SELECT 'vendedores' as tabela, COUNT(*) as total FROM core.vendedores
UNION ALL
SELECT 'vendedores_lojas' as tabela, COUNT(*) as total FROM core.vendedores_lojas;

SELECT 'População normalizada finalizada - SEM DUPLICAÇÕES!' as status;