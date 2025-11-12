# ANÁLISE COMPARATIVA DOS CABEÇALHOS DOS ARQUIVOS DE CLIENTES

## PROBLEMA IDENTIFICADO
Os arquivos têm estruturas completamente diferentes em 2 grupos:

### GRUPO 1: Estrutura "Clássica" (MAUA e SUZANO)
- **Arquivos**: clientes_maua.csv, clientes_suzano.csv
- **Colunas**: 34 colunas
- **Estrutura**: Dados de cadastro clássico da ótica
- **ID Principal**: Coluna `ID`

### GRUPO 2: Estrutura "Normalizada" (PERUS, RIO_PEQUENO, SAO_MATEUS, SUZANO2)
- **Arquivos**: clientes_perus.csv, clientes_rio_pequeno.csv, clientes_sao_mateus.csv, clientes_suzano2.csv
- **Colunas**: 86-87 colunas
- **Estrutura**: Dados normalizados com UUIDs e OS detalhadas
- **ID Principal**: Coluna `cliente_id_x`

## DIFERENÇA CRÍTICA ENCONTRADA
**SUZANO2** tem uma diferença no cabeçalho em relação aos outros do Grupo 2:

### SUZANO2 vs OUTROS DO GRUPO 2
- **PERUS/RIO_PEQUENO/SAO_MATEUS**: Coluna `os_chave` na posição 9
- **SUZANO2**: Coluna `OS N°` na posição 9

## COLUNAS PRINCIPAIS PARA MAPEAMENTO

### GRUPO 1 (MAUA/SUZANO) - 34 colunas
```
['ID', 'Cliente', 'Nome Completo', 'Endereço', 'Bairro', 'Cidade', 'UF', 'CEP', 'Fone', 'E-mail', 'Vendedor', 'Como nos conheceu', 'Sexo', 'loja_id', 'loja_nome', 'loja_uuid', 'data_normalizacao', 'etapa_processamento', 'canal_uuid', 'data_normalizacao_canais', 'vendedor_uuid', 'data_padronizacao_vendedores', 'data_normalizacao_vendedores_final', 'tem_compra', 'total_compras', 'cliente_id_x', 'data_compra', 'total_os', 'match_method', 'confidence', 'data_enriquecimento', 'fonte_enriquecimento', 'cliente_id_y', 'id_legado']
```

### GRUPO 2 (PERUS/RIO_PEQUENO/SAO_MATEUS) - 87 colunas
```
['cliente_id_x', 'cliente_source', 'cliente_nome_normalizado', 'loja_id', 'loja_nome', 'vendedor_uuid', 'vendedor_nome_normalizado', 'canal_captacao_uuid', 'canal_captacao_nome', 'os_chave', 'numero_os', 'LOJA', 'data_compra', 'CONSULTOR', 'VENDA', 'ANEXA À:', 'NOME:', 'data_nascimento', 'CPF', 'RG', 'CEP', 'END:', 'Nº', 'BAIRRO:', 'COMP', 'TELEFONE :', 'CELULAR:', 'EMAIL:', 'previsao_entrega', 'VTA?', 'COMO CONHECEU', 'PONTE', 'HORIZONTAL', 'DIAG MAIOR', 'VERTICAL', 'ESF', 'CIL', 'EIXO', 'DNP', 'ALTURA', 'ESF2', 'CIL3', 'EIXO4', 'DNP5', 'ALTURA6', 'ESF7', 'CIL8', 'EIXO9', 'DNP10', 'ALTURA11', 'ESF12', 'CIL13', 'EIXO14', 'DNP15', 'ALTURA16', 'ADIÇÃO', 'OBS:', 'Cod_trello', 'Descrição', 'Valor', 'Cod17', 'Descrição18', 'Valor19', 'Cod20', 'Descrição21', 'Valor22', 'Cod23', 'Descrição24', 'Valor25', 'Cod26', 'Descrição27', 'Valor28', 'TOTAL', 'PAGTO 1', 'SINAL 1:', 'PAGTO 2', 'SINAL 2:', 'RESTA', 'ARMAÇÃO COM GARANTIA:', 'OBS ARMAÇÃO', 'arquivo_origem', 'OS N°', 'data_normalizacao_ids', 'etapa_processamento', 'loja_processamento', 'cliente_id_y', 'id_legado']
```

### SUZANO2 - 87 colunas (DIFERENÇA na posição 9)
```
['cliente_id_x', 'cliente_source', 'cliente_nome_normalizado', 'loja_id', 'loja_nome', 'vendedor_uuid', 'vendedor_nome_normalizado', 'canal_captacao_uuid', 'canal_captacao_nome', 'OS N°', 'LOJA', 'data_compra', 'CONSULTOR', 'VENDA', 'ANEXA À:', 'NOME:', 'data_nascimento', 'CPF', 'RG', 'CEP', 'END:', 'Nº', 'BAIRRO:', 'COMP', 'TELEFONE :', 'CELULAR:', 'EMAIL:', 'previsao_entrega', 'VTA?', 'COMO CONHECEU', 'PONTE', 'HORIZONTAL', 'DIAG MAIOR', 'VERTICAL', 'ESF', 'CIL', 'EIXO', 'DNP', 'ALTURA', 'ESF2', 'CIL3', 'EIXO4', 'DNP5', 'ALTURA6', 'ESF7', 'CIL8', 'EIXO9', 'DNP10', 'ALTURA11', 'ESF12', 'CIL13', 'EIXO14', 'DNP15', 'ALTURA16', 'ADIÇÃO', 'OBS:', 'Cod_trello', 'Descrição', 'Valor', 'Cod17', 'Descrição18', 'Valor19', 'Cod20', 'Descrição21', 'Valor22', 'Cod23', 'Descrição24', 'Valor25', 'Cod26', 'Descrição27', 'Valor28', 'TOTAL', 'PAGTO 1', 'SINAL 1:', 'PAGTO 2', 'SINAL 2:', 'RESTA', 'ARMAÇÃO COM GARANTIA:', 'OBS ARMAÇÃO', 'arquivo_origem', 'numero_os', 'os_chave', 'data_normalizacao_ids', 'etapa_processamento', 'loja_processamento', 'cliente_id_y', 'id_legado']
```

## MAPEAMENTO NECESSÁRIO

### Colunas Comuns para União:
1. **ID Principal**: 
   - GRUPO 1: `ID` 
   - GRUPO 2: `cliente_id_x`

2. **UUID do Cliente**: 
   - TODOS: `cliente_id_y`

3. **Loja**: 
   - GRUPO 1: `loja_id` (numérico), `loja_uuid` 
   - GRUPO 2: `loja_id` (UUID), `loja_nome`

4. **OS/Chave**: 
   - PERUS/RIO_PEQUENO/SAO_MATEUS: `os_chave` 
   - SUZANO2: `os_chave` (posição diferente)

## SOLUÇÃO PROPOSTA
Criar script que:
1. Identifica automaticamente o tipo de estrutura (Grupo 1 ou 2)
2. Mapeia as colunas principais para nomes padronizados
3. Trata a diferença específica do SUZANO2
4. Une todos em estrutura comum