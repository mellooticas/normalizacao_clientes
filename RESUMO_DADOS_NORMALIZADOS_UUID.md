# RESUMO DOS DADOS NORMALIZADOS COM UUID

## Dados Processados com Sucesso

### Total de Registros
- **Originais consolidados**: 7.646 registros
- **Normalizados com UUID**: 5.228 registros  
- **Duplicatas eliminadas**: 2.418 registros (31.62% de consolidação)

### Detalhamento por Loja

| Loja | UUID Supabase | Registros Originais | Normalizados | Duplicatas Eliminadas | Taxa Consolidação |
|------|---------------|--------------------|--------------|-----------------------|-------------------|
| **MAUA** | `9a22ccf1-36fe-4b9f-9391-ca31433dc31e` | 894 | 737 | 157 | 17.6% |
| **PERUS** | `da3978c9-bba2-431a-91b7-970a406d3acf` | 1.070 | 609 | 461 | 43.1% |
| **RIO_PEQUENO** | `4e94f51f-3b0f-4e0f-ba73-64982b870f2c` | 491 | 411 | 80 | 16.3% |
| **SAO_MATEUS** | `1c35e0ad-3066-441e-85cc-44c0eb9b3ab4` | 194 | 171 | 23 | 11.9% |
| **SUZANO2** | `aa7a5646-f7d6-4239-831c-6602fbabb10a` | 342 | 238 | 104 | 30.4% |
| **SUZANO** | `52f92716-d2ba-441a-ac3c-94bdfabd9722` | 4.655 | 3.062 | 1.593 | 34.2% |

## Arquivos Gerados (Prontos para Importação)

### Localização
```
data/originais/oss/normalizadas/
```

### Arquivos
1. `MAUA_normalizado_uuid.csv` - 737 registros
2. `PERUS_normalizado_uuid.csv` - 609 registros  
3. `RIO_PEQUENO_normalizado_uuid.csv` - 411 registros
4. `SAO_MATEUS_normalizado_uuid.csv` - 171 registros
5. `SUZANO2_normalizado_uuid.csv` - 238 registros
6. `SUZANO_normalizado_uuid.csv` - 3.062 registros

## Estrutura dos Dados

### Colunas Incluídas
- **loja_id**: UUID da loja no Supabase (chave estrangeira)
- **loja_nome**: Nome da loja (MAUA, PERUS, etc.)
- **numero_os**: Número da OS
- **os_chave**: Chave única (LOJA_NUMEROOS)
- **Dados do Cliente**: Nome, CPF, RG, telefones, email, endereço
- **Dados da Venda**: Consultor, total, formas de pagamento, observações
- **Dados Técnicos**: Receita, produtos, valores específicos

### Qualidade dos Dados
- ✅ **UUIDs corretos** mapeados do Supabase
- ✅ **Deduplicação inteligente** consolidando informações fragmentadas
- ✅ **Integridade relacional** com core.lojas
- ✅ **Dados limpos** prontos para importação

## Scripts Disponíveis

### Para Importação
- `importar_para_supabase.py` - Script completo para importar para tabelas core.vendas e core.clientes
- `normalizar_os_duplicadas_com_uuid.py` - Script de normalização (já executado)

### Para Consultas
- `consultas_lojas_supabase.sql` - Consultas SQL com mapeamento de lojas

## Próximos Passos

1. **Testar Importação**: Executar `importar_para_supabase.py` em ambiente de teste
2. **Validar Dados**: Verificar integridade após importação
3. **Dashboard**: Criar visualizações dos dados importados
4. **Backup**: Manter cópias dos arquivos normalizados

## Observações Técnicas

- Todos os UUIDs foram validados contra a tabela `core.lojas` do Supabase
- A normalização preserva informações importantes consolidando duplicatas
- Os arquivos estão prontos para importação direta
- Sistema de chaves únicas evita duplicações futuras

---
*Processamento concluído em: 29/10/2025*
*Total de OS únicas identificadas: 5.228*
*Eficiência de consolidação: 31.62%*