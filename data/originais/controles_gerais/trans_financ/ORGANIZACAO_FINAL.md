# Organização Trans_Financ - ORDEM DE SERVIÇO PDV

## Estrutura Corrigida e Simplificada

```
trans_financ/
├── 📄 Arquivos CSV originais (40 arquivos mensais)
│   ├── ABR_21.csv, ABR_22.csv, ABR_23.csv
│   ├── AGO_21.csv, AGO_22.csv, AGO_23.csv
│   ├── DEZ_20.csv, DEZ_21.csv, DEZ_22.csv, DEZ_23.csv
│   ├── FEV_21.csv, FEV_22.csv, FEV_23.csv
│   ├── JAN_21.csv, JAN_22.csv, JAN_23.csv
│   ├── JUL_21.csv, JUL_22.csv, JUL_23.csv
│   ├── JUN_21.csv, JUN_22.csv, JUN_23.csv
│   ├── MAI_21.csv, MAI_22.csv, MAI_23.csv
│   ├── MAR_21.csv, MAR_22.csv, MAR_23.csv
│   ├── NOV_20.csv, NOV_21.csv, NOV_22.csv, NOV23.csv
│   ├── OUT_20.csv, OUT_21.csv, OUT_22.csv, OUT_23.csv
│   └── SET_21.csv, SET_22.csv, SET_23.csv
│
├── 📁 trans_financ_consolidado/por_origem/
│   ├── 🍖 ORDEM DE SERVIÇO PDV.csv (10.6M) ← ARQUIVO PRINCIPAL
│   ├── REC. CORRENTISTA.csv (2.3M)
│   ├── SANGRIA.csv (427K)
│   ├── FUNDO DE CAIXA.csv (101K)
│   └── VENDA.csv (49K)
│
└── 📁 separados_por_pagamento/
    ├── 🍖 ordem_servico_pdv_carne_lancaster.csv (3.6M)
    ├── 🔷 ordem_servico_pdv_outros_pagamentos.csv (7.0M)
    ├── 📋 relatorio_separacao_ordem_servico_pdv.json
    └── 📄 RESUMO_ORDEM_SERVICO_PDV.txt
```

## Processamento Realizado

### ✅ Foco: ORDEM DE SERVIÇO PDV
- **Arquivo base**: `trans_financ_consolidado/por_origem/ORDEM DE SERVIÇO PDV.csv`
- **Registros**: 20,863 transações (maior volume)
- **Período**: 2020-2023
- **Valor total**: R$ 5.146.257,94

### 🍖 CARNE LANCASTER
- **Registros**: 6,835 (32.8%)
- **Valor**: R$ 617.242,70 (12.0%)
- **Clientes únicos**: 1,068
- **Variações**: 
  - "CARNE LANCASTER" (6,353)
  - "CARNE LANCASTER                         " (482 - com espaços)

### 🔷 OUTROS PAGAMENTOS
- **Registros**: 14,028 (67.2%)
- **Valor**: R$ 4.529.015,24 (88.0%)
- **Clientes únicos**: 5,844
- **Tipos principais**: DINHEIRO, CREDITO MASTER, CREDITO VISA, DEP. EM CONTA

### 👥 CLIENTES CRUZADOS
- **Clientes que usam ambos tipos**: 790
- **Somente Carne Lancaster**: 278
- **Somente outros pagamentos**: 5,054

## Scripts Utilizados

1. **analisar_ordem_servico_pdv_especifico.py** - Análise inicial
2. **processar_ordem_servico_pdv_separacao.py** - Separação final

## Metodologia Aplicada

### ✅ Base Correta
- Usado arquivo da pasta `por_origem` como solicitado
- Focado apenas no `ORDEM DE SERVIÇO PDV.csv` (principal)
- Removidos processamentos incorretos anteriores

### ✅ Separação Inteligente
- Identificação automática de variações do CARNE LANCASTER
- Preservação de todas as colunas originais (66 campos)
- Análise de sobreposição de clientes

### ✅ Estrutura Limpa
- Mantida organização original em `trans_financ/`
- Pasta `separados_por_pagamento/` para resultados
- Relatórios detalhados e resumos executivos

## Próximos Passos

1. **Integração com Master Clients** - Buscar UUIDs para os clientes
2. **Análise dos outros arquivos** - REC. CORRENTISTA, SANGRIA, etc.
3. **Dashboard especializado** - Diferenciação Carne Lancaster vs Outros
4. **Importação para Supabase** - Tabelas separadas por tipo de pagamento

## Data do Processamento
30 de outubro de 2025 - 22:46

---
**Observação**: Processamento corrigido conforme solicitação para usar apenas a pasta `por_origem` e focar no arquivo principal.