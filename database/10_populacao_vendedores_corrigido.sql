-- =============================================
-- POPULAÇÃO NORMALIZADA - VERSÃO CORRIGIDA
-- =============================================
-- 38 vendedores únicos (incluindo BRUNA e THIAGO)

TRUNCATE TABLE core.vendedores_lojas CASCADE;
TRUNCATE TABLE core.vendedores CASCADE;

-- Inserir 38 vendedores únicos
INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at) VALUES
('de96b3f7-cf3b-428f-9cd3-c92a6042a110', '/////////////////////////', '/////////////////////////', '/////////////////////////', true, NOW(), NOW()),
('cd780caa-3cf0-42ac-ada8-17964f7cad60', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', 'ADRIANA ANSELMO', true, NOW(), NOW()),
('28382574-3270-4a12-a820-87f03276ef33', 'ANA', 'ANA', 'ANA', true, NOW(), NOW()),
('e36a93ed-6f79-4ccd-b278-646a94367410', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', 'ANDRESSA DE SOUZA', true, NOW(), NOW()),
('df105bdf-d92b-44e7-86dd-2f486b4eb17b', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', 'ARIANI DIAS FERNANDES CARDOSO', true, NOW(), NOW()),
('4699b10f-5f94-42b6-bf1b-e2afe1b096fa', 'BRUNA', 'BRUNA', 'BRUNA', true, NOW(), NOW()),
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
('9467a1e0-f1ad-4b9c-b126-7060fad638fa', 'THIAGO', 'THIAGO', 'THIAGO', true, NOW(), NOW()),
('c0023125-cf07-42bc-8462-4ddcbe586ce7', 'WEVILLY', 'WEVILLY', 'WEVILLY', true, NOW(), NOW()),
('e68a248c-43af-492a-b758-44a56e835e76', 'WILLIAM', 'WILLIAM', 'WILLIAM', true, NOW(), NOW()),
('0e9c6cc8-e1b1-47a2-b34d-42895ea5a320', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', 'ZAINE DE LIMA SIQUEIRA', true, NOW(), NOW()),
('28352073-a532-4304-ae71-811c51cf54ba', 'ÉRIKA', 'ÉRIKA', 'ÉRIKA', true, NOW(), NOW());

-- Relacionamentos básicos para vendedores corrigidos
INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES
('4699b10f-5f94-42b6-bf1b-e2afe1b096fa', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'VEN12BRUNA', true, '2023-01-01'),
('9467a1e0-f1ad-4b9c-b126-7060fad638fa', '52f92716-d2ba-441a-ac3c-94bdfabd9722', 'VEN42THIAGO', true, '2023-01-01');

-- Verificações
SELECT 'vendedores' as tabela, COUNT(*) as total FROM core.vendedores
UNION ALL
SELECT 'vendedores_lojas' as tabela, COUNT(*) as total FROM core.vendedores_lojas;

SELECT 'População corrigida finalizada!' as status;