-- ====================================================================
-- EXECUÇÃO DOS CANAIS NOVOS DO VIXEN
-- ====================================================================
-- Data: 30/10/2025
-- Objetivo: Inserir 5 canais novos identificados na limpeza do VIXEN
-- Status: PRONTO PARA EXECUÇÃO
-- ====================================================================

-- VERIFICAÇÃO PRÉ-EXECUÇÃO
-- Verificar quantos canais existem atualmente
SELECT COUNT(*) as total_canais_atual 
FROM marketing.canais_aquisicao;

| total_canais_atual |
| ------------------ |
| 171                |

-- Verificar se os códigos 173-177 já existem
SELECT codigo, nome 
FROM marketing.canais_aquisicao 
WHERE codigo::int >= 173 
ORDER BY codigo::int;

-- ====================================================================
-- INSERÇÃO DOS CANAIS NOVOS
-- ====================================================================

BEGIN;

-- Canal 1: CAMPANHA CBA (7 clientes)
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('173', 'CAMPANHA CBA', 'Canal importado do VIXEN - 7 clientes', 'OUTROS', true);

-- Canal 2: WHATSAPP ROBÔ (5 clientes)
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('174', 'WHATSAPP ROBÔ', 'Canal importado do VIXEN - 5 clientes', 'OUTROS', true);

-- Canal 3: CAMPANHA ANIVERSARIANTES (2 clientes)
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('175', 'CAMPANHA ANIVERSARIANTES', 'Canal importado do VIXEN - 2 clientes', 'OUTROS', true);

-- Canal 4: PROSPECÇÃO MABIO (1 cliente)
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('176', 'PROSPECÇÃO MABIO', 'Canal importado do VIXEN - 1 clientes', 'OUTROS', true);

-- Canal 5: CAMPANHA AILTON (1 cliente)
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('177', 'CAMPANHA AILTON', 'Canal importado do VIXEN - 1 clientes', 'OUTROS', true);

COMMIT;

-- ====================================================================
-- VERIFICAÇÃO PÓS-EXECUÇÃO
-- ====================================================================

-- Verificar se os canais foram inseridos
SELECT codigo, nome, descricao, categoria, ativo
FROM marketing.canais_aquisicao 
WHERE codigo::int >= 173 
ORDER BY codigo::int;

-- Contar total após inserção
SELECT COUNT(*) as total_canais_final 
FROM marketing.canais_aquisicao;

-- ====================================================================
-- RESPOSTA: INFORME O RESULTADO
-- ====================================================================
-- 
-- ✅ SUCESSO: Os 5 canais foram inseridos
-- ❌ ERRO: [descreva o erro aqui]
-- 
-- Total de canais após execução: ___
-- Códigos inseridos: 173, 174, 175, 176, 177
-- 
-- PRÓXIMO PASSO: Aplicar mapeamento limpo nos arquivos VIXEN
-- ====================================================================