# Guia de Importação de Vendas para o Banco de Dados

## 📋 Visão Geral

Este guia descreve como importar os dados de vendas do arquivo `vendas_oss.csv` para a tabela `vendas.vendas` no banco de dados.

**Arquivo de origem**: `dados_processados/vendas_para_importar/vendas_oss.csv`
**Total de registros**: ~7.549 vendas
**Período**: 2024-2025

## 🎯 Métodos de Importação

### Método 1: SQL Direto (Recomendado para Supabase)

1. **Execute as consultas de verificação** (opcional):
   ```bash
   # Arquivo: queries/verificar_estrutura_vendas.sql
   ```

2. **Execute o script de importação**:
   ```bash
   # Arquivo: scripts/importar_vendas_para_banco.sql
   ```

3. **Passos importantes no script SQL**:
   - ✅ Cria tabela temporária
   - ✅ Carrega dados do CSV (via COPY ou \copy)
   - ✅ Valida dados antes da importação
   - ✅ Insere na tabela definitiva
   - ✅ Verifica resultados

### Método 2: Python (Mais controle e feedback)

1. **Instale as dependências** (se necessário):
   ```bash
   pip install pandas psycopg2-binary
   ```

2. **Configure as credenciais do banco** no arquivo `scripts/importar_vendas_python.py`:
   ```python
   DB_CONFIG = {
       'host': 'seu_host_supabase',
       'port': 5432,
       'database': 'postgres',
       'user': 'postgres',
       'password': 'sua_senha'
   }
   ```

3. **Execute o script**:
   ```bash
   cd 1_normalizacao
   python scripts/importar_vendas_python.py
   ```

4. **O script irá**:
   - Carregar e validar o CSV
   - Mostrar estatísticas dos dados
   - Solicitar confirmação
   - Importar em batches de 500 registros
   - Exibir progresso em tempo real
   - Verificar dados importados

## 📊 Estrutura dos Dados

### Colunas do CSV

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| numero_venda | VARCHAR(50) | ✅ | Número único da venda por loja |
| cliente_id | UUID | ❌ | ID do cliente (pode ser NULL) |
| loja_id | UUID | ✅ | ID da loja |
| vendedor_id | UUID | ❌ | ID do vendedor |
| data_venda | DATE | ✅ | Data da venda |
| valor_total | NUMERIC(12,2) | ✅ | Valor total da venda |
| valor_entrada | NUMERIC(12,2) | ❌ | Valor da entrada (default: 0) |
| nome_cliente_temp | VARCHAR(200) | ❌ | Nome temporário do cliente |
| observacoes | TEXT | ❌ | Observações |
| cancelado | BOOLEAN | ❌ | Se está cancelada (default: false) |
| tipo_operacao | VARCHAR(20) | ❌ | VENDA, GARANTIA, etc. |
| created_by | VARCHAR(100) | ❌ | Criado por (vendedor_id) |

### Validações Automáticas

✅ Valores obrigatórios presentes
✅ Valores não negativos
✅ Entrada <= Total
✅ Lojas existentes no banco
✅ Vendedores existentes
✅ Datas válidas

## 🔍 Validações no Banco

Antes de importar, execute estas consultas para garantir que o banco está pronto:

```sql
-- 1. Tabela vendas está vazia?
SELECT COUNT(*) FROM vendas.vendas;
-- Resultado esperado: 0

-- 2. Todas as lojas existem?
SELECT COUNT(*) FROM core.lojas;
-- Resultado esperado: 6 lojas

-- 3. Vendedores cadastrados?
SELECT COUNT(*) FROM core.vendedores;
-- Resultado esperado: > 0

-- 4. Clientes cadastrados?
SELECT COUNT(*) FROM core.clientes;
-- Resultado esperado: > 0 (para os IDs no CSV)
```

## ⚠️ Pontos de Atenção

### 1. Clientes NULL
- ~117 vendas têm `cliente_id = NULL`
- Isso é permitido pela tabela (cliente_id é opcional)
- Campo `nome_cliente_temp` contém o nome do cliente

### 2. Garantias
- Vendas com `tipo_operacao = 'GARANTIA'`
- Geralmente têm `valor_total = 0`
- São vendas válidas no sistema

### 3. Constraint de Unicidade
- Existe UNIQUE constraint em `(loja_id, numero_venda)`
- Se tentar importar duplicatas, serão ignoradas
- O script usa `ON CONFLICT DO NOTHING`

### 4. Campos Gerados Automaticamente
- `id`: UUID gerado automaticamente
- `valor_restante`: Calculado como (valor_total - valor_entrada)
- `is_garantia`: Calculado a partir de tipo_operacao
- `updated_at`: Timestamp automático

### 5. Triggers
- `trigger_vendas_updated_at`: Atualiza updated_at em UPDATEs
- Desabilitado durante importação para performance
- Reabilitado automaticamente ao final

## 📈 Resultados Esperados

Após a importação bem-sucedida, você verá:

```
✓ Total de vendas importadas: 7.549
✓ Lojas com vendas: 6
✓ Período: 2024-01-25 a 2025-XX-XX
✓ Valor total: R$ X.XXX.XXX,XX

Por Loja:
   Loja 9 (Perus): XXX vendas
   Loja 10 (Suzano 2): XXX vendas
   Loja 11 (Rio Pequeno): XXX vendas
   Loja 12 (São Mateus): XXX vendas
   Loja 42 (Suzano): XXX vendas
   Loja 48 (Mauá): XXX vendas

Por Tipo:
   VENDA: XXX vendas
   GARANTIA: XXX vendas
```

## 🚨 Solução de Problemas

### Erro: "duplicate key value violates unique constraint"
- **Causa**: Já existem vendas com mesmo (loja_id, numero_venda)
- **Solução**: Verifique se já importou antes, ou use DO NOTHING

### Erro: "violates foreign key constraint vendas_loja_id_fkey"
- **Causa**: loja_id não existe em core.lojas
- **Solução**: Verifique os UUIDs das lojas no CSV

### Erro: "violates check constraint vendas_valor_entrada_check"
- **Causa**: valor_entrada negativo ou > valor_total
- **Solução**: Revise os dados do CSV

### Erro: "permission denied"
- **Causa**: Usuário sem permissão na tabela
- **Solução**: Execute com usuário admin ou ajuste permissões

## 📞 Próximos Passos

Após importação bem-sucedida:

1. ✅ Verificar integridade dos dados
2. ✅ Importar formas de pagamento (próxima etapa)
3. ✅ Importar parcelas (próxima etapa)
4. ✅ Importar itens de venda (próxima etapa)
5. ✅ Criar views de análise
6. ✅ Testar consultas e relatórios

## 📝 Logs e Auditoria

O sistema mantém:
- `created_at`: Data/hora da criação (importação)
- `created_by`: Vendedor responsável
- `updated_at`: Última atualização
- `version`: Controle de versão

## ✅ Checklist de Importação

- [ ] Backup do banco realizado
- [ ] Arquivo CSV validado
- [ ] Estrutura do banco verificada
- [ ] Lojas cadastradas
- [ ] Vendedores cadastrados
- [ ] Clientes principais cadastrados
- [ ] Script de importação revisado
- [ ] Importação executada
- [ ] Dados verificados no banco
- [ ] Estatísticas conferidas
- [ ] Logs revisados

---

**Última atualização**: 10/11/2025
**Arquivo**: `1_normalizacao/docs/GUIA_IMPORTACAO_VENDAS.md`
