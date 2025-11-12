-- CONSULTAS PARA VALIDAR ESTRUTURA ANTES DA IMPORTAÇÃO

-- 1. Verificar se tabela está vazia
SELECT COUNT(*) as total_vendas FROM vendas.vendas;

| total_vendas |
| ------------ |
| 0            |

-- 2. Verificar lojas disponíveis
SELECT id, codigo, nome FROM core.lojas ORDER BY codigo;

| id                                   | codigo | nome        |
| ------------------------------------ | ------ | ----------- |
| da3978c9-bba2-431a-91b7-970a406d3acf | 009    | Perus       |
| aa7a5646-f7d6-4239-831c-6602fbabb10a | 010    | Suzano 2    |
| 4e94f51f-3b0f-4e0f-ba73-64982b870f2c | 011    | Rio Pequeno |
| 1c35e0ad-3066-441e-85cc-44c0eb9b3ab4 | 012    | São Mateus  |
| 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 042    | Suzano      |
| 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 048    | Mauá        |


-- 3. Verificar vendedores disponíveis  
SELECT id, nome FROM core.vendedores LIMIT 10;

| id                                   | nome                          |
| ------------------------------------ | ----------------------------- |
| de96b3f7-cf3b-428f-9cd3-c92a6042a110 | /////////////////////////     |
| cd780caa-3cf0-42ac-ada8-17964f7cad60 | ADRIANA ANSELMO               |
| 28382574-3270-4a12-a820-87f03276ef33 | ANA                           |
| e36a93ed-6f79-4ccd-b278-646a94367410 | ANDRESSA DE SOUZA             |
| df105bdf-d92b-44e7-86dd-2f486b4eb17b | ARIANI DIAS FERNANDES CARDOSO |
| c9a76e06-f67b-4b36-a44f-a55716679a2a | BRUNO                         |
| 2cba056b-4da2-486c-a295-485eba8a3d01 | CARLA CRISTINA                |
| bf95e71d-a56d-42fc-bef5-5b571f2f8ce7 | CHINASA DORIS                 |
| 54412296-152b-4b4a-92fe-ad72595f12a2 | ERICA DE CASSIA JESUS SILVA   |
| dda060e8-01cd-4843-a97e-75b9887292db | FELIPE MIRANDA                |

-- 4. Verificar clientes (amostra)
SELECT id, nome FROM core.clientes LIMIT 10;


| id                                   | nome                                |
| ------------------------------------ | ----------------------------------- |
| 9d48416c-c0ff-4215-9887-a828c84f6516 | NATALIA SANCHES VIANA               |
| 9029bc78-af0d-41f7-8539-e2d5e5e32457 | ELIENE ALVES DOS SANTOS             |
| db2b7b95-f126-4d49-ad61-170c9d5e0ae0 | ROSANGELA SILVA PEREIRA             |
| e2667fe9-7ff8-4875-ae69-f236946665ff | ROSANGELA SILVA PEREIRA             |
| f64f085b-26f9-455d-bd19-140560ac6c54 | GILDA MARQUES DE CARVALHO DA SILVA  |
| 3cf1f772-5765-49a8-b6cf-af671f4e52d9 | ANDRESSA SOUZA SANTOS               |
| aa217b3a-0a8c-4ab1-ae5e-731b1c61702b | EDEVALDO BISPO DOS SANTOS           |
| 66981a0c-7530-418c-9cd3-fdd6b6ee8f11 | CLAUDIA MATOS DE MIRANDA DA SILVA   |
| ef901ca2-14c6-4cd3-804a-e839749b24c2 | RAUL ALVES DA SILVA                 |
| ed2f49b4-f5a5-4636-9f59-41a5a4a2e1bd | JAKELINE RODRIGUES DA SILVA         |


-- 5. Verificar estrutura da tabela vendas
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vendas' 
  AND table_name = 'vendas'
ORDER BY ordinal_position;

| column_name         | data_type                   | is_nullable | column_default             |
| ------------------- | --------------------------- | ----------- | -------------------------- |
| id                  | uuid                        | NO          | uuid_generate_v4()         |
| numero_venda        | character varying           | NO          | null                       |
| cliente_id          | uuid                        | YES         | null                       |
| loja_id             | uuid                        | NO          | null                       |
| vendedor_id         | uuid                        | YES         | null                       |
| data_venda          | date                        | NO          | null                       |
| valor_total         | numeric                     | NO          | null                       |
| valor_entrada       | numeric                     | YES         | 0                          |
| valor_restante      | numeric                     | YES         | null                       |
| nome_cliente_temp   | character varying           | YES         | null                       |
| observacoes         | text                        | YES         | null                       |
| status              | USER-DEFINED                | YES         | 'ATIVO'::status_type       |
| cancelado           | boolean                     | YES         | false                      |
| data_cancelamento   | timestamp without time zone | YES         | null                       |
| motivo_cancelamento | text                        | YES         | null                       |
| created_at          | timestamp without time zone | YES         | null                       |
| updated_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP          |
| created_by          | character varying           | YES         | null                       |
| updated_by          | character varying           | YES         | null                       |
| deleted_at          | timestamp without time zone | YES         | null                       |
| version             | integer                     | YES         | 1                          |
| tipo_operacao       | character varying           | YES         | 'VENDA'::character varying |
| is_garantia         | boolean                     | YES         | null                       |
| origem_venda        | character varying           | YES         | null                       |
| utm_source          | character varying           | YES         | null                       |
| utm_medium          | character varying           | YES         | null                       |
| utm_campaign        | character varying           | YES         | null                       |
| utm_content         | character varying           | YES         | null                       |
| campanha_id         | uuid                        | YES         | null                       |

-- 6. Verificar constraints
SELECT 
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'vendas' 
  AND table_name = 'vendas';


| constraint_name                | constraint_type |
| ------------------------------ | --------------- |
| chk_vendas_entrada_menor_total | CHECK           |
| uq_vendas_loja_numero          | UNIQUE          |
| vendas_campanha_id_fkey        | FOREIGN KEY     |
| vendas_cliente_id_fkey         | FOREIGN KEY     |
| vendas_loja_id_fkey            | FOREIGN KEY     |
| vendas_pkey                    | PRIMARY KEY     |
| vendas_tipo_operacao_check     | CHECK           |
| vendas_valor_entrada_check     | CHECK           |
| vendas_valor_total_check       | CHECK           |
| vendas_vendedor_id_fkey        | FOREIGN KEY     |
| 17891_18185_1_not_null         | CHECK           |
| 17891_18185_2_not_null         | CHECK           |
| 17891_18185_4_not_null         | CHECK           |
| 17891_18185_6_not_null         | CHECK           |
| 17891_18185_7_not_null         | CHECK           |