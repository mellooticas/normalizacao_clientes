-- Consultas SQL para verificar IDs das lojas no Supabase
-- Tabela: core.lojas

-- 1. Consulta básica para ver todas as lojas e seus IDs
SELECT 
    id,
    nome,
    codigo,
    ativo,
    created_at
FROM core.lojas
ORDER BY nome;

| id                                   | nome        | codigo | ativo | created_at                 |
| ------------------------------------ | ----------- | ------ | ----- | -------------------------- |
| 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | Mauá        | 048    | true  | 2025-10-23 12:44:48.208282 |
| da3978c9-bba2-431a-91b7-970a406d3acf | Perus       | 009    | true  | 2025-10-23 15:49:19.953044 |
| 4e94f51f-3b0f-4e0f-ba73-64982b870f2c | Rio Pequeno | 011    | true  | 2025-10-23 12:44:48.208282 |
| 1c35e0ad-3066-441e-85cc-44c0eb9b3ab4 | São Mateus  | 012    | true  | 2025-10-23 12:44:48.208282 |
| 52f92716-d2ba-441a-ac3c-94bdfabd9722 | Suzano      | 042    | true  | 2025-10-23 12:44:48.208282 |
| aa7a5646-f7d6-4239-831c-6602fbabb10a | Suzano 2    | 010    | true  | 2025-10-23 15:49:19.953044 |

-- 2. Consulta específica para mapear nomes das lojas com IDs
SELECT 
    id,
    nome,
    codigo,
    CASE 
        WHEN UPPER(nome) LIKE '%MAUA%' OR UPPER(nome) LIKE '%MAUÁ%' THEN 'MAUA'
        WHEN UPPER(nome) LIKE '%SUZANO%' AND (UPPER(nome) LIKE '%2%' OR UPPER(nome) LIKE '%II%') THEN 'SUZANO2'
        WHEN UPPER(nome) LIKE '%SUZANO%' THEN 'SUZANO'
        WHEN UPPER(nome) LIKE '%PERUS%' THEN 'PERUS'
        WHEN UPPER(nome) LIKE '%RIO%PEQUENO%' OR UPPER(nome) LIKE '%RIO PEQUENO%' THEN 'RIO_PEQUENO'
        WHEN UPPER(nome) LIKE '%SAO%MATEUS%' OR UPPER(nome) LIKE '%SÃO%MATEUS%' THEN 'SAO_MATEUS'
        ELSE 'OUTROS'
    END AS loja_mapeada
FROM core.lojas
WHERE ativo = true
ORDER BY nome;

| id                                   | nome        | codigo | loja_mapeada |
| ------------------------------------ | ----------- | ------ | ------------ |
| 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | Mauá        | 048    | MAUA         |
| da3978c9-bba2-431a-91b7-970a406d3acf | Perus       | 009    | PERUS        |
| 4e94f51f-3b0f-4e0f-ba73-64982b870f2c | Rio Pequeno | 011    | RIO_PEQUENO  |
| 1c35e0ad-3066-441e-85cc-44c0eb9b3ab4 | São Mateus  | 012    | SAO_MATEUS   |
| 52f92716-d2ba-441a-ac3c-94bdfabd9722 | Suzano      | 042    | SUZANO       |
| aa7a5646-f7d6-4239-831c-6602fbabb10a | Suzano 2    | 010    | SUZANO2      |

-- 3. Consulta para contar quantas lojas temos por tipo
SELECT 
    CASE 
        WHEN UPPER(nome) LIKE '%MAUA%' OR UPPER(nome) LIKE '%MAUÁ%' THEN 'MAUA'
        WHEN UPPER(nome) LIKE '%SUZANO%' AND (UPPER(nome) LIKE '%2%' OR UPPER(nome) LIKE '%II%') THEN 'SUZANO2'
        WHEN UPPER(nome) LIKE '%SUZANO%' THEN 'SUZANO'
        WHEN UPPER(nome) LIKE '%PERUS%' THEN 'PERUS'
        WHEN UPPER(nome) LIKE '%RIO%PEQUENO%' OR UPPER(nome) LIKE '%RIO PEQUENO%' THEN 'RIO_PEQUENO'
        WHEN UPPER(nome) LIKE '%SAO%MATEUS%' OR UPPER(nome) LIKE '%SÃO%MATEUS%' THEN 'SAO_MATEUS'
        ELSE 'OUTROS'
    END AS loja_tipo,
    COUNT(*) as quantidade,
    STRING_AGG(nome, ', ') as nomes_encontrados
FROM core.lojas
WHERE ativo = true
GROUP BY loja_tipo
ORDER BY quantidade DESC;


| loja_tipo   | quantidade | nomes_encontrados |
| ----------- | ---------- | ----------------- |
| RIO_PEQUENO | 1          | Rio Pequeno       |
| SAO_MATEUS  | 1          | São Mateus        |
| SUZANO      | 1          | Suzano            |
| PERUS       | 1          | Perus             |
| SUZANO2     | 1          | Suzano 2          |
| MAUA        | 1          | Mauá              |

-- 4. Consulta para verificar estrutura da tabela
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'core' 
  AND table_name = 'lojas'
ORDER BY ordinal_position;

| column_name       | data_type                   | is_nullable | column_default     |
| ----------------- | --------------------------- | ----------- | ------------------ |
| id                | uuid                        | NO          | uuid_generate_v4() |
| codigo            | character varying           | NO          | null               |
| nome              | character varying           | NO          | null               |
| nome_fantasia     | character varying           | YES         | null               |
| cnpj              | character varying           | YES         | null               |
| cidade            | character varying           | YES         | null               |
| estado            | character                   | YES         | null               |
| endereco_completo | text                        | YES         | null               |
| telefone          | character varying           | YES         | null               |
| email             | character varying           | YES         | null               |
| ativo             | boolean                     | YES         | true               |
| data_abertura     | date                        | YES         | null               |
| data_fechamento   | date                        | YES         | null               |
| created_at        | timestamp without time zone | YES         | CURRENT_TIMESTAMP  |
| updated_at        | timestamp without time zone | YES         | CURRENT_TIMESTAMP  |
| deleted_at        | timestamp without time zone | YES         | null               |
| updated_by        | character varying           | YES         | null               |


-- 5. Verificar se existem lojas inativas que precisamos considerar
SELECT 
    id,
    nome,
    codigo,
    ativo,
    created_at,
    updated_at
FROM core.lojas
WHERE ativo = false
ORDER BY nome;

Success. No rows returned


