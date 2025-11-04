-- ===============================================
-- ESTRUTURA COMPLETA DE CANAIS DE AQUISIÇÃO
-- ===============================================
-- Gerado automaticamente em: 2025-10-29
-- Total de canais: 171

-- Remover tabela anterior se existir
DROP TABLE IF EXISTS marketing.canais_captacao CASCADE;
DROP TABLE IF EXISTS marketing.canais_aquisicao CASCADE;

-- Criar tabela com estrutura UUID
CREATE TABLE marketing.canais_aquisicao (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    codigo VARCHAR(10) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NULL,
    categoria VARCHAR(50) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT true,
    criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT canais_aquisicao_pkey PRIMARY KEY (id),
    CONSTRAINT canais_aquisicao_codigo_key UNIQUE (codigo)
);

-- Criar índices para performance
CREATE INDEX idx_canais_aquisicao_codigo ON marketing.canais_aquisicao (codigo);
CREATE INDEX idx_canais_aquisicao_categoria ON marketing.canais_aquisicao (categoria);
CREATE INDEX idx_canais_aquisicao_ativo ON marketing.canais_aquisicao (ativo);
CREATE INDEX idx_canais_aquisicao_nome ON marketing.canais_aquisicao (nome);

-- Trigger para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_canais_aquisicao_updated_at
    BEFORE UPDATE ON marketing.canais_aquisicao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Inserir 171 canais de aquisição
INSERT INTO marketing.canais_aquisicao (
    id,
    codigo,
    nome,
    descricao,
    categoria,
    ativo
) VALUES
    ('abe868a2-e462-4d01-969d-338cd1db900e', '1', 'REDE SOCIAL', 'REDE SOCIAL', 'DIGITAL', true),
    ('06ab4dc9-11ab-416e-91a1-e51b3c02d16d', '2', 'SITE', 'SITE', 'DIGITAL', true),
    ('d71a5107-9088-4016-bf1f-9a42cf16409d', '3', 'QUEM INDICA AMIGO É', 'QUEM INDICA AMIGO É', 'INDICACAO', true),
    ('d8f4935d-6226-484b-a061-816efd307add', '4', 'JÁ É CLIENTE', 'JÁ É CLIENTE', 'INDICACAO', true),
    ('f7856afe-c69f-402d-8e81-a8b890ca1b73', '5', 'PANFLETOS', 'PANFLETOS', 'MARKETING', true),
    ('2df5d718-2388-4b3d-824d-481686e311f4', '6', 'EMPRESA ATENTO', 'EMPRESA ATENTO', 'PARCERIA', true),
    ('8e5c8565-208f-4938-a9df-fc1aec2e2c5e', '7', 'DR ÁLVARO', 'DR ÁLVARO', 'MEDICO', true),
    ('709242cb-4d7d-45db-be68-e6f23c6ffc77', '8', 'TERMINAL SANTANA', 'TERMINAL SANTANA', 'OUTROS', true),
    ('2f57a988-6ee4-4637-a612-c10fc7f21872', '9', 'CLINICA MED', 'CLINICA MED', 'MEDICO', true),
    ('15d63509-98fb-4c3e-ac73-d544f89fb505', '10', 'MAGAZINE LUIZA', 'MAGAZINE LUIZA', 'PARCERIA', true),
    ('68e0f96d-f0a8-4279-86fd-28f33326ba47', '11', 'PASSAGEM', 'PASSAGEM', 'ABORDAGEM', true),
    ('d2ea6adc-2bcb-4dc3-9fcf-6e8627f44215', '12', 'CARRO DE SOM', 'CARRO DE SOM', 'MARKETING', true),
    ('bbdeefdb-eefb-474c-86db-98576299ca97', '13', 'VITRINE', 'VITRINE', 'OUTROS', true),
    ('25e79af4-17e9-4235-8e6d-90a6bfd75540', '14', 'PLACA DE LOJA', 'PLACA DE LOJA', 'MARKETING', true),
    ('b7c80865-bd26-4253-849f-1932f3feb607', '15', 'ORÇAMENTO', 'ORÇAMENTO', 'OUTROS', true),
    ('6a71ed7c-0a9a-4c6b-87a1-878292507ab3', '16', 'INDICAÇÃO', 'INDICAÇÃO', 'INDICACAO', true),
    ('0f34df74-93d2-4817-ac1d-d1a2b6f77c78', '17', 'ABORDAGEM', 'ABORDAGEM', 'ABORDAGEM', true),
    ('ccd54f11-c9b8-47f5-8b1b-b2023e5f2b01', '18', 'RADIO TROPICAL', 'RADIO TROPICAL', 'RADIO', true),
    ('715b33a7-28c5-48b2-a900-65c19fc8c5ff', '19', 'CARRETA', 'CARRETA', 'OUTROS', true),
    ('43c29836-ebdc-4c01-8593-1c9b3a56f0cb', '20', 'RADIO ESPERANCA', 'RADIO ESPERANCA', 'RADIO', true),
    ('48959092-6a20-439c-8fe0-24432e70e385', '21', 'TELEMARKETING', 'TELEMARKETING', 'ABORDAGEM', true),
    ('c0ea407e-3fcf-4432-9c55-ed2281ca0fb5', '22', 'OUTDOOR', 'OUTDOOR', 'MARKETING', true),
    ('5b1f187c-6041-4ba4-9197-0351b8b40fdd', '23', 'CAMPANHA VADO', 'CAMPANHA VADO', 'MARKETING', true),
    ('5d26b48f-0d65-4c64-8310-138d4c4ce5e6', '24', 'CLINICA', 'CLINICA', 'MEDICO', true),
    ('fb2292e4-27b9-45e4-8081-fe33d0b7a7ad', '25', 'DR EDSON', 'DR EDSON', 'MEDICO', true),
    ('1e6265af-34a2-4855-8af0-17f4083762b0', '26', 'DROGARIA SÃO PAULO', 'DROGARIA SÃO PAULO', 'FARMACIA', true),
    ('5ac12c06-6f1b-4063-8253-103ab54e7160', '27', 'DROGARIA SUPERMED', 'DROGARIA SUPERMED', 'FARMACIA', true),
    ('455a8516-8b12-40e0-b5cb-92048ea1ecba', '28', 'DROGARIA DROGALIS', 'DROGARIA DROGALIS', 'FARMACIA', true),
    ('658d82fd-4819-4c32-a02e-3fe3a5d16654', '29', 'SIND SINETROSV', 'SIND SINETROSV', 'INSTITUCIONAL', true),
    ('78a2248c-de8a-4406-afcc-136bc9e8003e', '30', 'MEDILINE ASSISTENCIA', 'MEDILINE ASSISTENCIA', 'OUTROS', true),
    ('6a9c003c-5e60-4a00-ba87-49f15ba3b309', '31', 'SIND CORREIOS', 'SIND CORREIOS', 'INSTITUCIONAL', true),
    ('e9295138-93dd-4766-b0df-1e246bfe79d5', '32', 'IAMSPE', 'IAMSPE', 'OUTROS', true),
    ('c5a04a4e-53a1-4867-a397-93cb9c02fe9e', '33', 'OPEN LINE', 'OPEN LINE', 'OUTROS', true),
    ('437e3806-dfcf-4891-b003-5d2eff82c3d2', '34', 'ABMED', 'ABMED', 'OUTROS', true),
    ('28c4e4a5-a82f-44c4-9bb6-424343160801', '35', 'CLUB GOLD STAR', 'CLUB GOLD STAR', 'OUTROS', true),
    ('8d0b0865-6bcf-489b-980e-5478c56b72e8', '36', 'VALE SAUDE JEQUITI', 'VALE SAUDE JEQUITI', 'OUTROS', true),
    ('0dea79f0-86e7-4691-9d31-39478e05da92', '37', 'SIND SINDSERVITA', 'SIND SINDSERVITA', 'INSTITUCIONAL', true),
    ('120378ae-6cb8-4763-84ee-16c9984c67c1', '38', 'DIVULGADOR', 'DIVULGADOR', 'DIVULGADOR', true),
    ('45c80de7-1f50-4706-9a7d-23ae11924df4', '39', 'DV BARBARA MATOS', 'DV BARBARA MATOS', 'DIVULGADOR', true),
    ('a529868a-5c2d-4f6e-a45d-1237d15dae03', '40', 'SIND SINTRAMMSP', 'SIND SINTRAMMSP', 'INSTITUCIONAL', true),
    ('fb315d0c-3663-4d20-9677-6f05c70da677', '41', 'SEGUROS UNIMED', 'SEGUROS UNIMED', 'CONVENIO', true),
    ('a7ad8056-8c5e-4d4a-a8d2-1df24bd441d1', '42', 'AMEPLAN', 'AMEPLAN', 'OUTROS', true),
    ('8c913e35-b471-46ee-bf3f-40069ef2b644', '43', 'CRUZ AZUL', 'CRUZ AZUL', 'OUTROS', true),
    ('ae3e4828-b4b6-4d52-a7eb-bf5437e601f9', '44', 'CONVENIO FL', 'CONVENIO FL', 'CONVENIO', true),
    ('8983f4f5-fec5-4d80-8082-8dcac4c4ee23', '45', 'RADIO ADORE FM', 'RADIO ADORE FM', 'RADIO', true),
    ('fdabd3cd-1ba0-4152-8771-05bb866c8f5b', '46', 'CONVENIO JASON', 'CONVENIO JASON', 'CONVENIO', true),
    ('d1b843e6-7d37-4146-bfa8-39489a36e3b4', '47', 'DV NAYARA COSTA', 'DV NAYARA COSTA', 'DIVULGADOR', true),
    ('f74db1ab-c63c-4b7a-bc5b-7422875aab35', '48', 'RX DE FORA', 'RX DE FORA', 'OUTROS', true),
    ('be28b84f-a99c-402d-bf67-384a2d78e482', '49', 'ALEFARMA', 'ALEFARMA', 'FARMACIA', true),
    ('9c127565-6841-4120-8cc3-06db34fd75b0', '50', 'PROGRAMA SHOW', 'PROGRAMA SHOW', 'OUTROS', true),
    ('80494142-6a31-4e6e-8d31-7812465dcc11', '51', 'NOVA X', 'NOVA X', 'OUTROS', true),
    ('8e169657-e3f3-498f-9c40-309711cd293e', '52', 'DROGARIA CAMPEA', 'DROGARIA CAMPEA', 'FARMACIA', true),
    ('1c45dd34-eca4-440a-a7ad-1469e693d8ae', '53', 'SANTA TEREZINHA ASSOCIAÇÃO', 'SANTA TEREZINHA ASSOCIAÇÃO', 'OUTROS', true),
    ('3cd4dc88-7476-4c62-8684-5b9e31fd2d7d', '54', 'PREFEITURA', 'PREFEITURA', 'INSTITUCIONAL', true),
    ('518b9cc8-59de-4887-927e-0bcd4f30c1a1', '55', 'CARTAO DE TODOS', 'CARTAO DE TODOS', 'OUTROS', true),
    ('1a381ab9-17e7-4907-af11-1ba06734de3d', '56', 'PLENA SAÚDE', 'PLENA SAÚDE', 'MEDICO', true),
    ('d708709e-54cc-4dcf-86cd-b1ca909a5a40', '57', 'SUBPREFEITURA', 'SUBPREFEITURA', 'INSTITUCIONAL', true),
    ('966b912d-2330-43a4-b5ed-1dbf9ace452f', '58', 'CARTÃO INDICAÇÃO', 'CARTÃO INDICAÇÃO', 'INDICACAO', true),
    ('245a43ab-0e12-4ace-938c-3040bbca576a', '59', 'SITAP - LINEX', 'SITAP - LINEX', 'OUTROS', true),
    ('70349148-fbf1-4ed2-9d61-44a398bb0bb1', '60', 'ASSEMBLEIA DE DEUS', 'ASSEMBLEIA DE DEUS', 'RELIGIOSO', true),
    ('de3ce605-f83e-4b26-bb57-01ce8fac25ad', '61', 'INDICAÇÃO CONVÊNIO PREFEITURA', 'INDICAÇÃO CONVÊNIO PREFEITURA', 'INDICACAO', true),
    ('245bf991-8378-4233-a747-efb1aae76c0a', '62', 'CONVENIO MWI', 'CONVENIO MWI', 'CONVENIO', true),
    ('f6a931ec-21db-4f11-9f9a-774cf43a01e9', '63', '1ª COMPRA', '1ª COMPRA', 'OUTROS', true),
    ('9f73eeff-22ed-4283-865c-a3c2833d3795', '64', 'CONVENIO FAN', 'CONVENIO FAN', 'CONVENIO', true),
    ('708b0b04-42e7-41e6-a924-8407d47e12bb', '65', 'VISIOTESTE', 'VISIOTESTE', 'OUTROS', true),
    ('153b0222-2948-432d-b26b-9b633d1428b7', '66', 'CLINICA ALPHA VISION', 'CLINICA ALPHA VISION', 'MEDICO', true),
    ('5495f595-2d64-4e26-b8b7-69d22be870c5', '67', 'DV JOÃO PAULO', 'DV JOÃO PAULO', 'DIVULGADOR', true),
    ('6e55a821-8248-440f-af42-6b53f375f936', '68', 'RADIO NOVA X 103.1', 'RADIO NOVA X 103.1', 'RADIO', true),
    ('93e45709-a824-4e12-8475-09b7c12c0634', '69', 'RADIO REDE UNÇÃO 96.5', 'RADIO REDE UNÇÃO 96.5', 'RADIO', true),
    ('a7bb9956-54f1-4f0d-84c3-ee8bee798eda', '70', 'DV SUELEN RODRIGUES', 'DV SUELEN RODRIGUES', 'DIVULGADOR', true),
    ('b8f6a97c-b862-4ee9-b774-e978cc8ea0be', '71', 'DV GABRIELA SILVA', 'DV GABRIELA SILVA', 'DIVULGADOR', true),
    ('cb60b851-f745-4cdf-9adc-feb8a74cfca5', '72', 'ULTRASOM', 'ULTRASOM', 'OUTROS', true),
    ('be1dcad0-3881-4ed1-b343-69d9a5cbd03c', '73', 'RADIO ATALAIA', 'RADIO ATALAIA', 'RADIO', true),
    ('d3348120-f108-4cca-a3fd-6543ad803b39', '74', 'DV MIKELY FORTALEZA', 'DV MIKELY FORTALEZA', 'DIVULGADOR', true),
    ('218eb2ff-df6a-40f3-ab60-941a09129c0e', '75', 'DR RAFAEL BORGES', 'DR RAFAEL BORGES', 'MEDICO', true),
    ('429c048b-2b6d-4814-a04a-063e8f18b244', '76', 'DR RENATO MACCIONE', 'DR RENATO MACCIONE', 'MEDICO', true),
    ('e196578e-2cab-49fc-8ecd-530be7abf70d', '77', 'AMIGOS', 'AMIGOS', 'INDICACAO', true),
    ('dff22673-5a5c-4444-ba71-a4b9f7c21c30', '78', 'DR RAFAEL PIVATTO', 'DR RAFAEL PIVATTO', 'MEDICO', true),
    ('64922d96-e0b9-4a26-944c-5ae17417a995', '79', 'SUS', 'SUS', 'INSTITUCIONAL', true),
    ('e3cbad79-42dc-4968-8ad0-a7d6b0219c00', '80', 'CESTA BÁSICA', 'CESTA BÁSICA', 'OUTROS', true),
    ('4ff53bf6-7f5c-4e5d-9880-2fb5603ba169', '81', 'ADEASP', 'ADEASP', 'OUTROS', true),
    ('bb64ce7f-f560-4105-9937-dc1029611fa2', '82', 'RADIO IMPRENSA FM', 'RADIO IMPRENSA FM', 'RADIO', true),
    ('b1da2af4-4aad-4a7e-bb6c-583ff08b156a', '83', 'RADIO TERRA', 'RADIO TERRA', 'RADIO', true),
    ('f5eae224-7d81-448e-9e95-bddeff8fe9a1', '84', 'PROJETO CUIDAR', 'PROJETO CUIDAR', 'OUTROS', true),
    ('fad47b90-8520-423a-84ed-155ddc969579', '85', 'CONVENIO INTERMÉDICA', 'CONVENIO INTERMÉDICA', 'CONVENIO', true),
    ('61bbfd37-5bf9-41ac-86ff-59acd1a6357c', '86', 'BIO SAÚDE', 'BIO SAÚDE', 'MEDICO', true),
    ('036ef220-07da-4e79-af43-a54573e8eb38', '87', 'CARTÃO COMPLETO', 'CARTÃO COMPLETO', 'MARKETING', true),
    ('2c3d43eb-6792-4857-a384-8b2eb2019e84', '88', 'DV VICTOR HUGO', 'DV VICTOR HUGO', 'DIVULGADOR', true),
    ('eaa240d6-bd79-49ad-a498-2125f752f6be', '89', 'RADIO FÉ 101.5', 'RADIO FÉ 101.5', 'RADIO', true),
    ('c336e218-f9b1-438d-9e05-d88d2788382e', '90', 'DV LARISSA SILVA', 'DV LARISSA SILVA', 'DIVULGADOR', true),
    ('72ef1d14-abbc-4283-81c3-9c13b5de533c', '91', 'DV LARISSA COSTA', 'DV LARISSA COSTA', 'DIVULGADOR', true),
    ('b38270ad-3236-47b6-81d1-35be269021ca', '92', 'DV MARIANA COSTA', 'DV MARIANA COSTA', 'DIVULGADOR', true),
    ('7828f3c9-d005-4225-adbf-458f20c1f525', '93', 'DV MAICON OLIVEIRA', 'DV MAICON OLIVEIRA', 'DIVULGADOR', true),
    ('36a9db95-f171-4a74-8f26-3391b705beca', '94', 'DV ERICK ANJOS', 'DV ERICK ANJOS', 'DIVULGADOR', true),
    ('bfa09302-eb7f-427a-9fd9-c5e377cfce40', '95', 'DV ALINE CRUZ', 'DV ALINE CRUZ', 'DIVULGADOR', true),
    ('662a0d93-c9ff-4ccb-973c-ac9821722fff', '96', 'DROGARIA DROGASIL', 'DROGARIA DROGASIL', 'FARMACIA', true),
    ('63b34d36-d631-4cb5-981b-32d0e8729501', '97', 'LOJA FECHADA', 'LOJA FECHADA', 'OUTROS', true),
    ('9d74fc0a-11c1-4a1e-b11d-fd0207cd2f87', '98', 'WHATSAPP', 'WHATSAPP', 'DIGITAL', true),
    ('6e86d96a-121b-45e6-a1a4-2848e6d59f85', '99', 'OUTROS', 'OUTROS', 'OUTROS', true),
    ('64dd4ea8-f919-458f-999b-8d0f7eae67a6', '100', 'TESTE', 'TESTE', 'OUTROS', true),
    ('a0fb4bf4-6e5b-4c15-9c95-789b183bf0a0', '101', 'DV JACIANE DINIZ', 'DV JACIANE DINIZ', 'DIVULGADOR', true),
    ('7490ef31-eb86-4efe-a18b-74950030d71d', '102', 'DV ANDERSON KENION', 'DV ANDERSON KENION', 'DIVULGADOR', true),
    ('b7efa8b5-3d20-4b3b-885f-2bcf03aaca4d', '103', 'DV WESLLEY ABREU', 'DV WESLLEY ABREU', 'DIVULGADOR', true),
    ('de26e261-3c1d-49a8-b609-ef2c26f4aa3f', '104', 'DV EMERSON DE JESUS', 'DV EMERSON DE JESUS', 'DIVULGADOR', true),
    ('7a8b5d05-8c50-419f-81f3-4d28deb94114', '105', 'SUPERMERCADO SÃO JOSE', 'SUPERMERCADO SÃO JOSE', 'PARCERIA', true),
    ('98d84b5f-7f6a-41b1-8187-2ce2fc57bf1d', '106', 'FEIRA VILA AMORIM', 'FEIRA VILA AMORIM', 'PARCERIA', true),
    ('9541dc6b-79e8-4952-83ef-a4817781cff7', '107', 'LUIS FIO FOLHETOS', 'LUIS FIO FOLHETOS', 'OUTROS', true),
    ('c7f1d3fe-1da9-4359-8d0f-8f9150464c2b', '108', 'DV BRYAN NASCIMENTO', 'DV BRYAN NASCIMENTO', 'DIVULGADOR', true),
    ('14b42bdf-849a-4877-88ba-8dd8d18324ab', '109', 'PREVINA JORDANESIA', 'PREVINA JORDANESIA', 'OUTROS', true),
    ('5eb59ba2-e778-4d89-b42e-f99e70a7c93a', '110', 'PREFEITO NO SEU BAIRRO', 'PREFEITO NO SEU BAIRRO', 'OUTROS', true),
    ('0b0f23d6-1546-48bd-9d75-22ae3997b28d', '111', 'BOLIVIANOS', 'BOLIVIANOS', 'OUTROS', true),
    ('f1599c20-68f7-4aae-9bf1-e727e4a9711a', '112', 'ELIS', 'ELIS', 'OUTROS', true),
    ('471710df-b89c-4c6d-9882-ff20bb821ef2', '113', 'MARTINS LOCOCO', 'MARTINS LOCOCO', 'OUTROS', true),
    ('1a43532d-47c1-4b2d-a452-76dad4f984ff', '114', 'HOSPITAL STELLA MARIS', 'HOSPITAL STELLA MARIS', 'MEDICO', true),
    ('eda29104-94ef-4860-b56f-c999bc9c0c4c', '115', 'FLORIPARK', 'FLORIPARK', 'OUTROS', true),
    ('5bb60fc5-d779-436a-92ef-e09bc365cc4c', '116', 'RD ESP', 'RD ESP', 'OUTROS', true),
    ('b84f75de-de72-44e2-b3ad-2276f811c4b8', '117', 'MINDBE', 'MINDBE', 'OUTROS', true),
    ('771809e6-0ed5-4981-ac23-4b116fe58f9f', '118', 'GUIMA', 'GUIMA', 'OUTROS', true),
    ('fa815349-9eec-46c4-8f4c-b077402f821a', '119', 'DR GUILHERME H J', 'DR GUILHERME H J', 'MEDICO', true),
    ('988c1546-635e-406a-9be2-77c4cda30ab0', '120', 'CONVENIO INTERMÉDICA', 'CONVENIO INTERMÉDICA', 'CONVENIO', true),
    ('b1a0912d-ace5-40cf-8404-bbfa79a4b3a0', '121', 'DR MARIA EUGENIA BUSCA', 'DR MARIA EUGENIA BUSCA', 'MEDICO', true),
    ('2f0f277c-eea9-41ad-9274-6b353d65c7bd', '122', 'DR MARCELO KENDI FUJII', 'DR MARCELO KENDI FUJII', 'MEDICO', true),
    ('254bb499-e501-4430-bb44-6394f4539d7e', '123', 'DR KIU SUB SHIN', 'DR KIU SUB SHIN', 'MEDICO', true),
    ('70840c12-1d2d-4780-9b30-f3a8844933b5', '124', 'DR MARCUS TAKATSU', 'DR MARCUS TAKATSU', 'MEDICO', true),
    ('aea169db-21b1-4767-a6fb-3e2f7f91c9ea', '125', 'DV THALITA ASSIS', 'DV THALITA ASSIS', 'DIVULGADOR', true),
    ('bcb4d2af-0541-4b32-9b81-7f045be26501', '126', 'DV DENILSON', 'DV DENILSON', 'DIVULGADOR', true),
    ('0e8d97a1-be1a-4d5b-8efe-53a2c9c1d6f7', '127', 'DV ANDERSON', 'DV ANDERSON', 'DIVULGADOR', true),
    ('132eb0c3-123c-4905-9600-4fdf383f1e48', '128', 'DV ROBSON OLIVEIRA', 'DV ROBSON OLIVEIRA', 'DIVULGADOR', true),
    ('b524029f-87a5-43e1-b304-664a7d5df3d3', '129', 'DV RAFAELA GOMES', 'DV RAFAELA GOMES', 'DIVULGADOR', true),
    ('9f1dc73c-eef3-4223-99d2-e264dfded512', '130', 'DV JEAN LEANDRO', 'DV JEAN LEANDRO', 'DIVULGADOR', true),
    ('cfdd63ec-e949-4c8c-b24b-7b5759296435', '131', 'DV NIKE', 'DV NIKE', 'DIVULGADOR', true),
    ('0a98b982-e1af-42a8-a384-5e323ec15fdd', '132', 'DV NATALIA', 'DV NATALIA', 'DIVULGADOR', true),
    ('dd5ef344-3fbd-453f-92c9-441edef8d5f3', '133', 'DV LETICIA', 'DV LETICIA', 'DIVULGADOR', true),
    ('5395a65f-6f3d-4e30-a0ef-f448126e97e9', '134', 'INTERGALAXY SA', 'INTERGALAXY SA', 'OUTROS', true),
    ('32b44322-1a0e-4a2c-b25b-00b89031c7a6', '135', 'DR BEATRIZ NAKAGOME', 'DR BEATRIZ NAKAGOME', 'MEDICO', true),
    ('9b7b0f05-86b0-4ffe-b5ab-982210ea10b7', '136', 'DR GILVAN VILARINHO', 'DR GILVAN VILARINHO', 'MEDICO', true),
    ('7c17b301-1b7f-49a2-8216-1e29559cfef2', '137', 'DR MARCOS VINICIUS PRADO', 'DR MARCOS VINICIUS PRADO', 'MEDICO', true),
    ('a14a2eac-53ec-40d5-a1b6-c218006503f6', '138', 'SAÚDE DOS OLHOS', 'SAÚDE DOS OLHOS', 'MEDICO', true),
    ('bda66e19-69b9-40bf-8573-da8f008a66fe', '139', 'DR JOÃO VICTOR RAMOS DE TOLEDO', 'DR JOÃO VICTOR RAMOS DE TOLEDO', 'MEDICO', true),
    ('d0c3f201-2d18-4f60-974d-2953c33f7344', '140', 'DR ALEXANDRE TOMIO UMINO', 'DR ALEXANDRE TOMIO UMINO', 'MEDICO', true),
    ('99d81798-6598-4717-8f0a-f7e331523428', '141', 'DR ALLAN GOMES DA SILVA', 'DR ALLAN GOMES DA SILVA', 'MEDICO', true),
    ('7ab9a463-1f01-4b34-86c2-2d2b1639f5a1', '142', 'DR AMANDA A VV DE CASTRO', 'DR AMANDA A VV DE CASTRO', 'MEDICO', true),
    ('0233c9b7-08ac-4895-819b-d2842276b57c', '143', 'DR GABRIEL CASTILHO SANDOVAL', 'DR GABRIEL CASTILHO SANDOVAL', 'MEDICO', true),
    ('4e935cc0-bc84-4a72-9d06-04d0eb3444cb', '144', 'DR MAURICIO FLANK', 'DR MAURICIO FLANK', 'MEDICO', true),
    ('aaf7ec6c-38a0-44e2-97e1-3c49e2effc84', '145', 'INTS', 'INTS', 'OUTROS', true),
    ('2dd30e98-447d-438a-95a4-5fb837ab13ab', '146', 'DR MARCIA FERRARI PEREZ', 'DR MARCIA FERRARI PEREZ', 'MEDICO', true),
    ('439e1731-4e91-49e6-b82d-1f12faf64c31', '147', 'INSTITUTO SUEL ABUJAMRA', 'INSTITUTO SUEL ABUJAMRA', 'OUTROS', true),
    ('ddb9b0a3-1171-46e6-a96c-b44bd4028a2b', '149', 'RADIO ÔMEGA', 'RADIO ÔMEGA', 'RADIO', true),
    ('7e3706b7-bf5c-493b-aac1-23edb01bf98c', '150', 'DR CRISTINA FREIRE', 'DR CRISTINA FREIRE', 'MEDICO', true),
    ('7a63b302-1ad9-4008-9041-536455668867', '151', 'ARKIMEDES CENTRO MÉDICO', 'ARKIMEDES CENTRO MÉDICO', 'MEDICO', true),
    ('04ad35d2-cd24-415b-852c-c9203bddd833', '152', 'GOOGLE/FACE/INSTA - PATROCÍNIO', 'GOOGLE/FACE/INSTA - PATROCÍNIO', 'DIGITAL', true),
    ('8174f746-0f9e-40a4-a2e9-390fa9cfc886', '153', 'DR CAROLINA REZENDE', 'DR CAROLINA REZENDE', 'MEDICO', true),
    ('29c5a511-7698-4db2-aa28-b7bd78ccf9f0', '154', 'DR GUILHERME  M.KAPPEL', 'DR GUILHERME  M.KAPPEL', 'MEDICO', true),
    ('017b6295-c5bf-43ee-b8c8-9cab19d3a00c', '155', 'DR WALTHER CAMPOS NETO', 'DR WALTHER CAMPOS NETO', 'MEDICO', true),
    ('9ac5be31-cd0a-439c-afc3-c243df4de4a0', '156', 'DR ANESIO RUIZ', 'DR ANESIO RUIZ', 'MEDICO', true),
    ('4c2c7207-dc2a-454e-bab8-193ddb8df5b5', '157', 'DR LIVIA FERRAZ', 'DR LIVIA FERRAZ', 'MEDICO', true),
    ('a87cff4c-2893-4fa3-b55c-0f97591c5501', '158', 'TRANSPPASS', 'TRANSPPASS', 'OUTROS', true),
    ('70f07f01-53e8-4632-b7e2-e85ff75550bc', '159', 'CLINICA DIMEG', 'CLINICA DIMEG', 'MEDICO', true),
    ('27b009ac-5144-4861-8b1b-e7462545a0ab', '160', 'CONVENIO PARTMED', 'CONVENIO PARTMED', 'CONVENIO', true),
    ('3211e1c4-48de-4886-9be5-8717bff60818', '161', 'OUTRA LOJA', 'OUTRA LOJA', 'INDICACAO', true),
    ('815fc461-9cdd-4a89-a841-3482b963aef0', '162', 'DR GUILHERME S. MOTTA', 'DR GUILHERME S. MOTTA', 'MEDICO', true),
    ('205fd0e6-c82a-4a0b-a650-d0efe2ad058e', '163', 'IGREJA PLENITUDE', 'IGREJA PLENITUDE', 'RELIGIOSO', true),
    ('501e0018-6756-49ff-a461-00da3266e180', '164', 'CAMPANHA COMPRE 1 LEVE 3', 'CAMPANHA COMPRE 1 LEVE 3', 'MARKETING', true),
    ('42d5d6f6-5919-4ed0-8eb7-b1f884c74703', '165', 'CAMPANHA NINJAS', 'CAMPANHA NINJAS', 'MARKETING', true),
    ('a9f5deda-8f4a-4ec1-96d4-7d610d2702c9', '166', 'DV BRUNA RAFAELLA DA SILVA', 'DV BRUNA RAFAELLA DA SILVA', 'DIVULGADOR', true),
    ('6058ee92-1d45-4196-830f-ec4686692bba', '167', 'DV GRAZIELA SANTOS FERREIRA', 'DV GRAZIELA SANTOS FERREIRA', 'DIVULGADOR', true),
    ('9dc8d9cd-cf21-4129-b7a2-af2011c13728', '168', 'DV TAIS CARDOSO', 'DV TAIS CARDOSO', 'DIVULGADOR', true),
    ('4c9995a2-c585-4956-8150-8d1aed4d17ab', '169', 'DV DOUGLAS JESUS DA SILVA', 'DV DOUGLAS JESUS DA SILVA', 'DIVULGADOR', true),
    ('5ba76386-f46d-4f29-8fbf-3f2216939548', '170', 'PENITENCIARIA FEM SÃO PAULO', 'PENITENCIARIA FEM SÃO PAULO', 'OUTROS', true),
    ('b055deac-9a76-45d3-9762-32af80573fd0', '171', 'KOMBOS', 'KOMBOS', 'OUTROS', true),
    ('e4b03b40-f564-4f2e-8e25-a87121548237', '172', 'CAMPANHA LYOR', 'CAMPANHA LYOR', 'MARKETING', true);

-- ===============================================
-- ESTATÍSTICAS E CONSULTAS
-- ===============================================

-- Total de canais inseridos: 171

-- Verificar inserção por categoria:
SELECT 
    categoria,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
FROM marketing.canais_aquisicao
GROUP BY categoria
ORDER BY quantidade DESC;

-- Listar todos os canais por categoria:
SELECT 
    categoria,
    codigo,
    nome,
    ativo
FROM marketing.canais_aquisicao
ORDER BY categoria, CAST(codigo AS INTEGER);

-- Top 10 canais mais baixos (provavelmente mais importantes):
SELECT 
    codigo,
    nome,
    categoria
FROM marketing.canais_aquisicao
ORDER BY CAST(codigo AS INTEGER)
LIMIT 10;

-- Contar por categoria:
-- OUTROS: 43 canais
-- MEDICO: 36 canais
-- DIVULGADOR: 32 canais
-- RADIO: 10 canais
-- MARKETING: 9 canais
-- CONVENIO: 8 canais
-- INDICACAO: 7 canais
-- INSTITUCIONAL: 7 canais
-- FARMACIA: 6 canais
-- DIGITAL: 4 canais
-- PARCERIA: 4 canais
-- ABORDAGEM: 3 canais
-- RELIGIOSO: 2 canais

-- ===============================================
-- COMENTÁRIOS SOBRE AS CATEGORIAS
-- ===============================================
-- MEDICO: Médicos e profissionais de saúde que indicam pacientes
-- DIVULGADOR: Pessoas físicas que fazem divulgação ativa
-- DIGITAL: Canais online (redes sociais, site, WhatsApp, Google)
-- RADIO: Estações de rádio e propaganda sonora
-- CONVENIO: Planos de saúde e convênios médicos
-- INDICACAO: Indicações de clientes, amigos e outras lojas
-- MARKETING: Campanhas, outdoor, panfletos, placas
-- FARMACIA: Parcerias com farmácias e drogarias
-- INSTITUCIONAL: Órgãos públicos, sindicatos, SUS
-- PARCERIA: Empresas parceiras (Magazine Luiza, supermercados)
-- ABORDAGEM: Abordagem direta, telemarketing, passagem
-- RELIGIOSO: Igrejas e instituições religiosas
-- OUTROS: Demais canais não categorizados especificamente
