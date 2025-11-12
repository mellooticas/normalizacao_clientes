-- ========================================
-- DIAGNÓSTICO DE DUPLICAÇÕES PÓS-NORMALIZAÇÃO
-- ========================================

-- 1. Verificar quais números vão causar duplicação
WITH numeros_normalizados AS (
    SELECT 
        id,
        loja_id,
        numero_venda as original,
        CASE 
            WHEN numero_venda::text LIKE '4801%' AND numero_venda::text != '4801.0' 
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 
                TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
            WHEN numero_venda::text LIKE '4201%' AND numero_venda::text != '4201.0' 
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 
                TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
            WHEN TRIM(SPLIT_PART(numero_venda::text, '.', 1)) != ''
                 AND TRIM(SPLIT_PART(numero_venda::text, '.', 1)) ~ '^[0-9]+$' THEN
                TRIM(SPLIT_PART(numero_venda::text, '.', 1))::bigint
            ELSE NULL
        END as numero_normalizado
    FROM vendas.vendas
),
numeros_validos AS (
    SELECT *
    FROM numeros_normalizados
    WHERE numero_normalizado IS NOT NULL
),
duplicacoes AS (
    SELECT 
        loja_id,
        numero_normalizado,
        COUNT(*) as quantidade,
        STRING_AGG(id::text || ':' || original::text, ', ') as registros
    FROM numeros_validos
    GROUP BY loja_id, numero_normalizado
    HAVING COUNT(*) > 1
)
SELECT 
    'DUPLICAÇÕES DETECTADAS' as status,
    loja_id,
    numero_normalizado,
    quantidade,
    registros
FROM duplicacoes
ORDER BY quantidade DESC, numero_normalizado;


| status                 | loja_id                              | numero_normalizado | quantidade | registros                                                                                   |
| ---------------------- | ------------------------------------ | ------------------ | ---------- | ------------------------------------------------------------------------------------------- |
| DUPLICAÇÕES DETECTADAS | aa7a5646-f7d6-4239-831c-6602fbabb10a | 1104               | 2          | 25bc8877-0cdb-4609-90f1-f2ab8968db57:1104, 03b69a5e-e627-48d0-b844-8ae222c779b5:480101104.0 |
| DUPLICAÇÕES DETECTADAS | aa7a5646-f7d6-4239-831c-6602fbabb10a | 1108               | 2          | d09f3552-1dc9-4c5f-b001-ae3077027255:1108, 993acc39-dca0-43d8-9d49-321a6448d493:480101108.0 |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4004               | 2          | 471e8a0d-431b-4401-bb4e-a831edffc513:4004.0, 52632ef0-d4f9-46aa-9e6b-4dc2a2c41f92:4004      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4030               | 2          | 34bb616e-1956-4e28-bf8f-a6d6d384598e:4030.0, bcdcf879-2d82-48f4-b9b8-b662435f7d7a:4030      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4034               | 2          | 7ddc1718-73f5-4ef6-b555-4ca065c95cca:4034.0, 33540340-ea45-4045-a1aa-5468d97e553a:4034      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4052               | 2          | ef1890c1-d1be-496e-a3e7-456c1c1e716e:4052.0, b11cc4bd-ee24-41d1-a334-1d66f8e71901:4052      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4059               | 2          | 331bd1ad-d8f5-4438-9ec2-1b32851ff45e:4059.0, 087c73bc-a4d2-4237-8d47-d7debaf4df36:4059      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4060               | 2          | 9c3deae9-c5df-4be6-9261-6b29cc54463e:4060.0, 63034548-9241-419b-9221-18d90fe60b88:4060      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4068               | 2          | 31d289bc-8c74-432b-9d8f-a2667eaa717a:4068.0, f509f3ef-d4c4-45ea-ac8c-a27f02d0297d:4068      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4078               | 2          | 8226cbf1-effe-45ac-a3af-a2e7ba576819:4078.0, 0d3a2ffd-e521-4d8f-abd5-b9eb1f0bd858:4078      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4082               | 2          | a4c1def8-10af-4268-b2a7-1ce03b85c3ce:4082.0, 790c62ad-f992-4eca-aab0-33155e74b3bb:4082      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4085               | 2          | 0aa178a7-7f7e-498d-b90d-c2c909e096dd:4085.0, 5db9a1b7-950d-46a0-9f50-4ef9b684dd9e:4085      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4086               | 2          | 4dd31aef-27d2-4e06-9b5a-a3fa793482aa:4086.0, 3152d93f-2616-4f1e-8857-ae56ddc71b0a:4086      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4088               | 2          | 93435a1c-ee46-403b-8adb-9bb0a321ea8f:4088.0, ca1964d9-a629-4a59-8d36-0d8a2a8892a8:4088      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4089               | 2          | bd5cf001-1a28-42c4-afa0-5ae2f9a90fec:4089.0, dc2d7702-34b8-4852-b037-57e1af8477eb:4089      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4095               | 2          | 9e342d96-1e95-4596-afe7-b41b388a6994:4095.0, 2c4dbca5-19db-44cd-a45b-7466f175b603:4095      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4100               | 2          | a6583386-8cdb-4f1e-8c66-0607e340797f:4100.0, 4685145e-6f2b-488f-a1ad-59712bc15bae:4100      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4107               | 2          | 6b3f287f-c8ca-4369-bdbd-2b333a2a5237:4107.0, 9a0d08c7-83fa-4b0f-b144-93fc75feff96:4107      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4108               | 2          | 170112a2-1c6b-4124-a229-0e088fdf85d6:4108.0, f6310bd1-5db2-4d51-981f-e064c3bd14ec:4108      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4110               | 2          | 0d77d8f0-621e-4ae4-b4c3-1f5a0e4dd36b:4110.0, 9b58e06c-60f7-4521-94e3-2cd568b7f0ec:4110      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4119               | 2          | 02547228-feaf-41dd-bb19-fbed24e58c73:4119.0, 0638b53f-21bb-406f-85a2-b8706c1aa647:4119      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4121               | 2          | c31c64ec-16ee-476c-9f29-3de7bde68971:4121.0, adcc6847-a397-4ce1-b18e-ed74d528125f:4121      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4122               | 2          | 4d7bc19e-0beb-4770-b2c2-6023802a125d:4122.0, 33d2e2fa-ff53-460e-959f-71584d4b32e4:4122      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4124               | 2          | d396980b-688e-4828-ab80-46fe553f340a:4124.0, 19dfa48c-7f0a-415f-864e-8f031aae70a9:4124      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4126               | 2          | dd23643f-39ee-40e9-a6cd-6f59a955590b:4126.0, c390b35f-e75a-43b4-92fb-36314f9ef3de:4126      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4127               | 2          | d08fe627-3836-4f3a-a347-fd6abe840bce:4127.0, 55e0855d-fec3-424d-ba96-f11bbabbf5ef:4127      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4129               | 2          | ab19668a-10aa-4905-94a6-2f3ad5f20276:4129.0, 798e4544-7fbc-451c-9cf1-e7ba074b0917:4129      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4130               | 2          | f41547d2-1bcb-431d-8094-182d64cb3664:4130.0, 2973716b-6a3f-4ef3-9a33-824ae5bfe25c:4130      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4134               | 2          | f77e715d-e4e6-40c2-b199-f1738b457333:4134.0, ea0b72d0-7c33-418d-8378-c87c67b7da61:4134      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4136               | 2          | 162718f1-a831-4997-acaa-a56291654f02:4136.0, ae125c7b-8572-476e-b4d0-a87bde27f3e3:4136      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4138               | 2          | d06bc8b2-4124-4dd8-814d-40ae2e41867a:4138.0, 7d40664f-f71b-402f-afc4-7a19fc8a9a2f:4138      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4142               | 2          | 7e6565d3-5f4d-47b6-8f5e-2dcf7d424d3b:4142.0, 263316fc-3451-4f7f-b6ae-b129128b71c7:4142      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4147               | 2          | 7b4f1be7-0519-4066-8b0c-983a3201c2c0:4147.0, 367601d9-3e4f-463b-af3c-18db8ba476ef:4147      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4151               | 2          | 086aa607-49cf-4885-9ed2-7782a399f7b9:4151.0, d9d44070-5451-43de-812f-17f80915811b:4151      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4159               | 2          | 24eaebe2-fbee-41fd-b54d-d293fc4bdad1:4159.0, 4b3e796c-175b-4f08-937b-e8383d6b837a:4159      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4162               | 2          | e707ef20-dacf-4ae2-b8bc-fcdd4685ef6f:4162.0, 025b11a5-173d-410a-80d3-97498f93b84f:4162      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4163               | 2          | 45b34219-976b-4fd0-8e6a-44e342248efb:4163.0, a7c8b37c-2c34-4a13-be01-c9baf3084fd1:4163      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4166               | 2          | 59702d05-42b3-42f6-87e6-cd7b5809a993:4166.0, fb31b9cd-a503-4877-b4b8-62fbcdc9559b:4166      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4180               | 2          | 1f771eab-c6b2-46a9-bf62-b3f728a7ac08:4180.0, 6186f6f3-b945-44ca-b77f-89664047783d:4180      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4186               | 2          | 57d5f75a-dbc3-4c24-8ad9-536c3f892323:4186.0, 56ef3296-407d-45b4-abc5-162f5ec92eac:4186      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4189               | 2          | 20078b55-3419-4989-84a4-22ca32f6758e:4189.0, 16ee47c6-b133-40c5-b792-713d37c2db51:4189      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4192               | 2          | 1ec51cba-5c73-484f-8c8b-a3cbcf9f89b4:4192.0, 4a14bc54-4ea1-4bc7-b767-082f1440c544:4192      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4193               | 2          | 702ce55f-7538-45fe-a70b-263876ec8037:4193.0, bbebff7a-ade6-4032-85c2-c65a796e439d:4193      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4197               | 2          | 642d6737-b31d-46e9-b468-78eba34d649a:4197.0, c30db2d3-2fa2-4e1f-b7e5-ab8450e9e67c:4197      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4200               | 2          | 454e4420-3d0e-4f3a-ad49-d9b3a361d5f9:4200.0, d807cb0a-db65-45da-ab5a-e89ad37e8586:4200      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4201               | 2          | e333f9dd-9f1f-432a-a919-0f3aa4198ffe:4201.0, 85e3664b-7937-4837-bd89-e581d988bfbb:4201      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4202               | 2          | a07ca906-bf99-42d7-a2c7-f8786bc7eeab:4202.0, 49b362cd-d225-4eb6-b8e4-4ed071dcdf88:4202      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4204               | 2          | 3c4926e7-648c-499f-a878-a81318144556:4204.0, a6fdcc5e-aefa-4cb2-860f-8e48b1a01061:4204      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4208               | 2          | 1bd5e63d-79d2-4bb2-a4cc-334ffaa19fc6:4208.0, 93c26534-bdc8-4e82-a652-f83233b49d8b:4208      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4209               | 2          | e21feec5-a70a-4187-adea-884ec7be3392:4209.0, 444881aa-33fe-43ef-82cd-2a183445d0e2:4209      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4214               | 2          | f8a9f1b8-a3f5-447e-aa01-e7bd2be5ab0f:4214.0, 9de6b5c3-18bf-42bc-90ff-363abac3638d:4214      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4215               | 2          | 192b5c72-43a1-4c7f-8da7-9d1e2ddefba6:4215.0, 9b2d0a92-bbf6-4976-9cb4-bd6c26966872:4215      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4219               | 2          | 18802931-8050-404a-a16e-72fc6efc9302:4219.0, f3498463-b98b-4417-a09a-d901dd4380da:4219      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4221               | 2          | ec579bb6-273f-4842-9747-9a0eced86918:4221.0, 22dc0435-4fd6-4064-89b7-4eec714fb322:4221      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4222               | 2          | 4001a7f8-d22f-455f-82df-38bfd84b14bb:4222.0, 4a621402-d8ad-4968-9e57-56b8bb7bd66f:4222      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4225               | 2          | f13f0fd2-25ae-4d21-94bf-b574d6ac193b:4225.0, f2ce9e55-e634-4bd0-b16b-ebb7f10ac8e1:4225      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4231               | 2          | aa6127ce-1968-42ee-8428-a0ea71cced71:4231.0, 67ffe6c6-e6fe-4080-a9ea-002f4a6aa156:4231      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4233               | 2          | c50f35f4-e1c8-42f2-90ac-d13665eee2f6:4233.0, b85e8cce-60fe-4165-98ff-63652b698c03:4233      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4236               | 2          | 707a0069-b32a-4ae3-8660-4bdbbc1ef075:4236.0, 51ec935f-73e3-4069-9991-b7f57010806b:4236      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4246               | 2          | 56400d11-4b3d-4499-9087-ad30d1d6812b:4246.0, 937047df-91a5-4662-a4a5-aac079c165bc:4246      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4250               | 2          | 981ef032-de85-4054-89c2-b1b6ee9f3beb:4250.0, db8b14fe-a648-4c3b-ba8b-8c626cdea586:4250      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4251               | 2          | 6258424c-3680-4056-a113-cc42fa633950:4251.0, a79d37f1-5164-43fb-98e5-caaee3b16519:4251      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4261               | 2          | bc5edcbe-559d-4408-b98b-f8a019b62aa1:4261.0, 4ae947dc-a99b-4f66-af9d-0cf4594538bd:4261      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4263               | 2          | 12704863-e2b3-4a20-a6a4-a7106c8d636f:4263.0, d4b9b162-dd88-4e86-93bb-ef92a9d915c2:4263      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4269               | 2          | 684259e3-224f-4a2b-9f73-1ba02edb468c:4269.0, 10031bc9-78f8-4274-aa86-4027ade96346:4269      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4270               | 2          | df92ac68-ed1e-4ea1-aeac-f95e5519985a:4270.0, ad7f030d-dd8a-4f17-b462-685af604cb3b:4270      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4271               | 2          | cc1dd7b3-76a9-4875-b453-3d03357ab8f1:4271.0, d87a3f5c-7d1b-4830-846a-83d7b6c0350a:4271      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4279               | 2          | cd8adc4e-7c33-4fb7-bea5-d005ae511fc1:4279.0, 15d703f8-0db5-4385-89ef-c14835971699:4279      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4280               | 2          | 743aa915-ee30-4d41-8dc8-65ac3fdb17a7:4280.0, b560b2ee-7a31-407f-93d4-94a1c65bc8ef:4280      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4292               | 2          | 0ff73f20-91f6-4174-8c37-19525e4e99a8:4292.0, e22d53d8-adf8-48c3-9886-d3f0221c9fde:4292      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4299               | 2          | 90110dc0-5d0e-42e6-878b-85095e549624:4299.0, c7bf317a-881c-4f10-bd2e-9f7ded2f194b:4299      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4302               | 2          | 279b29fc-beb3-48c5-9c64-fb478bd81227:4302.0, 2f7c53bb-c311-45d5-838d-f366614e72a7:4302      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4305               | 2          | e223dcfd-be98-4d85-b36f-caedac77cc43:4305.0, 87e429c3-ad32-4fc1-bca6-f945a7c682e5:4305      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4310               | 2          | 8ec7460b-2902-4bcb-8917-3f1e3564abfe:4310.0, d38c1aac-ebf6-4073-bc5e-671a5489c31a:4310      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4325               | 2          | 50715e48-bbc6-440c-95b4-9a0f82d3fddb:4325.0, 004a1f90-97ed-4b78-a04c-744454672b26:4325      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4334               | 2          | 71ae111d-fb3b-4b7e-aed4-a3e1bca653e5:4334.0, 8001e6be-52ca-48ca-9602-f14addfc9947:4334      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4342               | 2          | febf5816-3209-4b75-b275-285c823747c8:4342.0, ccef716b-90a5-468a-9895-41ef3a8a6708:4342      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4345               | 2          | 37b0eee2-ec8f-4a77-8bed-59944ea3b5d5:4345.0, 6577e4b3-14c9-446c-bb54-c8521a68e6a4:4345      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4351               | 2          | 50d6f832-6312-47f9-9c51-2561dbbc9521:4351.0, 81740aed-7a30-49fd-b1ca-e6454ab23f12:4351      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4358               | 2          | b77daf13-169a-4744-b411-90166860a4e7:4358.0, 1067b57f-2205-4be2-9df0-ac4f6dc57314:4358      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4359               | 2          | e32b8973-d525-430f-a755-e4f0b7f07796:4359.0, 8226842a-14cd-4dd5-9027-23eaeb7d1e3d:4359      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4370               | 2          | d47c06fc-f363-4399-abb0-7f6e1d5a30fe:4370.0, d4d2298c-79ed-4950-bca7-c4682de1e8ef:4370      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4391               | 2          | bfaa17a6-0e07-4550-a65a-df0115554e23:4391.0, e99026f8-9052-45a9-8991-edd899206e24:4391      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4395               | 2          | af448e7b-d3b9-4877-bb07-ed36b4f855aa:4395.0, 760ab6ea-44e6-4052-b7ac-48e6163dba3a:4395      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4409               | 2          | 1756b4a5-2183-42e2-810b-6cfe864f929d:4409.0, 9727208f-c743-47e3-995d-794e434cec4d:4409      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4417               | 2          | 2bba002e-c524-4bc6-bc9f-88f500445555:4417.0, c82815ae-57a1-4751-be01-5eaf81fb5299:4417      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4440               | 2          | f61db109-d26b-4bfe-9f8f-3e51a937296f:4440.0, 0a75e453-f678-445f-b185-98387128bce0:4440      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4445               | 2          | ea2a331f-592c-4127-81c2-a17a4e780796:4445.0, f414c106-dd5d-416f-903d-97e0e8a3f14f:4445      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4446               | 2          | 3cff8b18-aa87-4391-8269-061daeebc066:4446.0, ea35151c-64ea-471c-ac70-330a50c6aa0f:4446      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4452               | 2          | 91a0baa4-1f2f-4dc9-8d70-10b80bc7268d:4452.0, 7fbfe6ff-f20d-4b23-8798-a8ab60f0218a:4452      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4463               | 2          | 4baf8876-bcd1-4597-b92c-9b4fdea65901:4463.0, 39cdb5c6-cde0-4285-bbdb-e87347f812d7:4463      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4466               | 2          | b03a6e1e-5ddb-4d53-8851-591e2decf733:4466.0, 7db3bc34-b4f7-4580-889d-d96e9840b6ce:4466      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4467               | 2          | ece7d3b2-2c5d-4d27-9503-3bde837b9275:4467.0, c6b3789f-41ab-4ec1-a0b2-0b1e00a4cf96:4467      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4470               | 2          | efa74ecd-dafa-4deb-bb78-94c328ee5c8c:4470.0, 761d7909-9a22-47d2-ab3c-b5847781f6ca:4470      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4489               | 2          | 08349e7b-7eb4-4dc0-9a5d-5b7f90f3c005:4489.0, 9238c25a-2b6e-4dde-b45e-a80be56209af:4489      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4497               | 2          | 2e852e25-e66f-41a5-828f-3c4b34658960:4497.0, 5f8eb945-2ea2-4e91-be07-a30641aaf5e6:4497      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4501               | 2          | ca83b9f2-cbc8-42a5-99af-101fa16407c9:4501.0, 4c18f907-5d4d-49d7-9b8e-5941ea86f2e5:4501      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4522               | 2          | d08704d9-ac65-49c7-90bc-1ea52a9d1885:4522.0, 03212d50-1e34-4887-8521-10a3ed01fca6:4522      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4533               | 2          | 152135aa-13c7-4ede-9241-1157a932af37:4533.0, 87478002-292a-4118-a7b3-d778e300ae3a:4533      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4541               | 2          | 0b6646b4-8087-43cd-8952-e71ca6beeca1:4541.0, 2f069dfe-ef1b-4191-bf46-e84b8d867768:4541      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4543               | 2          | 36fb61e7-234d-4fce-bc09-61b50064ecb5:4543.0, 2b7a055f-59ad-452e-a833-557ea1cef518:4543      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4549               | 2          | ef86f1b1-f707-4e0a-9b65-bc34c321dd9c:4549.0, 8f65ec46-32df-45db-865c-9b4754a9cd64:4549      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4610               | 2          | a18cf458-21cf-40c5-9fc6-1de6c217b698:4610.0, e8a31784-cf43-437f-939c-fb94e5042a31:4610      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4620               | 2          | 9521f8f1-73d7-43c2-9c69-7d47769541bc:4620.0, 2a5e8ae4-d8d2-4a38-b8d9-1d7076381c7c:4620      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4640               | 2          | 8c97b63d-7dba-4ef9-a7d8-26e57186da23:4640.0, 5c4e7aed-6db3-4daa-8e5e-638ebdf40b88:4640      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4643               | 2          | fd445ceb-dd6f-4f44-ab6a-a60a21e0e2f2:4643.0, 37dbaa7a-ca8c-48b9-9f20-d3fd3166c810:4643      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4645               | 2          | 6d4411a2-1cfb-43c2-9d62-5f872fc60885:4645.0, ee5b72f8-a1f5-4fb2-a8a2-c1dfd9f5706e:4645      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4666               | 2          | 2eb33089-34b1-43a2-bca7-c77ba4a79712:4666.0, 4f0424b3-3405-4b32-bab0-d3f615fc341e:4666      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4730               | 2          | 552bd1a9-228b-4b31-a162-b82be8436288:4730.0, 4f94b346-99b9-4c21-98da-cc6e1dd3949e:4730      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4748               | 2          | a76927e9-9b87-45eb-978d-c094131a5844:4748.0, e14fe1aa-213a-4013-9fa5-b6358e28fcf5:4748      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4793               | 2          | f46520f8-0e76-4d2a-b092-cdf0c0276460:4793.0, 3f81f83a-9228-4491-b161-729f2a0d5547:4793      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4847               | 2          | 9d6721d7-7c72-4853-a522-6934d255aca4:4847.0, c87accf0-83f8-42b0-8d76-5e4e93a049d8:4847      |
| DUPLICAÇÕES DETECTADAS | 52f92716-d2ba-441a-ac3c-94bdfabd9722 | 4855               | 2          | 02b620d2-7e53-4524-9979-44018b6dd381:4855.0, 03ac5361-3040-40a1-9855-463689085f02:4855      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 8614               | 2          | e566ba06-5757-48ca-9b7a-1249348f9773:8614, 1446ce63-5953-40df-a874-1ef615c8594e:8614.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 8960               | 2          | e01fed74-60ef-44c3-800b-1cbffaf3de87:8960, f4be6215-61d8-4843-a2d0-f1a869b16e4d:8960.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9049               | 2          | 8e2c7e04-7629-4a89-8a71-a1afc18c3c9f:9049, a7ccbfff-fbce-44e8-b087-347ce573dc5d:9049.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9081               | 2          | d1b19ec2-74ae-47f9-a620-298a1cda6f0e:9081, 38b6eb45-5270-4e8c-a99f-b74a1d5fe759:9081.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9082               | 2          | b52ef7f6-d02a-4426-86d8-f0fcafbc50a3:9082, a7eb3fab-8065-430b-a57c-4bba0e87b352:9082.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9268               | 2          | 2d691696-f556-45ee-a26d-1dc97515d777:9268, 79e0e3c7-4b13-448f-9430-ee761d7752c4:9268.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9269               | 2          | fe79314d-29a0-40ab-95f6-7df771af15d2:9269, 4939633b-cb68-4538-8b90-38fabb10a7ab:9269.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9276               | 2          | 78be5ec4-4c0c-4f72-8edf-0d4e967c1fef:9276, 2eef1199-523a-4668-8d47-70c6eeae22a1:9276.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9324               | 2          | 79477655-a0fa-4c13-bad6-6dfd7a101a3b:9324, d8e58652-c4ff-43f9-94fa-3bfb4c19a5de:9324.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9335               | 2          | 558f597f-988b-4862-a905-ffc60aefb9b6:9335, 64eea1d7-6b20-401b-a78d-f4b0c3b56dd1:9335.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9655               | 2          | 3580b0ac-00f3-4f06-a395-74149aaff04c:9655, 61924330-7d03-4fb0-84e3-22b710bdc700:9655.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9658               | 2          | e90c4333-7318-4ca1-b296-289793aa7808:9658, 9ce23eec-db01-49d1-85ac-e98cb24d9cf3:9658.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9787               | 2          | 709ea389-9c96-4be7-bfa7-3520e0f202c1:9787, 06066601-f6b7-4c58-9c6d-9dea4a248d1d:9787.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 9788               | 2          | c6f37a3f-0053-40a5-acb2-a2447540f017:9788, d27520e7-e5fe-4283-9ed0-934213ac5fad:9788.0      |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10066              | 2          | a54ad7a4-3f57-497d-a662-068dbf5a8614:10066, 8b7238af-7943-45b2-8c82-908875c916d7:10066.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10190              | 2          | 24c87f5f-85ed-4085-86a7-59581370c46a:10190, d065e37f-c776-4be9-b14e-974db32c8001:10190.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10313              | 2          | f06d6660-ffc2-4147-9e64-e3f0f31a84a7:10313, dcb6323e-77aa-4f12-a2dd-a3206995108a:10313.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10905              | 2          | 05f75d30-9226-4fb9-ab55-1a8461ed7b1e:10905, 49a4852f-d598-4235-a7c9-a6e6861840f6:10905.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10934              | 2          | 11e587d3-1446-4222-bcbb-31f465303431:10934, 0a4097a2-256f-4a32-9526-80dc00d31916:10934.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 10961              | 2          | c7571a24-f5d6-458a-834b-34cfbe6014ec:10961, 5f9a0d5a-ec05-4204-911d-e825f40a1b8a:10961.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11015              | 2          | 92b987c3-197b-44b5-a121-99fca1a3bb24:11015, 62ea8657-c723-40a1-9254-46fa8b9d870f:11015.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11682              | 2          | 285a39f0-1fd3-429a-9fca-4fdf07db7504:11682, f0d7f920-c798-4a7e-b650-5ebb32e5fe2d:11682.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11771              | 2          | 663542b3-bd9a-4218-98b7-f8ddbc7a250e:11771, b1ed376d-f82e-4770-8295-70eab7f6c1b1:11771.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11797              | 2          | 422e22b3-da60-46c4-8a6f-e1f62492ab3a:11797, a958ef4c-03af-482f-9982-d0588cd0ad89:11797.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11842              | 2          | a0e94fe3-0ebe-4e64-aca9-91c7d19359da:11842, 65fe146a-46c4-45a9-b044-9f727daff669:11842.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11863              | 2          | 47c09c2d-86c8-4304-8032-323cfaae3419:11863, 9d194f0d-f27a-4fb8-a1b2-395730aea0f7:11863.0    |
| DUPLICAÇÕES DETECTADAS | 9a22ccf1-36fe-4b9f-9391-ca31433dc31e | 11884              | 2          | e0296d83-695e-4842-bbf4-23216aa0591f:11884, 39a8728c-1341-4b45-a483-eaa1f3e68408:11884.0    |



-- 2. Ver especificamente o caso do erro (numero 1104)
SELECT 
    'CONFLITO 1104' as info,
    id,
    loja_id,
    numero_venda as original,
    numero_venda::text LIKE '4%01%' as tem_prefixo,
    CASE 
        WHEN numero_venda::text LIKE '4801%' THEN 'PREFIXO_4801'
        WHEN numero_venda::text LIKE '4201%' THEN 'PREFIXO_4201'
        ELSE 'SEM_PREFIXO'
    END as tipo
FROM vendas.vendas 
WHERE (
    numero_venda = 1104 
    OR (numero_venda::text LIKE '4%01%' AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint = 1104)
)
AND loja_id = 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
ORDER BY numero_venda;

-- 3. Contar total de duplicações por loja
WITH numeros_normalizados AS (
    SELECT 
        loja_id,
        CASE 
            WHEN numero_venda::text LIKE '4801%' AND numero_venda::text != '4801.0' 
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 
                TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
            WHEN numero_venda::text LIKE '4201%' AND numero_venda::text != '4201.0' 
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) != ''
                 AND TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5)) ~ '^[0-9]+$' THEN 
                TRIM(SUBSTRING(SPLIT_PART(numero_venda::text, '.', 1) FROM 5))::bigint
            WHEN TRIM(SPLIT_PART(numero_venda::text, '.', 1)) != ''
                 AND TRIM(SPLIT_PART(numero_venda::text, '.', 1)) ~ '^[0-9]+$' THEN
                TRIM(SPLIT_PART(numero_venda::text, '.', 1))::bigint
            ELSE NULL
        END as numero_normalizado
    FROM vendas.vendas
),
numeros_validos AS (
    SELECT *
    FROM numeros_normalizados
    WHERE numero_normalizado IS NOT NULL
),
duplicacoes_por_loja AS (
    SELECT 
        loja_id,
        COUNT(*) - COUNT(DISTINCT numero_normalizado) as duplicacoes
    FROM numeros_validos
    GROUP BY loja_id
)
SELECT 
    'RESUMO DUPLICAÇÕES' as info,
    l.nome as loja,
    d.duplicacoes as registros_duplicados
FROM duplicacoes_por_loja d
JOIN public.lojas l ON l.id = d.loja_id
WHERE d.duplicacoes > 0
ORDER BY d.duplicacoes DESC;

-- 4. Estratégia para resolver: números com prefixo devem virar negativos
SELECT 
    'ESTRATÉGIA RESOLUÇÃO' as info,
    'Converter números com prefixo para negativos para evitar conflitos' as solucao,
    'Exemplo: 420101104 vira -1104, 480101104 vira -1104' as exemplo;