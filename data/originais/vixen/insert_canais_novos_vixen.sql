-- Inserção de canais novos do VIXEN
-- Gerado em: 2025-10-30 15:15:52.086752
-- Total de canais novos: 5

BEGIN;


INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('173', 'CAMPANHA CBA', 'Canal importado do VIXEN - 7 clientes', 'OUTROS', true);

INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('174', 'WHATSAPP ROBÔ', 'Canal importado do VIXEN - 5 clientes', 'OUTROS', true);

INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('175', 'CAMPANHA ANIVERSARIANTES', 'Canal importado do VIXEN - 2 clientes', 'OUTROS', true);

INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('176', 'PROSPECÇÃO MABIO', 'Canal importado do VIXEN - 1 clientes', 'OUTROS', true);

INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('177', 'CAMPANHA AILTON', 'Canal importado do VIXEN - 1 clientes', 'OUTROS', true);

COMMIT;
