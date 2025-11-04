# CONSULTAS VENDEDORES - INSTRUÇÕES PARA EXECUÇÃO

## Consultores Identificados nos Dados

### Ranking por Quantidade de Vendas
1. **BETH**: 641 vendas (65.7% do total)
2. **FELIPE**: 208 vendas (21.3% do total)  
3. **LARISSA**: 58 vendas (5.9% do total)
4. **TATY**: 37 vendas (3.8% do total)
5. **WEVILLY**: 17 vendas (1.7% do total)
6. **ERIKA**: 9 vendas (0.9% do total)
7. **ROGÉRIO**: 5 vendas (0.5% do total)

**Total**: 975 vendas com consultor identificado

## Arquivo de Consultas SQL

📁 **Arquivo**: `consultas_vendedores_supabase.sql`

### Consultas Incluídas

1. **Consulta Básica**: Lista todos os vendedores
2. **Mapeamento**: Associa nomes do Supabase com consultores dos dados
3. **Agrupamento**: Conta vendedores por consultor
4. **Estrutura**: Verifica colunas da tabela
5. **Inativos**: Lista vendedores desativados
6. **JOIN com Lojas**: Associa vendedores às lojas
7. **Resumo**: Estatísticas dos dados

## Como Executar

### 1. Acesse o Supabase SQL Editor
```
https://supabase.com/dashboard/project/[SEU_PROJECT_ID]/sql
```

### 2. Execute as Consultas
- Copie e cole cada consulta do arquivo `consultas_vendedores_supabase.sql`
- Execute uma por vez
- Anote os resultados (especialmente os UUIDs)

### 3. Principais Resultados Esperados

#### Consulta 2 - Mapeamento (mais importante)
```sql
SELECT id, nome, consultor_mapeado FROM core.vendedores...
```
**Resultado esperado**: UUIDs dos vendedores e suas associações

#### Consulta 3 - Agrupamento  
```sql
SELECT consultor_tipo, COUNT(*), STRING_AGG(id::text, ', ') as uuids...
```
**Resultado esperado**: UUIDs agrupados por consultor

## Formato de Resposta Esperado

### Para Cada Consultor Encontrado
```
BETH: uuid-aqui (Nome Real: [nome_completo])
FELIPE: uuid-aqui (Nome Real: [nome_completo])
LARISSA: uuid-aqui (Nome Real: [nome_completo])
etc...
```

## Próximos Passos

1. ✅ Execute as consultas no Supabase
2. ⏳ Copie os UUIDs dos vendedores encontrados
3. ⏳ Atualize o script de normalização com os UUIDs
4. ⏳ Reprocesse os dados incluindo `vendedor_id`
5. ⏳ Importe para Supabase com relações completas

## Casos Especiais

### Se Consultor Não For Encontrado
- Verificar grafias alternativas no Supabase
- Consultor pode estar cadastrado com nome completo
- Pode estar inativo (consulta 5)
- Pode estar em loja diferente (consulta 6)

### Se Encontrar Múltiplos Vendedores para Um Consultor
- Escolher o mais recente (created_at)
- Preferir o ativo
- Considerar a loja principal

---
*Execute as consultas e compartilhe os resultados para continuar o processamento!* 🚀