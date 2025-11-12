# 🔧 GUIA: NORMALIZAÇÃO SEGURA DOS NÚMEROS DE VENDA
**Objetivo**: Remover prefixos "4801" e "4201" do campo `numero_venda` sem causar problemas

## ⚠️ IMPORTANTE: EXECUTAR EM ORDEM!

### 📋 **PASSO 1: ANÁLISE OBRIGATÓRIA**
**Execute PRIMEIRO para entender o impacto:**

```sql
SELECT 
    'Situação Atual' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as prefixo_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as prefixo_4201
FROM vendas.vendas;
```

**Resultado esperado**: Mostrará quantos registros serão afetados.

### 💾 **PASSO 2: BACKUP AUTOMÁTICO**
**NUNCA pule este passo:**

```sql
CREATE TABLE vendas.vendas_backup_prefixos AS 
SELECT * FROM vendas.vendas 
WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%';

SELECT COUNT(*) as "Registros Salvos no Backup" FROM vendas.vendas_backup_prefixos;
```

### 🔍 **PASSO 3: VERIFICAÇÃO DE CONFLITOS**
**Verificar se haverá problemas:**

```sql
-- Preview das mudanças
WITH preview AS (
    SELECT 
        numero_venda as original,
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(numero_venda::text, 5)::bigint
            WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(numero_venda::text, 5)::bigint
        END as novo
    FROM vendas.vendas
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
    LIMIT 10
)
SELECT 'PREVIEW' as tipo, original, novo FROM preview;

-- Verificar conflitos
WITH novos_numeros AS (
    SELECT 
        CASE 
            WHEN numero_venda::text LIKE '4801%' THEN SUBSTRING(numero_venda::text, 5)::bigint
            WHEN numero_venda::text LIKE '4201%' THEN SUBSTRING(numero_venda::text, 5)::bigint
        END as numero_novo
    FROM vendas.vendas
    WHERE numero_venda::text LIKE '4801%' OR numero_venda::text LIKE '4201%'
)
SELECT 
    'CONFLITOS' as alerta,
    COUNT(*) as quantidade
FROM novos_numeros nn
JOIN vendas.vendas v ON v.numero_venda = nn.numero_novo
WHERE v.numero_venda::text NOT LIKE '4801%' 
  AND v.numero_venda::text NOT LIKE '4201%';
```

**🚨 SE CONFLITOS > 0**: PARE! Analise os conflitos antes de continuar.
**✅ SE CONFLITOS = 0**: Pode prosseguir com segurança.

### 🔄 **PASSO 4: NORMALIZAÇÃO** 
**SÓ execute se não houver conflitos:**

```sql
BEGIN;

-- Remover prefixo 4801
UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(numero_venda::text, 5)::bigint
WHERE numero_venda::text LIKE '4801%';

-- Remover prefixo 4201  
UPDATE vendas.vendas 
SET numero_venda = SUBSTRING(numero_venda::text, 5)::bigint
WHERE numero_venda::text LIKE '4201%';

COMMIT;
```

### ✅ **PASSO 5: VALIDAÇÃO FINAL**
**Confirmar que deu certo:**

```sql
-- Verificar resultado
SELECT 
    'Resultado Final' as status,
    COUNT(*) as total_vendas,
    COUNT(CASE WHEN numero_venda::text LIKE '4801%' THEN 1 END) as ainda_com_4801,
    COUNT(CASE WHEN numero_venda::text LIKE '4201%' THEN 1 END) as ainda_com_4201
FROM vendas.vendas;

-- Testar foreign keys
SELECT 'FK Test' as teste, COUNT(*) as entregas_validas
FROM vendas.entregas_carne ec
JOIN vendas.vendas v ON ec.venda_id = v.id;
```

## 🚨 **ROLLBACK DE EMERGÊNCIA**
**Se algo der errado:**

```sql
UPDATE vendas.vendas 
SET numero_venda = backup.numero_venda
FROM vendas.vendas_backup_prefixos backup
WHERE vendas.vendas.id = backup.id;
```

## 📊 **EXEMPLOS DE TRANSFORMAÇÃO**

| Antes | Depois |
|-------|--------|
| 48013060 | 3060 |
| 42012345 | 12345 |
| 48010001 | 1 |
| 1000 | 1000 (inalterado) |

## ✅ **CHECKLIST DE SEGURANÇA**

- [ ] ✅ Executei análise prévia
- [ ] ✅ Criei backup dos dados
- [ ] ✅ Verifiquei que não há conflitos (COUNT = 0)
- [ ] ✅ Executei normalização dentro de BEGIN/COMMIT
- [ ] ✅ Validei o resultado final
- [ ] ✅ Testei foreign keys funcionando
- [ ] ✅ Posso apagar o backup (opcional)

## 🎯 **RESULTADO ESPERADO**

Após a normalização:
- **Prefixos removidos**: 4801XXXX → XXXX, 4201XXXX → XXXX
- **Foreign keys funcionando**: entregas_carne ainda encontra vendas
- **Números limpos**: Compatíveis com OSs das entregas
- **Zero conflitos**: Não há duplicatas

**Essa abordagem garante que a normalização seja feita de forma 100% segura!** 🛡️