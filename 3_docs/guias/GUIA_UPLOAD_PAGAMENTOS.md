# 📋 GUIA DE UPLOAD - SCHEMA PAGAMENTOS NO SUPABASE

## ✅ STATUS ATUAL
- ✅ Schema `pagamentos` criado no Supabase
- ✅ Tabelas, índices, views e triggers configurados
- ✅ Constraints ajustadas para permitir upload
- ✅ Arquivos CSV preparados e corrigidos

## 📁 ARQUIVOS PARA UPLOAD

### 1. Movimentos de Caixa
**Arquivo:** `movimentos_caixa_upload_20251106_100717.csv`
- **Registros:** 6,668 movimentos
- **Tabela destino:** `pagamentos.movimentos_caixa`
- **Status:** ✅ Pronto para upload
- **Dependências:** Nenhuma

### 2. Parcelas de Carnê
**Arquivo:** `parcelas_carne_upload_20251106_100717.csv`
- **Registros:** 4,911 parcelas
- **Tabela destino:** `pagamentos.parcelas_carne`
- **Status:** ✅ Pronto para upload (constraints ajustadas)
- **Dependências:** Nenhuma (FK removida temporariamente)

## 🔧 PROCEDIMENTO DE UPLOAD

### Passo 1: Upload Movimentos de Caixa
1. Acesse o Table Editor do Supabase
2. Navegue para `pagamentos.movimentos_caixa`
3. Clique em "Insert" → "Upload CSV"
4. Selecione `movimentos_caixa_upload_20251106_100717.csv`
5. Confirme o mapeamento de colunas
6. Execute o upload

### Passo 2: Upload Parcelas de Carnê
1. Navegue para `pagamentos.parcelas_carne`
2. Clique em "Insert" → "Upload CSV"
3. Selecione `parcelas_carne_upload_20251106_100717.csv`
4. Confirme o mapeamento de colunas
5. Execute o upload

### Passo 3: Verificação Pós-Upload
Execute estas queries para verificar:

```sql
-- Verificar movimentos importados
SELECT 
    COUNT(*) as total_movimentos,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_movimento) as valor_total,
    MIN(data_movimento) as primeira_data,
    MAX(data_movimento) as ultima_data
FROM pagamentos.movimentos_caixa;

-- Verificar parcelas importadas
SELECT 
    COUNT(*) as total_parcelas,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_parcela) as valor_total,
    MIN(data_pagamento) as primeiro_pagamento,
    MAX(data_pagamento) as ultimo_pagamento
FROM pagamentos.parcelas_carne;

-- Testar views
SELECT * FROM pagamentos.v_pagamentos_basicos LIMIT 5;
SELECT * FROM pagamentos.v_carnes_basico LIMIT 5;
```

## 📊 RESULTADOS ESPERADOS

### Movimentos de Caixa
- **Total:** 6,668 registros
- **Período:** 2020-2023
- **Valor Total:** R$ 654.441,99
- **Clientes únicos:** ~973

### Parcelas de Carnê
- **Total:** 4,911 registros
- **Período:** 2020-2023
- **Valor Total:** R$ 587.659,99
- **Clientes únicos:** ~973

## 🔄 PRÓXIMOS PASSOS (Após Upload)

### 1. Recriar Relacionamentos (Opcional)
```sql
-- Recriar FK se necessário
ALTER TABLE pagamentos.parcelas_carne 
ADD CONSTRAINT fk_parcelas_movimento 
FOREIGN KEY (movimento_caixa_id) 
REFERENCES pagamentos.movimentos_caixa(id);
```

### 2. Popular Resumos de Clientes
```sql
-- População automática via triggers já está ativa
-- Verificar resumos criados
SELECT COUNT(*) FROM pagamentos.resumo_clientes;
```

### 3. Integração com Core
- Relacionar `cliente_uuid` com `core.clientes`
- Relacionar `loja_uuid` com `core.lojas`
- Ajustar views para incluir JOINs

## ✅ VALIDAÇÃO FINAL

### Testes de Integridade
```sql
-- Verificar dados carregados
SELECT 
    'SCHEMA CRIADO' as status,
    EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'pagamentos') as ok;

-- Verificar tabelas populadas
SELECT 
    table_name,
    (SELECT COUNT(*) FROM pagamentos.movimentos_caixa) as movimentos,
    (SELECT COUNT(*) FROM pagamentos.parcelas_carne) as parcelas,
    (SELECT COUNT(*) FROM pagamentos.resumo_clientes) as resumos;
```

## 🎯 SUCESSO!
Após o upload, teremos o **sistema completo de pagamentos** operacional:
- ✅ 6,668 movimentos de caixa normalizados
- ✅ 4,911 parcelas de carnê controladas
- ✅ Schema completo com triggers automáticos
- ✅ Views para consultas otimizadas
- ✅ Base para integração com sistema principal

---
**Data:** 06/11/2025  
**Status:** Pronto para upload nos arquivos CSV  
**Responsável:** Schema pagamentos consolidado